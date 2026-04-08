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
        self._all_results = [] # Resultados brutos del motor
        self._show_favorites_only = False

    countChanged = Signal()

    @Property(int, notify=countChanged)
    def count(self):
        return len(self._games)

    @Property(bool, notify=countChanged)
    def showFavoritesOnly(self):
        return self._show_favorites_only

    @showFavoritesOnly.setter
    def showFavoritesOnly(self, val):
        if self._show_favorites_only != val:
            self.beginResetModel()
            self._show_favorites_only = val
            self._apply_filter()
            self.endResetModel()
            self.countChanged.emit()

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
        if role == self.TitleRole: return game.get("display_name") or game.get("title") or ""
        if role == self.PlatformRole: return game["platform"]
        if role == self.Cover2dRole: 
            p = game.get("cover_2d_path", "") or ""
            if p:
                # --- SISTEMA DE MINIATURAS NATIVAS M.A.N.G.O ---
                # Si existe una versión 256w en .cache, la usamos para fluidez total
                import os
                thumb = p.replace("covers/2d", ".cache/thumbs/256w")
                if os.path.exists(thumb):
                    return thumb.replace("\\", "/")
            return p.replace("\\", "/")
        if role == self.Cover3dRole: 
            p = game.get("cover_3d_path", "") or ""
            return p.replace("\\", "/")
        if role == self.IdRole: return game.get("id", 0)
        if role == self.DeveloperRole: return game.get("developer", "") or ""
        if role == self.PublisherRole: return game.get("publisher", "") or ""
        if role == self.ReleaseDateRole: return game.get("release_date", "") or ""
        if role == self.GenreRole: return game.get("genre", "") or ""
        if role == self.DescriptionRole: return game.get("description", "") or ""
        if role == self.IsFavoriteRole: return bool(game.get("is_favorite", 0))
        
        return None

    @Slot(str)
    def filter_by_platform(self, platform):
        """Filtra la lista de juegos por plataforma (p.ej. 'snes', 'ps1' o 'all')."""
        self.search_games("", platform)

    @Slot(str, str)
    def search_games(self, query: str, platform: str):
        """Delega la búsqueda en lotes a M.A.N.G.O con Fuzzymatch y filtros."""
        from core.config import AppConfig
        
        from core.logger import EmuLog
        
        try:
            import mango_engine
        except ImportError:
            mango_engine = None
            
        if not mango_engine:
            EmuLog.warning("M.A.N.G.O (Rust) no disponible. Búsqueda Desactivada.")
            return
            
        self.beginResetModel()
        try:
            db_path = str(AppConfig.get_database_path())
            self._all_results = mango_engine.search_games(db_path, query, platform)
            self._apply_filter()
            EmuLog.info(f"M.A.N.G.O (Model): Búsqueda completada para '{query}' en '{platform}'. Resultados: {len(self._games)}")
        except Exception as e:
            EmuLog.error(f"Error fatal en búsqueda fuzzymatch: {e}")
            self._all_results = []
            self._games = []
        self.endResetModel()
        self.countChanged.emit()

    def _apply_filter(self):
        """Aplica el filtro de favoritos sobre los resultados actuales."""
        if self._show_favorites_only:
            self._games = [g for g in self._all_results if bool(g.get("is_favorite", 0))]
        else:
            self._games = self._all_results

    @Slot(int, bool)
    def set_favorite_locally(self, game_id, is_favorite):
        """Actualiza el estado de favorito solo en memoria para una respuesta instantánea."""
        try:
            target_id = int(game_id)
            # Actualizar en el buffer global
            for g in self._all_results:
                if int(g.get("id", -1)) == target_id:
                    g["is_favorite"] = 1 if is_favorite else 0
                    break
            
            # Si estamos filtrando, debemos re-aplicar y resetear
            if self._show_favorites_only:
                self.beginResetModel()
                self._apply_filter()
                self.endResetModel()
                self.countChanged.emit()
                return

            # Si no estamos filtrando, basta con notificar el cambio de fila
            for i, game in enumerate(self._games):
                if int(game.get("id", -1)) == target_id:
                    game["is_favorite"] = 1 if is_favorite else 0
                    idx = self.index(i, 0)
                    self.dataChanged.emit(idx, idx, [self.IsFavoriteRole])
                    return 
        except Exception as e:
            EmuLog.error(f"Error en set_favorite_locally: {e}")
