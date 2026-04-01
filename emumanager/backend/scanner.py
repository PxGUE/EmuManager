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
        [NATIVE ENGINE] Escanea y registra juegos directamente en la BD usando M.A.N.G.O (Rust).
        Esta solución es de alto rendimiento, libera el GIL y evita cualquier congelamiento.
        """
        if not directory_path or not mango_engine:
            EmuLog.error("Entorno no preparado para escaneo nativo.")
            return 0

        extensions = self.SUPPORTED_EXTENSIONS
        db_path = str(self.db.db_path)

        try:
            # Delegamos TODO el trabajo pesado (escaneo, MD5 y escritura DB) a Rust.
            # Rust reportará el progreso directamente a través de los callbacks.
            new_games_count = mango_engine.scan_directory_to_db(
                db_path,
                directory_path,
                extensions,
                progress_callback,
                status_callback
            )
            
            EmuLog.info(f"Escaneo Nativo Finalizado. {new_games_count} juegos nuevos registrados.")
            return new_games_count

        except Exception as e:
            EmuLog.error(f"Error fatal en Escaneo Nativo M.A.N.G.O: {e}")
            return 0

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
