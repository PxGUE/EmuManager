import flet as ft
import asyncio
import platform

class SettingsView(ft.Container):
    def __init__(self, emu_manager, translator, on_update_dashboard_status=None, on_language_change=None):
        super().__init__()
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_dashboard_status = on_update_dashboard_status
        self.on_language_change = on_language_change
        
        self.path_field = ft.TextField(
            label=self.translator.t("set_emus_title"),
            value=self.emu_manager.install_path,
            expand=True,
            on_submit=self.on_path_submit
        )

        self.roms_path_field = ft.TextField(
            label=self.translator.t("set_roms_title"),
            value=self.emu_manager.roms_path,
            expand=True,
            on_submit=self.on_roms_path_submit
        )
        
        self.lang_dropdown = ft.Dropdown(
            label=self.translator.t("set_lang_lbl"),
            value=self.emu_manager.language,
            options=[
                ft.dropdown.Option("es", "Español"),
                ft.dropdown.Option("en", "English")
            ],
            on_select=self.on_lang_changed,
            width=200
        )

        self.content = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text(self.translator.t("set_title"), size=32, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    self.lang_dropdown,
                    ft.Divider(),
                    
                    ft.Text(self.translator.t("set_emus_title"), size=18, weight=ft.FontWeight.W_500),
                    ft.Text(self.translator.t("set_emus_sub"), size=14, color=ft.Colors.GREY_400),
                    ft.Row([
                        self.path_field,
                        ft.FilledButton(self.translator.t("set_btn_select"), icon=ft.Icons.FOLDER_OPEN, on_click=self.seleccionar_carpeta_click),
                    ]),
                    ft.Divider(),
                    ft.Text(self.translator.t("set_roms_title"), size=18, weight=ft.FontWeight.W_500),
                    ft.Text(self.translator.t("set_roms_sub"), size=14, color=ft.Colors.GREY_400),
                    ft.Row([
                        self.roms_path_field,
                        ft.FilledButton(self.translator.t("set_btn_select"), icon=ft.Icons.FOLDER_OPEN, on_click=self.seleccionar_roms_click),
                    ]),
                    ft.Text(self.translator.t("set_auto_save"), size=12, italic=True, color=ft.Colors.GREY_500),
                    
                    ft.Divider(height=40),
                    ft.Text(self.translator.t("set_info_title"), size=18, weight=ft.FontWeight.W_500),
                    ft.ElevatedButton(self.translator.t("set_btn_about"), icon=ft.Icons.INFO_OUTLINE, on_click=self.mostrar_acerca_de)
                ], spacing=15),
                margin=ft.margin.only(right=40)
            )
        ], spacing=0, scroll=ft.ScrollMode.AUTO)
        self.padding = 30
        self.expand = True
        self.alignment = ft.Alignment.TOP_LEFT

    def on_lang_changed(self, e):
        new_lang = self.lang_dropdown.value
        if new_lang:
            self.emu_manager.save_config(language=new_lang)
            if self.on_language_change:
                self.on_language_change(new_lang)

    def mostrar_acerca_de(self, e):
        dlg = ft.AlertDialog(
            title=ft.Text(self.translator.t("set_about_title"), weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(self.translator.t("set_about_ver"), size=16, color=ft.Colors.BLUE_400),
                ft.Text(self.translator.t("set_about_desc"), size=13, color=ft.Colors.GREY_300),
                ft.Divider(),
                ft.Text(self.translator.t("set_about_copy"), size=13, color=ft.Colors.GREY_400),
                ft.Divider(),
                ft.Text(self.translator.t("set_about_license"), size=14),
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            self.translator.t("set_about_link"),
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
                ft.TextButton(self.translator.t("set_btn_close"), on_click=lambda _: self._close_dialog(dlg))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def _close_dialog(self, dlg):
        dlg.open = False
        self.page.update()

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
        path = await self.abrir_selector_directorio(self.translator.t("set_dlg_emus"))
        if path:
            self.path_field.value = path
            self.emu_manager.save_config(install_path=path)
            self.path_field.update()
            if self.on_update_dashboard_status:
                self.on_update_dashboard_status()

    async def seleccionar_roms_click(self, e):
        path = await self.abrir_selector_directorio(self.translator.t("set_dlg_roms"))
        if path:
            self.roms_path_field.value = path
            self.emu_manager.save_config(roms_path=path)
            self.roms_path_field.update()

    async def abrir_selector_directorio(self, titulo):
        try:
            system = platform.system()
            if system == "Linux":
                try:
                    proc = await asyncio.create_subprocess_exec(
                        "zenity", "--file-selection", "--directory", f"--title={titulo}",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, _ = await proc.communicate()
                    if stdout:
                        return stdout.decode().strip()
                except FileNotFoundError:
                    # Zenity no está instalado, informar al usuario
                    print("[DEBUG] Zenity no encontrado. Por favor instala 'zenity' o ingresa la ruta manualmente.")
                    # Aquí podrías mostrar un Banner en Flet si quisieras, 
                    # pero por ahora evitamos el crash.
                    return None
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
