from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtWidgets import QFileDialog
from core.config import AppConfig
from core.logger import EmuLog

class AppConfigController(QObject):
    """
    Controlador especializado en ajustes, credenciales y configuración del sistema.
    """
    language_changed = Signal(str)
    emulators_path_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(result=str)
    def get_language(self):
        return AppConfig.get_language()

    @Slot(str)
    def set_language(self, lang):
        if lang in ["es", "en"]:
            AppConfig.set_language(lang)
            self.language_changed.emit(lang)
            EmuLog.info(f"M.A.N.G.O I18n: Idioma cambiado a: {lang}")

    @Slot(str, result=str)
    def get_api_credential(self, service: str) -> str:
        if service == "screenscraper_user":
            return AppConfig.get_screenscraper_user()
        elif service == "screenscraper_pass":
            return AppConfig.get_screenscraper_pass()
        elif service == "gametdb_mode":
            return AppConfig.get_gametdb_mode()
        elif service == "discord_rpc":
            return str(AppConfig.get_discord_rpc_enabled()).lower()
        return ""

    @Slot(str, str)
    def set_api_credential(self, service: str, value: str):
        if service == "screenscraper_user":
            AppConfig.set_screenscraper_user(value)
        elif service == "screenscraper_pass":
            AppConfig.set_screenscraper_pass(value)
        elif service == "gametdb_mode":
            AppConfig.set_gametdb_mode(value)
        elif service == "discord_rpc":
            AppConfig.set_discord_rpc_enabled(value.lower() == "true")

    @Slot(result=str)
    def select_roms_directory(self):
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
        directory = QFileDialog.getExistingDirectory(
            None, "Seleccionar Directorio Principal para Emuladores", AppConfig.get_emulators_path() or ""
        )
        if directory:
            AppConfig.set_emulators_path(directory)
            self.emulators_path_changed.emit()
            EmuLog.info(f"Configurada nueva ruta de Emuladores: {directory}")
            return directory
        return AppConfig.get_emulators_path()
