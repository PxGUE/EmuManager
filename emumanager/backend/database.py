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
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Inicializa la base de datos completa de EmuManager."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
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
                    platform TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
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
                    cover_image_path TEXT,
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
            
            conn.commit()
