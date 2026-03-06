import flet as ft
import asyncio
import platform

class SettingsView(ft.Container):
    def __init__(self, emu_manager, on_update_dashboard_status=None):
        super().__init__()
        self.emu_manager = emu_manager
        self.on_update_dashboard_status = on_update_dashboard_status
        
        self.path_field = ft.TextField(
            label="Carpeta de Emuladores",
            value=self.emu_manager.install_path,
            expand=True,
            on_submit=self.on_path_submit
        )

        self.roms_path_field = ft.TextField(
            label="Carpeta de ROMs/Juegos",
            value=self.emu_manager.roms_path,
            expand=True,
            on_submit=self.on_roms_path_submit
        )

        self.content = ft.Column([
            ft.Text("Configuración", size=32, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Ruta de Emuladores", size=18, weight=ft.FontWeight.W_500),
            ft.Text("Donde se instalarán los programas (mGBA, Dolphin, etc.):", size=14, color=ft.Colors.GREY_400),
            ft.Row([
                self.path_field,
                ft.FilledButton("Seleccionar", icon=ft.Icons.FOLDER_OPEN, on_click=self.seleccionar_carpeta_click),
            ]),
            ft.Divider(),
            ft.Text("Ruta de ROMs / Juegos", size=18, weight=ft.FontWeight.W_500),
            ft.Text("Donde guardas tus copias de seguridad de juegos:", size=14, color=ft.Colors.GREY_400),
            ft.Row([
                self.roms_path_field,
                ft.FilledButton("Seleccionar", icon=ft.Icons.FOLDER_OPEN, on_click=self.seleccionar_roms_click),
            ]),
            ft.Text("(Presiona Enter en el texto o usa el botón para guardar automáticamente)", size=12, italic=True, color=ft.Colors.GREY_500),
            
            ft.Divider(height=40),
            ft.Text("Información de la Aplicación", size=18, weight=ft.FontWeight.W_500),
            ft.ElevatedButton("Acerca de EmuManager", icon=ft.Icons.INFO_OUTLINE, on_click=self.mostrar_acerca_de)
        ], spacing=15)
        self.padding = 30
        self.expand = True
        self.alignment = ft.alignment.top_left

    def mostrar_acerca_de(self, e):
        dlg = ft.AlertDialog(
            title=ft.Text("Acerca de EmuManager", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Versión 0.1.0-alpha", size=16, color=ft.Colors.BLUE_400),
                ft.Text("Gestor integral de juegos retro con interfaz moderna. Descarga, organiza y ejecuta tus emuladores y ROMs clásicas en un solo lugar.", size=13, color=ft.Colors.GREY_300),
                ft.Divider(),
                ft.Text("Copyright © 2026 Christian A. Ordoñez", size=13, color=ft.Colors.GREY_400),
                ft.Divider(),
                ft.Text("Software libre y gratuito bajo licencia GNU GPLv3.", size=14),
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            "Leer detalles de la licencia",
                            ft.TextStyle(color=ft.Colors.BLUE, decoration=ft.TextDecoration.UNDERLINE),
                            url="https://www.gnu.org/licenses/gpl-3.0.html"
                        )
                    ],
                    size=12
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.Text("🇨🇴", size=24)
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], tight=True, spacing=10, width=350),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self.page.close(dlg))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)

    async def on_path_submit(self, e):
        path = self.path_field.value.strip()
        if path:
            print(f"[DEBUG] Auto-guardando ruta emus: {path}")
            self.emu_manager.save_config(install_path=path)
            if self.on_update_dashboard_status:
                self.on_update_dashboard_status()

    async def on_roms_path_submit(self, e):
        path = self.roms_path_field.value.strip()
        if path:
            print(f"[DEBUG] Auto-guardando ruta roms: {path}")
            self.emu_manager.save_config(roms_path=path)

    async def seleccionar_carpeta_click(self, e):
        path = await self.abrir_selector_directorio("Selecciona Carpeta de Emuladores")
        if path:
            self.path_field.value = path
            self.emu_manager.save_config(install_path=path)
            self.path_field.update()
            if self.on_update_dashboard_status:
                self.on_update_dashboard_status()

    async def seleccionar_roms_click(self, e):
        path = await self.abrir_selector_directorio("Selecciona Carpeta de ROMs")
        if path:
            self.roms_path_field.value = path
            self.emu_manager.save_config(roms_path=path)
            self.roms_path_field.update()

    async def abrir_selector_directorio(self, titulo):
        try:
            system = platform.system()
            if system == "Linux":
                proc = await asyncio.create_subprocess_exec(
                    "zenity", "--file-selection", "--directory", f"--title={titulo}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                if stdout:
                    return stdout.decode().strip()
            elif system == "Windows":
                powershell_cmd = (
                    "Add-Type -AssemblyName System.Windows.Forms; "
                    "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
                    f"$f.Description = '{titulo}'; "
                    "if($f.ShowDialog() -eq 'OK') { $f.SelectedPath }"
                )
                proc = await asyncio.create_subprocess_exec(
                    "powershell", "-Command", powershell_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                if stdout:
                    return stdout.decode().strip()
        except Exception as ex:
            print(f"Error al abrir el selector: {ex}")
