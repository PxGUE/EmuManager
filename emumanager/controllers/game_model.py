from PySide6.QtCore import QAbstractListModel, Qt, Slot, QModelIndex
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
    CoverRole = Qt.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self._games = []
        self._all_games = [] # Cache para filtrado rápido

    def roleNames(self):
        return {
            self.FileHashRole: b"fileHash",
            self.FilePathRole: b"filePath",
            self.TitleRole: b"title",
            self.PlatformRole: b"platform",
            self.CoverRole: b"coverPath"
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
        if role == self.CoverRole: return game["cover_image_path"] or ""
        
        return None

    @Slot()
    def update_games(self):
        """Carga o refresca todos los juegos de la base de datos."""
        self.beginResetModel()
        self._all_games = []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Unimos las tablas juegos y metadata para tenerlo todo
            cursor.execute('''
                SELECT g.file_hash, g.file_path, g.platform, m.title, m.cover_image_path
                FROM games g
                JOIN game_metadata m ON g.id = m.game_id
            ''')
            rows = cursor.fetchall()
            for row in rows:
                self._all_games.append(dict(row))
        
        self._games = list(self._all_games)
        self.endResetModel()

    @Slot(str)
    def filter_by_platform(self, platform):
        """Filtra la lista de juegos por plataforma (p.ej. 'snes', 'ps1' o 'all')."""
        self.beginResetModel()
        if platform.lower() == "all":
            self._games = list(self._all_games)
        else:
            self._games = [g for g in self._all_games if g["platform"].lower() == platform.lower()]
        self.endResetModel()
