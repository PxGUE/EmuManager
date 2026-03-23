import core_scanner
from typing import List, Dict, Any, Callable, Optional
from pathlib import Path
from backend.database import DatabaseManager
from core.config import AppConfig
from core.logger import EmuLog

class ScannerManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        # Extensiones comunes por plataforma
        self.platform_map = {
            "snes": ["smc", "sfc", "fig"],
            "nes": ["nes"],
            "gb": ["gb"],
            "gba": ["gba"],
            "gbc": ["gbc"],
            "n64": ["z64", "n64", "v64"],
            "ps1": ["iso", "bin", "cue", "img"],
            "megadrive": ["md", "gen", "bin"]
        }

    def _get_all_extensions(self) -> List[str]:
        all_exts = []
        for exts in self.platform_map.values():
            all_exts.extend(exts)
        return list(set(all_exts))

    def _get_platform_from_ext(self, ext: str) -> str:
        ext = ext.lower().replace(".", "")
        for platform, exts in self.platform_map.items():
            if ext in exts:
                return platform
        return "unknown"

    def scan_and_register(self, directory_path: str, progress_callback: Optional[Callable[[float], None]] = None, status_callback: Optional[Callable[[str], None]] = None):
        """
        Escanea un directorio usando el motor de Rust y registra los juegos.
        Reporta el progreso a través de los callbacks proporcionados.
        """
        if not directory_path:
            return 0

        extensions = self._get_all_extensions()
        if status_callback: status_callback("Escaneando archivos con motor Rust...")
        
        # Invocación al motor de RUST (Esto es lo más rápido)
        raw_results = core_scanner.scan_directory(directory_path, extensions)
        total_files = len(raw_results)
        
        if total_files == 0:
            if status_callback: status_callback("No se encontraron ROMs soportadas.")
            return 0

        new_games_count = 0
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            for index, item in enumerate(raw_results):
                f_path = item["path"]
                f_hash = item["md5"]
                f_size = item["size"]
                f_ext = Path(f_path).suffix
                platform = self._get_platform_from_ext(f_ext)
                game_title = Path(f_path).stem

                # Reportar progreso a la UI
                if progress_callback:
                    progress_callback( (index + 1) / total_files )
                if status_callback and index % 5 == 0: # Reportar cada 5 juegos para no saturar
                    status_callback(f"Registrando: {game_title}")
                
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO games (file_hash, file_path, platform, file_size)
                        VALUES (?, ?, ?, ?)
                    ''', (f_hash, f_path, platform, f_size))
                    
                    if cursor.rowcount > 0:
                        new_games_count += 1
                        game_id = cursor.lastrowid
                        cursor.execute('''
                            INSERT OR IGNORE INTO game_metadata (game_id, title)
                            VALUES (?, ?)
                        ''', (game_id, game_title))
                except Exception as e:
                    EmuLog.error(f"Error al registrar {f_path}: {e}")
            
            conn.commit()
            
        EmuLog.info(f"Escaneo finalizado. {new_games_count} juegos nuevos registrados.")
        return new_games_count
