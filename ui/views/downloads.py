import flet as ft
import asyncio
import os
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork

class DownloadsView(ft.Container):
    def __init__(self, emu_manager, translator, on_update_library_bg=None):
        super().__init__()
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_library_bg = on_update_library_bg
        
        self.descargar_lista_column = ft.Column([
            ft.Text(self.translator.t("dl_title"), size=28, weight=ft.FontWeight.BOLD),
            ft.Text(self.translator.t("dl_subtitle"), size=14, color=ft.Colors.GREY_400),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        self.content = self.descargar_lista_column
        self.padding = 30
        self.expand = True
        self.alignment = ft.Alignment.TOP_LEFT

    def did_mount(self):
        self.page.run_task(self.cargar_emuladores_validos)

    async def cargar_emuladores_validos(self):
        try:
            # Verificar rutas y existencia física
            path_emus = self.emu_manager.install_path
            path_roms = self.emu_manager.roms_path
            
            emus_ok = bool(path_emus and os.path.exists(path_emus))
            roms_ok = bool(path_roms and os.path.exists(path_roms))
            paths_configured = emus_ok and roms_ok

            valid_emus = AVAILABLE_EMULATORS
            cards = [self.crear_tarjeta_emulador(emu, disabled=not paths_configured) for emu in valid_emus]
            
            self.descargar_lista_column.controls.clear()
            self.descargar_lista_column.controls.append(
                ft.Text(self.translator.t("dl_title"), size=28, weight=ft.FontWeight.BOLD)
            )
            if not paths_configured:
                self.descargar_lista_column.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.BLACK),
                            ft.Text(self.translator.t("dl_warn_paths"), 
                                    color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)
                        ]),
                        bgcolor=ft.Colors.AMBER_400,
                        padding=15,
                        border_radius=10,
                        margin=ft.margin.only(bottom=20, right=40)
                    )
                )

            self.descargar_lista_column.controls.append(
                ft.Text(self.translator.t("dl_list_sub"), size=14, color=ft.Colors.GREY_400)
            )
            self.descargar_lista_column.controls.append(
                ft.Container(
                    content=ft.GridView(
                        cards,
                        max_extent=400,
                        spacing=20,
                        run_spacing=20,
                        expand=False,
                    ),
                    margin=ft.margin.only(right=40) # Espacio para el scroll
                )
            )
        except Exception as e:
            print(f"Error cargando emuladores: {e}")
            self.descargar_lista_column.controls.clear()
            self.descargar_lista_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED, size=40),
                        ft.Text(self.translator.t("dl_err_load"), size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(self.translator.t("dl_err_sub", str(e)), size=12, color=ft.Colors.GREY_400),
                        ft.FilledButton(self.translator.t("dl_btn_retry"), icon=ft.Icons.REFRESH, 
                                        on_click=lambda _: self.page.run_task(self.cargar_emuladores_validos))
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    alignment=ft.Alignment.CENTER
                )
            )
            
        try: self.descargar_lista_column.update()
        except: pass

    def crear_tarjeta_emulador(self, emu, disabled=False):
        is_installed = self.emu_manager.esta_instalado(emu["github"])
        progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)
        progress_bar = ft.ProgressBar(width=150, height=8, color=ft.Colors.BLUE, bgcolor=ft.Colors.BLUE_GREY_900, value=0, visible=False, border_radius=5)
        status_text = ft.Text("", size=11, color=ft.Colors.GREY_400, italic=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        
        btn_icon = ft.Icon(ft.Icons.DOWNLOAD)
        btn_label = ft.Text(self.translator.t("dl_btn_install"))
        
        install_btn = ft.FilledButton(
            content=ft.Row(
                [btn_icon, btn_label],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5
            ),
            width=150,
            disabled=disabled
        )

        def update_button_ui(installed, immediate=True):
            txt = self.translator.t("dl_btn_uninstall") if installed else self.translator.t("dl_btn_install")
            icon = ft.Icons.DELETE if installed else ft.Icons.DOWNLOAD
            color = ft.Colors.RED_700 if installed else None
            
            btn_icon.name = icon
            btn_label.value = txt
            install_btn.bgcolor = color
            
            if immediate:
                try: install_btn.update()
                except: pass

        update_button_ui(is_installed, immediate=False)

        async def clear_status_after_delay(seconds=8):
            await asyncio.sleep(seconds)
            try:
                status_text.value = ""
                try: status_text.update()
                except: pass
            except:
                pass
        
        async def on_action_click(e):
            # Verificar que las rutas existan para poder escribir en ellas
            path_emus = self.emu_manager.install_path
            path_roms = self.emu_manager.roms_path
            
            if not path_emus or not path_roms or not os.path.exists(path_emus) or not os.path.exists(path_roms):
                missing = []
                if not path_emus: missing.append("Configurar Carpeta Emuladores")
                elif not os.path.exists(path_emus): missing.append("Ruta de Emuladores No Encontrada")
                
                if not path_roms: missing.append("Configurar Carpeta ROMs")
                elif not os.path.exists(path_roms): missing.append("Ruta de ROMs No Encontrada")

                sb = ft.SnackBar(
                    ft.Text(self.translator.t("dl_blocked", ', '.join(missing))),
                    bgcolor=ft.Colors.RED_800
                )
                try:
                    self.page.snack_bar = sb
                    sb.open = True
                    self.page.update()
                except: pass
                return

            if btn_label.value == "Cancelar":
                # Reiniciar estado si el usuario cancela tras un error
                actualmente_instalado = self.emu_manager.esta_instalado(emu["github"])
                update_button_ui(actualmente_instalado)
                status_text.value = ""
                status_text.color = ft.Colors.GREY_400
                progress_bar.visible = False
                progress_bar.value = 0
                progress_bar.color = ft.Colors.BLUE
                self.update()
                return

            install_btn.disabled = True
            progress_ring.visible = True
            progress_bar.color = ft.Colors.BLUE # Reset color
            status_text.color = ft.Colors.GREY_400
            try:
                install_btn.update()
                progress_ring.update()
            except: pass
            
            repo = emu["github"]
            if not self.emu_manager.esta_instalado(repo):
                btn_label.value = self.translator.t("dl_installing")
                try: install_btn.update()
                except: pass
                
                error_ocurred = False
                async for output_line in self.emu_manager.instalar_emulador(repo):
                    if output_line.startswith("PROGRESS:"):
                        try:
                            # Formato: PROGRESS:0.5|Mensaje
                            parts = output_line.replace("PROGRESS:", "").split("|")
                            val = float(parts[0])
                            msg = parts[1] if len(parts) > 1 else "Procesando..."
                            
                            progress_bar.visible = True
                            progress_bar.value = val
                            status_text.value = msg
                            
                            if val >= 1.0:
                                # Forzar visualización del 100%
                                progress_bar.value = 1.0
                                if progress_bar.page: progress_bar.update()
                                await asyncio.sleep(0.5)
                                progress_bar.visible = False
                        except:
                            status_text.value = output_line
                    elif output_line.startswith("ERROR:") or "Error" in output_line:
                        error_ocurred = True
                        msg = output_line.replace("ERROR:", "")
                        status_text.value = msg
                        status_text.color = ft.Colors.RED_400
                        progress_bar.color = ft.Colors.RED_400
                        btn_label.value = "Cancelar"
                        btn_icon.name = ft.Icons.CLOSE
                        install_btn.bgcolor = ft.Colors.RED_900
                    else:
                        status_text.value = output_line
                    
                    try:
                        status_text.update()
                        if progress_bar.visible: progress_bar.update()
                        install_btn.update()
                    except: pass
                
                if not error_ocurred:
                    installed_now = self.emu_manager.esta_instalado(repo)
                    update_button_ui(installed_now)
                    if installed_now:
                        status_text.value = self.translator.t("dl_installed_ok")
                        status_text.color = ft.Colors.GREEN_400
                        progress_bar.visible = False
                        if progress_bar.visible:
                            try:
                                status_text.update()
                                progress_bar.update()
                            except: pass
                        
                        # Desaparece después de 3 segundos
                        await asyncio.sleep(3)
                        status_text.value = ""
                        try: status_text.update()
                        except: pass
                    
                    if self.on_update_library_bg:
                        self.on_update_library_bg()
                else:
                    # Si hubo error, dejamos que el usuario interactue con "Cancelar"
                    install_btn.disabled = False
                    install_btn.update()
                    progress_ring.visible = False
                    progress_ring.update()
                    return # No seguir al bloque final común

            else:
                btn_label.value = self.translator.t("dl_uninstalling")
                install_btn.update()
                
                async for output_line in self.emu_manager.desinstalar_emulador(repo):
                    status_text.value = output_line[-50:]
                    try: status_text.update()
                    except: pass
                
                installed_now = self.emu_manager.esta_instalado(repo)
                update_button_ui(installed_now)
                status_text.value = self.translator.t("dl_uninstalled_ok") if not installed_now else self.translator.t("dl_err_sub", "Desinstalar")
                
                if self.on_update_library_bg:
                    self.on_update_library_bg()
                
            progress_ring.visible = False
            install_btn.disabled = False
            try:
                install_btn.update()
                progress_ring.update()
                status_text.update()
            except: pass
            
            self.page.run_task(clear_status_after_delay)

        install_btn.on_click = on_action_click

        logo_fisico = artwork.obtener_ruta_logo_emulador(emu["id"])
        has_logo = os.path.exists(logo_fisico)
        logo_assets = artwork.obtener_ruta_logo_emulador(emu["id"], flet_path=True)

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Image(src=logo_assets, width=40, height=40, fit=ft.BoxFit.CONTAIN) if has_logo else ft.Icon(ft.Icons.VIDEOGAME_ASSET),
                            title=ft.Text(emu["name"], weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(self.translator.t("dl_console_lbl", emu['console'])),
                        ),
                        ft.Container(
                            content=ft.Column([
                                status_text,
                                progress_bar,
                            ], spacing=2),
                            padding=ft.Padding(15, 0, 15, 5)
                        ),
                        ft.Row(
                            [
                                progress_ring,
                                install_btn,
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=10,
                height=180,
            )
        )
