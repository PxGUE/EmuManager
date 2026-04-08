import sqlite3
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
        # Tabla: scan_paths
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

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

            fallback_title = row["display_name"] or Path(row["file_path"]).stem
            
            conn.execute('''
                INSERT INTO game_metadata (game_id, is_favorite, title)
                VALUES (?, ?, ?)
                ON CONFLICT(game_id) DO UPDATE SET is_favorite = excluded.is_favorite
            ''', (game_id, val, fallback_title))
            conn.commit()
