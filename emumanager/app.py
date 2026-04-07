import sys
import os
import platform
import warnings
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from dotenv import load_dotenv

# --- OPTIMIZACIÓN DE ASYNCIO EN WINDOWS ---
if sys.platform == 'win32':
    import asyncio
    # Usamos SelectorEventLoop en Windows para evitar errores de tuberías cerradas al salir.
    # Es una solución estructural más limpia que parchear el destructor del transporte.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # Silenciamos warnings de recursos que ya no deberían ocurrir pero por higiene de consola:
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed transport")

# --- CARGAR SECRETOS (SS_DEV_ID, SS_DEV_PASS) ---
# Buscamos .env o secrets.env en la raíz del proyecto
# MODO ESTÁNDAR (Seguro para Instaladores y AppImage)
# Define una carpeta de datos persistente en el perfil del usuario (~/.local/share o %APPDATA%)
if getattr(sys, 'frozen', False) or "APPIMAGE" in os.environ:
    if os.name == 'nt':
        # Windows: C:\Users\Nombre\AppData\Roaming\EmuManager
        appdata = os.getenv('APPDATA')
        root_dir = Path(appdata).resolve() / "EmuManager" if appdata else Path.home() / "AppData" / "Roaming" / "EmuManager"
    else:
        # Linux: /home/usuario/.local/share/EmuManager
        root_dir = Path.home() / ".local" / "share" / "EmuManager"
else:
    # En desarrollo usamos la raíz del proyecto para mayor comodidad
    root_dir = Path(__file__).resolve().parent.parent


load_dotenv(root_dir / ".env")
load_dotenv(root_dir / "secrets.env")


# --- CONFIGURACIÓN DE RUTAS ---
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Agregar backend al path
backend_dir = current_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# AGREGAR MOTOR NATIVO BINARIO (Linux/Windows)
os_name = platform.system().lower()

# Buscamos el motor nativo en dos ubicaciones posibles:
# 1. Al lado del binario (Estructura optimizada de Windows)
# 2. En la carpeta superior (Estructura de Desarrollo y AppImage)
bin_path_prod = current_dir / "mango" / "bin" / os_name
bin_path_dev = current_dir.parent / "mango" / "bin" / os_name

if bin_path_prod.exists():
    bin_path = bin_path_prod
else:
    bin_path = bin_path_dev

if bin_path.exists() and str(bin_path) not in sys.path:
    sys.path.insert(0, str(bin_path))


# --- IMPORTACIONES DEL SISTEMA ---
from controllers.main_ctrl import MainController
from controllers.game_model import GameListModel

# --- INICIALIZACIÓN DE ECOSISTEMA DE DATOS ---
def init_storage():
    """Asegura que la estructura de carpetas local exista para EmuManager."""
    data_dir = root_dir / "data"
    subdirs = ["db", "media", "logs", "temp"]
    
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        
    for sub in subdirs:
        (data_dir / sub).mkdir(parents=True, exist_ok=True)

def main():
    # Asegurar entorno de almacenamiento antes de cualquier otra cosa
    init_storage()
    
    # Registrar info del sistema al iniciar
    from core.logger import log_system_info
    log_system_info()
    
    # Setup de UI application env params
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    
    # Silenciar avisos de perfiles de color de libpng (iCCP warnings)
    os.environ["QT_LOGGING_RULES"] = "qt.gui.imageio=false"
    
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # --- REGISTRAR CONTROLADOR GLOBAL ---
    # Esto evita que cada vista QML cree su propio motor, limpiando los logs y ahorrando RAM
    main_controller = MainController()
    engine.rootContext().setContextProperty("mainController", main_controller)
    
    # También registramos los modelos para que QML los vea globalmente si se desea
    # (En este caso los seguiremos instanciando en QML pero vinculados al controlador global)
    
    qml_file = current_dir / "ui" / "main.qml"
    
    # Cargamos la interfaz principal
    engine.load(str(qml_file))
    
    if not engine.rootObjects():
        sys.exit(-1)

    # El cierre limpio es fundamental para los hilos de Rust
    app.aboutToQuit.connect(main_controller.shutdown)
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
