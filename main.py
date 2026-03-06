import flet as ft
from ui.app import EmuApp

async def main(page: ft.Page):
    page.title = "EmuManager"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1000
    page.window_height = 700
    page.padding = 0

    app = EmuApp(page)
    page.add(app)
    
if __name__ == "__main__":
    ft.app(target=main, assets_dir="media", view=ft.AppView.FLET_APP)
