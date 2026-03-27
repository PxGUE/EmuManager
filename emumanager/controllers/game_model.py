from PySide6.QtCore import QAbstractListModel, Qt, Slot, QModelIndex, Property, Signal
from PySide6.QtQml import QmlElement
from backend.database import DatabaseManager

QML_IMPORT_NAME = "EmuManager.Models"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class GameListModel(QAbstractListModel):
    # Roles para acceder a los datos desde QML
    FileHashRole = Qt.UserRole + 1
    FilePathRole = Qt.UserRole + 2
    TitleRole = Qt.UserRole + 3
    PlatformRole = Qt.UserRole + 4
    Cover2dRole = Qt.UserRole + 5
    Cover3dRole = Qt.UserRole + 6
    IdRole = Qt.UserRole + 7
    DeveloperRole = Qt.UserRole + 8
    PublisherRole = Qt.UserRole + 9
    ReleaseDateRole = Qt.UserRole + 10
    GenreRole = Qt.UserRole + 11
    DescriptionRole = Qt.UserRole + 12
    IsFavoriteRole = Qt.UserRole + 13

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self._games = []
        self._all_games = [] # Cache para filtrado rápido

    countChanged = Signal()
    
    @Property(int, notify=countChanged)
    def count(self):
        return len(self._games)

    def roleNames(self):
        return {
            self.FileHashRole: b"fileHash",
            self.FilePathRole: b"filePath",
            self.TitleRole: b"title",
            self.PlatformRole: b"platform",
            self.Cover2dRole: b"cover2dPath",
            self.Cover3dRole: b"cover3dPath",
            self.IdRole: b"gameId",
            self.DeveloperRole: b"developer",
            self.PublisherRole: b"publisher",
            self.ReleaseDateRole: b"releaseDate",
            self.GenreRole: b"genre",
            self.DescriptionRole: b"description",
            self.IsFavoriteRole: b"isFavorite"
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._games)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._games)):
            return None
        
        game = self._games[index.row()]
        
        if role == self.FileHashRole: return game["file_hash"]
        if role == self.FilePathRole: return game["file_path"]
        if role == self.TitleRole: return game["title"]
        if role == self.PlatformRole: return game["platform"]
        if role == self.Cover2dRole: 
            p = game.get("cover_2d_path", "") or ""
            return p.replace("\\", "/")
        if role == self.Cover3dRole: 
            p = game.get("cover_3d_path", "") or ""
            return p.replace("\\", "/")
        if role == self.IdRole: return game.get("id", 0)
        if role == self.DeveloperRole: return game.get("developer", "") or ""
        if role == self.PublisherRole: return game.get("publisher", "") or ""
        if role == self.ReleaseDateRole: return game.get("release_date", "") or ""
        if role == self.GenreRole: return game.get("genre", "") or ""
        if role == self.DescriptionRole: return game.get("description", "") or "Sin descripción disponible."
        if role == self.IsFavoriteRole: return bool(game.get("is_favorite", 0))
        
        return None

    @Slot()
    def update_games(self):
        """Carga o refresca todos los juegos de la base de datos."""
        self.search_games("", "all")

    @Slot(str)
    def filter_by_platform(self, platform):
        """Filtra la lista de juegos por plataforma (p.ej. 'snes', 'ps1' o 'all')."""
        self.search_games("", platform)

    @Slot(str, str)
    def search_games(self, query: str, platform: str):
        """Delega la búsqueda en lotes a M.A.N.G.O con Fuzzymatch y filtros."""
        from core.config import AppConfig
        
        try:
            import mango_engine
        except ImportError:
            mango_engine = None
            
        if not mango_engine:
            from core.logger import EmuLog
            EmuLog.warning("M.A.N.G.O (Rust) no disponible. Búsqueda Desactivada.")
            return
            
        self.beginResetModel()
        try:
            db_path = str(AppConfig.get_database_path())
            self._games = mango_engine.search_games(db_path, query, platform)
        except Exception as e:
            from core.logger import EmuLog
            EmuLog.error(f"Error fatal en búsqueda fuzzymatch: {e}")
            self._games = []
        self.endResetModel()
        self.countChanged.emit()
