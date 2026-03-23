from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtWidgets import QFileDialog
from core.security import CredentialsManager
from core.config import AppConfig
from core.logger import EmuLog
from backend.database import DatabaseManager
from backend.scanner import ScannerManager

QML_IMPORT_NAME = "EmuManager.Controllers"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class MainController(QObject):
    # Señales para comunicación con QML en tiempo real
    scanProgressChanged = Signal(float)  # 0.0 a 1.0
    scanStatusChanged = Signal(str)      # "Escanenando..." "Listo"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        EmuLog.info("EmuManager Iniciando: Cargando componentes de backend...")
        try:
            self.db = DatabaseManager()
            self.scanner = ScannerManager(self.db)
            EmuLog.info(f"Base de Datos Conectada en {AppConfig.get_database_path()}")
        except Exception as e:
            EmuLog.error(f"Fallo crítico al inicializar el backend: {e}")

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
            return directory
        return AppConfig.get_cores_path()

    @Slot(result=str)
    def get_roms_path(self):
        return AppConfig.get_roms_path() or "No configurado"

    @Slot(result=str)
    def get_cores_path(self):
        return AppConfig.get_cores_path() or "No configurado"

    @Slot(result=int)
    def start_full_scan(self):
        """Inicia el escaneo de la ruta de ROMs configurada."""
        path = AppConfig.get_roms_path()
        if not path:
            EmuLog.warning("Se intentó escanear pero no hay ruta configurada.")
            return 0
        EmuLog.info(f"Escaneo Manual Iniciado por Usuario en {path}")
        
        # Conectamos las señales del scanner a nuestras señales de QML
        # (Aunque por ahora el escanner es síncrono para simplicidad inicial)
        self.scanStatusChanged.emit("Iniciando escaneo...")
        self.scanProgressChanged.emit(0.0)
        
        count = self.scanner.scan_and_register(path, 
            progress_callback=self.scanProgressChanged.emit,
            status_callback=self.scanStatusChanged.emit
        )
        
        self.scanStatusChanged.emit(f"Escaneo completado: {count} juegos encontrados.")
        self.scanProgressChanged.emit(1.0)
        return count

    @Slot(result=int)
    def get_games_count(self):
        """Retorna el número total de juegos en la biblioteca."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM games")
            count = cursor.fetchone()[0]
            EmuLog.debug(f"Consulta de conteo de juegos: {count}")
            return count
