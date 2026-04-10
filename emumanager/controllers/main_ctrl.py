from pathlib import Path
from PySide6.QtCore import QObject, Slot, Signal, QThread
from PySide6.QtQml import QmlElement

from core.config import AppConfig
from core.logger import EmuLog
from backend.database import DatabaseManager
from backend.scanner import ScannerManager
from backend.libretro import LibretroManager
from controllers.workers import StartupWorker

# Importar Sub-Controladores
from controllers.lib_ctrl import LibraryController
from controllers.orch_ctrl import OrchestraController
from controllers.stats_ctrl import StatsController
from controllers.config_ctrl import AppConfigController

QML_IMPORT_NAME = "EmuManager.Controllers"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class MainController(QObject):
    # --- PROPIEDADES DINÁMICAS (Para AboutView etc) ---
    EMUMANAGER_VERSION = AppConfig.APP_VERSION
    MANGO_VERSION = AppConfig.MANGO_VERSION

    # --- SEÑALES (Agregador para QML) ---
    language_changed = Signal(str)
    engineActivityChanged = Signal()
    scanProgressChanged = Signal(float)
    scanStatusChanged = Signal(str)
    scanFinished = Signal(int)
    scrapeProgressChanged = Signal(float)
    scrapeStatusChanged = Signal(str)
    scrapeFinished = Signal(int)
    gamesUpdated = Signal()
    gamesCountChanged = Signal()
    favoriteToggled = Signal(int, bool)
    
    coreDownloadProgressChanged = Signal(str, float)
    coreDownloadStatusChanged = Signal(str, str)
    coreDownloadFinished = Signal(str, str)
    
    startupProgressChanged = Signal(float)
    startupStatusChanged = Signal(str)
    startupFinished = Signal()
    notificationRequested = Signal(str, str, str) # (title, message, type)
    libraryChangedRequested = Signal(bool, bool) # (force_sync, clear_cache)

    from PySide6.QtCore import Property
    @Property(str, constant=True)
    def appVersion(self): return self.EMUMANAGER_VERSION
    
    @Property(str, constant=True)
    def mangoVersion(self): return self.MANGO_VERSION

    # --- ATRIBUTOS DE ESTADO ---
    _scan_progress = 0.0
    _scrape_progress = 0.0
    _is_scanning = False
    _is_scraping = False
    _is_orchestrating = False
    _engine_status_key = "status_system_idle"

    @Property(str, notify=engineActivityChanged)
    def engineStatusKey(self): 
        if not self.isEngineBusy:
            return "status_system_idle"
        return self._engine_status_key

    @Property(bool, notify=engineActivityChanged)
    def isScanning(self): return self._is_scanning

    @Property(bool, notify=engineActivityChanged)
    def isScraping(self): return self._is_scraping

    @Property(bool, notify=engineActivityChanged)
    def isOrchestrating(self): return self._is_orchestrating

    @Property(bool, notify=engineActivityChanged)
    def isEngineBusy(self):
        return bool(self._is_scanning or self._is_scraping or self._is_orchestrating)

    @Property(float, notify=scanProgressChanged)
    def scanProgress(self): return self._scan_progress

    @Property(float, notify=scrapeProgressChanged)
    def scrapeProgress(self): return self._scrape_progress

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Inicializar Managers de Backend
        self.db = DatabaseManager()
        self.scanner = ScannerManager(self.db)
        self.libretro = LibretroManager(Path(AppConfig.get_emulators_path() or "."))
        
        # 2. Inicializar Sub-Controladores
        self.lib_ctrl = LibraryController(self.db, self.scanner, self)
        self.orch_ctrl = OrchestraController(self.db, self.libretro, self)
        self.stats_ctrl = StatsController(self.db, self)
        self.config_ctrl = AppConfigController(self)
        
        # 3. Temporizador de "Debounce" para señales de biblioteca
        from PySide6.QtCore import QTimer
        self._library_update_timer = QTimer(self)
        self._library_update_timer.setSingleShot(True)
        self._library_update_timer.setInterval(250) # 250ms de pausa antes de notificar cambios
        self._library_update_timer.timeout.connect(self._do_notify_library_changed)
        
        # 4. Conexión de Señales Internas para Propagación a QML
        self._connect_signals()
        self.libraryChangedRequested.connect(self.notify_library_changed)
        
        # Estados internos
        self._startup_thread = None
        self._startup_worker = None
        self._is_precharged = False

    def _connect_signals(self):
        """Conecta las señales de los sub-controladores a las señales de MainController."""
        # Configuración
        self.config_ctrl.language_changed.connect(self.language_changed.emit)
        
        # Biblioteca
        self.lib_ctrl.scanProgressChanged.connect(self._on_scan_progress)
        self.lib_ctrl.scanStatusChanged.connect(self._on_scan_status)
        self.lib_ctrl.scanFinished.connect(self._on_scan_finished)
        self.lib_ctrl.scrapeProgressChanged.connect(self._on_scrape_progress)
        self.lib_ctrl.scrapeStatusChanged.connect(self._on_scrape_status)
        self.lib_ctrl.scrapeFinished.connect(self._on_scrape_finished)
        self.lib_ctrl.gamesUpdated.connect(self.notify_library_changed)
        self.lib_ctrl.gamesCountChanged.connect(self.gamesCountChanged.emit)
        
        # Orquesta (Emuladores/Cores)
        self.orch_ctrl.coreDownloadProgressChanged.connect(self.coreDownloadProgressChanged.emit)
        self.orch_ctrl.coreDownloadStatusChanged.connect(self.coreDownloadStatusChanged.emit)
        self.orch_ctrl.coreDownloadFinished.connect(self.coreDownloadFinished.emit)
        self.orch_ctrl.coreDownloadFinished.connect(self._on_emu_install_success)
        self.orch_ctrl.coreDownloadFinished.connect(self.notify_library_changed)
        self.orch_ctrl.notify_library_changed.connect(self.notify_library_changed)

    @Slot()
    def proactive_background_load(self):
        """Carga inicial del motor y sincronización de logs."""
        if self._is_precharged: return
            
        try:
            # Sincronización de Logs M.A.N.G.O (Rust -> Python)
            try:
                import mango_engine
                def _mango_log_bridge(level, msg):
                    if level == "INFO": EmuLog.info(f"M.A.N.G.O: {msg}")
                    elif level == "ERROR": EmuLog.error(f"M.A.N.G.O: {msg}")
                    elif level == "WARN": EmuLog.warning(f"M.A.N.G.O: {msg}")
                    else: EmuLog.debug(f"M.A.N.G.O: {msg}")
                mango_engine.set_log_callback(_mango_log_bridge)
            except ImportError:
                EmuLog.warning("M.A.N.G.O: Motor nativo no detectado.")

            # Warm-up de estadísticas
            self._is_precharged = True
            EmuLog.info(f"M.A.N.G.O: Inicialización del Orquestador v{self.EMUMANAGER_VERSION} completada.")
        except Exception as e:
            EmuLog.error(f"Error en carga proactiva: {e}")

    @Slot(result='QVariant')
    def precharge_ecosystem(self):
        """Llamada unificada al motor nativo para una carga de alta fidelidad."""
        try:
            import mango_engine
            db_path = str(self.db.db_path)
            media_path = str(AppConfig.get_app_data_dir() / "media")
            emus_path = str(AppConfig.get_emulators_path())
            
            # La magia sucede aquí: Rust hace todo en paralelo liberando el GIL
            data = mango_engine.precharge_ecosystem(db_path, media_path, emus_path)
            return data
        except Exception as e:
            EmuLog.error(f"M.A.N.G.O Engine: Error en precarga nativa: {e}")
            return {}

    @Slot()
    def start_startup_sequence(self):
        """Dispara la secuencia de arranque oficial."""
        if self._startup_thread and self._startup_thread.isRunning(): return
            
        self._startup_thread = QThread()
        self._startup_worker = StartupWorker(self)
        self._startup_worker.moveToThread(self._startup_thread)
        
        self._startup_worker.progress.connect(self.startupProgressChanged.emit)
        self._startup_worker.status.connect(self.startupStatusChanged.emit)
        self._startup_worker.finished.connect(self.startupFinished.emit)
        self._startup_worker.finished.connect(self._startup_thread.quit)
        self._startup_thread.started.connect(self._startup_worker.run)
        self._startup_thread.start()

    # --- DELEGACIÓN DE SLOTS (Compatibilidad con QML) ---
    
    # Biblioteca
    @Slot()
    def start_full_scan(self):
        # Reset de progreso para evitar que la barra aparezca llena de sesiones previas
        self._scan_progress = 0.0
        self.scanProgressChanged.emit(0.0)
        self.scanStatusChanged.emit("initializing")
        
        self._is_scanning = True
        self._engine_status_key = "initializing"
        self.engineActivityChanged.emit()
        self.lib_ctrl.start_full_scan()

    @Slot()
    def start_scraping(self):
        # Reset de estado para garantizar que el motor arranque de cero en la UI
        self._scrape_progress = 0.0
        self.scrapeProgressChanged.emit(0.0)
        self.scrapeStatusChanged.emit("initializing")
        
        self._is_scraping = True
        self._engine_status_key = "initializing"
        self.engineActivityChanged.emit()
        self.lib_ctrl.start_scraping()
    
    @Slot()
    def stop_scraping(self): self.lib_ctrl.stop_scraping()

    @Slot(float)
    def _on_scan_progress(self, p):
        self._scan_progress = p
        self.scanProgressChanged.emit(p)

    @Slot(str)
    def _on_scan_status(self, s):
        if not self._is_scanning: return
        self._engine_status_key = s
        self.scanStatusChanged.emit(s)
        self.engineActivityChanged.emit()

    @Slot(int)
    def _on_scan_finished(self, n):
        self._is_scanning = False
        self._scan_progress = 1.0
        self._engine_status_key = "status_system_idle"
        self.scanProgressChanged.emit(1.0)
        self.scanFinished.emit(n)
        self.engineActivityChanged.emit()
        self.notify_library_changed()

    @Slot(float)
    def _on_scrape_progress(self, p):
        self._scrape_progress = p
        self.scrapeProgressChanged.emit(p)

    @Slot(str)
    def _on_scrape_status(self, s):
        if not self._is_scraping: return
        self._engine_status_key = s
        self.scrapeStatusChanged.emit(s)
        self.engineActivityChanged.emit()

    @Slot(int)
    def _on_scrape_finished(self, n):
        self._is_scraping = False
        self._scrape_progress = 1.0
        self._engine_status_key = "status_system_idle"
        self.scrapeProgressChanged.emit(1.0)
        self.scrapeFinished.emit(n)
        self.engineActivityChanged.emit()

    @Slot(str, result="QVariantList")
    def search_library(self, q): return self.lib_ctrl.search(q)
    
    @Slot(int, bool)
    def toggle_favorite(self, i, f): 
        self.lib_ctrl.toggle_favorite(i, f)
        self.favoriteToggled.emit(i, f)
    
    @Slot(int, result="QVariantMap")
    def get_game_details(self, i): return self.lib_ctrl.get_game_details(i)

    # Orquesta
    @Slot(str, str, str, result=bool)
    def install_emulator(self, e, u="", ex=""): return self.orch_ctrl.install_emulator(e, u, ex)
    
    @Slot(str, result=bool)
    def is_emulator_installed(self, e): return self.orch_ctrl._find_emulator_executable(e) is not None
    
    @Slot(str, result=bool)
    def start_core_download(self, c): return self.orch_ctrl.start_core_download(c)
    
    @Slot(str)
    def uninstall_core(self, c): self.orch_ctrl.uninstall_core(c)
    
    @Slot(str)
    def uninstall_emulator(self, e): 
        res = self.orch_ctrl.uninstall_emulator(e)
        if res:
            self.notificationRequested.emit(
                "mission_terminated",
                f"emu_uninstalled_success|{e.capitalize()}",
                "info"
            )
        return res
    
    @Slot(str)
    def open_emulator_folder(self, e): self.orch_ctrl.open_emulator_folder(e)
    
    @Slot(int)
    def launch_game_by_id(self, i): self.orch_ctrl.launch_game(i)
    
    @Slot()
    def launch_random_game(self): self.orch_ctrl.launch_random_game()
    
    @Slot(str, result=str)
    def get_random_cover_for_platform(self, platform):
        """Devuelve la ruta de una carátula aleatoria de la plataforma dada."""
        return self.lib_ctrl.get_random_cover(platform)
    
    @Slot(str, str)
    def _on_emu_install_success(self, emu_id, path):
        """Notifica éxito de orquestación."""
        if path:
            self.notificationRequested.emit(
                "mission_accomplished",
                f"emu_installed_ready|{emu_id.capitalize()}|{Path(path).name}",
                "success"
            )

    @Slot(result='QVariantList')
    def get_emulator_repositories(self): return self.orch_ctrl.get_emulator_repositories()
    
    @Slot(result="QVariantList")
    def fetch_available_cores(self):
        """Coordina entre estadísticas de biblioteca y catálogo de cores."""
        summary = self.stats_ctrl.get_consoles_summary(True)
        active_platforms = [p['platform'] for p in summary if p['platform'] != "all"]
        return self.libretro.fetch_filtered_cores(active_platforms)

    @Slot()
    def check_for_updates(self):
        """Inicia el proceso real de verificación consolidada vía M.A.N.G.O Sync."""
        from controllers.workers import UpdateWorker
        
        if hasattr(self, "_update_thread") and self._update_thread and self._update_thread.isRunning():
            return

        # 1. Recopilar objetivos de sincronización
        targets = {
            "emumanager": "PxGUE/EmuManager" # Repositorio de la App
        }
        
        # Añadir todos los emuladores con github_repo
        repo_manifest = self.get_emulator_repositories()
        for emu in repo_manifest:
            repo = emu.get("github_repo")
            if repo:
                targets[emu["id"]] = repo

        self._update_thread = QThread()
        self._update_worker = UpdateWorker(self.EMUMANAGER_VERSION, targets)
        self._update_worker.moveToThread(self._update_thread)
        
        self._update_worker.finished.connect(self._handle_update_result)
        self._update_worker.error.connect(self._handle_update_error)
        self._update_worker.finished.connect(self._update_thread.quit)
        self._update_worker.error.connect(self._update_thread.quit)
        self._update_thread.started.connect(self._update_worker.run)
        
        EmuLog.info(f"M.A.N.G.O Sync: Iniciando seguimiento para {len(targets)} repositorios...")
        self.coreDownloadStatusChanged.emit("all", "syncing_msg")
        self._update_thread.start()

    def _handle_update_result(self, results):
        """Procesa los resultados de actualización y dispara notificaciones."""
        updates_found = 0
        remote_tags_to_save = {}

        # 1. Obtener estado actual una sola vez (Evitar N+1)
        installed_map = self.orch_ctrl.get_installed_tags()
        
        for res in results:
            item_id = res.get("id")
            remote_tag = res.get("remote_tag")
            
            if item_id == "emumanager":
                # Lógica especial para la App
                current = self.EMUMANAGER_VERSION.replace("v", "").strip().split(" ")[0]
                latest = remote_tag.replace("v", "").strip()
                if latest != current:
                    updates_found += 1
                    self.notificationRequested.emit(
                        "update_available",
                        f"app_update_ready|{latest}",
                        "info"
                    )
            else:
                # Lógica para emuladores
                emu_data = installed_map.get(item_id, {})
                installed_tag = emu_data.get("installed_tag", "")
                
                # Coleccionar remote_tag para guardado por lotes
                remote_tags_to_save[item_id] = remote_tag
                
                if installed_tag != remote_tag:
                    updates_found += 1
                    emu_name = item_id.capitalize()
                    self.notificationRequested.emit(
                        "new_emulator_version",
                        f"emu_update_msg|{emu_name}|{remote_tag}",
                        "success"
                    )

        # 2. Guardar todos los tags remotos en una sola transacción
        if remote_tags_to_save:
            self.orch_ctrl.save_remote_tags_batch(remote_tags_to_save)

        if updates_found > 0:
            EmuLog.info(f"M.A.N.G.O (Updater): Se han detectado {updates_found} actualizaciones.")
            self.coreDownloadStatusChanged.emit("all", f"updates_found_msg|{updates_found}")
        else:
            EmuLog.info("M.A.N.G.O (Updater): Ecosistema al día.")
            self.coreDownloadStatusChanged.emit("all", "system_up_to_date")
        
        self.gamesUpdated.emit()

    def _handle_update_error(self, error):
        """Maneja fallos en la conexión de actualización."""
        EmuLog.error(f"Fallo en motor de sincronización: {error}")
        self.coreDownloadStatusChanged.emit("all", "connection_error")
        self.gamesUpdated.emit()

    # Estadísticas
    @Slot(result="QVariantMap")
    def get_dashboard_stats(self): return self.stats_ctrl.get_dashboard_stats()
    
    @Slot(result="QVariantList")
    @Slot(bool, result="QVariantList")
    def get_consoles_summary(self, c=True): return self.stats_ctrl.get_consoles_summary(c)
    
    @Slot(result=int)
    def get_games_count(self): return self.stats_ctrl.get_games_count()
    
    @Slot(result="QVariantMap")
    def get_system_info(self): return self.stats_ctrl.get_system_info()

    # Configuración
    @Slot(result=str)
    def get_language(self): return self.config_ctrl.get_language()
    
    @Slot(str)
    def set_language(self, l): self.config_ctrl.set_language(l)
    
    @Slot(result=str)
    def get_roms_path(self): return AppConfig.get_roms_path() or "No configurado"
    
    @Slot(result=str)
    def get_emulators_path(self): return AppConfig.get_emulators_path() or "No configurado"

    @Slot(result=str)
    def select_roms_directory(self): return self.config_ctrl.select_roms_directory()
    
    @Slot(result=str)
    def select_cores_directory(self): return self.config_ctrl.select_cores_directory()
    
    @Slot(str, result=str)
    def get_api_credential(self, s): return self.config_ctrl.get_api_credential(s)
    
    @Slot(str, str)
    def set_api_credential(self, s, v): self.config_ctrl.set_api_credential(s, v)
    
    @Slot(str, str)
    def saveScreenScraperCredentials(self, u, p):
        self.config_ctrl.set_api_credential("screenscraper_user", u)
        self.config_ctrl.set_api_credential("screenscraper_pass", p)

    # --- UTILIDADES ---
    def notify_library_changed(self, force_sync=False, clear_cache=True):
        """Dispara el temporizador de notificación (Debounce)."""
        if force_sync:
            self._do_notify_library_changed(clear_cache)
        else:
            # El timer siempre limpia cache por defecto para seguridad
            self._library_update_timer.start()

    def _do_notify_library_changed(self, clear_cache=True):
        """Impacto global de cambios en la biblioteca tras periodo de calma."""
        EmuLog.debug("M.A.N.G.O (UI): Sincronizando estado global de la biblioteca...")
        if clear_cache:
            self.stats_ctrl.clear_cache()
        self.gamesUpdated.emit()
        self.gamesCountChanged.emit()

    @Slot()
    def shutdown(self):
        """Apagado de seguridad de todos los motores."""
        EmuLog.info("M.A.N.G.O: Protocolo de apagado modular iniciado...")
        self.lib_ctrl.shutdown()
        self.orch_ctrl.shutdown()
        EmuLog.info("M.A.N.G.O (Modular): Motores detenidos con éxito.")
