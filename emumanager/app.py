import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

# Modificamos el import path para resolver módulos desde la raíz emumanager
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Importamos el controlador y modelos
from controllers.main_ctrl import MainController
from controllers.game_model import GameListModel

def main():
    # Setup de UI application env params
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    qml_file = current_dir / "ui" / "main.qml"
    
    # Cargamos la interfaz principal
    engine.load(str(qml_file))
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
