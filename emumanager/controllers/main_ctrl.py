from pathlib import Path
from PySide6.QtCore import QObject, Slot, Signal, QThread
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QFileDialog
from core.security import CredentialsManager
from core.config import AppConfig
from core.logger import EmuLog
from backend.database import DatabaseManager
from backend.scanner import ScannerManager
import sys
import os

QML_IMPORT_NAME = "EmuManager.Controllers"
QML_IMPORT_MAJOR_VERSION = 1

class ScanWorker(QObject):
    """Trabajador que ejecuta el escaneo en un hilo separado."""
    finished = Signal(int)
    progress = Signal(float)
    status = Signal(str)

    def __init__(self, scanner_manager, directory: str):
        super().__init__()
        self.scanner = scanner_manager
        self.directory = directory
        self._is_active = True

    @Slot()
    def stop(self):
        self._is_active = False

    @Slot()
    def run(self):
        try:
            count = self.scanner.scan_and_register(
                self.directory,
                progress_callback=self.progress.emit,
                status_callback=self.status.emit,
                is_active_check=lambda: self._is_active
            )
            self.finished.emit(count)
        except Exception as e:
            EmuLog.error(f"Error fatal en hilo de escaneo: {e}")
            self.finished.emit(0)


class ScrapeWorker(QObject):
    finished = Signal(int)
    progress = Signal(float)
    status = Signal(str)

    def __init__(self, scanner_manager):
        super().__init__()
        self.scanner = scanner_manager
        self._is_active = True

    @Slot()
    def stop(self):
        self._is_active = False

    @Slot()
    def run(self):
        try:
            # Nuevo callback que recibe (progreso, status_text) desde Rust
            def _handle_progress(p, s=None):
                self.progress.emit(p)
                if s: self.status.emit(s)

            count = self.scanner.scrape_missing_metadata(
                self._is_active, 
                progress_callback=_handle_progress,
                status_callback=self.status.emit
            )
            self.finished.emit(count)
        except Exception as e:
            EmuLog.error(f"Error fatal en hilo de scraping: {e}")
            self.finished.emit(0)

class CoreDownloadWorker(QObject):
    finished = Signal(str)
    progress = Signal(float)
    status = Signal(str)

    def __init__(self, libretro_manager, core_name: str):
        super().__init__()
        self.libretro = libretro_manager
        self.core_name = core_name

    @Slot()
    def run(self):
        try:
            self.status.emit(f"Descargando {self.core_name} usando M.A.N.G.O (Rust)...")
            # El progress callback llamará self.progress.emit(p)
            def progress_cb(p: float):
                self.progress.emit(p)
                
            path = self.libretro.download_core(self.core_name, progress_cb)
            if path:
                self.status.emit("¡Core instalado!")
                self.finished.emit(path)
            else:
                self.status.emit("Fallo en la descarga.")
                self.finished.emit("")
        except Exception as e:
            EmuLog.error(f"Error fatal descargando core: {e}")
            self.status.emit("Error en la instalación.")
            self.finished.emit("")

from backend.libretro import LibretroManager, CORE_DATABASE

@QmlElement
class MainController(QObject):
    # Señales para comunicación con QML en tiempo real
    scanProgressChanged = Signal(float)  # 0.0 a 1.0
    scanStatusChanged = Signal(str)      # "Escanenando..." "Listo"
    scanFinished = Signal(int)           # Juegos encontrados
    scrapeProgressChanged = Signal(float) # 0.0 a 1.0
    scrapeStatusChanged = Signal(str)     # "Scrapeando..." "Listo"
    scrapeFinished = Signal(int)         # Descargas realizadas
    gamesUpdated = Signal()               # Emitir cuando se agreguen/actualicen juegos
    gamesCountChanged = Signal()          # Notificar cuando cambie el total de juegos
    
    # Señales para descarga de Cores
    coreDownloadProgressChanged = Signal(float)
    coreDownloadStatusChanged = Signal(str)
    coreDownloadFinished = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- ASEGURAR QUE EL BACKEND ESTÁ EN EL PATH ---
        backend_dir = Path(__file__).resolve().parent.parent / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
            
        try:
            self.db = DatabaseManager()
            self.scanner = ScannerManager(self.db)
            self.libretro = LibretroManager(Path(AppConfig.get_cores_path() or "."))
            self._scan_thread = None
            self._scan_worker = None
            self._scrape_thread = None
            self._scrape_worker = None
            self._core_thread = None
            self._core_worker = None
            self._cached_summary = None 
            self._is_precharged = False # Flag para evitar re-carga redundante
        except (ImportError, ModuleNotFoundError) as e:
            EmuLog.error(f"Error de dependencia en MainController: No se pudo importar un módulo crítico: {e}")
        except PermissionError as e:
            EmuLog.error(f"Error de permisos al inicializar el backend: No se puede acceder a la base de datos o directorios: {e}")
        except Exception as e:
            EmuLog.error(f"Fallo crítico inesperado al inicializar el backend de MainController: {e}")

    @Slot()
    def proactive_background_load(self):
        """
        Carga proactiva inteligente. Sólo se ejecuta una vez.
        """
        if self._is_precharged:
            return
            
        try:
            db_path = AppConfig.get_database_path()
            EmuLog.info(f"M.A.N.G.O: Inicializando puente con backend en {db_path}")
            
            # Verificación del motor nativo e inicialización de logs
            try:
                import mango_engine
                
                # BRIDGE DE LOGS: Redirigir logs de Rust a EmuLog de Python
                def _mango_log_bridge(level, msg):
                    if level == "INFO": EmuLog.info(f"M.A.N.G.O: {msg}")
                    elif level == "ERROR": EmuLog.error(f"M.A.N.G.O: {msg}")
                    elif level == "WARN": EmuLog.warning(f"M.A.N.G.O: {msg}")
                    else: EmuLog.debug(f"M.A.N.G.O: {msg}")
                
                mango_engine.set_log_callback(_mango_log_bridge)
                EmuLog.info("M.A.N.G.O: Motor nativo Rust y sistema de logs sincronizado.")
            except ImportError:
                EmuLog.warning("M.A.N.G.O: Motor Rust no encontrado. Operando en modo degradado (Python-only).")

            EmuLog.info("M.A.N.G.O: Generando caché de consolas...")
            self._cached_summary = self.get_consoles_summary(use_cache=False)
            
            # Notificar que los juegos están listos
            self.gamesUpdated.emit()
            
            self._is_precharged = True
            EmuLog.info("M.A.N.G.O: Pre-carga completada con éxito.")
        except ImportError:
            EmuLog.warning("M.A.N.G.O: Motor Rust (mango_engine) no encontrado en el sistema. Operando en modo degradado (Python-only).")
        except Exception as e:
            EmuLog.error(f"Error inesperado durante la carga proactiva de M.A.N.G.O: {str(e)}")

    # --- Gestión de Credenciales ---
    @Slot(str, str)
    def saveScreenScraperCredentials(self, username, password):
        EmuLog.info(f"Guardando credenciales para ScreenScraper: {username}")
        CredentialsManager.save_user_password("screenscraper", username, password)

    # --- Gestión de Rutas de Configuración ---
    @Slot(result=str)
    def select_roms_directory(self):
        """Abre un diálogo nativo para seleccionar la carpeta de juegos."""
        directory = QFileDialog.getExistingDirectory(
            None, "Seleccionar Carpeta de ROMs", AppConfig.get_roms_path() or ""
        )
        if directory:
            AppConfig.set_roms_path(directory)
            EmuLog.info(f"Configurada nueva ruta de ROMs: {directory}")
            return directory
        return AppConfig.get_roms_path()

    @Slot(result=str)
    def select_cores_directory(self):
        """Abre un diálogo nativo para seleccionar la carpeta de Cores."""
        directory = QFileDialog.getExistingDirectory(
            None, "Seleccionar Directorio de Cores Libretro", AppConfig.get_cores_path() or ""
        )
        if directory:
            AppConfig.set_cores_path(directory)
            EmuLog.info(f"Configurada nueva ruta de Cores: {directory}")
            self.libretro.cores_path = Path(directory)
            return directory
        return AppConfig.get_cores_path()

    @Slot()
    def stop_scraping(self):
        """Mantiene la integridad del motor de scraping permitiendo que termine en segundo plano."""
        EmuLog.info("M.A.N.G.O: Tarea ocultada. El motor terminará el proceso actual de forma segura.")
        self.scrapeStatusChanged.emit("FINALIZANDO EN SEGUNDO PLANO")

    @Slot()
    def shutdown(self):
        """Detiene todos los procesos de fondo de forma SEGURA e INSTANTÁNEA."""
        EmuLog.info("M.A.N.G.O: Iniciando protocolo de apagado seguro...")
        
        # 1. DESCONECTAR SEÑALES INMEDIATAMENTE
        # Esto evita "Signal source has been deleted" si el hilo recibe un flush de Qt
        try:
            if self._scan_worker:
                self._scan_worker.progress.disconnect()
                self._scan_worker.status.disconnect()
                self._scan_worker.finished.disconnect()
            if self._scrape_worker:
                self._scrape_worker.progress.disconnect()
                self._scrape_worker.status.disconnect()
                self._scrape_worker.finished.disconnect()
            if self._core_worker:
                self._core_worker.progress.disconnect()
                self._core_worker.status.disconnect()
                self._core_worker.finished.disconnect()
        except (RuntimeError, Exception):
            pass 

        # 2. SEÑALIZAR CIERRE A LOS TRABAJADORES
        if self._scan_worker: self._scan_worker.stop()
        if self._scrape_worker: self._scrape_worker.stop()
        # _core_worker no tiene flag de parada manual todavía por ir amarrado al runtime directo de Rust
        
        # 3. DETENER HILOS CON TIMEOUT AGRESIVO (MAX 500ms)
        hilos = []
        if self._scan_thread and self._scan_thread.isRunning(): hilos.append(self._scan_thread)
        if self._scrape_thread and self._scrape_thread.isRunning(): hilos.append(self._scrape_thread)
        if self._core_thread and self._core_thread.isRunning(): hilos.append(self._core_thread)
        
        for t in hilos:
            t.quit()
            if not t.wait(500):
                EmuLog.warning("M.A.N.G.O: Forzando terminación de hilo persistente.")
                t.terminate()
        
        # NOTA: DatabaseManager no tiene .close(), usa conexiones por contexto.
        EmuLog.info("M.A.N.G.O: Motores apagados correctamente.")

    @Slot(result=str)
    def get_roms_path(self):
        return AppConfig.get_roms_path() or "No configurado"

    @Slot(result=str)
    def get_cores_path(self):
        return AppConfig.get_cores_path() or "No configurado"

    @Slot(result=bool)
    def scan_directories(self):
        """Puente para iniciar el escaneo desde QML (Downloads Center)."""
        return self.start_full_scan()

    @Slot(result=bool)
    def start_full_scan(self):
        """Inicia el escaneo de la ruta de ROMs configurada en un hilo separado."""
        path = AppConfig.get_roms_path()
        if not path:
            EmuLog.warning("Se intentó escanear pero no hay ruta configurada.")
            return False
            
        # Verificar si ya existe un hilo y si sigue siendo válido/corriendo
        try:
            if self._scan_thread and self._scan_thread.isRunning():
                EmuLog.warning("Ya hay un escaneo en progreso.")
                return False
        except RuntimeError:
            # El objeto C++ fue eliminado pero la referencia en Python persiste
            self._scan_thread = None

        EmuLog.info(f"Escaneo Asíncrono Iniciado en {path}")
        
        # Configurar Hilo y Trabajador
        self._scan_thread = QThread()
        self._scan_worker = ScanWorker(self.scanner, path)
        self._scan_worker.moveToThread(self._scan_thread)

        # Conectar Señales
        self._scan_thread.started.connect(self._scan_worker.run)
        self._scan_worker.progress.connect(self.scanProgressChanged.emit)
        self._scan_worker.status.connect(self.scanStatusChanged.emit)
        self._scan_worker.finished.connect(self._on_scan_finished)
        self._scan_worker.finished.connect(self._scan_thread.quit)
        self._scan_thread.finished.connect(self._scan_thread.deleteLater)
        self._scan_thread.finished.connect(self._clear_thread_reference)

        self._scan_thread.start()
        return True
    def _clear_thread_reference(self):
        """Limpia la referencia al hilo de escaneo."""
        # IMPORTANTE: No limpiar si el hilo sigue vivo
        if self._scan_thread and not self._scan_thread.isRunning():
            self._scan_thread = None
            self._scan_worker = None

    def _clear_scrape_thread(self):
        """Limpia la referencia al hilo de scraping."""
        if self._scrape_thread and not self._scrape_thread.isRunning():
            self._scrape_thread = None
            self._scrape_worker = None

    @Slot(str, result=str)
    def get_api_credential(self, service: str) -> str:
        """Obtiene credenciales de servicios externos para la UI."""
        if service == "screenscraper_user":
            return AppConfig.get_screenscraper_user()
        elif service == "screenscraper_pass":
            return AppConfig.get_screenscraper_pass()
        return ""

    @Slot(str, str)
    def set_api_credential(self, service: str, value: str):
        """Guarda credenciales de servicios externos desde la UI."""
        if service == "screenscraper_user":
            AppConfig.set_screenscraper_user(value)
        elif service == "screenscraper_pass":
            AppConfig.set_screenscraper_pass(value)

    def _on_scan_finished(self, count):
        EmuLog.info(f"Escaneo finalizado desde hilo: {count} juegos.")
        self.scanStatusChanged.emit(f"Escaneo completado: {count} juegos encontrados.")
        self.scanProgressChanged.emit(1.0)
        self.scanFinished.emit(count) # <--- FUNDAMENTAL PARA EL RESET DE QML
        
        # Emitir señal de que se agregaron juegos!
        self.gamesUpdated.emit()

    @Slot(result=bool)
    def start_scraping(self):
        """Inicia el M.A.N.G.O (Rust) Engine para buscar portadas faltantes en ScreenScraper."""
        if self._scrape_thread and self._scrape_thread.isRunning():
            EmuLog.warning("Ya hay un scraping en curso.")
            return False

        self.scrapeStatusChanged.emit("Inicializando M.A.N.G.O Engine...")
        self.scrapeProgressChanged.emit(0.0)

        self._scrape_thread = QThread()
        self._scrape_worker = ScrapeWorker(self.scanner)
        self._scrape_worker.moveToThread(self._scrape_thread)

        self._scrape_thread.started.connect(self._scrape_worker.run)
        self._scrape_worker.progress.connect(self.scrapeProgressChanged.emit)
        self._scrape_worker.status.connect(self.scrapeStatusChanged.emit)
        self._scrape_worker.finished.connect(self._on_scrape_finished)
        self._scrape_worker.finished.connect(self._scrape_thread.quit)
        self._scrape_thread.finished.connect(self._scrape_thread.deleteLater)
        self._scrape_thread.finished.connect(self._clear_scrape_thread)

        self._scrape_thread.start()
        return True

    @Slot()
    def stop_scraping(self):
        """Mantiene la integridad del motor permitiendo que termine los juegos actuales de forma segura."""
        EmuLog.info("M.A.N.G.O: Tarea ocultada. El motor terminará el proceso actual en segundo plano para evitar corrupción.")
        self.scrapeStatusChanged.emit("FINALIZANDO EN SEGUNDO PLANO")

    def _clear_scrape_thread(self):
        """Limpia la referencia al hilo de scraping."""
        self._scrape_thread = None
        self._scrape_worker = None

    def _clear_core_thread(self):
        """Limpia la referencia al hilo de cores."""
        self._core_thread = None
        self._core_worker = None

    @Slot(result="QVariantList")
    def fetch_available_cores(self):
        """
        Obtiene la lista de cores filtrados por las consolas que el usuario 
        realmente tiene en su biblioteca. Solo muestra nombres amigables.
        """
        EmuLog.info("M.A.N.G.O: Consultando catálogo de núcleos relevantes para tu biblioteca...")
        
        # 1. Obtener plataformas que tienen juegos
        summary = self.get_consoles_summary(use_cache=True)
        active_platforms = [p['platform'] for p in summary if p['platform'] != "all"]
        
        # 2. Obtener cores filtrados y amigables
        return self.libretro.fetch_filtered_cores(active_platforms)

    @Slot(str, result=bool)
    def start_core_download(self, core_name: str):
        if self._core_thread and self._core_thread.isRunning():
            EmuLog.warning("Ya hay una descarga de core en curso.")
            return False

        self.coreDownloadStatusChanged.emit(f"Iniciando descarga de {core_name}...")
        self.coreDownloadProgressChanged.emit(0.0)

        self._core_thread = QThread()
        self._core_worker = CoreDownloadWorker(self.libretro, core_name)
        self._core_worker.moveToThread(self._core_thread)

        self._core_thread.started.connect(self._core_worker.run)
        self._core_worker.progress.connect(self.coreDownloadProgressChanged.emit)
        self._core_worker.status.connect(self.coreDownloadStatusChanged.emit)
        self._core_worker.finished.connect(self._on_core_download_finished)
        self._core_worker.finished.connect(lambda x: self._core_thread.quit())
        self._core_thread.finished.connect(self._core_thread.deleteLater)
        self._core_thread.finished.connect(self._clear_core_thread)

        self._core_thread.start()
        return True

    def _on_core_download_finished(self, path: str):
        if path:
            self.coreDownloadStatusChanged.emit(f"Instalación completada: {Path(path).name}")
            self.coreDownloadProgressChanged.emit(1.0)
            self.coreDownloadFinished.emit(path)
            
            # Forzar actualización de UI para mostrar el nuevo core
            self._cached_summary = None
            self.gamesUpdated.emit()
        else:
            self.coreDownloadStatusChanged.emit("Fallo en la descarga.")
            self.coreDownloadProgressChanged.emit(0.0)
            self.coreDownloadFinished.emit("")

    def _on_scrape_finished(self, count):
        EmuLog.info(f"Scraping M.A.N.G.O completado: {count} descargas.")
        self.scrapeStatusChanged.emit(f"Scraping completado. {count} portadas descargadas.")
        self.scrapeProgressChanged.emit(1.0)
        self.scrapeFinished.emit(count)
        
        # Recargar modelos de UI para mostrar portadas nuevas
        self.gamesUpdated.emit()

    @Slot(result=int)
    def get_games_count(self):
        """Retorna el número total de juegos en la biblioteca."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM games")
                count = cursor.fetchone()[0]
                return count
        except sqlite3.Error as e:
            EmuLog.error(f"Error de SQLite al contar juegos: {e}")
            return 0
        except Exception as e:
            EmuLog.error(f"Error inesperado al contar juegos: {e}")
            return 0

    @Slot(result="QVariantList")
    @Slot(bool, result="QVariantList")
    def get_consoles_summary(self, use_cache=True):
        """Retorna un resumen dinámico de juegos por plataforma para el carrusel QML."""
        if use_cache and self._cached_summary:
            return self._cached_summary

        # Sincronizar ruta de cores antes de listar
        self.libretro.cores_path = Path(AppConfig.get_cores_path())

        base_platforms = [
            {"title": "SNES", "fullName": "Super Nintendo", "platform": "snes", "icon": "🕹️", "color": "#ff4b2b"},
            {"title": "NES", "fullName": "Nintendo Entertainment System", "platform": "nes", "icon": "📺", "color": "#ff416c"},
            {"title": "GBA", "fullName": "Game Boy Advance", "platform": "gba", "icon": "📱", "color": "#9d50bb"},
            {"title": "N64", "fullName": "Nintendo 64", "platform": "n64", "icon": "🏰", "color": "#3a7bd5"},
            {"title": "PS1", "fullName": "PlayStation 1", "platform": "ps1", "icon": "💿", "color": "#00d2ff"},
            {"title": "PS2", "fullName": "PlayStation 2", "platform": "ps2", "icon": "🚀", "color": "#00d2ff"},
            {"title": "PSP", "fullName": "PlayStation Portable", "platform": "psp", "icon": "🔋", "color": "#00d2ff"},
            {"title": "DS", "fullName": "Nintendo DS", "platform": "ds", "icon": "📖", "color": "#16a085"},
            {"title": "GAMECUBE", "fullName": "Nintendo GameCube", "platform": "gc", "icon": "🧊", "color": "#8e44ad"},
            {"title": "WII", "fullName": "Nintendo Wii", "platform": "wii", "icon": "🎾", "color": "#ffffff"},
            {"title": "MEGADRIVE", "fullName": "Sega Mega Drive", "platform": "megadrive", "icon": "🌀", "color": "#2c3e50"},
            {"title": "DREAMCAST", "fullName": "Sega Dreamcast", "platform": "dreamcast", "icon": "🍥", "color": "#e67e22"},
            {"title": "OTROS", "fullName": "Misceláneo", "platform": "unknown", "icon": "❓", "color": "#95a5a6"}
        ]
        
        summary = []
        try:
            installed_cores = self.libretro.list_installed_cores()
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                for p in base_platforms:
                    # 1. Contar Juegos
                    q_count = "SELECT COUNT(*) FROM games"
                    params = []
                    if p["platform"] != "all":
                        q_count += " WHERE platform = ?"
                        params = [p["platform"]]
                    cursor.execute(q_count, params)
                    count = cursor.fetchone()[0]
                    
                    # 2. Verificar Nucleos Instalados (Cores)
                    # Ahora buscamos TODOS los cores instalados que correspondan a esta plataforma
                    platform_cores = CORE_DATABASE.get(p["platform"], [])
                    installed_for_platform = []
                    for cid, cname in platform_cores:
                        if f"{cid}_libretro" in installed_cores:
                            installed_for_platform.append(cname.split('(')[0].strip()) # Guardamos solo el nombre del emu
                    
                    has_core = len(installed_for_platform) > 0
                    emu_text = ", ".join(installed_for_platform) if has_core else "Sin emuladores"

                    # 3. Calcular Tiempo
                    time_h = "0h"
                    # ... (resto de la lógica de tiempo)
                    try:
                        q_time = "SELECT SUM(play_time_seconds) FROM play_stats"
                        if p["platform"] != "all":
                            q_time = "SELECT SUM(play_time_seconds) FROM play_stats s JOIN games g ON s.game_id = g.id WHERE g.platform = ?"
                        cursor.execute(q_time, params)
                        seconds = cursor.fetchone()[0] or 0
                        time_h = f"{seconds // 3600}h"
                    except Exception: pass

                    # Mostramos ÚNICAMENTE las plataformas que tengan juegos.
                    # Excepción: la opción 'all' si hay al menos un juego de cualquier tipo.
                    total_at_all = self.get_games_count()
                    if count > 0 or (p["platform"] == "all" and total_at_all > 0):
                        summary.append({
                            "title": p["title"],
                            "fullName": p.get("fullName", p["title"]),
                            "platform": p["platform"],
                            "iconEmoji": p["icon"],
                            "accentColor": p["color"],
                            "gameCount": str(count),
                            "playTime": time_h,
                            "hasCore": has_core,
                            "emulatorName": emu_text
                        })
        except Exception as e:
            EmuLog.error(f"Error al generar resumen de consolas: {e}")
            return []
            
        self._cached_summary = summary
        return summary
