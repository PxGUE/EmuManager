import sqlite3
import json
from typing import Optional
from pathlib import Path
from core.config import AppConfig

class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Usamos la ruta centralizada definida en core/config.py
            db_path = Path(AppConfig.get_database_path())
        self.db_path = db_path
        # Asegurar que el directorio data/ existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._count_cache = None
        self._init_db()

    def clear_count_cache(self):
        """Invalida el caché de conteo de ROMs."""
        self._count_cache = None

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            timeout=30.0 # Esperar hasta 30s si está bloqueada antes de fallar
        )
        conn.row_factory = sqlite3.Row
        # Habilitar WAL (Write-Ahead Logging) para permitir lectores concurrentes mientras se escribe
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_db(self):
        """Inicializa la base de datos completa de EmuManager."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            self._create_tables(cursor)
            self._apply_migrations(cursor)
            self._create_indexes(cursor)
            conn.commit()

    def _create_tables(self, cursor: sqlite3.Cursor):
        """Crea las tablas básicas de la base de datos."""

        # Tabla: games (Identidad inmutable basada en hash del archivo)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                display_name TEXT,
                platform TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                serial TEXT,
                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla: game_metadata (Scraping y presentacion)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_metadata (
                game_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                developer TEXT,
                publisher TEXT,
                release_date TEXT,
                genre TEXT,
                description TEXT,
                cover_2d_path TEXT,
                cover_3d_path TEXT,
                is_favorite INTEGER DEFAULT 0,
                FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE
            )
        ''')

        # Tabla: play_stats (Telemetría pura local)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS play_stats (
                game_id INTEGER PRIMARY KEY,
                play_time_seconds INTEGER DEFAULT 0,
                last_played_at TIMESTAMP,
                play_count INTEGER DEFAULT 0,
                FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE
            )
        ''')

        # Tabla: emulator_status (Seguimiento de versiones para M.A.N.G.O Sync)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emulator_status (
                emu_id TEXT PRIMARY KEY,
                installed_tag TEXT,
                last_checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                remote_tag TEXT
            )
        ''')

    def _apply_migrations(self, cursor: sqlite3.Cursor):
        """Aplica migraciones individuales para asegurar robustez."""
        for cmd in [
            "ALTER TABLE games ADD COLUMN display_name TEXT",
            "ALTER TABLE games ADD COLUMN serial TEXT",
            "ALTER TABLE game_metadata ADD COLUMN cover_2d_path TEXT",
            "ALTER TABLE game_metadata ADD COLUMN cover_3d_path TEXT",
            "ALTER TABLE game_metadata ADD COLUMN is_favorite INTEGER DEFAULT 0"
        ]:
            try:
                cursor.execute(cmd)
            except sqlite3.OperationalError:
                pass # La columna ya existe

    def _create_indexes(self, cursor: sqlite3.Cursor):
        """Crea índices para optimización de consultas."""
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_platform ON games(platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_filepath ON games(file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_title ON game_metadata(title)")

    def count_all_roms(self) -> int:
        if self._count_cache is not None:
            return self._count_cache

        with self.get_connection() as conn:
            self._count_cache = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
            return self._count_cache

    def get_all_games(self, limit: int = 0):
        """Retorna todos los juegos con su metadata básica (usado para warm-up)."""
        query = '''
            SELECT g.id, g.file_path, g.display_name, g.platform, m.title, m.cover_2d_path as media_path, m.is_favorite
            FROM games g
            LEFT JOIN game_metadata m ON g.id = m.game_id
            LEFT JOIN play_stats s ON g.id = s.game_id
            ORDER BY COALESCE(s.play_time_seconds, 0) DESC, COALESCE(g.display_name, m.title) ASC
        '''
        params = []
        if limit > 0:
            query += " LIMIT ?"
            params.append(limit)
            
        with self.get_connection() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def get_games_by_platform(self, platform: str):
        """Retorna juegos filtrados por plataforma."""
        query = '''
            SELECT g.id, g.file_path, g.display_name, g.platform, m.title, m.cover_2d_path, m.is_favorite
            FROM games g
            LEFT JOIN game_metadata m ON g.id = m.game_id
            LEFT JOIN play_stats s ON g.id = s.game_id
            WHERE g.platform = ?
            ORDER BY COALESCE(s.play_time_seconds, 0) DESC, COALESCE(g.display_name, m.title) ASC
        '''
        with self.get_connection() as conn:
            return [dict(row) for row in conn.execute(query, (platform.lower(),)).fetchall()]

    def search_games(self, search_query: str):
        """Búsqueda instantánea en títulos de la biblioteca."""
        query = '''
            SELECT g.id, g.file_path, g.display_name, g.platform, m.title, m.cover_2d_path, m.is_favorite
            FROM games g
            LEFT JOIN game_metadata m ON g.id = m.game_id
            WHERE g.display_name LIKE ? OR m.title LIKE ?
            ORDER BY COALESCE(g.display_name, m.title) ASC
            LIMIT 100
        '''
        with self.get_connection() as conn:
            return [dict(row) for row in conn.execute(query, (f'%{search_query}%', f'%{search_query}%')).fetchall()]

    def update_game_favorite(self, game_id: int, is_favorite: bool):
        """Marca o desmarca un juego como favorito, creando la entrada en metadata si no existe."""
        val = 1 if is_favorite else 0
        with self.get_connection() as conn:
            # Primero intentamos obtener el título del juego de la tabla principal para el fallback
            row = conn.execute("SELECT display_name, file_path FROM games WHERE id = ?", (game_id,)).fetchone()
            if not row:
                return # El juego no existe en la base de datos

            conn.execute('''
                INSERT INTO game_metadata (game_id, is_favorite, title)
                VALUES (?, ?, ?)
                ON CONFLICT(game_id) DO UPDATE SET is_favorite = excluded.is_favorite
            ''', (game_id, val, ""))
            conn.commit()

    def get_game_titles_map(self, game_ids: list) -> dict:
        """Retorna un mapeo de ID -> display_name para una lista de IDs usando optimización JSON."""
        if not game_ids:
            return {}

        json_ids = json.dumps(list(game_ids))
        query = "SELECT id, display_name FROM games WHERE id IN (SELECT value FROM json_each(?))"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (json_ids,))
            return {row[0]: row[1] for row in cursor.fetchall() if row[1]}

    # --- Métodos de Metadata y Detalles ---
    def get_game_details(self, game_id: int) -> dict:
        """Obtiene todos los detalles y metadatos de un juego específico."""
        query = '''
            SELECT g.id, g.platform, g.display_name, m.title, m.developer, m.publisher, 
                   m.release_date, m.genre, m.description, 
                   m.cover_2d_path, m.cover_3d_path, m.is_favorite
            FROM games g
            LEFT JOIN game_metadata m ON g.id = m.game_id
            WHERE g.id = ?
        '''
        with self.get_connection() as conn:
            row = conn.execute(query, (game_id,)).fetchone()
            if not row:
                return {}
            
            display_title = row[3] or row[2]
            return {
                "id": row[0],
                "platform": row[1],
                "title": display_title,
                "developer": row[4] or "",
                "publisher": row[5] or "",
                "release_date": row[6] or "",
                "genre": row[7] or "",
                "description": row[8] or "",
                "cover2d": (row[9] or "").replace("\\", "/"),
                "cover3d": (row[10] or "").replace("\\", "/"),
                "isFavorite": bool(row[11])
            }

    def update_metadata(self, game_id: int, data: dict):
        """Actualiza manualmente los metadatos de un juego."""
        query = """
            INSERT INTO game_metadata (
                game_id, title, developer, publisher, release_date, 
                genre, description, cover_2d_path, cover_3d_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(game_id) DO UPDATE SET
                title = excluded.title,
                developer = excluded.developer,
                publisher = excluded.publisher,
                release_date = excluded.release_date,
                genre = excluded.genre,
                description = excluded.description,
                cover_2d_path = excluded.cover_2d_path,
                cover_3d_path = excluded.cover_3d_path
        """
        with self.get_connection() as conn:
            conn.execute(query, (
                game_id,
                data.get("title", ""),
                data.get("developer", ""),
                data.get("publisher", ""),
                data.get("releaseDate", ""),
                data.get("genre", ""),
                data.get("description", ""),
                data.get("cover2d", ""),
                data.get("cover3d", "")
            ))
            conn.commit()

    # --- Métodos de Orchestrator (Lanzamiento y Random) ---
    def get_random_game(self) -> Optional[int]:
        """Obtiene un game_id aleatorio de toda la biblioteca."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT id FROM games ORDER BY RANDOM() LIMIT 1").fetchone()
            return row["id"] if row else None

    def get_random_game_by_platform(self, platform: str) -> Optional[int]:
        """Obtiene un game_id aleatorio de una plataforma específica."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT id FROM games WHERE platform = ? ORDER BY RANDOM() LIMIT 1", (platform.lower(),)).fetchone()
            return row["id"] if row else None

    def get_game_path_and_platform(self, game_id: int) -> Optional[tuple]:
        """Devuelve (file_path, platform) para un juego."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT file_path, platform FROM games WHERE id = ?", (game_id,)).fetchone()
            return (row["file_path"], row["platform"]) if row else None

    def get_game_name(self, game_id: int) -> Optional[str]:
        """Devuelve el nombre para mostrar de un juego."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT display_name FROM games WHERE id = ?", (game_id,)).fetchone()
            return row["display_name"] if row else None

    # --- Métodos de Estadísticas (Play Stats) ---
    def get_play_stats(self, query_type: str, limit: int = 6) -> list:
        """Consultas genéricas de telemetría y datos recientes."""
        if query_type == "recent":
            query = """
                SELECT g.id, g.platform, m.title, m.release_date, m.cover_2d_path
                FROM play_stats ps
                JOIN games g ON ps.game_id = g.id
                LEFT JOIN game_metadata m ON g.id = m.game_id
                ORDER BY ps.last_played_at DESC
                LIMIT ?
            """
        elif query_type == "most_played":
            query = """
                SELECT g.id, g.platform, m.title, m.cover_2d_path
                FROM play_stats ps
                JOIN games g ON ps.game_id = g.id
                LEFT JOIN game_metadata m ON g.id = m.game_id
                ORDER BY ps.play_time_seconds DESC
                LIMIT ?
            """
        elif query_type == "random_covers":
            query = """
                SELECT g.id, m.cover_2d_path as cover
                FROM games g
                JOIN game_metadata m ON g.id = m.game_id
                WHERE m.cover_2d_path IS NOT NULL AND m.cover_2d_path != ''
                ORDER BY RANDOM()
                LIMIT ?
            """
        else:
            return []

        with self.get_connection() as conn:
            return [dict(row) for row in conn.execute(query, (limit,)).fetchall()]

    # --- Métodos de Sync / Emuladores ---
    def get_emulator_status(self) -> list:
        with self.get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT emu_id, installed_tag, remote_tag FROM emulator_status").fetchall()]

    def update_emulator_local_tag(self, emu_id: str, tag: str):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO emulator_status (emu_id, installed_tag, last_checked_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(emu_id) DO UPDATE SET 
                    installed_tag=excluded.installed_tag, 
                    last_checked_at=CURRENT_TIMESTAMP
            """, (emu_id, tag))
            conn.commit()

    def update_emulator_remote_tag(self, emu_id: str, tag: str):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO emulator_status (emu_id, remote_tag, last_checked_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(emu_id) DO UPDATE SET 
                    remote_tag=excluded.remote_tag, 
                    last_checked_at=CURRENT_TIMESTAMP
            """, (emu_id, tag))
            conn.commit()

    def get_discovery_data(self, today_md: str) -> dict:
        """Genera el contenido para el 'Discovery Hub'."""
        discovery = {
            "on_this_day": [],
            "hidden_gems": [],
            "random_batch": []
        }
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. On This Day (Mismo mes y día)
            cursor.execute("""
                SELECT g.id, g.platform, m.title, m.release_date, m.cover_2d_path
                FROM games g
                JOIN game_metadata m ON g.id = m.game_id
                WHERE m.release_date LIKE ?
                LIMIT 10
            """, (f"%{today_md}",))
            discovery["on_this_day"] = [dict(row) for row in cursor.fetchall()]
            
            # 2. Hidden Gems (0 Playtime, pero tienen metadata y buena descripción)
            cursor.execute("""
                SELECT g.id, g.platform, m.title, m.cover_2d_path
                FROM games g
                JOIN game_metadata m ON g.id = m.game_id
                LEFT JOIN play_stats s ON g.id = s.game_id
                WHERE (s.play_time_seconds IS NULL OR s.play_time_seconds = 0)
                  AND m.description IS NOT NULL AND length(m.description) > 100
                ORDER BY RANDOM()
                LIMIT 10
            """)
            discovery["hidden_gems"] = [dict(row) for row in cursor.fetchall()]
            
            # 3. Random Visual Batch (Para el muro 3D)
            cursor.execute("""
                SELECT g.id, m.cover_2d_path as cover
                FROM games g
                JOIN game_metadata m ON g.id = m.game_id
                WHERE m.cover_2d_path IS NOT NULL AND m.cover_2d_path != ''
                ORDER BY RANDOM()
                LIMIT 40
            """)
            discovery["random_batch"] = [dict(row) for row in cursor.fetchall()]
            
        return discovery

    def update_play_stats(self, game_id: int, duration: int):
        if duration < 1: return
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO play_stats (game_id, play_time_seconds, last_played_at, play_count)
                VALUES (?, ?, CURRENT_TIMESTAMP, 1)
                ON CONFLICT(game_id) DO UPDATE SET
                    play_time_seconds = play_time_seconds + excluded.play_time_seconds,
                    last_played_at = CURRENT_TIMESTAMP,
                    play_count = play_count + 1
            """, (game_id, duration))
            conn.commit()

    def save_installed_tags_batch(self, tag_map: dict):
        if not tag_map: return
        with self.get_connection() as conn:
            data = [(emu_id, tag) for emu_id, tag in tag_map.items()]
            conn.executemany("""
                INSERT INTO emulator_status (emu_id, installed_tag, last_checked_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(emu_id) DO UPDATE SET
                    installed_tag = excluded.installed_tag,
                    last_checked_at = CURRENT_TIMESTAMP
            """, data)
            conn.commit()

    def save_remote_tags_batch(self, tag_map: dict):
        if not tag_map: return
        with self.get_connection() as conn:
            data = [(emu_id, tag) for emu_id, tag in tag_map.items()]
            conn.executemany("""
                INSERT INTO emulator_status (emu_id, remote_tag, last_checked_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(emu_id) DO UPDATE SET
                    remote_tag = excluded.remote_tag,
                    last_checked_at = CURRENT_TIMESTAMP
            """, data)
            conn.commit()


