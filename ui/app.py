"""
EmuApp - Clase de la Ventana Principal (QMainWindow)
Controla la navegación lateral (Sidebar) y el intercambio de vistas.
"""

import asyncio
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from core.emulators import EmuladorManager
from core.i18n import Translator

# Importación diferida para las vistas principales
from ui.views.dashboard import DashboardView
from ui.views.library import LibraryView
from ui.views.downloads import DownloadsView
from ui.views.settings import SettingsView

class EmuApp(QMainWindow):
    """Interfaz principal del programa que gestiona el menú lateral y las páginas."""
    
    def __init__(self):
        super().__init__()
        # 1. Configurar título de la aplicación
        self.emu_name = "EmuManager"
        self.emu_version = "v0.1.3 alpha"
        self.update_window_title()
        
        # 2. Inicializar los gestores fundamentales
        self.emu_manager = EmuladorManager()                     # Gestión de carpetas/procesos emuladores
        self.translator = Translator(self.emu_manager.language) # Traducciones dinámicas (i18n)
        
        # 3. Configurar rutas de arte dinámicas
        import core.artwork as artwork
        if self.emu_manager.install_path:
            media_path = os.path.join(self.emu_manager.install_path, "media")
            artwork.set_base_media_path(media_path)
        
        # 3. Mapeo de plataformas para las carátulas (Libretro)
        from core.constants import AVAILABLE_EMULATORS
        self.emu_platform_map = {
            emu["id"]: emu.get("libretro_platform")
            for emu in AVAILABLE_EMULATORS
        }
        
        # 4. Construir la interfaz estructural
        self.init_ui()
        
        # 5. Iniciar hilos o tareas en segundo plano (como el monitoreo de tiempo jugado)
        self.start_background_tasks()
        
    def init_ui(self):
        """Inicializa los controles visuales, el menú lateral (Sidebar) y el Stack de vistas."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal: [Menú Lateral | Contenido Dinámico]
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- MENÚ LATERAL (Sidebar) ---
        sidebar_container = QWidget()
        sidebar_container.setObjectName("sidebarContainer")
        sidebar_container.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # --- App name (en lugar del logo) ---
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import Qt, QSize
        import os
        
        app_name_lbl = QLabel("EmuManager")
        app_name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name_lbl.setStyleSheet("""
            color: #4da6ff;
            font-size: 15px;
            font-weight: 900;
            letter-spacing: 1px;
            padding: 24px 10px 8px 10px;
            background: transparent;
        """)
        sidebar_layout.addWidget(app_name_lbl)
        
        # Línea separadora sutil
        from PyQt6.QtWidgets import QFrame
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #1a1c24; border: none; max-height: 1px; margin: 0 16px;")
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(10)
        
        self.sidebar = QListWidget()
        self.sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sidebar.setObjectName("sidebarMenu")
        self.sidebar.currentRowChanged.connect(self.change_view)
        
        self.add_sidebar_item(self.translator.t("nav_home"), "home")
        self.add_sidebar_item(self.translator.t("nav_library"), "folder")
        self.add_sidebar_item(self.translator.t("nav_downloads"), "download")
        self.add_sidebar_item(self.translator.t("nav_settings"), "settings")
        
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()
        
        # Versión al fondo
        ver_lbl = QLabel("v0.1.3 alpha")
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver_lbl.setStyleSheet("""
            color: #333344;
            font-size: 10px;
            padding: 12px;
            background: transparent;
        """)
        sidebar_layout.addWidget(ver_lbl)
        
        # --- CONTENEDOR DE VISTAS (Stacked Widget) ---
        # Este controla qué página (Dashboard, Biblioteca, etc.) se muestra
        self.views_stack = QStackedWidget()
        
        # Instanciar las vistas pasando los gestores necesarios
        self.dashboard_view = DashboardView(self.emu_manager, self.translator)
        self.library_view = LibraryView(self.emu_manager, self.emu_platform_map, self.translator, self)
        def on_library_needs_refresh():
            """Marca la biblioteca para que recargue la próxima vez que se muestre."""
            self.library_view._needs_refresh = True
            # Si la biblioteca ya está visible, recargar ahora
            if self.views_stack.currentIndex() == 1:
                self.library_view.mostrar_consolas()
        
        # La vista de descargas necesita poder recargar la biblioteca cuando termine de instalar algo
        self.downloads_view = DownloadsView(self.emu_manager, self.translator, on_library_needs_refresh)
        # Los ajustes necesitan poder actualizar el dashboard (si cambia el idioma)
        self.settings_view = SettingsView(self.emu_manager, self.translator, self.dashboard_view.update_dashboard_status, self.on_language_change)
        
        # Apilar las vistas en el stacker
        self.views_stack.addWidget(self.dashboard_view) # Index 0
        self.views_stack.addWidget(self.library_view)   # Index 1
        self.views_stack.addWidget(self.downloads_view) # Index 2
        self.views_stack.addWidget(self.settings_view)  # Index 3
        
        # Inyectar componentes al layout principal
        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(self.views_stack)
        
        # Iniciar en la página de inicio (Dashboard)
        self.sidebar.setCurrentRow(0)
        
    def update_window_title(self):
        """Actualiza el título de la ventana con la versión actual."""
        self.setWindowTitle(f"{self.emu_name} {self.emu_version}")

    def add_sidebar_item(self, text, icon_name):
        """Añade una fila al menú lateral."""
        item = QListWidgetItem(text)
        self.sidebar.addItem(item)
        
    def change_view(self, index):
        """Intercambia el contenido de la ventana principal según el índice seleccionado."""
        self.views_stack.setCurrentIndex(index)
        
    def on_language_change(self, new_lang):
        """Actualiza todos los textos de la interfaz cuando el usuario cambia el idioma en Ajustes."""
        self.translator.set_language(new_lang)
        
        # 1. Repintar menú lateral
        self.sidebar.item(0).setText(self.translator.t("nav_home"))
        self.sidebar.item(1).setText(self.translator.t("nav_library"))
        self.sidebar.item(2).setText(self.translator.t("nav_downloads"))
        self.sidebar.item(3).setText(self.translator.t("nav_settings"))
        
        # 2. Recrear las vistas para forzar actualización de textos (hard reload)
        for i in reversed(range(self.views_stack.count())): 
            widget = self.views_stack.widget(i)
            self.views_stack.removeWidget(widget)
            widget.deleteLater()
            
        self.dashboard_view = DashboardView(self.emu_manager, self.translator)
        self.library_view = LibraryView(self.emu_manager, self.emu_platform_map, self.translator, self)
        self.downloads_view = DownloadsView(self.emu_manager, self.translator, self.library_view.mostrar_consolas)
        self.settings_view = SettingsView(self.emu_manager, self.translator, self.dashboard_view.update_dashboard_status, self.on_language_change)
        
        self.views_stack.addWidget(self.dashboard_view)
        self.views_stack.addWidget(self.library_view)
        self.views_stack.addWidget(self.downloads_view)
        self.views_stack.addWidget(self.settings_view)
        
        # Mantener al usuario en la pestaña de Ajustes tras la actualización
        self.views_stack.setCurrentIndex(3)
        self.update_window_title()

    def start_background_tasks(self):
        """Tareas asíncronas constantes (Playtime tracking)."""
        loop = asyncio.get_event_loop()
        loop.create_task(self._monitor_playtime())
        
    async def _monitor_playtime(self):
        """
        Observador de Tiempo Jugado:
        Cada 5 segundos comprueba si un emulador está abierto y suma tiempo a su ficha.
        """
        while True:
            if self.emu_manager.is_emulator_running():
                try:
                    game_obj = self.emu_manager.launcher.current_game
                    start_time = self.emu_manager.launcher.current_game_start
                    self.emu_manager.update_playtime(game_obj, start_time)
                except Exception as e:
                    pass
            # Intervalo de chequeo
            await asyncio.sleep(5)
