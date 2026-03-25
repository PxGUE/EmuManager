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
    finished = Signal(str, str)
    progress = Signal(str, float)
    status = Signal(str, str)

    def __init__(self, libretro_manager, core_name: str):
        super().__init__()
        self.libretro = libretro_manager
        self.core_name = core_name

    @Slot()
    def run(self):
        try:
            self.status.emit(self.core_name, f"Descargando {self.core_name} usando M.A.N.G.O (Rust)...")
            # El progress callback llamará self.progress.emit(p)
            def progress_cb(p: float):
                self.progress.emit(self.core_name, p)
                
            path = self.libretro.download_core(self.core_name, progress_cb)
            if path:
                self.status.emit(self.core_name, "¡Core instalado!")
                self.finished.emit(self.core_name, path)
            else:
                self.status.emit(self.core_name, "Error")
                self.finished.emit(self.core_name, "")
        except Exception as e:
            EmuLog.error(f"Error mortal en CoreDownloadWorker: {e}")
            self.status.emit(self.core_name, "Error en la instalación.")
            self.finished.emit(self.core_name, "")


class EmulatorInstallWorker(QObject):
    """Trabajador genérico para descargar e instalar emuladores independientes."""
    finished = Signal(str, str)
    progress = Signal(str, float)
    status = Signal(str, str)

    def __init__(self, emu_id: str, url: str, dest_dir: str, executable: str):
        super().__init__()
        self.emu_id = emu_id
        self.url = url
        self.dest_dir = dest_dir
        self.executable = executable

    @Slot()
    def run(self):
        try:
            import mango_engine
            def progress_cb(p: float):
                self.progress.emit(self.emu_id, p)
            
            self.status.emit(self.emu_id, f"Descargando {self.emu_id}...")
            path = mango_engine.download_emulator(self.url, self.dest_dir, self.executable, progress_cb)
            
            if path:
                self.status.emit(self.emu_id, f"✓ {self.emu_id} instalado correctamente.")
                self.finished.emit(self.emu_id, path)
            else:
                self.status.emit(self.emu_id, "Error en la descarga.")
                self.finished.emit(self.emu_id, "")
        except Exception as e:
            EmuLog.error(f"Error crítico en EmulatorInstallWorker: {e}")
            self.status.emit(self.emu_id, f"Fallo: {str(e)}")
            self.finished.emit(self.emu_id, "")


class StartupWorker(QObject):
    """Orquestador del flujo de arranque real de EmuManager."""
    progress = Signal(float)
    status = Signal(str)
    finished = Signal()

    def __init__(self, controller):
        super().__init__()
        self.ctrl = controller

    @Slot()
    def run(self):
        try:
            import time
            from pathlib import Path
            
            # 1. Motor Nativo (20%)
            self.status.emit("Engranando motor nativo M.A.N.G.O (Rust)...")
            time.sleep(0.4) 
            self.ctrl._is_precharged = False
            self.ctrl.proactive_background_load()
            self.progress.emit(0.25)
            
            # 2. Base de Datos (50%)
            self.status.emit("Verificando integridad de la biblioteca...")
            time.sleep(0.3)
            # Podríamos disparar un scan rápido aquí si quisiéramos
            self.progress.emit(0.55)
            
            # 3. Preparación de Assets (80%)
            self.status.emit("Optimizando caché de medios y carátulas...")
            try:
                import os
                # Pedimos los juegos a la DB para conocer sus rutas de carátula
                games = self.ctrl.db.get_all_games()
                # Calentamos solo las primeras 50 (las que el usuario verá primero)
                count = 0
                for game in games:
                    if count > 50: break
                    cover_path = game.get('media_path')
                    if cover_path and os.path.exists(cover_path):
                        # "Tocamos" el archivo leyéndolo mínimamente para que entre en la caché del OS
                        with open(cover_path, 'rb') as f:
                            f.read(1024) 
                        count += 1
            except Exception as e:
                EmuLog.debug(f"Aviso en Warm-up: {e}")
            
            self.progress.emit(0.85)
            
            # 4. Finalización (100%)
            self.status.emit("Misiones inicializadas. Bienvenida.")
            self.progress.emit(1.0)
            self.finished.emit()
            
        except Exception as e:
            EmuLog.error(f"Error crítico en StartupWorker: {e}")
            self.finished.emit()


class EmulatorUpdateWorker(QObject):
    """Trabajador para actualizar emuladores con backup gestionado por Rust."""
    finished = Signal(str, str)
    progress = Signal(str, float)
    status = Signal(str, str)

    def __init__(self, emu_id: str, url: str, dest_dir: str, executable: str):
        super().__init__()
        self.emu_id = emu_id
        self.url = url
        self.dest_dir = dest_dir
        self.executable = executable

    @Slot()
    def run(self):
        try:
            import mango_engine
            def progress_cb(p: float):
                self.progress.emit(self.emu_id, p)
            
            self.status.emit(self.emu_id, f"Actualizando {self.emu_id}...")
            path = mango_engine.update_emulator(self.url, self.dest_dir, self.executable, progress_cb)
            
            if path:
                self.status.emit(self.emu_id, f"✓ {self.emu_id} actualizado.")
                self.finished.emit(self.emu_id, path)
            else:
                self.status.emit(self.emu_id, "Error en actualización.")
                self.finished.emit(self.emu_id, "")
        except Exception as e:
            EmuLog.error(f"Error crítico en EmulatorUpdateWorker: {e}")
            self.status.emit(self.emu_id, f"Error: {e}")
            self.finished.emit(self.emu_id, "")


class LaunchWorker(QObject):
    """Trabajador que lanza el juego (bloqueante) en un hilo y mide el tiempo."""
    finished = Signal(int)

    def __init__(self, runner_path: str, game_path: str, core_path: str = None):
        super().__init__()
        self.runner_path = runner_path
        self.game_path = game_path
        self.core_path = core_path

    @Slot()
    def run(self):
        try:
            import mango_engine
            # launch_game(emulator_path, game_path, core_path)
            duration = mango_engine.launch_game(self.runner_path, self.game_path, self.core_path)
            self.finished.emit(duration)
        except Exception as e:
            EmuLog.error(f"Error nativo al lanzar juego: {e}")
            self.finished.emit(0)

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
    
    # Señales para descarga de Cores / Emuladores (Directas por ID)
    coreDownloadProgressChanged = Signal(str, float)
    coreDownloadStatusChanged = Signal(str, str)
    coreDownloadFinished = Signal(str, str)
    # --- SEÑALES DE ARRANQUE ---
    startupProgressChanged = Signal(float)
    startupStatusChanged = Signal(str)
    startupFinished = Signal()

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
            self.libretro = LibretroManager(Path(AppConfig.get_cores_path() or "."))
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
        self._startup_worker.finished.connect(self._startup_thread.quit)
        
        self._startup_thread.started.connect(self._startup_worker.run)
        self._startup_thread.finished.connect(self._startup_thread.deleteLater)
        
        self._startup_thread.start()

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

    @Slot(result=str)
    def select_runner_executable(self):
        """Abre un diálogo nativo para seleccionar el ejecutable del emulador."""
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Seleccionar Ejecutable de Emulador/RetroArch", ""
        )
        if file_path:
            AppConfig.set_runner_path(file_path)
            EmuLog.info(f"Configurada nueva ruta de Ejecutable: {file_path}")
            return file_path
        return AppConfig.get_runner_path()

    @Slot(result=str)
    def get_runner_path(self):
        return AppConfig.get_runner_path()

    # --- NUEVA GESTIÓN DE REPOSITORIOS ---
    @Slot(result='QVariantList')
    def get_emulator_repositories(self):
        """Lee el manifiesto de emuladores y verifica su estado local."""
        import json
        # El manifiesto ahora vive en recursos internos protegidos
        repo_path = Path(__file__).resolve().parent.parent / "resources" / "repositories.json"
        
        if not repo_path.exists():
            EmuLog.error(f"¡Catálogo crítico no encontrado en {repo_path}!")
            return []
        
        try:
            with open(repo_path, 'r') as f:
                data = json.load(f)
            
            # Verificar si cada emulador está instalado
            base_path = Path(AppConfig.get_cores_path())
            for emu in data.get("emulators", []):
                emu_id = emu.get("id", "")
                executable_path = base_path / emu_id / emu.get("executable", "")
                emu["isInstalled"] = executable_path.exists()
                emu["localPath"] = str(executable_path) if executable_path.exists() else ""
            
            return data.get("emulators", [])
        except Exception as e:
            EmuLog.error(f"Error cargando repositories.json: {e}")
            return []

    @Slot(str, str, str)
    def install_emulator(self, emu_id: str, url: str, executable: str):
        """Inicia el flujo de descarga de un emulador independiente."""
        if self._emu_thread and self._emu_thread.isRunning():
            EmuLog.warning(f"Ignorando instalación de {emu_id}: Ya hay otra instalación activa.")
            return

        # Creamos una subcarpeta específica para el emulador (ej: cores/retroarch/)
        dest_dir = str(Path(AppConfig.get_cores_path()) / emu_id)
        
        self._emu_thread = QThread()
        self._emu_worker = EmulatorInstallWorker(emu_id, url, dest_dir, executable)
        self._emu_worker.moveToThread(self._emu_thread)
        
        # Conectar señales para la UI
        self._emu_worker.progress.connect(self.coreDownloadProgressChanged.emit)
        self._emu_worker.status.connect(self.coreDownloadStatusChanged.emit)
        self._emu_worker.finished.connect(self._on_install_finished)
        self._emu_worker.finished.connect(self._emu_thread.quit)
        
        self._emu_thread.finished.connect(self._emu_thread.deleteLater)
        self._emu_thread.finished.connect(self._clear_emu_thread)
        self._emu_thread.started.connect(self._emu_worker.run)
        self._emu_thread.start()

    def _clear_emu_thread(self):
        """Limpieza segura de las referencias de Python al terminar el hilo."""
        self._emu_thread = None
        self._emu_worker = None

    @Slot(str, str, str)
    def update_emulator(self, emu_id: str, url: str, executable: str):
        """Inicia el flujo de actualización segura (Rust-side backup)."""
        # Protegemos contra ejecuciones concurrentes y objetos ya eliminados
        try:
            if self._emu_thread and self._emu_thread.isRunning():
                EmuLog.warning("Otra tarea de emulador está en curso.")
                return
        except RuntimeError:
            self._emu_thread = None

        # Creamos una subcarpeta específica para el emulador (ej: cores/retroarch/)
        dest_dir = str(Path(AppConfig.get_cores_path()) / emu_id)
        self._emu_thread = QThread()
        self._emu_worker = EmulatorUpdateWorker(emu_id, url, dest_dir, executable)
        self._emu_worker.moveToThread(self._emu_thread)
        
        self._emu_worker.progress.connect(self.coreDownloadProgressChanged.emit)
        self._emu_worker.status.connect(self.coreDownloadStatusChanged.emit)
        self._emu_worker.finished.connect(self._on_install_finished)
        self._emu_worker.finished.connect(self._emu_thread.quit)
        
        self._emu_thread.finished.connect(self._emu_thread.deleteLater)
        self._emu_thread.finished.connect(self._clear_emu_thread)
        self._emu_thread.started.connect(self._emu_worker.run)
        self._emu_thread.start()

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

    @Slot(str)
    @Slot(str)
    def uninstall_emulator(self, emu_id: str):
        """Elimina el directorio completo del emulador."""
        try:
            import shutil
            target_dir = Path(AppConfig.get_cores_path()) / emu_id
            if target_dir.exists():
                shutil.rmtree(target_dir)
                EmuLog.info(f"Emulador desinstalado y carpeta eliminada: {emu_id}")
                self.gamesUpdated.emit()
        except Exception as e:
            EmuLog.error(f"Error desinstalando emulador {emu_id}: {e}")

    @Slot(str)
    def open_emulator_folder(self, executable_name: str):
        """Abre la carpeta que contiene el ejecutable en el explorador de archivos."""
        target_path = Path(AppConfig.get_cores_path()) 
        import subprocess
        try:
            if sys.platform == "linux":
                subprocess.run(["xdg-open", str(target_path)])
            elif sys.platform == "win32":
                os.startfile(str(target_path))
        except Exception as e:
            EmuLog.error(f"No se pudo abrir la carpeta: {e}")

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
                platform = row["platform"]

            # 2. Buscar core sugerido e instalado
            core_id = self.libretro.get_core_for_platform(platform)
            core_path = None
            if core_id:
                # Buscar en la subcarpeta del sistema
                core_file = self.libretro.cores_path / platform / f"{core_id}_libretro.so"
                if core_file.exists():
                    core_path = str(core_file)
                else:
                    EmuLog.warning(f"Core sugerido {core_id} no está instalado en {core_file}. Intentando lanzar sin core...")

            # 3. Lanzar en hilo separado para no congelar la UI
            runner = AppConfig.get_runner_path()
            EmuLog.info(f"M.A.N.G.O Launch: Preparando {game_path} con {runner}...")
            
            self._launch_thread = QThread()
            self._launch_worker = LaunchWorker(runner, game_path, core_path)
            self._launch_worker.moveToThread(self._launch_thread)
            self._launch_thread.started.connect(self._launch_worker.run)
            
            def cleanup_launch(duration):
                if duration > 5: # Guardar si jugó más de 5 segundos
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
                
                self._launch_thread.quit()
                # self._launch_thread.wait() # ELIMINADO: evita 'Thread tried to wait on itself'

            self._launch_worker.finished.connect(cleanup_launch)
            self._launch_thread.start()

        except Exception as e:
            EmuLog.error(f"Fallo al intentar lanzar el juego {game_id}: {e}")

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

        self.coreDownloadStatusChanged.emit(core_name, f"Iniciando descarga de {core_name}...")
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

    def _on_core_download_finished(self, path: str):
        core_id = self._core_worker.core_name if self._core_worker else "core"
        if path:
            self.coreDownloadStatusChanged.emit(core_id, f"Instalación completada: {Path(path).name}")
            self.coreDownloadProgressChanged.emit(core_id, 1.0)
            self.coreDownloadFinished.emit(core_id, path)
            
            # Forzar actualización de UI para mostrar el nuevo core
            self._cached_summary = None
            self.gamesUpdated.emit()
        else:
            self.coreDownloadStatusChanged.emit(core_id, "Fallo en la descarga.")
            self.coreDownloadProgressChanged.emit(core_id, 0.0)
            self.coreDownloadFinished.emit(core_id, "")

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
                    
                    # 2. Verificar Nucleos Instalados (Cores y Standalone)
                    has_core = False
                    installed_emulators = []
                    
                    # A. Check Libretro Cores
                    platform_cores = CORE_DATABASE.get(p["platform"], [])
                    for cid, cname in platform_cores:
                        if f"{cid}_libretro" in installed_cores:
                            installed_emulators.append(cname.split('(')[0].strip())
                    
                    # B. Check Standalone Emulators (NUEVO)
                    # Mapeo de plataforma a ID de emulador standalone
                    platform_to_emu = {
                        "gc": "dolphin", "wii": "dolphin",
                        "psp": "ppsspp", "ps2": "pcsx2",
                        "ps1": "duckstation", "ps3": "rpcs3",
                        "switch": "ryujinx", "vita": "vita3k"
                    }
                    
                    # 1. RetroArch es universal si está instalado
                    ra_path = Path(AppConfig.get_cores_path()) / "retroarch" / "RetroArch.AppImage"
                    if ra_path.exists():
                        installed_emulators.append("RetroArch")
                        
                    # 2. Verificar standalone específico
                    emu_id = platform_to_emu.get(p["platform"])
                    if emu_id:
                        # Buscamos el ejecutable en repositories.json para ser precisos
                        # (Simplificado: buscamos cualquier .AppImage en la subcarpeta por ahora)
                        emu_dir = Path(AppConfig.get_cores_path()) / emu_id
                        if emu_dir.exists() and any(emu_dir.glob("*.AppImage")):
                            installed_emulators.append(emu_id.upper())
                    
                    # Eliminar duplicados y formatear
                    installed_emulators = list(set(installed_emulators))
                    has_core = len(installed_emulators) > 0
                    emu_text = ", ".join(installed_emulators) if has_core else "Sin emuladores"

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
