import sys
import os
import time
from pathlib import Path
from PySide6.QtCore import QObject, Slot, Signal
from core.logger import EmuLog

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

    def __init__(self, emu_id: str, system_id: str, url: str, dest_dir: str, executable: str):
        super().__init__()
        self.emu_id = emu_id
        self.system_id = system_id
        self.url = url
        self.dest_dir = dest_dir
        self.executable = executable

    @Slot()
    def run(self):
        try:
            import mango_engine
            def progress_cb(p: float):
                self.progress.emit(self.emu_id, p)
            def status_cb(s: str):
                self.status.emit(self.emu_id, s)
            
            EmuLog.info(f"M.A.N.G.O Orchestra: Instalando '{self.emu_id}' (System: {self.system_id or 'N/A'})")
            
            path = mango_engine.install_emulator_orchestra(
                self.emu_id, 
                self.system_id or "", 
                self.url or "", 
                self.dest_dir, 
                self.executable, 
                progress_cb,
                status_cb
            )
            
            if path:
                EmuLog.info(f"Éxito en orquestación de '{self.emu_id}' -> {path}")
                self.status.emit(self.emu_id, "install_success")
                self.finished.emit(self.emu_id, path)
            else:
                self.status.emit(self.emu_id, "install_failed")
                self.finished.emit(self.emu_id, "")
        except Exception as e:
            EmuLog.error(f"Error en M.A.N.G.O Orchestra: {e}")
            self.status.emit(self.emu_id, f"install_error|{str(e)}")
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
            # 1. Motor Nativo (20%)
            self.status.emit("startup_native")
            time.sleep(0.4) 
            self.ctrl._is_precharged = False
            self.ctrl.proactive_background_load()
            self.progress.emit(0.25)
            
            # 2. Base de Datos (50%)
            self.status.emit("startup_db")
            time.sleep(0.3)
            # Podríamos disparar un scan rápido aquí si quisiéramos
            self.progress.emit(0.55)
            
            # 3. Preparación de Assets (80%)
            self.status.emit("startup_assets")
            try:
                # Pedimos los juegos a la DB para conocer sus rutas de carátula
                # Usamos el nuevo método optimizado con límite inicial
                games = self.ctrl.db.get_all_games(limit=200)
                # Calentamos solo las primeras 100 (las que el usuario verá primero)
                count = 0
                for game in games:
                    if count > 100: break
                    cover_path = game.get('media_path')
                    if cover_path and os.path.exists(cover_path):
                        # Pre-carga suave en caché del OS
                        try:
                            with open(cover_path, 'rb') as f:
                                f.read(4096) 
                            count += 1
                        except: pass
            except Exception as e:
                EmuLog.debug(f"Aviso en Warm-up: {e}")
            
            self.progress.emit(0.85)
            
            # 4. Finalización (100%)
            self.status.emit("startup_ready")
            self.progress.emit(1.0)
            self.finished.emit()
            
        except Exception as e:
            EmuLog.error(f"Error crítico en StartupWorker: {e}")
            self.finished.emit()


# EmulatorUpdateWorker ELIMINADO: La lógica está unificada en EmulatorInstallWorker (Orchestra).


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
