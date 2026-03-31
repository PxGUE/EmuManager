try:
    import mango_engine
except ImportError:
    mango_engine = None
from typing import Callable, Optional
from pathlib import Path
from backend.database import DatabaseManager
from core.config import AppConfig
from core.logger import EmuLog

class ScannerManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # Lista estática de extensiones de ROMs soportadas (las plataformas en sí, las infiere M.A.N.G.O)
        self.SUPPORTED_EXTENSIONS = [
            "smc", "sfc", "fig", "swc", "nes", "fds", "gb", "gba", "gbc", 
            "z64", "n64", "v64", "iso", "bin", "cue", "img", "mdf", "pbp", 
            "gz", "chd", "cso", "nds", "gcm", "rvz", "wbfs", "md", "gen", 
            "smd", "sms", "gg", "cdi", "gdi", "zip"
        ]

    def scan_and_register(self, directory_path: str, progress_callback: Optional[Callable[[float], None]] = None, status_callback: Optional[Callable[[str], None]] = None, is_active_check: Optional[Callable[[], bool]] = None):
        """
        Escanea un directorio usando el motor de Rust y registra los juegos.
        Reporta el progreso a través de los callbacks proporcionados.
        """
        if not directory_path:
            return 0

        extensions = self.SUPPORTED_EXTENSIONS

        if status_callback: status_callback("scan_starting")
        
        # Invocación al motor M.A.N.G.O
        if mango_engine:
            raw_results = mango_engine.scan_directory(directory_path, extensions)
        else:
            EmuLog.error("El motor M.A.N.G.O. no está disponible. No se puede escanear el directorio.")
            return 0

        total_files = len(raw_results)
        
        if total_files == 0:
            if status_callback: status_callback("scan_no_roms")
            return 0

        new_games_count = 0
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            for index, item in enumerate(raw_results):
                # Chequeo de interrupción rápido
                if is_active_check and not is_active_check():
                    EmuLog.info("Escaneo abortado por solicitud del sistema.")
                    break

                f_path_str = item["path"]
                f_path = Path(f_path_str)
                f_hash = item["md5"]
                f_size = item["size"]
                f_ext = f_path.suffix.lower().replace(".", "")
                
                platform = item.get("platform", "unknown")
                
                display_name = item.get("display_name", f_path.stem)

                # Reportar progreso a la UI
                if progress_callback:
                    progress_callback( (index + 1) / total_files )
                if status_callback and index % 5 == 0: # Reportar cada 5 juegos para no saturar
                    status_callback(f"scan_registering|{display_name}")
                
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO games (file_hash, file_path, display_name, platform, file_size)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (f_hash, f_path_str, display_name, platform, f_size))
                    
                    if cursor.rowcount > 0:
                        new_games_count += 1
                        game_id = cursor.lastrowid
                        cursor.execute('''
                            INSERT OR IGNORE INTO game_metadata (game_id, title)
                            VALUES (?, ?)
                        ''', (game_id, display_name)) # Ahora usamos display_name también en metadata title
                except Exception as e:
                    EmuLog.error(f"Error al registrar {f_path}: {e}")
            
            conn.commit()
            
        EmuLog.info(f"Escaneo finalizado. {new_games_count} juegos nuevos registrados.")
        return new_games_count

    def scrape_missing_metadata(self, progress_callback: Optional[Callable[[float], None]] = None, status_callback: Optional[Callable[[str], None]] = None):
        """
        Busca metadatos y portadas (2D/3D) para las ROMs que aún no tengan.
        Usa el motor M.A.N.G.O para peticiones de ultra-baja latencia.
        """
        if not mango_engine:
            EmuLog.error("El motor M.A.N.G.O. no está disponible para el scraping.")
            return 0
            
        ss_id = AppConfig.get_screenscraper_user()
        ss_pass = AppConfig.get_screenscraper_pass()
        
        db_path = str(AppConfig.get_database_path())
        roms_path = AppConfig.get_roms_path()
        if not roms_path:
            return 0
            
        project_root = Path(__file__).parent.parent.parent
        media_base = str(project_root / "data" / "media")
        
        if status_callback: status_callback("scrape_starting")
        
        try:
            import os
            dev_id = os.getenv("SS_DEV_ID", "")
            dev_pass = os.getenv("SS_DEV_PASS", "")

            success_count = mango_engine.start_batch_scrape(
                db_path,
                ss_id,
                ss_pass,
                dev_id,
                dev_pass,
                media_base,
                progress_callback
            )
            
            if status_callback:
                status_callback("scrape_finished")
                
            return success_count
        except Exception as e:
            EmuLog.error(f"[MANGO] Error fatal en Batch Scraper: {e}")
            return 0
