from PySide6.QtCore import QObject, Signal, Slot, QThread
from pathlib import Path
from core.config import AppConfig
from core.logger import EmuLog
from controllers.workers import ScanWorker, ScrapeWorker

class LibraryController(QObject):
    """
    Controlador especializado en la gestión de la biblioteca, escaneo y metadatos.
    """
    # Señales (Espejo de lo que QML espera)
    scanProgressChanged = Signal(float)
    scanStatusChanged = Signal(str)
    scanFinished = Signal(int)
    scrapeProgressChanged = Signal(float)
    scrapeStatusChanged = Signal(str)
    scrapeFinished = Signal(int)
    gamesUpdated = Signal()
    gamesCountChanged = Signal()

    def __init__(self, db, scanner, parent=None):
        super().__init__(parent)
        self.db = db
        self.scanner = scanner
        
        self._scan_thread = None
        self._scan_worker = None
        self._scrape_thread = None
        self._scrape_worker = None

    @Slot(result=bool)
    def start_full_scan(self):
        """Inicia el escaneo de la ruta de ROMs configurada en un hilo separado."""
        path = AppConfig.get_roms_path()
        if not path:
            EmuLog.warning("Se intentó escanear pero no hay ruta configurada.")
            self.scanStatusChanged.emit("scan_no_path")
            self.scanFinished.emit(0)
            return False
            
        if self._scan_thread and self._scan_thread.isRunning():
            EmuLog.warning("Ya hay un escaneo en progreso.")
            return False

        EmuLog.info(f"M.A.N.G.O (Lib): Escaneo Asíncrono Iniciado en {path}")
        
        self._scan_thread = QThread()
        # Usamos la ruta de la DB centralizada para el worker aislado
        db_path = Path(AppConfig.get_database_path())
        self._scan_worker = ScanWorker(db_path, path)
        self._scan_worker.moveToThread(self._scan_thread)

        # Conectar Señales
        self._scan_thread.started.connect(self._scan_worker.run)
        self._scan_worker.progress.connect(self.scanProgressChanged.emit)
        self._scan_worker.status.connect(self.scanStatusChanged.emit)
        self._scan_worker.finished.connect(self._on_scan_finished)
        self._scan_worker.finished.connect(self._scan_thread.quit)
        self._scan_thread.finished.connect(self._scan_thread.deleteLater)
        self._scan_thread.finished.connect(self._clear_scan_thread)

        self._scan_thread.start(QThread.LowPriority)
        return True

    def _clear_scan_thread(self):
        self._scan_thread = None
        self._scan_worker = None

    def _on_scan_finished(self, count):
        EmuLog.info(f"M.A.N.G.O (Lib): Escaneo finalizado. {count} juegos encontrados.")
        self.scanStatusChanged.emit(f"scan_finished_msg|{count}")
        self.scanProgressChanged.emit(1.0)
        self.scanFinished.emit(count)
        self.notify_library_changed()

    @Slot(result=bool)
    def start_scraping(self):
        """Inicia el M.A.N.G.O Engine para buscar portadas faltantes."""
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

    def _clear_scrape_thread(self):
        self._scrape_thread = None
        self._scrape_worker = None

    def _on_scrape_finished(self, count):
        EmuLog.info(f"M.A.N.G.O (Lib): Scraping completado con {count} descargas.")
        self.scrapeStatusChanged.emit(f"scrape_finished_msg|{count}")
        self.scrapeProgressChanged.emit(1.0)
        self.scrapeFinished.emit(count)
        self.notify_library_changed()

    @Slot(str, result="QVariantList")
    def search(self, query):
        """Realiza una búsqueda inteligente (Fuzzy) usando el motor nativo."""
        if not query or len(query) < 2:
            return []
        try:
            import mango_engine
            db_path = str(AppConfig.get_database_path())
            return mango_engine.search_games(db_path, query, "all")
        except Exception as e:
            EmuLog.error(f"Fallo en búsqueda nativa: {e}")
            return self.db.search_games(query)

    @Slot(int, bool)
    def toggle_favorite(self, game_id, is_favorite):
        self.db.update_game_favorite(game_id, is_favorite)
        self.gamesUpdated.emit()

    @Slot(int, result="QVariantMap")
    def get_game_details(self, game_id):
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
                        "description": row[7] or "",
                        "cover2d": (row[8] or "").replace("\\", "/"),
                        "cover3d": (row[9] or "").replace("\\", "/"),
                        "isFavorite": bool(row[10])
                    }
        except Exception as e:
            EmuLog.error(f"Error cargando detalle del juego {game_id}: {e}")
        return {}

    @Slot()
    def stop_scraping(self):
        """Detiene el scraping de forma segura."""
        if self._scrape_worker:
            self._scrape_worker.stop()
        self.scrapeStatusChanged.emit("status_finishing_bg")

    def notify_library_changed(self):
        self.gamesUpdated.emit()
        self.gamesCountChanged.emit()

    def shutdown(self):
        """Cierre seguro de hilos."""
        if self._scan_thread and self._scan_thread.isRunning():
            self._scan_thread.quit()
            self._scan_thread.wait()
        if self._scrape_thread and self._scrape_thread.isRunning():
            if self._scrape_worker: self._scrape_worker.stop()
            self._scrape_thread.quit()
            self._scrape_thread.wait()
