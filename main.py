import sys
import os
import asyncio
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import qInstallMessageHandler, Qt
from PySide6.QtQuickControls2 import QQuickStyle
from qasync import QEventLoop

from core.emulators.manager import EmuladorManager
from core.i18n import Translator
from ui.bridge import AppBridge

def get_resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso, compatible con Nuitka."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def qt_message_handler(mode, context, message):
    if "libpng warning: iCCP" in message or "CRC error" in message:
        return
    print(f"[QT] {message}")

qInstallMessageHandler(qt_message_handler)

async def monitor_playtime(emu_manager):
    while True:
        if emu_manager.is_emulator_running():
            try:
                launcher = emu_manager.launcher
                game_obj = launcher.current_game
                start_time = launcher.current_game_start
                emu_manager.update_playtime(game_obj, start_time)
            except: pass
        await asyncio.sleep(5)

def main():
    # 0. Configurar estilo
    QQuickStyle.setStyle("Fusion")
    
    # 1. Configurar aplicación
    app = QApplication(sys.argv)
    
    # Configurar el icono de la aplicación
    icon_path = get_resource_path(os.path.join("media", "icon.svg"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 2. Inicializar lógica central
    emu_manager = EmuladorManager()
    translator = Translator(emu_manager.language)
    
    # 3. Crear el puente Python-QML
    bridge = AppBridge(emu_manager, translator)
    
    # 4. Configurar motor QML
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("bridge", bridge)
    
    # Cargar archivo principal
    qml_file = get_resource_path(os.path.join("ui", "qml", "Main.qml"))
    engine.load(qml_file)
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    # 5. Integrar Asyncio con el loop de Qt
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    
    # Tareas en segundo plano
    event_loop.create_task(monitor_playtime(emu_manager))
    
    with event_loop:
        event_loop.run_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
