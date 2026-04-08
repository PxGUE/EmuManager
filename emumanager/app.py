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
# --- DETECTAR SI ESTAMOS EN MODO CONGELADO (BUILD) ---
# Nuitka Onefile extrae a una carpeta temporal, pero sys.frozen o banderas internas deben estar presentes.
_is_frozen_standard = getattr(sys, 'frozen', False) or '__nuitka_binary__' in sys.modules or os.environ.get('NUITKA_ONEFILE_PARENT') is not None
# Detección por "Evidencia Física" de carpeta temporal o AppImage
_is_in_temp = "AppData\\Local\\Temp\\onefile_" in str(Path(__file__).resolve())
_is_appimage = "APPIMAGE" in os.environ

IS_FROZEN = _is_frozen_standard or _is_in_temp or _is_appimage

if IS_FROZEN:
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
if IS_FROZEN:
    # En modo empaquetado, Path(__file__) es el directorio de extracción (Onefile) o el .dist (Standalone)
    base_dir = Path(__file__).resolve().parent
    
    # Buscamos la carpeta UI (Ahora plana en la raíz del paquete)
    if (base_dir / "ui").exists():
        ui_root = base_dir
    elif (base_dir / "emumanager" / "ui").exists():
        ui_root = base_dir / "emumanager"
    else:
        ui_root = base_dir 
else:
    # En desarrollo
    ui_root = Path(__file__).resolve().parent

# Registrar la raíz de la app en la configuración para que todos los controladores la usen
from core.config import AppConfig
AppConfig.set_app_root(ui_root)

if str(ui_root) not in sys.path:
    sys.path.insert(0, str(ui_root))

# Agregar backend al path
backend_dir = ui_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# AGREGAR MOTOR NATIVO BINARIO (Linux/Windows)
os_name = platform.system().lower()

# En un paquete Onefile/Standalone, mango debe estar relativo a la raíz del paquete
if IS_FROZEN:
    base_dir = Path(__file__).resolve().parent
    # El mapeo nuevo es plano: mango/mango_engine.pyd
    possible_bins = [
        base_dir / "mango",
        base_dir / "emumanager" / "mango", 
        ui_root / "mango"
    ]
    bin_path = base_dir # Default fallback
    for p in possible_bins:
        if p.exists():
            bin_path = p
            break
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
