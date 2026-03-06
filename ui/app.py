import flet as ft
from core.emulators import EmuladorManager
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork

from ui.views.dashboard import DashboardView
from ui.views.library import LibraryView
from ui.views.downloads import DownloadsView
from ui.views.settings import SettingsView

class EmuApp(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.expand = True
        self.padding = 0
        self.margin = 0
        self._page_ref = page
        self.emu_manager = EmuladorManager()
        
        self.emu_platform_map = {
            emu["id"]: emu.get("libretro_platform")
            for emu in AVAILABLE_EMULATORS
        }

        # Inicializar vistas (Lazy mounting handles the actual build)
        self.dashboard_view = DashboardView(self.emu_manager)
        self.library_view = LibraryView(self.emu_manager, self.emu_platform_map, self._page_ref)
        self.downloads_view = DownloadsView(self.emu_manager, on_update_library_bg=self.library_view.mostrar_consolas)
        self.settings_view = SettingsView(self.emu_manager, on_update_dashboard_status=self.dashboard_view.update_dashboard_status)

        self.content_area = ft.Container(content=self.dashboard_view, expand=True, padding=0, margin=0)

        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Inicio"),
                ft.NavigationRailDestination(icon=ft.Icons.LIBRARY_BOOKS_OUTLINED, selected_icon=ft.Icons.LIBRARY_BOOKS, label="Biblioteca"),
                ft.NavigationRailDestination(icon=ft.Icons.DOWNLOAD_OUTLINED, selected_icon=ft.Icons.DOWNLOAD, label="Descargar"),
                ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Configuración"),
            ],
            on_change=self.on_nav_change,
        )

        self.content = ft.Row(
            [
                self.rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
        )

    def on_nav_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.content_area.content = self.dashboard_view
        elif index == 1:
            self.content_area.content = self.library_view
        elif index == 2:
            self.content_area.content = self.downloads_view
        elif index == 3:
            self.content_area.content = self.settings_view
            
        self.content_area.update()

    def did_mount(self):
        # Pre-descargar imágenes de consola en segundo plano
        self._page_ref.run_task(self._predescargar_arte_consola)

    async def _predescargar_arte_consola(self):
        if self.emu_manager.roms_path:
            await artwork.predescargar_imagenes_consola(self.emu_platform_map, self.emu_manager.roms_path)
