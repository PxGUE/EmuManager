"""
EmuManager - Punto de entrada principal
Versión: 0.1.1 alpha
Descripción: Gestor de emuladores y ROMs basado en PyQt6 y Asyncio.
"""

import sys
import os
import asyncio
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
from qasync import QEventLoop
from ui.app import EmuApp

# --- CONFIGURACIÓN DE LOGS Y FILTROS ---
def qt_message_handler(mode, context, message):
    """Filtra y silencia las advertencias molestas de perfiles de color PNG (iCCP)"""
    if "libpng warning: iCCP" in message or "CRC error" in message:
        return
    # Puedes habilitar estos prints si necesitas debuggear otros errores de Qt
    # print(f"Qt Msg: {message}")

# Instalar el manejador de mensajes de Qt para limpiar la consola
qInstallMessageHandler(qt_message_handler)

def set_dark_theme(app):
    """Configura el esquema de colores Oscuro Premium (Fusion)"""
    app.setStyle("Fusion")
    palette = QPalette()
    
    # Colores principales
    bg_color = QColor(26, 28, 36)      # Fondo principal
    accent_color = QColor(77, 166, 255) # Azul acento (#4da6ff)
    
    palette.setColor(QPalette.ColorRole.Window, bg_color)
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.ColorRole.AlternateBase, bg_color)
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(36, 40, 50))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, accent_color)
    palette.setColor(QPalette.ColorRole.Highlight, accent_color)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

def main():
    """Inicialización del bucle de eventos asíncrono y la ventana principal"""
    # 1. Crear la instancia de aplicación de Qt
    app = QApplication(sys.argv)
    
    # Configurar el icono de la aplicación
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "media", "icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    set_dark_theme(app)
    
    # 2. Integrar Asyncio con el Event Loop de Qt usando qasync
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # 3. Lanzar la ventana principal
    window = EmuApp()
    window.resize(1200, 800) # Tamaño inicial recomendado
    window.show()
    
    # 4. Iniciar el loop infinito
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
