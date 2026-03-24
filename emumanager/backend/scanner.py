try:
    import mango_engine
except ImportError:
    mango_engine = None
import zipfile
from typing import List, Dict, Any, Callable, Optional
from pathlib import Path
from backend.database import DatabaseManager
from core.config import AppConfig
from core.logger import EmuLog

class ScannerManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # Mapeo EXTENSIÓN -> PLATAFORMA (Uso como fallback)
        self.platform_map = {
            "snes": ["smc", "sfc", "fig", "swc"],
            "nes": ["nes", "fds"],
            "gb": ["gb"],
            "gba": ["gba"],
            "gbc": ["gbc"],
            "n64": ["z64", "n64", "v64"],
            "ps1": ["iso", "bin", "cue", "img", "mdf", "pbp"],
            "ps2": ["iso", "bin", "cue", "gz", "chd"],
            "psp": ["iso", "cso", "pbp"],
            "ds": ["nds"],
            "gc": ["iso", "gcm", "rvz"],
            "wii": ["iso", "wbfs", "rvz"],
            "megadrive": ["md", "gen", "bin", "smd"],
            "mastersystem": ["sms"],
            "gamegear": ["gg"],
            "dreamcast": ["cdi", "gdi", "chd"]
        }

        # Mapeo DIRECTORIO -> PLATAFORMA (Prioridad Máxima)
        self.alias_map = {
            "snes": ["snes", "super nintendo", "super famicom", "sfc"],
            "nes": ["nes", "nintendo entertainment system", "famicom"],
            "gb": ["gb", "gameboy", "game boy"],
            "gba": ["gba", "gameboy advance", "game boy advance"],
            "gbc": ["gbc", "gameboy color", "game boy color"],
            "n64": ["n64", "nintendo 64"],
            "ps1": ["ps1", "playstation", "psx"],
            "ps2": ["ps2", "playstation 2", "ps2 iso"],
            "psp": ["psp", "playstation portable"],
            "ds": ["ds", "nintendo ds", "nds"],
            "gc": ["gc", "gamecube", "game cube"],
            "wii": ["wii"],
            "megadrive": ["megadrive", "genesis", "sega genesis", "md"],
            "mastersystem": ["mastersystem", "master system", "sms"],
            "gamegear": ["gamegear", "game gear"],
            "dreamcast": ["dreamcast", "dc"]
        }

    def _get_platform_from_path(self, file_path: Path) -> Optional[str]:
        """Intenta deducir la plataforma basándose en los nombres de las carpetas superiores."""
        # Revisamos los dos últimos niveles de directorios (padre y abuelo)
        parts_to_check = [file_path.parent.name.lower()]
        if len(file_path.parents) > 1:
            parts_to_check.append(file_path.parents[1].name.lower())
            
        for part in parts_to_check:
            for platform, aliases in self.alias_map.items():
                if part in aliases:
                    return platform
        return None

    def _peek_zip_platform(self, zip_path: str) -> str:
        """Mira dentro de un .zip (solo nombres de archivo) para deducir la plataforma."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Obtenemos la primera extensión válida que encontremos dentro
                for info in z.infolist():
                    if info.is_dir(): continue
                    ext = Path(info.filename).suffix.lower().replace(".", "")
                    platform = self._get_platform_from_ext(ext)
                    if platform != "unknown":
                        return platform
        except Exception:
            pass
        return "unknown"

    def _get_platform_from_ext(self, ext: str) -> str:
        ext = ext.lower().replace(".", "")
        for platform, exts in self.platform_map.items():
            if ext in exts:
                return platform
        return "unknown"

    def scan_and_register(self, directory_path: str, progress_callback: Optional[Callable[[float], None]] = None, status_callback: Optional[Callable[[str], None]] = None, is_active_check: Optional[Callable[[], bool]] = None):
        """
        Escanea un directorio usando el motor de Rust y registra los juegos.
        Reporta el progreso a través de los callbacks proporcionados.
        """
        if not directory_path:
            return 0

        extensions = []
        for exts in self.platform_map.values():
            extensions.extend(exts)
        extensions.append("zip") # Incluir ZIP siempre
        extensions = list(set(extensions))

        if status_callback: status_callback("Escaneando archivos con motor Rust...")
        
        # Invocación al motor de RUST
        if mango_engine:
            # El motor M.A.N.G.O. (Multithreaded Asynchronous Native Game Orchestrator)
            # se encarga del heavy lifting en paralelo
            raw_results = mango_engine.scan_directory(directory_path, extensions)
        else:
            EmuLog.error("El motor M.A.N.G.O. no está disponible. No se puede escanear el directorio.")
            return 0

        total_files = len(raw_results)
        
        if total_files == 0:
            if status_callback: status_callback("No se encontraron ROMs soportadas.")
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
                
                # --- ESTRATEGIA DE CLASIFICACIÓN MULTI-CAPA ---
                # 1. Prioridad: ¿La carpeta nos dice qué es?
                platform = self._get_platform_from_path(f_path)
                
                # 2. Si no sabemos por carpeta, ¿es un ZIP?
                if not platform and f_ext == "zip":
                    platform = self._peek_zip_platform(f_path_str)
                
                # 3. Fallback: ¿La extensión nos dice qué es?
                if not platform or platform == "unknown":
                    platform = self._get_platform_from_ext(f_ext)
                
                game_title = f_path.stem

                # Reportar progreso a la UI
                if progress_callback:
                    progress_callback( (index + 1) / total_files )
                if status_callback and index % 5 == 0: # Reportar cada 5 juegos para no saturar
                    status_callback(f"Registrando: {game_title}")
                
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO games (file_hash, file_path, platform, file_size)
                        VALUES (?, ?, ?, ?)
                    ''', (f_hash, f_path_str, platform, f_size))
                    
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

    def scrape_missing_metadata(self, interrupt_flag, progress_callback: Optional[Callable[[float], None]] = None, status_callback: Optional[Callable[[str], None]] = None):
        """
        Busca metadatos y portadas (2D/3D) para las ROMs que aún no tengan.
        Usa el motor M.A.N.G.O (Rust) para peticiones de ultra-baja latencia.
        Delegate native interruption to Rust via 'interrupt_flag'.
        """
        if not mango_engine:
            EmuLog.error("El motor M.A.N.G.O. no está disponible para el scraping.")
            return 0
            
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Obtenemos juegos sin portada 2d
            cursor.execute('''
                SELECT g.id, g.file_hash, g.platform, g.file_path, g.file_size, m.title
                FROM games g
                JOIN game_metadata m ON g.id = m.game_id
                WHERE m.cover_2d_path IS NULL OR m.cover_2d_path = ''
            ''')
            pending = cursor.fetchall()
            
        if not pending:
            EmuLog.info("Todos los juegos tienen todos sus metadatos al día.")
            return 0
            
        total = len(pending)
        success_count = 0
        
        ss_id = AppConfig.get_screenscraper_user()
        ss_pass = AppConfig.get_screenscraper_pass()
        
        import json
        
        for index, row in enumerate(pending):
            game_id = row["id"]
            md5_hash = row["file_hash"]
            file_path = row["file_path"]
            platform = row["platform"]
            original_title = row["title"]
            
            # Map platform to ScreenScraper System ID (Principales)
            sys_id_map = {
                "gba": "12", "snes": "4", "nes": "3", "n64": "14", 
                "gb": "9", "gbc": "10", "megadrive": "1", "mastersystem": "2",
                "gamegear": "21", "ps1": "57", "ps2": "58", "psp": "61", 
                "gc": "38", "wii": "5", "ds": "15", "dreamcast": "16"
            }
            system_id = sys_id_map.get(platform.lower(), "")
            filename = Path(file_path).name
            media_dir = str(AppConfig.get_media_dir(platform, ""))
            
            if status_callback: status_callback(f"Buscando portadas para: {original_title}")
            
            try:
                # El motor de Rust ahora recibe el 'interrupt_flag' directamente
                json_str = mango_engine.scrape_game_metadata(
                    interrupt_flag, md5_hash, "", filename, system_id, ss_id, ss_pass, media_dir
                )
                
                if json_str and json_str != "{}" and json_str != "null":
                    meta = json.loads(json_str)
                    title = meta.get("title") or original_title
                    
                    with self.db.get_connection() as conn:
                        c = conn.cursor()
                        c.execute('''
                            UPDATE game_metadata SET
                                title = ?, developer = ?, publisher = ?,
                                release_date = ?, genre = ?, description = ?,
                                cover_2d_path = ?, cover_3d_path = ?
                            WHERE game_id = ?
                        ''', (title, meta.get("developer"), meta.get("publisher"), 
                              meta.get("release_date"), meta.get("genre"), meta.get("description"), 
                              meta.get("cover_2d_path"), meta.get("cover_3d_path"), game_id))
                        conn.commit()
                        
                    success_count += 1
                    EmuLog.info(f"[MANGO] Scrapeado: {title}")
                else:
                    if interrupt_flag: EmuLog.info(f"[MANGO] Operación abortada o sin resultados para: {original_title}")
            except Exception as e:
                EmuLog.error(f"[MANGO] Error scraping {original_title}: {e}")
                
            if progress_callback:
                progress_callback( (index + 1) / float(total) )
                
        return success_count
