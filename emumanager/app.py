import sys
import os
import platform
import warnings
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from dotenv import load_dotenv

# --- BOOTSTRAP DE ENTORNO (Single Source of Truth) ---
from core.config import AppConfig
AppConfig.initialize()

# --- OPTIMIZACIÓN DE ASYNCIO EN WINDOWS ---
if sys.platform == 'win32':
    import asyncio
    # Detectamos si es frozen usando el mismo criterio profesional
    _exe_name = os.path.basename(sys.executable).lower()
    _is_frozen = getattr(sys, 'frozen', False) or '__nuitka_binary__' in sys.modules or not _exe_name.startswith("python")
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed transport")

# --- CARGAR CONFIGURACIÓN Y SECRETOS ---
# Cargar desde la raíz de almacenamiento (donde reside .env y data/)
storage_root = AppConfig.get_storage_root()
load_dotenv(storage_root / ".env")
load_dotenv(storage_root / "secrets.env")

# Assets Internos (UI, QML)
package_root = AppConfig.get_package_root()

# Asegurar que el paquete esté en el path para importaciones internas
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

# --- AGREGAR MOTOR NATIVO BINARIO ---
os_name = platform.system().lower()
mango_found = False

# 1. Intentar importación directa (Nuitka module inclusion)
try:
    import mango_engine
    from core.logger import EmuLog
    EmuLog.debug("M.A.N.G.O Engine: Detectado como módulo interno.")
    mango_found = True
except ImportError:
    pass

if not mango_found:
    # 2. Fallback a rutas físicas
    possible_bins = [
        package_root / "mango",
        package_root / "emumanager" / "mango",
        Path(sys.executable).parent / "mango"
    ]
    if not AppConfig.is_frozen():
        # En desarrollo, el binario está en la raíz de mango/
        possible_bins.append(package_root.parent / "mango" / "bin" / os_name)

    for bin_path in possible_bins:
        if bin_path.exists():
            if str(bin_path) not in sys.path:
                sys.path.insert(0, str(bin_path))
            break

# --- IMPORTACIONES DEL SISTEMA ---
from controllers.main_ctrl import MainController
from controllers.game_model import GameListModel # noqa: F401

def init_storage():
    """Asegura la estructura esencial de carpetas local."""
    data_dir = AppConfig.get_app_data_dir()
    for sub in ["db", "media", "logs", "temp"]:
        (data_dir / sub).mkdir(parents=True, exist_ok=True)

def main():
    init_storage()
    
    from core.logger import log_system_info
    log_system_info()
    
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    os.environ["QT_LOGGING_RULES"] = "qt.gui.imageio=false"
    
    from PySide6.QtGui import QIcon
    app = QApplication(sys.argv)
    
    icon_path = AppConfig.get_asset_path("ui", "assets", "logo.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    engine = QQmlApplicationEngine()
    
    # Registrar Controlador Global
    main_controller = MainController()
    engine.rootContext().setContextProperty("mainController", main_controller)
    
    qml_file = AppConfig.get_asset_path("ui", "main.qml")
    engine.load(str(qml_file))
    
    if not engine.rootObjects():
        sys.exit(-1)

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
