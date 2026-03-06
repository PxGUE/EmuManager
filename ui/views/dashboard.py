import flet as ft
import os

class DashboardView(ft.Container):
    def __init__(self, emu_manager):
        super().__init__()
        self.emu_manager = emu_manager
        
        # Indicadores de estado sutiles
        self.status_emus = ft.Icon(ft.Icons.SUBDIRECTORY_ARROW_RIGHT_ROUNDED, size=24, tooltip="")
        self.status_roms = ft.Icon(ft.Icons.FOLDER_SPECIAL_ROUNDED, size=24, tooltip="")
        
        self.ui_status_section = ft.Column([
            ft.Text("Estado de rutas", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_500),
            ft.Row([
                self.status_emus,
                self.status_roms,
            ], spacing=20, alignment=ft.MainAxisAlignment.END)
        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.END)

        self.welcome_content = ft.Column(
            [
                ft.Text("Bienvenido a EmuManager", size=42, weight=ft.FontWeight.BOLD),
                ft.Text("Tu centro de control para la emulación clásica y moderna.", size=18, color=ft.Colors.BLUE_200),
            ],
            expand=True,
        )

        self.content = ft.Stack([
            self.welcome_content,
            ft.Container(
                content=self.ui_status_section,
                alignment=ft.alignment.bottom_right,
                expand=True
            )
        ], expand=True)

        self.padding = 30
        self.expand = True
        self.alignment = ft.alignment.top_left
        self.update_dashboard_status()

    def update_dashboard_status(self):
        def get_status_data(path, label):
            if not path:
                return ft.Icons.ERROR_OUTLINE, ft.Colors.RED, f"{label}: No configurado"
            if not os.path.exists(path):
                return ft.Icons.WARNING_AMBER_ROUNDED, ft.Colors.AMBER_400, f"{label}: La ruta no existe físicamente"
            return ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, ft.Colors.GREEN, f"{label}: Configurado correctamente"

        # Actualizar Emuladores
        icon_e, color_e, tip_e = get_status_data(self.emu_manager.install_path, "Emuladores")
        self.status_emus.name = icon_e
        self.status_emus.color = color_e
        self.status_emus.tooltip = tip_e

        # Actualizar ROMs
        icon_r, color_r, tip_r = get_status_data(self.emu_manager.roms_path, "ROMs/Juegos")
        self.status_roms.name = icon_r
        self.status_roms.color = color_r
        self.status_roms.tooltip = tip_r

        if self.ui_status_section.page:
            self.ui_status_section.update()
