from PySide6.QtCore import QObject, Signal, Slot, QThread
from pathlib import Path
import json
import os
import platform as py_platform
from core.config import AppConfig
from core.logger import EmuLog
from controllers.workers import (
    EmulatorInstallWorker, CoreDownloadWorker, LaunchWorker,
    EmulatorUninstallWorker, EmulatorInstallConfig
)
from backend.discord_rpc import DiscordRPCManager

class OrchestraController(QObject):
    """
    Controlador especializado en la instalación de emuladores, núcleos y lanzamiento de juegos.
    """
    # Señales (Espejo de lo que QML espera)
    coreDownloadProgressChanged = Signal(str, float)
    coreDownloadStatusChanged = Signal(str, str)
    coreDownloadFinished = Signal(str, str)
    notify_library_changed = Signal()
    
    def __init__(self, db, libretro_manager, parent=None):
        super().__init__(parent)
        self.db = db
        self.libretro = libretro_manager
        
        self._emu_thread = None
        self._emu_worker = None
        self._core_thread = None
        self._core_worker = None
        self._active_launches = {} # Track de hilos de juego para evitar GC
        self._installed_versions = {} # Cache local de versiones registradas
        
        # Iniciar Discord RPC
        self.discord_rpc = DiscordRPCManager()
        self.discord_rpc.set_enabled(AppConfig.get_discord_rpc_enabled())

    def _get_manifest(self):
        """Lee el archivo de catálogos y devuelve su JSON, o una lista vacía si falla."""
        repo_path = AppConfig.get_asset_path("resources", "repositories.json")
        if not repo_path.exists():
            EmuLog.error(f"¡Catálogo crítico no encontrado en {repo_path}!")
            return []
        try:
            with open(repo_path, 'r', encoding='utf-8') as f:
                return json.load(f).get("emulators", [])
        except Exception as e:
            EmuLog.error(f"Error cargando repositories.json: {e}")
            return []

    def _check_system_installed(self, emu_id, executable_name, system_id, base_path, mango=None):
        """Verifica localmente y a través de M.A.N.G.O (Rust) si un motor está instalado."""
        local_path = base_path / emu_id / executable_name
        is_installed = local_path.exists()
        if not is_installed and mango and system_id:
            try: is_installed = mango.check_system_installed(system_id)
            except Exception: pass
        return is_installed, local_path

    @Slot(result='QVariantList')
    def get_emulator_repositories(self):
        """Devuelve el catálogo de emuladores con el estado en vivo de instalación y actualizaciones."""
        emulators = self._get_manifest()
        if not emulators: return []
            
        os_name = py_platform.system().lower()
        base_path = Path(AppConfig.get_emulators_path() or ".")
        
        try: import mango_engine
        except ImportError: mango_engine = None

        updates_map = self.get_installed_tags()

        for emu in emulators:
            emu_id = emu.get("id", "")
            orchestra = emu.get("orchestration", {})
            
            # Resoluciones
            os_orchestra = orchestra.get(os_name, {})
            system_id = os_orchestra.get("id", "")
            emu["systemId"] = system_id
            emu["downloadUrl"] = orchestra.get("portable", {}).get(os_name, "")
            emu["executable"] = emu.get("executable", {}).get(os_name, "")
            
            is_installed, local_path = self._check_system_installed(
                emu_id, emu["executable"], system_id, base_path, mango_engine
            )
            
            emu_data = updates_map.get(emu_id, {})
            # Forzamos boolean para evitar 'undefined' en QML
            has_update = bool(is_installed and emu_data.get("remote_tag") and (emu_data.get("installed_tag") != emu_data.get("remote_tag")))

            emu["isInstalled"] = is_installed
            emu["hasUpdate"] = has_update
            emu["localPath"] = str(local_path) if is_installed else ""
            emu["progress"] = 0.0
            
            # Asignación de textos automáticos
            if is_installed:
                emu["statusText"] = "btn_update" if has_update else "emu_status_installed"
            else:
                emu["statusText"] = "emu_status_available"
                
        return emulators

    @Slot(str, str, str, result=bool)
    def install_emulator(self, emu_id, url="", executable=""):
        """Inicia el hilo de instalación de un emulador."""
        if self._emu_thread and self._emu_thread.isRunning():
            EmuLog.warning(f"Ya hay una tarea de emulador en curso ({emu_id}).")
            return False

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
        if emu_id == "retroarch":
            dest_dir.mkdir(parents=True, exist_ok=True)
            (dest_dir / "cores").mkdir(parents=True, exist_ok=True)

        EmuLog.info(f"M.A.N.G.O Orchestra: Iniciando misión para {emu_id}...")
        
        config = EmulatorInstallConfig(emu_id, system_id, url, str(dest_dir), executable)
        self._emu_thread = QThread()
        self._emu_worker = EmulatorInstallWorker(config)
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

    def _clear_emu_thread(self):
        self._emu_thread = None
        self._emu_worker = None

    def _on_emu_install_finished(self, emu_id, path):
        if path:
            EmuLog.info(f"✓ La misión de instalación de {emu_id} ha sido un éxito en {path}")
            
            # Registrar versión instalada si es un update
            remote_data = self.get_installed_tags().get(emu_id)
            if remote_data and remote_data.get("remote_tag"):
                self.save_installed_tag(emu_id, remote_data["remote_tag"])

            self.coreDownloadStatusChanged.emit(emu_id, "install_success_tag")
            self.coreDownloadFinished.emit(emu_id, path)
            self.notify_library_changed.emit()
        else:
            EmuLog.error(f"La misión de instalación de {emu_id} ha fallado.")
            self.coreDownloadStatusChanged.emit(emu_id, "install_failed_tag")
            self.coreDownloadFinished.emit(emu_id, "")

    @Slot(str, result=bool)
    def start_core_download(self, core_id):
        if self._core_thread and self._core_thread.isRunning():
            EmuLog.warning("Ya hay una descarga de core en curso.")
            return False

        self.coreDownloadStatusChanged.emit(core_id, f"core_download_init_msg|{core_id}")
        self.coreDownloadProgressChanged.emit(core_id, 0.0)

        self._core_thread = QThread()
        self._core_worker = CoreDownloadWorker(self.libretro, core_id)
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

    def _clear_core_thread(self):
        self._core_thread = None
        self._core_worker = None

    def _on_core_download_finished(self, path):
        core_id = self._core_worker.core_name if self._core_worker else "core"
        if path:
            self.coreDownloadStatusChanged.emit(core_id, f"core_install_finished_msg|{Path(path).name}")
            self.coreDownloadFinished.emit(core_id, path)
            self.notify_library_changed.emit()
        else:
            self.coreDownloadStatusChanged.emit(core_id, "download_failed")

    @Slot(str)
    def uninstall_core(self, core_id):
        """Solicita la eliminación de un núcleo específico."""
        if self.libretro.uninstall_core(core_id):
            self.notify_library_changed.emit()
            EmuLog.info(f"Core {core_id} desinstalado con éxito.")

    @Slot()
    def launch_random_game(self):
        """Busca un juego aleatorio en la DB y lo lanza."""
        try:
            with self.db.get_connection() as conn:
                row = conn.execute("SELECT id FROM games ORDER BY RANDOM() LIMIT 1").fetchone()
                if row:
                    EmuLog.info(f"M.A.N.G.O: Lanzando selección aleatoria {row['id']}...")
                    self.launch_game(row["id"])
                else:
                    EmuLog.warning("No hay juegos en la biblioteca para lanzar de forma aleatoria.")
        except Exception as e:
            EmuLog.error(f"Error al lanzar juego aleatorio: {e}")

    @Slot(int)
    def launch_game(self, game_id):
        """Lanza un juego de forma asíncrona."""
        try:
            with self.db.get_connection() as conn:
                row = conn.execute("SELECT file_path, platform FROM games WHERE id = ?", (game_id,)).fetchone()
                if not row: return
                game_path = row["file_path"]
                platform_id = row["platform"].lower()
            
            # Decidir Lanzador
            runner, core_path = self._resolve_runner(platform_id)
            if not runner:
                EmuLog.error(f"No se pudo encontrar un emulador compatible para {platform_id}.")
                return

            EmuLog.info(f"M.A.N.G.O Launch: Lanzando {Path(game_path).name} con {runner.name}...")
            
            thread = QThread(self)
            worker = LaunchWorker(str(runner), game_path, core_path)
            worker.moveToThread(thread)
            
            self._active_launches[game_id] = (thread, worker) # Persistencia para evitar GC
            
            # Actualizar Discord RPC
            with self.db.get_connection() as conn:
                game_data = conn.execute("SELECT display_name FROM games WHERE id = ?", (game_id,)).fetchone()
                game_title = game_data["display_name"] if game_data else Path(game_path).stem
            
            self.discord_rpc.set_enabled(AppConfig.get_discord_rpc_enabled())
            self.discord_rpc.update_presence(game_title, platform_id)
            
            def cleanup_launch(duration):
                if game_id in self._active_launches: del self._active_launches[game_id]
                self._update_play_stats(game_id, duration)
                self.discord_rpc.clear_presence()
                thread.quit()

            worker.finished.connect(cleanup_launch)
            thread.started.connect(worker.run)
            thread.start()
        except Exception as e:
            EmuLog.error(f"Fallo al lanzar el juego {game_id}: {e}")

    def _resolve_runner(self, platform_id):
        """Lógica interna para decidir entre RetroArch o Standalone."""
        standalone_map = {
            "ps2": "pcsx2", "gc": "dolphin", "wii": "dolphin",
            "psp": "ppsspp", "ps1": "duckstation", "ds": "desmume"
        }
        target_emu_id = standalone_map.get(platform_id)
        if target_emu_id:
            exe = self._find_emulator_executable(target_emu_id)
            if exe: return exe, None
        
        # Fallback RetroArch
        ra_exe = self._find_emulator_executable("retroarch")
        if ra_exe:
            core_id = self.libretro.get_core_for_platform(platform_id)
            if core_id:
                ext = ".dll" if py_platform.system() == "Windows" else ".so"
                core_file = self.libretro.cores_path / platform_id / f"{core_id}_libretro{ext}"
                if core_file.exists(): return ra_exe, str(core_file)
            return ra_exe, None
        return None, None

    def _find_emulator_executable(self, emu_id):
        """Ayudante para localizar el binario de un emulador."""
        is_win = py_platform.system() == "Windows"
        emu_id = emu_id.lower()
        executables = {
            "retroarch": "retroarch.exe" if is_win else "RetroArch.AppImage",
            "dolphin": "Dolphin.exe" if is_win else "Dolphin.AppImage",
            "pcsx2": "pcsx2-qt.exe" if is_win else "PCSX2.AppImage",
            "ppsspp": "PPSSPPWindows64.exe" if is_win else "PPSSPP.AppImage",
            "duckstation": "duckstation-qt-x64-release.exe" if is_win else "DuckStation.AppImage"
        }
        exe_name = executables.get(emu_id)
        if not exe_name: return None
        
        emu_dir = Path(AppConfig.get_emulators_path()) / emu_id
        if not emu_dir.exists(): return None
        
        # Búsqueda recursiva suave
        if (emu_dir / exe_name).exists(): return emu_dir / exe_name
        for sub in emu_dir.iterdir():
            if sub.is_dir() and (sub / exe_name).exists():
                return sub / exe_name
        return None

    @Slot(str, result=bool)
    def uninstall_emulator(self, emu_id):
        """Elimina la carpeta del emulador local en segundo plano."""
        if self._emu_thread and self._emu_thread.isRunning():
            return False

        dest_dir = Path(AppConfig.get_emulators_path()) / emu_id
        if not dest_dir.exists(): return False

        # Emitir estado para que la UI sepa que estamos ocupados
        self.coreDownloadStatusChanged.emit(emu_id, "emu_status_uninstalling")
        self.coreDownloadProgressChanged.emit(emu_id, 0.0)

        self._emu_thread = QThread()
        self._emu_worker = EmulatorUninstallWorker(emu_id, str(dest_dir))
        self._emu_worker.moveToThread(self._emu_thread)

        def _on_uninstall_finished(eid, success):
            if success:
                self.notify_library_changed.emit()
            else:
                self.coreDownloadStatusChanged.emit(eid, "install_failed_tag")
            self._emu_thread.quit()

        self._emu_thread.started.connect(self._emu_worker.run)
        self._emu_worker.finished.connect(_on_uninstall_finished)
        self._emu_thread.finished.connect(self._emu_thread.deleteLater)
        self._emu_thread.finished.connect(self._clear_emu_thread)

        self._emu_thread.start()
        return True

    @Slot(str)
    def open_emulator_folder(self, emu_id):
        """Abre la carpeta del emulador en el explorador del sistema de forma segura."""
        import sys, subprocess
        
        try:
            base_emus_path = Path(AppConfig.get_emulators_path()).resolve()
            # Sanitizar emu_id para evitar saltos (..) o rutas absolutas maliciosas
            target_path = (base_emus_path / emu_id.lstrip('/')).resolve()
            
            # Verificación de seguridad: El path debe estar dentro del directorio de emuladores
            try:
                target_path.relative_to(base_emus_path)
            except ValueError:
                EmuLog.error(f"⚠️ Intento de acceso no autorizado bloqueado: {emu_id}")
                target_path = base_emus_path
                
            if not target_path.exists():
                target_path = base_emus_path

            EmuLog.debug(f"Abriendo carpeta: {target_path}")
            if sys.platform == "linux":
                subprocess.run(["xdg-open", str(target_path)], check=False)
            elif sys.platform == "win32":
                os.startfile(str(target_path))
        except Exception as e:
            EmuLog.error(f"No se pudo abrir la carpeta: {e}")

    def _update_play_stats(self, game_id, duration):
        if duration < 1: return
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
        self.notify_library_changed.emit()

    def get_installed_tags(self):
        """Consulta la base de datos para obtener el historial de versiones."""
        try:
            with self.db.get_connection() as conn:
                rows = conn.execute("SELECT emu_id, installed_tag, remote_tag FROM emulator_status").fetchall()
                return {row["emu_id"]: dict(row) for row in rows}
        except Exception as e:
            EmuLog.error(f"Error consultando historial de versiones: {e}")
            return {}

    def save_installed_tag(self, emu_id, tag):
        """Registra una instalación exitosa en la DB."""
        self.save_installed_tags_batch({emu_id: tag})

    def save_installed_tags_batch(self, tag_map):
        """Registra múltiples tags de instalación en una sola transacción."""
        if not tag_map: return
        try:
            with self.db.get_connection() as conn:
                data = [(emu_id, tag) for emu_id, tag in tag_map.items()]
                conn.executemany("""
                    INSERT INTO emulator_status (emu_id, installed_tag, last_checked_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(emu_id) DO UPDATE SET
                        installed_tag = excluded.installed_tag,
                        last_checked_at = CURRENT_TIMESTAMP
                """, data)
                conn.commit()
        except Exception as e:
            EmuLog.error(f"Error guardando lote de tags de instalación: {e}")

    def save_remote_tag(self, emu_id, tag):
        """Registra que encontramos una versión nueva remotamente."""
        self.save_remote_tags_batch({emu_id: tag})

    def save_remote_tags_batch(self, tag_map):
        """Registra múltiples tags remotos en una sola transacción."""
        if not tag_map: return
        try:
            with self.db.get_connection() as conn:
                data = [(emu_id, tag) for emu_id, tag in tag_map.items()]
                conn.executemany("""
                    INSERT INTO emulator_status (emu_id, remote_tag, last_checked_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(emu_id) DO UPDATE SET
                        remote_tag = excluded.remote_tag,
                        last_checked_at = CURRENT_TIMESTAMP
                """, data)
                conn.commit()
        except Exception as e:
            EmuLog.error(f"Error guardando lote de tags remotos: {e}")

    def shutdown(self):
        self.discord_rpc.disconnect()
        if self._emu_thread and self._emu_thread.isRunning():
            self._emu_thread.quit()
        if self._core_thread and self._core_thread.isRunning():
            self._core_thread.quit()
