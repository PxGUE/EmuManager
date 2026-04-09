from pathlib import Path
from dataclasses import dataclass
from PySide6.QtCore import QObject, Slot, Signal
from core.logger import EmuLog

@dataclass
class EmulatorInstallConfig:
    emu_id: str
    system_id: str
    url: str
    dest_dir: str
    executable: str

class UpdateWorker(QObject):
    """Verifica actualizaciones consolidadas (App + Emuladores) vía M.A.N.G.O."""
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, current_version: str, targets: dict = None):
        super().__init__()
        self.current_version = current_version
        self.targets = targets or {}

    @Slot()
    def run(self):
        try:
            from core.config import AppConfig
            if AppConfig.IS_DEV_MODE:
                EmuLog.info("M.A.N.G.O Sync: Modo Desarrollo Detectado. Saltando comprobación nativa.")
                self.finished.emit([]) # No hay actualizaciones en modo dev
                return

            import mango_engine
            EmuLog.debug(f"Iniciando sincronización nativa para {len(self.targets)} objetivos...")
            
            # Llamada al motor Rust (Tokio paralelo)
            results = mango_engine.check_all_updates(self.targets)
            
            EmuLog.info(f"Sincronización finalizada. {len(results)} actualizaciones detectadas.")
            self.finished.emit(results)
            
        except Exception as e:
            EmuLog.error(f"Fallo en motor de sincronización nativo: {e}")
            self.error.emit(str(e))

class ScanWorker(QObject):
    """Trabajador profesional con aislamiento de recursos."""
    finished = Signal(int)
    progress = Signal(float)
    status = Signal(str)

    def __init__(self, db_path: Path, directory: str):
        super().__init__()
        self.db_path = db_path
        self.directory = directory
        self._is_active = True

    @Slot()
    def stop(self):
        self._is_active = False

    @Slot()
    def run(self):
        try:
            # 1. Crear entorno aislado en este hilo
            from backend.database import DatabaseManager
            from backend.scanner import ScannerManager
            
            # Instanciamos nuestra propia DB y Scanner para evitar colisiones de hilos
            db = DatabaseManager(self.db_path)
            scanner = ScannerManager(db)
            
            EmuLog.debug(f"ScanWorker: Iniciando escaneo aislado en {self.directory}")
            
            count = scanner.scan_and_register(
                self.directory,
                progress_callback=self.progress.emit,
                status_callback=self.status.emit,
                is_active_check=lambda: self._is_active
            )
            
            self.finished.emit(count)
        except Exception as e:
            EmuLog.error(f"¡Error Crítico en ScanWorker!: {e}")
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
            self.status.emit(self.core_name, "core_downloading|" + self.core_name)
            # El progress callback llamará self.progress.emit(p)
            def progress_cb(p: float):
                self.progress.emit(self.core_name, p)
            def status_cb(s: str):
                self.status.emit(self.core_name, s)
                
            path = self.libretro.download_core(self.core_name, progress_cb, status_cb)
            if path:
                EmuLog.info(f"Instalación exitosa del core '{self.core_name}' en {path}")
                self.status.emit(self.core_name, "core_installed")
                self.finished.emit(self.core_name, path)
            else:
                self.status.emit(self.core_name, "generic_error")
                self.finished.emit(self.core_name, "")
        except Exception as e:
            EmuLog.error(f"Error mortal en CoreDownloadWorker: {e}")
            self.status.emit(self.core_name, "generic_error")
            self.finished.emit(self.core_name, "")


class EmulatorInstallWorker(QObject):
    """Trabajador inteligente para instalar emuladores mediante orquestación nativa."""
    finished = Signal(str, str)
    progress = Signal(str, float)
    status = Signal(str, str)

    def __init__(self, config: EmulatorInstallConfig):
        super().__init__()
        self.config = config

    @Slot()
    def run(self):
        emu_id = self.config.emu_id
        try:
            import mango_engine
            def progress_cb(p: float):
                self.progress.emit(emu_id, p)
            def status_cb(s: str):
                EmuLog.debug(f"M.A.N.G.O Orchestra ({emu_id}): {s}")
                self.status.emit(emu_id, s)
            
            EmuLog.info(f"M.A.N.G.O Orchestra: Instalando '{emu_id}' (System: {self.config.system_id or 'N/A'})")
            
            path = mango_engine.install_emulator_orchestra(
                emu_id,
                self.config.system_id or "",
                self.config.url or "",
                self.config.dest_dir,
                self.config.executable,
                progress_cb,
                status_cb
            )
            
            if path:
                EmuLog.info(f"Éxito en orquestación de '{emu_id}' -> {path}")
                self.status.emit(emu_id, "install_success")
                self.finished.emit(emu_id, path)
            else:
                self.status.emit(emu_id, "install_failed")
                self.finished.emit(emu_id, "")
        except Exception as e:
            EmuLog.error(f"Error en M.A.N.G.O Orchestra: {e}")
            self.status.emit(emu_id, f"install_error|{str(e)}")
            self.finished.emit(emu_id, "")


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
            # 1. Activación de Motores & Logs (10%)
            self.status.emit("startup_native")
            self.ctrl.proactive_background_load()
            self.progress.emit(0.10)
            
            # --- PROTOCOLO DE PRECARGA NATIVO: M.A.N.G.O (60%) ---
            # Aquí es donde Rust toma el control y hace la carga pesada en hilos paralelos.
            self.status.emit("startup_db")
            
            # Llamada unificada: DB Stats + Asset Warmup + Emu Cache
            data = self.ctrl.precharge_ecosystem()
            
            self.progress.emit(0.60)
            
            # 3. Servicios y Conectividad (85%)
            self.status.emit("startup_services")
            try:
                # Comprobar si Discord RPC está habilitado y conectar en background
                if hasattr(self.ctrl.orch_ctrl, 'discord_rpc'):
                    self.ctrl.orch_ctrl.discord_rpc.connect()
            except Exception: pass
            
            # Si el motor detectó cambios, podrías inyectar datos aquí
            if data:
                EmuLog.debug(f"Protocolo de Precarga completado con {data.get('total_games', 0)} juegos.")
                
            self.progress.emit(0.85)
            
            # 4. Finalización de Estructura de UI (100%)
            self.status.emit("startup_ready")
            self.progress.emit(1.0)
            self.finished.emit()
            
        except Exception as e:
            EmuLog.error(f"Error crítico en StartupWorker: {e}")
            self.finished.emit()


class EmulatorUninstallWorker(QObject):
    """Trabajador para desinstalar emuladores en segundo plano."""
    finished = Signal(str, bool)

    def __init__(self, emu_id: str, dest_dir: str):
        super().__init__()
        self.emu_id = emu_id
        self.dest_dir = dest_dir

    @Slot()
    def run(self):
        try:
            import mango_engine
            EmuLog.info(f"M.A.N.G.O Orchestra: Iniciando desinstalación nativa de {self.emu_id}...")
            
            # Delegar al motor Rust
            mango_engine.uninstall_emulator(self.dest_dir)
            
            EmuLog.info(f"✓ {self.emu_id} desinstalado con éxito (Motor M.A.N.G.O).")
            self.finished.emit(self.emu_id, True)
        except Exception as e:
            EmuLog.error(f"Fallo en motor M.A.N.G.O durante desinstalación de {self.emu_id}: {e}")
            self.finished.emit(self.emu_id, False)


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
            # El motor nativo ya gestiona subprocess y mide el tiempo jugado
            duration = mango_engine.launch_game(self.runner_path, self.game_path, self.core_path)
            self.finished.emit(duration)
        except Exception as e:
            EmuLog.error(f"Error nativo al lanzar juego: {e}")
            self.finished.emit(0)
