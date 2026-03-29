from typing import Optional
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
import platform
import sqlite3
try:
    import psutil
except ImportError:
    psutil = None

QML_IMPORT_NAME = "EmuManager.Controllers"
QML_IMPORT_MAJOR_VERSION = 1

from controllers.workers import (
    ScanWorker, ScrapeWorker, CoreDownloadWorker, 
    EmulatorInstallWorker,
    LaunchWorker, StartupWorker
)
from backend.libretro import LibretroManager, CORE_DATABASE

@QmlElement
class MainController(QObject):
    # --- VERSIÓN DINÁMICA DEL ECOSISTEMA ---
    EMUMANAGER_VERSION = "0.3.5 - alpha"
    MANGO_VERSION = "0.2.1 - alpha"
    # Señales para comunicación con QML en tiempo real
    language_changed = Signal(str)
    scanProgressChanged = Signal(float)  # 0.0 a 1.0
    scanStatusChanged = Signal(str)      # "Escanenando..." "Listo"
    scanFinished = Signal(int)           # Juegos encontrados
    scrapeProgressChanged = Signal(float) # 0.0 a 1.0
    scrapeStatusChanged = Signal(str)     # "Scrapeando..." "Listo"
    scrapeFinished = Signal(int)         # Descargas realizadas
    gamesUpdated = Signal()               # Emitir cuando se agreguen/actualicen juegos
    gamesCountChanged = Signal()          # Notificar cuando cambie el total de juegos
    
    # Señales para descarga de Cores / Emuladores (Directas por ID)
    coreDownloadProgressChanged = Signal(str, float)
    coreDownloadStatusChanged = Signal(str, str)
    coreDownloadFinished = Signal(str, str)
    # --- SEÑALES DE ARRANQUE ---
    startupProgressChanged = Signal(float)
    startupStatusChanged = Signal(str)
    startupFinished = Signal()
    
    # Propiedades dinámicas para la UI
    from PySide6.QtCore import Property
    @Property(str, constant=True)
    def appVersion(self): return self.EMUMANAGER_VERSION
    
    @Property(str, constant=True)
    def mangoVersion(self): return self.MANGO_VERSION

    def __init__(self, parent=None):
        super().__init__(parent)
        self._startup_thread = None
        self._startup_worker = None
        
        # --- ASEGURAR QUE EL BACKEND ESTÁ EN EL PATH ---
        backend_dir = Path(__file__).resolve().parent.parent / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
            
        try:
            self.db = DatabaseManager()
            self.scanner = ScannerManager(self.db)
            self.libretro = LibretroManager(Path(AppConfig.get_emulators_path() or "."))
            self._scan_thread = None
            self._scan_worker = None
            self._scrape_thread = None
            self._scrape_worker = None
            self._core_thread = None
            self._core_worker = None
            self._emu_thread = None
            self._emu_worker = None
            self._cached_summary = None 
            self._is_precharged = False # Flag para evitar re-carga redundante
            self._active_launches = {} # Track de hilos de juego para evitar GC
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
            EmuLog.info(f"--------------------------------------------------")
            EmuLog.info(f"INICIANDO EmuManager v{self.EMUMANAGER_VERSION} ({self.MANGO_VERSION})")
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
                EmuLog.info("M.A.N.G.O: Motor nativo y sistema de logs sincronizados.")
            except ImportError:
                EmuLog.warning("M.A.N.G.O: Motor no encontrado. Operando en modo degradado (Python-only).")

            EmuLog.info("M.A.N.G.O: Generando caché de consolas...")
            self._cached_summary = self.get_consoles_summary(use_cache=False)
            
            # Notificar que los juegos están listos
            self.gamesUpdated.emit()
            
            self._is_precharged = True
            EmuLog.info("M.A.N.G.O: Pre-carga completada con éxito.")
        except Exception as e:
            EmuLog.error(f"Error en carga proactiva: {e}")

    @Slot()
    def start_startup_sequence(self):
        """Dispara el hilo de arranque real."""
        if self._startup_thread and self._startup_thread.isRunning():
            return
            
        self._startup_thread = QThread()
        self._startup_worker = StartupWorker(self)
        self._startup_worker.moveToThread(self._startup_thread)
        
        # Conexiones
        self._startup_worker.progress.connect(self.startupProgressChanged.emit)
        self._startup_worker.status.connect(self.startupStatusChanged.emit)
        self._startup_worker.finished.connect(self.startupFinished.emit)
        self._startup_worker.finished.connect(self.gamesUpdated.emit) 
        self._startup_worker.finished.connect(self._startup_thread.quit)
        
        self._startup_thread.started.connect(self._startup_worker.run)
        self._startup_thread.finished.connect(self._startup_thread.deleteLater)
        
        self._startup_thread.start()

    # --- Gestión de Idioma ---
    @Slot(result=str)
    def get_language(self):
        return AppConfig.get_language()

    @Slot(str)
    def set_language(self, lang):
        if lang in ["es", "en"]:
            AppConfig.set_language(lang)
            self.language_changed.emit(lang)
            EmuLog.info(f"M.A.N.G.O I18n: Idioma cambiado a: {lang}")

    @Slot(result=int)
    def get_games_count(self):
        try:
            return self.db.count_all_roms()
        except Exception:
            return 0

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
            None, "Seleccionar Directorio Principal para Emuladores", AppConfig.get_emulators_path() or ""
        )
        if directory:
            AppConfig.set_emulators_path(directory)
            EmuLog.info(f"Configurada nueva ruta de Emuladores: {directory}")
            # Ya no asignamos a cores_path porque es una propiedad dinámica en libretro
            return directory
        return AppConfig.get_emulators_path()


    # --- NUEVA GESTIÓN DE REPOSITORIOS ---
    @Slot(result='QVariantList')
    def get_emulator_repositories(self):
        """Lee el manifiesto de emuladores y verifica su estado local y de sistema."""
        import json
        repo_path = Path(__file__).resolve().parent.parent / "resources" / "repositories.json"
        
        if not repo_path.exists():
            EmuLog.error(f"¡Catálogo crítico no encontrado en {repo_path}!")
            return []
        
        try:
            with open(repo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            import platform
            os_name = platform.system().lower()
            base_path = Path(AppConfig.get_emulators_path())
            
            try:
                import mango_engine
            except ImportError:
                mango_engine = None

            for emu in data.get("emulators", []):
                emu_id = emu.get("id", "")
                orchestra = emu.get("orchestration", {})
                
                # 1. Resolver IDs y URLs según OS
                os_orchestra = orchestra.get(os_name, {})
                system_id = os_orchestra.get("id", "")
                
                portable_config = orchestra.get("portable", {})
                portable_url = portable_config.get(os_name, "")
                
                # 2. Resolver Ejecutable
                exe_config = emu.get("executable", {})
                executable_name = exe_config.get(os_name, "")
                
                emu["systemId"] = system_id
                emu["downloadUrl"] = portable_url
                emu["executable"] = executable_name
                
                # 3. Verificar Instalación (Local or System)
                local_path = base_path / emu_id / executable_name
                is_installed = local_path.exists()
                
                # Check sistémico si no está local
                if not is_installed and mango_engine and system_id:
                    try:
                        is_installed = mango_engine.check_system_installed(system_id)
                    except:
                        pass
                
                emu["isInstalled"] = is_installed
                emu["localPath"] = str(local_path) if is_installed else ""
                
                # Inicializar estados de progreso para la UI
                emu["progress"] = 0.0
                emu["statusText"] = "emu_status_installed" if is_installed else "emu_status_available"
                
                if is_installed:
                    EmuLog.debug(f"M.A.N.G.O (Check): {emu_id} detectado en {local_path}")
            
            return data.get("emulators", [])
        except Exception as e:
            EmuLog.error(f"Error cargando repositories.json: {e}")
            return []


    @Slot(str, result=bool)


    @Slot()
    def check_for_updates(self):
        """Simula una verificación de actualizaciones en el repositorio remoto."""
        EmuLog.info("M.A.N.G.O Sync: Conectando con repositorios de GitHub...")
        self.coreDownloadStatusChanged.emit("all", "Verificando actualizaciones...")
        self.gamesUpdated.emit()

    def _on_install_finished(self, emu_id, path):
        """Callback al finalizar la instalación de un emulador."""
        self.coreDownloadFinished.emit(emu_id, path)
        self.gamesUpdated.emit()

    def _find_emulator_executable(self, emu_id: str) -> Optional[Path]:
        """Ayudante interno para localizar el ejecutable real de un emulador (Búsqueda 1-nivel)."""
        import platform as py_platform
        is_win = py_platform.system() == "Windows"
        
        # 1. Obtener nombre del ejecutable del catálogo
        emu_id_lower = emu_id.lower()
        exe_name = None
        
        # Mapeo rápido para casos comunes si el repo no está cargado
        executables = {
            "retroarch": "retroarch.exe" if is_win else "RetroArch.AppImage",
            "dolphin": "Dolphin.exe" if is_win else "Dolphin.AppImage",
            "pcsx2": "pcsx2-qt.exe" if is_win else "PCSX2.AppImage",
            "ppsspp": "PPSSPPWindows64.exe" if is_win else "PPSSPP.AppImage",
            "duckstation": "duckstation-qt-x64-release.exe" if is_win else "DuckStation.AppImage"
        }
        exe_name = executables.get(emu_id_lower)
        
        if not exe_name: return None
        
        # 2. Buscar en la carpeta del emulador
        emu_dir = Path(AppConfig.get_emulators_path()) / emu_id_lower
        if not emu_dir.exists(): return None
        
        # Intento A: Raíz
        if (emu_dir / exe_name).exists(): return emu_dir / exe_name
        
        # Intento B: Subcarpeta (Ej: RetroArch-Win64)
        try:
            for sub in emu_dir.iterdir():
                if sub.is_dir() and (sub / exe_name).exists():
                    return sub / exe_name
        except: pass
        
        return None

    @Slot(str, result=bool)
    def is_emulator_installed(self, emu_id: str) -> bool:
        """Verifica si un emulador está instalado físicamente."""
        return self._find_emulator_executable(emu_id) is not None

    @Slot(str)
    def uninstall_emulator(self, emu_id: str):
        """Elimina el directorio completo del emulador usando el motor nativo."""
        try:
            target_dir = str(Path(AppConfig.get_emulators_path()) / emu_id)
            import mango_engine
            mango_engine.uninstall_emulator(target_dir)
            EmuLog.info(f"M.A.N.G.O Uninstall: Carpeta eliminada: {emu_id}")
            self._cached_summary = None 
            self.gamesUpdated.emit()
        except Exception as e:
            EmuLog.error(f"Error desinstalando emulador {emu_id}: {e}")

    @Slot(str)
    def open_emulator_folder(self, emu_id: str):
        """Abre la carpeta del emulador en el explorador."""
        target_path = Path(AppConfig.get_emulators_path()) / emu_id
        if not target_path.exists():
            target_path = Path(AppConfig.get_emulators_path())
            
        import subprocess
        try:
            if sys.platform == "linux":
                subprocess.run(["xdg-open", str(target_path)])
            elif sys.platform == "win32":
                os.startfile(str(target_path))
        except Exception as e:
            EmuLog.error(f"No se pudo abrir la carpeta: {e}")

    @Slot()
    def launch_random_game(self):
        """Picks a random game from the database and launches it."""
        try:
            with self.db.get_connection() as conn:
                row = conn.execute("SELECT id FROM games ORDER BY RANDOM() LIMIT 1").fetchone()
                if row:
                    EmuLog.info(f"M.A.N.G.O: Selección aleatoria detectada. Lanzando misión {row['id']}...")
                    self.launch_game_by_id(row["id"])
                else:
                    EmuLog.warning("No hay juegos en la biblioteca para lanzar de forma aleatoria.")
        except Exception as e:
            EmuLog.error(f"Error al lanzar juego aleatorio: {e}")

    @Slot(int)
    def launch_game_by_id(self, game_id: int):
        """Lanza el juego por ID, buscando su core y registrando telemetría al cerrar."""
        try:
            # 1. Obtener datos del juego desde DB
            with self.db.get_connection() as conn:
                row = conn.execute("SELECT file_path, platform FROM games WHERE id = ?", (game_id,)).fetchone()
                if not row:
                    EmuLog.error(f"No se encontró el juego con ID {game_id} en la base de datos.")
                    return
                game_path = row["file_path"]
                platform_id = row["platform"].lower()

            # 2. INTELIGENCIA DE LANZAMIENTO: ¿RetroArch o Standalone?
            # Prioridad A: Buscar si hay un emulador standalone instalado para esta plataforma
            standalone_map = {
                "ps2": "pcsx2",
                "gc": "dolphin",
                "wii": "dolphin",
                "psp": "ppsspp",
                "ps1": "duckstation",
                "ds": "desmume",
                "n64": "mupen64plus" # Opcional, RetroArch suele ser mejor para N64
            }
            
            target_emu_id = standalone_map.get(platform_id)
            runner = None
            core_path = None
            
            if target_emu_id:
                runner = self._find_emulator_executable(target_emu_id)
                if runner:
                    EmuLog.info(f"M.A.N.G.O Launch: Detectado emulador independiente para {platform_id} -> {target_emu_id}")
            
            # Prioridad B: RetroArch (Fallback universal)
            if not runner:
                runner = self._find_emulator_executable("retroarch")
                if runner:
                    import platform as py_platform
                    is_win = py_platform.system() == "Windows"
                    core_ext = ".dll" if is_win else ".so"
                    
                    core_id = self.libretro.get_core_for_platform(platform_id)
                    if core_id:
                        core_file = self.libretro.cores_path / platform_id / f"{core_id}_libretro{core_ext}"
                        if core_file.exists():
                            core_path = str(core_file)
                        else:
                            EmuLog.warning(f"Core sugerido {core_id} no encontrado. RetroArch intentará detección automática.")
                else:
                    EmuLog.error("No se encontró ningún emulador compatible (RetroArch o Standalone) instalado.")
                    return

            runner_str = str(runner)
            EmuLog.info(f"M.A.N.G.O Launch: Preparando {game_path} con {runner.name}...")
            
            # --- THREAD MANAGEMENT (M.A.N.G.O SAFE) ---
            # Guardamos referencia en dict para que Python no mate el hilo por GC
            if game_id in self._active_launches:
                EmuLog.warning(f"M.A.N.G.O: El juego {game_id} ya está en proceso de lanzamiento.")
                return

            thread = QThread(self)
            worker = LaunchWorker(runner_str, game_path, core_path)
            worker.moveToThread(thread)
            
            # Registrar para persistencia
            self._active_launches[game_id] = (thread, worker)
            
            def cleanup_launch(duration):
                # Limpiar rastro de hilos primero
                if game_id in self._active_launches:
                    del self._active_launches[game_id]

                if duration >= 1: # Umbral de 1 seg para tests rápidos
                    EmuLog.info(f"M.A.N.G.O: Sesión terminada. Tiempo jugado: {duration} segundos.")
                    with self.db.get_connection() as conn:
                        conn.execute("""
                            INSERT INTO play_stats (game_id, play_time_seconds, last_played_at, play_count)
                            VALUES (?, ?, CURRENT_TIMESTAMP, 1)
                            ON CONFLICT(game_id) DO UPDATE SET
                                play_time_seconds = play_time_seconds + excluded.play_time_seconds,
                                last_played_at = CURRENT_TIMESTAMP,
                                play_count = play_count + 1
                        """, (game_id, duration))
                        conn.commit()
                    self.gamesUpdated.emit()
                else:
                    EmuLog.debug(f"M.A.N.G.O (Launch): Sesión demasiado corta ({duration}s).")
                
                thread.quit()

            worker.finished.connect(cleanup_launch)
            thread.started.connect(worker.run)
            thread.finished.connect(thread.deleteLater)
            worker.finished.connect(worker.deleteLater)
            
            thread.start()

        except Exception as e:
            EmuLog.error(f"Fallo al intentar lanzar el juego {game_id}: {e}")

    @Slot()
    def stop_scraping(self):
        """Mantiene la integridad del motor de scraping permitiendo que termine en segundo plano."""
        EmuLog.info("M.A.N.G.O: Tarea ocultada. El motor terminará el proceso actual de forma segura.")
        self.scrapeStatusChanged.emit("status_finishing_bg")

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
    def get_emulators_path(self):
        return AppConfig.get_emulators_path() or "No configurado"

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
            self.scanStatusChanged.emit("scan_no_path")
            self.scanFinished.emit(0)
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
        self.scanStatusChanged.emit(f"scan_finished_msg|{count}")
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

        self.scrapeStatusChanged.emit("engine_init")
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
        self.scrapeStatusChanged.emit("status_finishing_bg")

    def _clear_scrape_thread(self):
        """Limpia la referencia al hilo de scraping."""
        self._scrape_thread = None
        self._scrape_worker = None

    def _clear_core_thread(self):
        """Limpia la referencia al hilo de cores."""
        self._core_thread = None
        self._core_worker = None
    @Slot(str, str, str, result=bool)
    def install_emulator(self, emu_id: str, url: str = "", executable: str = ""):
        """Instalación orquestada: Decide entre Winget/Flatpak o Direct Download."""
        if self._emu_thread and self._emu_thread.isRunning():
            EmuLog.warning(f"Ya hay una tarea de emulador en curso ({emu_id}).")
            return False

        # Si no se pasan URL/Executable, los buscamos en el manifest (Nueva API simplificada)
        system_id = ""
        if not url or not executable:
            manifest = self.get_emulator_repositories()
            for emu in manifest:
                if emu["id"] == emu_id:
                    url = emu.get("downloadUrl", "")
                    executable = emu.get("executable", "")
                    system_id = emu.get("systemId", "")
                    break

        dest_dir = Path(AppConfig.get_emulators_path()) / emu_id
        
        # 🧪 Pre-configuraciones especiales
        if emu_id == "retroarch":
            dest_dir.mkdir(parents=True, exist_ok=True)
            (dest_dir / "cores").mkdir(parents=True, exist_ok=True)

        EmuLog.info(f"M.A.N.G.O Orchestra: Iniciando misión para {emu_id}...")
        
        self._emu_thread = QThread()
        self._emu_worker = EmulatorInstallWorker(emu_id, system_id, url, str(dest_dir), executable)
        self._emu_worker.moveToThread(self._emu_thread)

        self._emu_thread.started.connect(self._emu_worker.run)
        self._emu_worker.progress.connect(lambda id, p: self.coreDownloadProgressChanged.emit(id, p))
        self._emu_worker.status.connect(lambda id, s: self.coreDownloadStatusChanged.emit(id, s))
        self._emu_worker.finished.connect(self._on_emu_install_finished)
        self._emu_worker.finished.connect(self._emu_thread.quit)
        self._emu_thread.finished.connect(self._emu_thread.deleteLater)
        self._emu_thread.finished.connect(self._clear_emu_thread)

        self._emu_thread.start()
        return True

    @Slot(str, str, str, result=bool)
    def update_emulator(self, emu_id: str, url: str = "", executable: str = ""):
        """Alias de install_emulator para compatibilidad con QML (El orquestador maneja el flujo)."""
        return self.install_emulator(emu_id, url, executable)

    @Slot(str, result=bool)
    def uninstall_emulator(self, emu_id: str):
        """Elimina por completo la carpeta y binarios de un emulador local."""
        dest_dir = str(Path(AppConfig.get_emulators_path()) / emu_id)
        if Path(dest_dir).exists():
            EmuLog.info(f"M.A.N.G.O: Desinstalando emulador local {emu_id}...")
            # Aquí podríamos llamar a una función nativa de limpieza o simplemente a shutil
            import shutil
            try:
                shutil.rmtree(dest_dir)
                EmuLog.info(f"✓ {emu_id} desinstalado correctamente.")
                self._cached_summary = None 
                self.gamesUpdated.emit()
                return True
            except Exception as e:
                EmuLog.error(f"Fallo al desinstalar {emu_id}: {e}")
        return False

    def _on_emu_install_finished(self, emu_id: str, path: str):
        if path:
            EmuLog.info(f"✓ La misión de instalación de {emu_id} ha sido un éxito en {path}")
            self.coreDownloadStatusChanged.emit(emu_id, "install_success_tag")
            self.coreDownloadFinished.emit(emu_id, path)
            self._cached_summary = None 
            self.gamesUpdated.emit()
        else:
            EmuLog.error(f"La misión de instalación de {emu_id} ha fallado estrepitosamente.")
            self.coreDownloadStatusChanged.emit(emu_id, "install_failed_tag")
            self.coreDownloadFinished.emit(emu_id, "")

    def _clear_emu_thread(self):
        self._emu_thread = None
        self._emu_worker = None

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

        self.coreDownloadStatusChanged.emit(core_name, f"core_download_init_msg|{core_name}")
        self.coreDownloadProgressChanged.emit(core_name, 0.0)

        self._core_thread = QThread()
        self._core_worker = CoreDownloadWorker(self.libretro, core_name)
        self._core_worker.moveToThread(self._core_thread)

        self._core_thread.started.connect(self._core_worker.run)
        self._core_worker.progress.connect(self.coreDownloadProgressChanged.emit)
        self._core_worker.status.connect(self.coreDownloadStatusChanged.emit)
        self._core_worker.finished.connect(self._on_core_download_finished)
        self._core_worker.finished.connect(self._core_thread.quit)
        self._core_thread.finished.connect(self._core_thread.deleteLater)
        self._core_thread.finished.connect(self._clear_core_thread)

        self._core_thread.start()
        return True

    @Slot(str)
    def uninstall_core(self, core_id: str):
        """Solicita la eliminación de un núcleo específico."""
        if self.libretro.uninstall_core(core_id):
            self._cached_summary = None
            self.gamesUpdated.emit()
            EmuLog.info(f"Core {core_id} desinstalado con éxito.")

    def _on_core_download_finished(self, path: str):
        core_id = self._core_worker.core_name if self._core_worker else "core"
        if path:
            self.coreDownloadStatusChanged.emit(core_id, f"core_install_finished_msg|{Path(path).name}")
            self.coreDownloadProgressChanged.emit(core_id, 1.0)
            self.coreDownloadFinished.emit(core_id, path)
            
            # Forzar actualización de UI para mostrar el nuevo core
            self._cached_summary = None
            self.gamesUpdated.emit()
        else:
            self.coreDownloadStatusChanged.emit(core_id, "download_failed")
            self.coreDownloadProgressChanged.emit(core_id, 0.0)
            self.coreDownloadFinished.emit(core_id, "")

    def _on_scrape_finished(self, count):
        EmuLog.info(f"Scraping M.A.N.G.O completado: {count} descargas.")
        self.scrapeStatusChanged.emit(f"scrape_finished_msg|{count}")
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

    @Slot(result="QVariantMap")
    def get_dashboard_stats(self):
        """Retorna un conjunto de estadísticas y datos para el Dashboard premium."""
        try:
            import mango_engine
            db_path = str(AppConfig.get_database_path())
            stats = mango_engine.fetch_dashboard_stats(db_path)
            if not stats:
                raise ValueError("Rust module returned null stats")
            return stats
        except Exception as e:
            EmuLog.error(f"Error cargando stats del dashboard nativo: {e}")
            return {
                "total_games": 0,
                "total_favorites": 0,
                "total_play_time": "0h 0m",
                "most_played_system": "N/A",
                "last_game": None,
                "recent_games": [],
                "top_platforms": []
            }

    @Slot(result="QVariantMap")
    def get_system_info(self):
        """Retorna información técnica unificada para la sección 'Acerca de'."""
        import platform as py_platform
        
        # M.A.N.G.O Status
        is_engine_ready = False
        mango_version = "N/A"
        try:
            import mango_engine
            mango_version = "v0.2.5"
            is_engine_ready = True
        except ImportError:
            pass

        # CPU info
        cpu_threads = os.cpu_count() or 0
        
        # RAM info
        ram_total = "N/A"
        if psutil:
            ram_total = f"{round(psutil.virtual_memory().total / (1024**3))} GB"

        return {
            "app_name": AppConfig.APP_NAME,
            "app_version": AppConfig.APP_VERSION,
            "os": f"{py_platform.system()} {py_platform.release()} ({py_platform.machine()})",
            "python": py_platform.python_version(),
            "cpu_threads": cpu_threads,
            "ram": ram_total,
            "mango_version": mango_version,
            "is_engine_ready": is_engine_ready,
            "runtime": "PySide6 (Qt Quick)"
        }

    # --- NUEVOS MÉTODOS DE FORTALECIMIENTO ---
    @Slot(int, bool)
    def toggle_favorite(self, game_id: int, is_favorite: bool):
        """Marca un juego como favorito en la base de datos."""
        self.db.update_game_favorite(game_id, is_favorite)
        self.gamesUpdated.emit()
        EmuLog.debug(f"Game {game_id} favorite status -> {is_favorite}")

    @Slot(int, result="QVariantMap")
    def get_game_details(self, game_id: int):
        """Retorna toda la metadata de un juego específico para la vista extendida."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT g.id, g.platform, m.title, m.developer, m.publisher, 
                           m.release_date, m.genre, m.description, 
                           m.cover_2d_path, m.cover_3d_path, m.is_favorite
                    FROM games g
                    JOIN game_metadata m ON g.id = m.game_id
                    WHERE g.id = ?
                """, (game_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "platform": row[1],
                        "title": row[2],
                        "developer": row[3] or "Desconocido",
                        "publisher": row[4] or "N/A",
                        "release_date": row[5] or "----",
                        "genre": row[6] or "Varios",
                        "description": row[7] or "Sin descripción disponible.",
                        "cover2d": (row[8] or "").replace("\\", "/"),
                        "cover3d": (row[9] or "").replace("\\", "/"),
                        "isFavorite": bool(row[10])
                    }
        except Exception as e:
            EmuLog.error(f"Error cargando detalle del juego {game_id}: {e}")
        return {}

    @Slot(str, result="QVariantList")
    def search_library(self, query: str):
        """Realiza una búsqueda rápida y retorna los resultados."""
        if not query or len(query) < 2:
            return []
        return self.db.search_games(query)

    @Slot(result="QVariantList")
    @Slot(bool, result="QVariantList")
    def get_consoles_summary(self, use_cache=True):
        """Retorna un resumen dinámico de juegos por plataforma para el carrusel QML (Optimizado por M.A.N.G.O)."""
        if use_cache and self._cached_summary:
            return self._cached_summary

        base_platforms = {
            "snes": {"title": "SNES", "fullName": "Super Nintendo", "icon": "🕹️", "color": "platSnes"},
            "nes": {"title": "NES", "fullName": "Nintendo Entertainment System", "icon": "📺", "color": "platNes"},
            "gba": {"title": "GBA", "fullName": "Game Boy Advance", "icon": "📱", "color": "platGba"},
            "n64": {"title": "N64", "fullName": "Nintendo 64", "icon": "🏰", "color": "platN64"},
            "ps1": {"title": "PS1", "fullName": "PlayStation 1", "icon": "💿", "color": "platPs1"},
            "ps2": {"title": "PS2", "fullName": "PlayStation 2", "icon": "🚀", "color": "platPs2"},
            "psp": {"title": "PSP", "fullName": "PlayStation Portable", "icon": "🔋", "color": "platPsp"},
            "ds": {"title": "DS", "fullName": "Nintendo DS", "icon": "📖", "color": "platDs"},
            "gc": {"title": "GAMECUBE", "fullName": "Nintendo GameCube", "icon": "🧊", "color": "platGc"},
            "wii": {"title": "WII", "fullName": "Nintendo Wii", "icon": "🎾", "color": "platWii"},
            "megadrive": {"title": "MEGADRIVE", "fullName": "Sega Mega Drive", "icon": "🌀", "color": "platMegaDrive"},
            "dreamcast": {"title": "DREAMCAST", "fullName": "Sega Dreamcast", "icon": "🍥", "color": "platDreamcast"},
            "unknown": {"title": "OTROS", "fullName": "Misceláneo", "icon": "❓", "color": "platUnknown"}
        }
        
        summary = []
        try:
            import mango_engine
            # Llamada al motor nativo que resuelve todo (DB + Cores + Standalones)
            native_results = mango_engine.fetch_consoles_summary(
                str(AppConfig.get_database_path()),
                str(AppConfig.get_emulators_path())
            )
            
            for item in native_results:
                platform_id = item["platform"]
                ui_info = base_platforms.get(platform_id, base_platforms["unknown"])
                
                # Combinar datos de negocio (Rust) con datos visuales (Python)
                summary.append({
                    "title": ui_info["title"],
                    "fullName": ui_info["fullName"],
                    "platform": platform_id,
                    "iconEmoji": ui_info["icon"],
                    "accentColor": ui_info["color"],
                    "gameCount": item["gameCount"],
                    "playTime": item["playTime"],
                    "hasCore": item["hasCore"],
                    "emulatorName": item["emulatorName"]
                })
            
            self._cached_summary = summary
            return summary
            
        except Exception as e:
            EmuLog.error(f"Error nativo en resumen de consola: {e}")
            return []
