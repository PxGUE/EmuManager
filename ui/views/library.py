import flet as ft
import os
import asyncio
import core.scanner as scanner
import core.artwork as artwork
from ui.components import create_console_card, create_game_card

class LibraryView(ft.Container):
    def __init__(self, emu_manager, emu_platform_map, page, translator):
        super().__init__()
        self.emu_manager = emu_manager
        self.emu_platform_map = emu_platform_map
        self._page_ref = page
        self.translator = translator
        self.info_dialog = None # Para rastrear el diálogo abierto
        self.search_field = ft.TextField(
            hint_text=self.translator.t("lib_search"),
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            height=40,
            width=300,
            bgcolor="#15171e",
            border_radius=10,
            border_color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_400),
            cursor_color=ft.Colors.BLUE_400,
            text_size=14,
            content_padding=ft.padding.only(left=10, right=10),
        )
        self.current_emu_data = None
        self.current_games_all = []
        self.game_grid = ft.GridView(
            controls=[],
            expand=True,
            runs_count=5,
            max_extent=160,
            child_aspect_ratio=0.65,
            spacing=30,
            run_spacing=30,
            padding=ft.padding.all(40),
        )
        self.game_grid_container = ft.Container(
            content=self.game_grid,
            expand=True
        )
        # Hero references for search updates
        self.hero_update_fn = None
        
        # Capa de fondo con transición suave (cross-fade)
        self.bg_container = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#0c0d12", "#1a1c26"]
            )
        )
        self.bg_layer = ft.AnimatedSwitcher(
            content=self.bg_container,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=1500,
            reverse_duration=1000,
            expand=True
        )

        # Overlays
        self.artwork_progress_bar = ft.ProgressBar(value=0, expand=True, color=ft.Colors.BLUE_400, bgcolor="#1a1c26")
        self.artwork_progress_label = ft.Text("", size=12, color=ft.Colors.GREY_300)
        self.artwork_overlay = ft.Container(
            content=ft.Column([
                self.artwork_progress_label,
                self.artwork_progress_bar,
            ], spacing=4),
            padding=ft.Padding(15, 8, 15, 10),
            bgcolor="#0d0e14",
            visible=False,
            bottom=0,
            left=0,
            right=0,
        )

        self.scan_overlay = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=3),
                ft.Text(self.translator.t("lib_search_games"), size=14, color=ft.Colors.GREY_300)
            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#0c0d12cc",  
            expand=True,
            visible=False,
            alignment=ft.Alignment(0, 0),
        )

        self.consola_grid = ft.ResponsiveRow(controls=[], spacing=25, run_spacing=25)
        self.consola_column = ft.Column([
            ft.Row([
                ft.Text(self.translator.t("nav_library"), size=32, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Container(
                content=self.consola_grid,
                padding=ft.padding.all(40), # Espacio generoso en todas las direcciones
            )
        ], scroll=ft.ScrollMode.HIDDEN, expand=True)

        self.biblioteca_main_area = ft.AnimatedSwitcher(
            content=self.consola_column,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=200,
            reverse_duration=200,
            switch_in_curve="ease",
            switch_out_curve="ease",
        )

        self.stack = ft.Stack([
            self.bg_layer,
            ft.Container(
                content=self.biblioteca_main_area,
                padding=30,
                expand=True,
                alignment=ft.Alignment.TOP_LEFT
            ),
            self.scan_overlay,
            self.artwork_overlay,
        ], expand=True)

        self.content = self.stack
        self.expand = True
        self.padding = 0
        self.margin = 0

    def did_mount(self):
        self.mostrar_consolas()
        
    def crear_tarjeta_consola(self, emu, count):
        return create_console_card(emu, count, self.translator, self.abrir_detalle_consola)

    def abrir_detalle_consola(self, emu):
        biblioteca = scanner.cargar_biblioteca_cache()
        juegos_consola = [j for j in biblioteca if j.get("id_emu") == emu["id"]]
        # Ordenamos alfanuméricamente por nombre
        juegos_consola.sort(key=lambda x: x.get("nombre", "").lower())
        self.mostrar_vista_detalle(emu, juegos_consola)

    def mostrar_consolas(self):
        biblioteca = scanner.cargar_biblioteca_cache()
        counts = {}
        for j in biblioteca:
            id_emu = j.get("id_emu")
            counts[id_emu] = counts.get(id_emu, 0) + 1
        
        from core.constants import AVAILABLE_EMULATORS
        # Ordenamos las consolas por nombre
        sorted_emus = sorted(AVAILABLE_EMULATORS, key=lambda x: x["console"].lower())
        
        consolas_activas = [
            self.crear_tarjeta_consola(emu, counts.get(emu["id"], 0))
            for emu in sorted_emus
            if self.emu_manager.esta_instalado(emu["github"])
        ]

        self.consola_grid.controls = consolas_activas
        
        if self.biblioteca_main_area.content is not self.consola_column:
            self.biblioteca_main_area.content = self.consola_column
            try: self.biblioteca_main_area.update()
            except: pass
        else:
            try: self.consola_grid.update()
            except: pass
        
        self.bg_container.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#0c0d12", "#1a1c26"]
        )
        try: self.bg_layer.update()
        except: pass

    def mostrar_vista_detalle(self, emu, juegos):
        self.current_emu_data = emu
        self.current_games_all = juegos
        self.search_field.value = "" # Reset search on entry

        hero_title = ft.Text(emu["console"], size=50, weight=ft.FontWeight.BOLD)
        hero_subtitle = ft.Text(emu["name"], size=20, color=ft.Colors.BLUE_200, weight=ft.FontWeight.W_500)
        hero_desc = ft.Text(emu.get("description", self.translator.t("lib_no_desc")), size=16, color=ft.Colors.GREY_300, width=600)

        
        console_colors = {
            "mgba": ["#0a0202", "#2a0a0a"],
            "dolphin": ["#051a2e", "#004080"],
            "pcsx2": ["#111111", "#222222"],
            "duckstation": ["#1a1005", "#503000"],
            "snes9x": ["#12051a", "#300050"],
            "genesis": ["#051a05", "#004000"],
        }
        base_colors = console_colors.get(emu["id"], ["#1a1c26", "#2d3240"])

        def update_hero(juego=None):
            if juego:
                hero_title.value = juego["nombre"]
                hero_desc.value = self.translator.t("lib_game_desc", juego['consola'], juego['extension'])
                # Creamos un nuevo contenedor para activar el AnimatedSwitcher
                self.bg_container = ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[base_colors[1], "#08090a"]
                    )
                )
                self.bg_layer.content = self.bg_container
            else:
                hero_title.value = emu["console"]
                hero_subtitle.value = emu["name"]
                hero_desc.value = emu.get("description", "Sin descripción disponible.")
                
                self.bg_container = ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=base_colors
                    )
                )
                self.bg_layer.content = self.bg_container
            
            try:
                hero_title.update()
                hero_subtitle.update()
                hero_desc.update()
                self.bg_layer.update()
            except: pass
        
        self.hero_update_fn = update_hero
        self._actualizar_rejilla_juegos(juegos)

        self.biblioteca_main_area.content = ft.Column([
            ft.Container(
                content=ft.Stack([
                    ft.Column([
                        hero_title,
                        hero_subtitle,
                        hero_desc,
                    ], spacing=5, expand=True),
                    ft.Container(
                        content=self.search_field,
                        alignment=ft.Alignment.BOTTOM_RIGHT,
                        margin=ft.margin.only(bottom=10, right=40)
                    )
                ]),
                height=250,
                padding=ft.Padding(0, 10, 0, 0)
            ),
            
            self.game_grid_container,
            
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=24, color=ft.Colors.BLUE_400),
                            ft.Text(emu["console"], size=18, weight=ft.FontWeight.BOLD),
                        ], spacing=8),
                        ft.Text(emu["name"], size=12, color=ft.Colors.GREY_400),
                    ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        ft.ElevatedButton(
                            self.translator.t("lib_refresh").upper(), 
                            icon=ft.Icons.SEARCH, 
                            on_click=lambda e: self._page_ref.run_task(self.refrescar_biblioteca, e, emu),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor={"": ft.Colors.BLUE_800, "hovered": ft.Colors.BLUE_700},
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.all(18),
                            )
                        ),
                        ft.TextButton(
                            self.translator.t("lib_btn_back").upper(), 
                            icon=ft.Icons.ARROW_BACK, 
                            on_click=lambda _: self.mostrar_consolas(),
                            style=ft.ButtonStyle(
                                color=ft.Colors.GREY_300,
                            )
                        ),
                    ], spacing=15),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                height=70,
                padding=ft.Padding(0, 10, 0, 10),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_800))
            )
        ], spacing=10, expand=True)
        
        try: self.biblioteca_main_area.update()
        except: pass
        update_hero()

    def _on_search_change(self, e):
        query = self.search_field.value.lower().strip()
        filtered = [
            j for j in self.current_games_all 
            if query in j["nombre"].lower()
        ]
        self._actualizar_rejilla_juegos(filtered)

    def _handle_card_hover(self, e, overlay, game_data):
        """Manejador de hover con actualización directa de componentes."""
        is_h = e.data == "true"
        card = e.control
        
        card.scale = 1.1 if is_h else 1.0
        card.border = ft.border.all(2, ft.Colors.BLUE_400 if is_h else ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
        overlay.opacity = 1.0 if is_h else 0.0
        
        try:
            card.update()
            overlay.update()
            if self.hero_update_fn:
                self.hero_update_fn(game_data if is_h else None)
        except:
            pass

    def _actualizar_rejilla_juegos(self, juegos):
        """Reconstruye la rejilla de juegos DESDE CERO con arquitectura simplificada."""
        game_boxes = []
        
        if not juegos:
            self.game_grid_container.content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH_OFF, size=50, color=ft.Colors.GREY_700),
                    ft.Text(self.translator.t("lib_no_games"), size=16, color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
            try: self.game_grid_container.update()
            except: pass
            return

        self.game_grid_container.content = self.game_grid

        for j in juegos:
            card = create_game_card(
                game=j,
                on_launch=lambda g: self._page_ref.run_task(self.lanzar_con_info, g),
                hero_update_fn=self.hero_update_fn
            )
            game_boxes.append(card)
        
        self.game_grid.controls = game_boxes
        try:
            self.game_grid.update()
        except: pass

    async def lanzar_con_info(self, juego):
        # Función interna para realizar el lanzamiento real
        async def ejecutar_lanzamiento(j):
            from core.constants import AVAILABLE_EMULATORS
            repo = next((emu["github"] for emu in AVAILABLE_EMULATORS if emu["id"] == j["id_emu"]), None)
            success, msg = await self.emu_manager.lanzar_juego(repo, j["ruta"], juego_obj=j)
            sb = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN if success else ft.Colors.RED)
            self._page_ref.snack_bar = sb
            sb.open = True
            self._page_ref.update()

        # Verificar si ya hay un emulador abierto
        if self.emu_manager.is_emulator_running():
            async def confirmar_y_lanzar(e):
                confirm_dlg.open = False
                self._page_ref.update()
                self.emu_manager.terminar_proceso_actual()
                await asyncio.sleep(0.5) # Pausa para que el SO cierre el proceso
                await ejecutar_lanzamiento(juego)

            # Obtener nombre del juego actual para el mensaje
            actual = self.emu_manager.launcher.current_game
            nombre_actual = actual["nombre"] if actual else "Un juego"
            consola_actual = actual["consola"] if actual else "el emulador"

            confirm_dlg = ft.AlertDialog(
                title=ft.Row([ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_400), ft.Text(self.translator.t("lib_change_game_title"))], spacing=10),
                content=ft.Text(self.translator.t("lib_change_game_msg", nombre_actual, consola_actual, juego['nombre'])),
                actions=[
                    ft.TextButton(self.translator.t("lib_keep_current"), on_click=lambda _: self._close_dialog(confirm_dlg)),
                    ft.ElevatedButton(self.translator.t("lib_yes_change"), bgcolor=ft.Colors.RED_800, color=ft.Colors.WHITE, on_click=confirmar_y_lanzar),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self._page_ref.show_dialog(confirm_dlg)
            return

        await ejecutar_lanzamiento(juego)

    def _close_dialog(self, dlg):
        dlg.open = False
        self._page_ref.update()

    async def refrescar_biblioteca(self, e, current_emu=None):
        if not self.emu_manager.roms_path:
            sb = ft.SnackBar(ft.Text(self.translator.t("lib_missing_roms")))
            self._page_ref.snack_bar = sb
            sb.open = True
            self._page_ref.update()
            return

        if self.scan_overlay.page:
            self.scan_overlay.visible = True
            self.scan_overlay.update()
        
        # Escaneo inteligente: si estamos en una consola, solo escaneamos esa carpeta
        id_filtro = current_emu["id"] if current_emu else None
        juegos = await scanner.escanear_roms(self.emu_manager.roms_path, emu_id=id_filtro)
        if self.scan_overlay.page:
            self.scan_overlay.visible = False
            try: self.scan_overlay.update()
            except: pass
        
        def refrescar_vista():
            if current_emu:
                self.abrir_detalle_consola(current_emu)
            else:
                self.mostrar_consolas()

        if not juegos:
            refrescar_vista()
            return
        
        self.artwork_progress_bar.value = 0
        if self.scan_overlay.page:
            self.artwork_overlay.visible = True
            try: self.artwork_overlay.update()
            except: pass
        
        refrescar_vista()
        
        def on_artwork_progress(actual, total, nombre_juego):
            self.artwork_progress_bar.value = actual / total
            nombre_corto = nombre_juego[:50] + "..." if len(nombre_juego) > 50 else nombre_juego
            self.artwork_progress_label.value = f"[{actual}/{total}] {nombre_corto}"
            if self.artwork_overlay.page:
                self.artwork_overlay.update()
        
        juegos_como_dict = [j if isinstance(j, dict) else j.__dict__ for j in juegos]
        
        # Si es un escaneo específico, solo buscamos carátulas para esa consola
        juegos_a_procesar = [j for j in juegos_como_dict if j.get("id_emu") == id_filtro] if id_filtro else juegos_como_dict
        
        self.artwork_progress_bar.value = 0
        self.artwork_progress_label.value = f"Buscando carátulas para {len(juegos_a_procesar)} juegos..."
        
        stats = await artwork.descargar_caratulas_biblioteca(
            juegos_a_procesar,
            self.emu_platform_map,
            ruta_roms_base=self.emu_manager.roms_path,
            on_progress=on_artwork_progress
        )
        
        if self.artwork_overlay.page:
            self.artwork_overlay.visible = False
            self.artwork_overlay.update()
        
        print(f"[ARTWORK] Completado: {stats['ok']} nuevas, {stats['skip']} existentes, {stats['fail']} no encontradas")
        refrescar_vista()
