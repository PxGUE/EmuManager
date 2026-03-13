"""
EmuManager - Punto de entrada principal
"""

from core.config import APP_VERSION, APP_NAME

import sys
import os
import asyncio
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import qInstallMessageHandler
from qasync import QEventLoop
from ui.app import EmuApp

def get_resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso, compatible con PyInstaller."""
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- CONFIGURACIÓN DE LOGS Y FILTROS ---
def qt_message_handler(mode, context, message):
    """Filtra y silencia las advertencias molestas de perfiles de color PNG (iCCP)"""
    if "libpng warning: iCCP" in message or "CRC error" in message:
        return
    # Puedes habilitar estos prints si necesitas debuggear otros errores de Qt
    # print(f"Qt Msg: {message}")

# Instalar el manejador de mensajes de Qt para limpiar la consola
qInstallMessageHandler(qt_message_handler)

def load_stylesheet(app):
    """Carga la hoja de estilos global QSS."""
    qss_path = get_resource_path(os.path.join("ui", "styles", "theme_dark.qss"))
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"[WARN] No se encontró el tema QSS en {qss_path}")

def main():
    """Inicialización del bucle de eventos asíncrono y la ventana principal"""
    # 1. Crear la instancia de aplicación de Qt
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # Aplicar el tema (QSS) en toda la App
    load_stylesheet(app)
    
    # Configurar el icono de la aplicación
    icon_path = get_resource_path(os.path.join("media", "icon.svg"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 2. Integrar Asyncio con el Event Loop de Qt usando qasync
    # qasync permite que las corrutinas de asyncio corran sobre el loop de Qt
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # 3. Lanzar la ventana principal
    window = EmuApp()
    window.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
    window.resize(1200, 800) # Tamaño inicial recomendado
    window.show()
    
    # 4. Iniciar el loop infinito
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
