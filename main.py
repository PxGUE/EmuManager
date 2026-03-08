"""
EmuManager - Punto de entrada principal
Versión: 0.1.3 alpha
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

def load_stylesheet(app):
    """Carga la hoja de estilos global QSS."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(base_dir, "ui", "styles", "theme_dark.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"[WARN] No se encontró el tema QSS en {qss_path}")

def main():
    """Inicialización del bucle de eventos asíncrono y la ventana principal"""
    # 1. Crear la instancia de aplicación de Qt
    app = QApplication(sys.argv)
    
    # Aplicar el tema (QSS) en toda la App
    load_stylesheet(app)
    
    # Configurar el icono de la aplicación
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "media", "icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
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
