from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QmlElement
from core.security import CredentialsManager

QML_IMPORT_NAME = "EmuManager.Controllers"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class MainController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str, str)
    def saveScreenScraperCredentials(self, username, password):
        """
        Recibe las credenciales desde QML y las guarda de forma segura usando
        el gestor de credenciales local del usuario final.
        """
        print(f"MainController: Recibida petición para guardar credenciales - User: {username}")
        CredentialsManager.save_user_password("screenscraper", username, password)
        print("Credenciales encriptadas y guardadas exitosamente en el llavero/keyring local.")
