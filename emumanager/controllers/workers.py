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

    def __init__(self, scanner_manager, mai_controller=None):
        super().__init__()
        self.scanner = scanner_manager
        self.mai = mai_controller
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
                status_callback=self.status.emit,
                is_active_check=lambda: self._is_active
            )
            
            # --- FASE 2: REFINAMIENTO M.A.I (SÓLO SI ESTÁ INSTALADA) ---
            if self._is_active and self.mai and self.mai.isReady and count > 0:
                self.status.emit("mai_refining_phase")
                EmuLog.info(f"M.A.I: Iniciando Fase de Refinamiento Inteligente para {count} juegos...")
                
                # Obtenemos los juegos que no tienen descripción (asumimos que son los recién scrapeados)
                # Esta lógica se puede mejorar después para ser más precisa
                try:
                    from backend.database import DatabaseManager
                    db = DatabaseManager() # Usamos una conexión fresca
                    cursor = db.get_connection().cursor()
                    cursor.execute("""
                        SELECT g.id, g.display_name 
                        FROM games g
                        LEFT JOIN game_metadata m ON g.id = m.game_id
                        WHERE m.description IS NULL OR m.description = ''
                        LIMIT ?
                    """, (count,))
                    games_to_refine = cursor.fetchall()
                    
                    for i, (game_id, name) in enumerate(games_to_refine):
                        if not self._is_active: break
                        
                        # Actualizamos progreso de fase 2
                        current_p = 0.9 + (0.1 * (i / len(games_to_refine)))
                        self.progress.emit(current_p)
                        self.status.emit(f"mai_processing|{name}")
                        
                        # Llamamos a la lógica de refinamiento (que ya definimos en LibraryController)
                        # Nota: Aquí podríamos refactorizar la lógica de refinamiento a una utilidad común
                        # Por ahora, simulamos el flujo de extracción
                        self._perform_mai_refinement(game_id, name)
                        
                except Exception as e:
                    EmuLog.error(f"Fallo en fase de refinamiento M.A.I: {e}")

            self.finished.emit(count)
        except Exception as e:
            EmuLog.error(f"Error fatal en hilo de scraping: {e}")
            self.finished.emit(0)

    def _perform_mai_refinement(self, game_id, title):
        """Versión simplificada de la lógica de refinamiento para el worker usando el motor nativo."""
        try:
            import json
            import mango_engine
            
            EmuLog.info(f"M.A.I (Brain): Analizando semánticamente '{title}'...")
            
            # Wikipedia Search (NATIVO - RUST)
            EmuLog.info(f"M.A.I (Brain): Buscando contexto en Wikipedia para '{title}'...")
            raw_text = mango_engine.scrape_wikipedia_text(title)
            
            if not raw_text:
                EmuLog.debug(f"M.A.I: No se encontró contexto para '{title}', saltando.")
                return
            
            EmuLog.info(f"M.A.I (Brain): Contexto obtenido. Extrayendo metadatos con IA...")
            # IA Extraction
            json_str = self.mai.extract_metadata(raw_text)
            if not json_str:
                EmuLog.warning(f"M.A.I: La IA no pudo interpretar el texto para '{title}'.")
                return
            
            json_str = json_str.replace("```json", "").replace("```", "").strip()
            data = json.loads(json_str)
            
            # DB Update
            EmuLog.info(f"M.A.I (Brain): Guardando metadatos refinados para '{title}'...")
            from backend.database import DatabaseManager
            db = DatabaseManager()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE game_metadata SET
                        developer = ?, publisher = ?, release_date = ?, 
                        genre = ?, description = ?
                    WHERE game_id = ?
                """, (
                    data.get("developer"), data.get("publisher"), str(data.get("year")),
                    data.get("genre"), data.get("description"), game_id
                ))
            EmuLog.info(f"M.A.I (Brain): ✓ Metadatos de '{title}' refinados con éxito.")
        except Exception as e:
            EmuLog.error(f"M.A.I (Error): Fallo al procesar '{title}': {e}")

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
            from core.config import AppConfig
            import time

            # 1. Validación de Estructura y Configuración (5%)
            self.status.emit("initializing")
            time.sleep(0.3) # Sutil pausa para legibilidad visual
            self.progress.emit(0.05)
            
            # 2. Activación de Motores & Logs (15%)
            self.status.emit("startup_native")
            self.ctrl.proactive_background_load()
            self.progress.emit(0.15)
            
            # 3. Verificación de Integridad de Datos (30%)
            self.status.emit("startup_db")
            db_path = AppConfig.get_database_path()
            if not db_path.exists():
                EmuLog.warning("Base de datos no encontrada. M.A.N.G.O creará un nuevo ecosistema.")
            self.progress.emit(0.30)

            # --- PROTOCOLO DE PRECARGA NATIVO: M.A.N.G.O (65%) ---
            # Sincronización Real de Sistemas y Estadísticas
            self.status.emit("startup_db_sync")
            data = self.ctrl.precharge_ecosystem()
            self.progress.emit(0.65)
            
            # 4. Optimización de Caché de Medios (80%)
            self.status.emit("startup_assets")
            # Forzamos que el controlador genere el sumario de consolas AHORA.
            # Esto evita que la UI se bloquee o se vea vacía al entrar.
            self.ctrl.stats_ctrl.get_consoles_summary(False) 
            self.progress.emit(0.80)
            
            # Notificamos a la biblioteca que los datos están listos en memoria
            self.ctrl.libraryChangedRequested.emit(True, False) 
            
            # 5. Servicios y Conectividad (95%)
            self.status.emit("startup_services")
            try:
                if AppConfig.get_discord_rpc_enabled():
                    if hasattr(self.ctrl.orch_ctrl, 'discord_rpc'):
                        self.ctrl.orch_ctrl.discord_rpc.connect()
            except Exception as e:
                EmuLog.debug(f"Startup: No se pudo iniciar Discord RPC: {e}")
            
            self.status.emit("startup_ready")
            self.progress.emit(1.0)
            # Carga finalizada
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
