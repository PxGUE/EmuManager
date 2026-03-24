import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from dotenv import load_dotenv

# --- CARGAR SECRETOS (SS_DEV_ID, SS_DEV_PASS) ---
load_dotenv()

# Modificamos el import path para resolver módulos desde la raíz emumanager
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# AGREGAR BACKEND PARA EL MOTOR NATIVO
backend_dir = current_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Importamos el controlador y modelos
from controllers.main_ctrl import MainController
from controllers.game_model import GameListModel

def main():
    # Setup de UI application env params
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    
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
