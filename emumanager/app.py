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
    # Nota: El sistema de políticas está deprecated desde Python 3.12, pero lo mantenemos
    # silenciado para evitar ruidos en la consola hasta que migremos a un Runner.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Silenciamos warnings de recursos que ya no deberían ocurrir pero por higiene de consola:
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed transport")

# --- CARGAR SECRETOS (SS_DEV_ID, SS_DEV_PASS) ---
# Buscamos .env o secrets.env en la raíz del proyecto
# MODO ESTÁNDAR (Seguro para Instaladores y AppImage)
# Define una carpeta de datos persistente en el perfil del usuario (~/.local/share o %APPDATA%)
# --- DETECTAR SI ESTAMOS EN MODO CONGELADO (BUILD) ---
_exe_name = os.path.basename(sys.executable).lower()
_is_python = _exe_name in ["python.exe", "pythonw.exe", "python", "python3"]
IS_FROZEN = not _is_python or getattr(sys, 'frozen', False) or '__nuitka_binary__' in sys.modules

# --- RESOLUCIÓN DE DIRECTORIO DE DATOS PERSISTENTES ---
if IS_FROZEN:
    appdata = os.getenv('APPDATA')
    if appdata:
        root_dir = Path(appdata).resolve() / "EmuManager"
    else:
        root_dir = Path.home() / "AppData" / "Roaming" / "EmuManager"
else:
    # Desarrollo: Subir un nivel desde emumanager/
    root_dir = Path(__file__).resolve().parent.parent

# Cargar configuración y secretos
load_dotenv(root_dir / ".env")
load_dotenv(root_dir / "secrets.env")

# --- RESOLUCIÓN DE DIRECTORIO DEL PAQUETE (Assets internos) ---
# En Nuitka Onefile, __file__ es la clave para llegar a los assets extraídos
_script_path = Path(__file__).resolve()
if IS_FROZEN:
    # Intentar detectar la raíz del bundle (donde están ui/, resources/, etc.)
    if (_script_path.parent / "ui").exists():
        ui_root = _script_path.parent
    elif (_script_path.parent.parent / "ui").exists():
        ui_root = _script_path.parent.parent
    else:
        ui_root = _script_path.parent
else:
    ui_root = _script_path.parent

# Registrar la raíz de la app
from core.config import AppConfig
AppConfig.set_app_root(ui_root)

# Asegurar que la raíz esté en el path para importaciones internas
if str(ui_root) not in sys.path:
    sys.path.insert(0, str(ui_root))

# AGREGAR MOTOR NATIVO BINARIO
os_name = platform.system().lower()
if IS_FROZEN:
    # En el bundle, buscamos la carpeta 'mango' que incluimos en el script de release
    possible_bins = [
        ui_root / "mango",
        ui_root / "emumanager" / "mango",
        Path(sys.executable).parent / "mango"
    ]
    bin_path = None
    for p in possible_bins:
        if p.exists():
            bin_path = p
            break
    
    if bin_path:
        if str(bin_path) not in sys.path:
            sys.path.insert(0, str(bin_path))
else:
    # Desarrollo
    bin_path = ui_root.parent / "mango" / "bin" / os_name
    if bin_path.exists() and str(bin_path) not in sys.path:
        sys.path.insert(0, str(bin_path))


# --- IMPORTACIONES DEL SISTEMA ---
from controllers.main_ctrl import MainController
from controllers.game_model import GameListModel  # noqa: F401 (Necesario para que PyQt6 registre el @QmlElement)

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
    
    qml_file = ui_root / "ui" / "main.qml"
    
    # Cargamos la interfaz principal
    engine.load(str(qml_file))
    
    if not engine.rootObjects():
        sys.exit(-1)

    # El cierre limpio es fundamental para los hilos de Rust
    app.aboutToQuit.connect(main_controller.shutdown)
        
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        error_msg = f"Error Crítico al iniciar EmuManager:\n\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, error_msg, "Error de Inicio - EmuManager", 0x10)
        sys.exit(1)
