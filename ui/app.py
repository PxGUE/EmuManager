import flet as ft
import asyncio
from core.emulators import EmuladorManager
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork
from core.i18n import Translator

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
        self.translator = Translator(self.emu_manager.language)
        
        self.emu_platform_map = {
            emu["id"]: emu.get("libretro_platform")
            for emu in AVAILABLE_EMULATORS
        }

        # Inicializar vistas (Lazy mounting handles the actual build)
        self.dashboard_view = DashboardView(self.emu_manager, self.translator)
        self.library_view = LibraryView(self.emu_manager, self.emu_platform_map, self._page_ref, self.translator)
        self.downloads_view = DownloadsView(self.emu_manager, self.translator, on_update_library_bg=self.library_view.mostrar_consolas)
        self.settings_view = SettingsView(
            self.emu_manager, 
            self.translator,
            on_update_dashboard_status=self.dashboard_view.update_dashboard_status,
            on_language_change=self.on_language_change
        )

        self.content_area = ft.Container(content=self.dashboard_view, expand=True, padding=0, margin=0)

        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label=self.translator.t("nav_home")),
                ft.NavigationRailDestination(icon=ft.Icons.LIBRARY_BOOKS_OUTLINED, selected_icon=ft.Icons.LIBRARY_BOOKS, label=self.translator.t("nav_library")),
                ft.NavigationRailDestination(icon=ft.Icons.DOWNLOAD_OUTLINED, selected_icon=ft.Icons.DOWNLOAD, label=self.translator.t("nav_downloads")),
                ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label=self.translator.t("nav_settings")),
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
        
        # Iniciar tarea periódica para actualizar el tiempo de juego
        page.run_task(self._monitor_playtime)

    async def _monitor_playtime(self):
        """Tarea de fondo para actualizar el tiempo de juego segundo a segundo mientras el emulador corre."""
        while True:
            if self.emu_manager.is_emulator_running():
                game_obj = self.emu_manager.launcher.current_game
                start_time = self.emu_manager.launcher.current_game_start
                self.emu_manager.update_playtime(game_obj, start_time)
            await asyncio.sleep(5) # Actualizar cada 5 segundos para no sobrecargar el disco

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

    def on_language_change(self, new_lang):
        # Update translator
        self.translator.set_language(new_lang)
        
        # Update Navigation Rail labels
        self.rail.destinations[0].label = self.translator.t("nav_home")
        self.rail.destinations[1].label = self.translator.t("nav_library")
        self.rail.destinations[2].label = self.translator.t("nav_downloads")
        self.rail.destinations[3].label = self.translator.t("nav_settings")
        self.rail.update()
        
        # We need to recreate the views to reflect the new language
        self.dashboard_view = DashboardView(self.emu_manager, self.translator)
        self.library_view = LibraryView(self.emu_manager, self.emu_platform_map, self._page_ref, self.translator)
        self.downloads_view = DownloadsView(self.emu_manager, self.translator, on_update_library_bg=self.library_view.mostrar_consolas)
        self.settings_view = SettingsView(
            self.emu_manager, 
            self.translator,
            on_update_dashboard_status=self.dashboard_view.update_dashboard_status,
            on_language_change=self.on_language_change
        )
        
        # Update current view
        index = self.rail.selected_index
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
