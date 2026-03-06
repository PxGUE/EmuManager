import flet as ft
import os
import asyncio
import core.scanner as scanner
import core.artwork as artwork

class LibraryView(ft.Container):
    def __init__(self, emu_manager, emu_platform_map, page):
        super().__init__()
        self.emu_manager = emu_manager
        self.emu_platform_map = emu_platform_map
        self._page_ref = page
        self.info_dialog = None # Para rastrear el diálogo abierto
        self.search_field = ft.TextField(
            hint_text="Buscar juego...",
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
            child_aspect_ratio=0.62,
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
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
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
                ft.Text("Buscando juegos...", size=14, color=ft.Colors.GREY_300)
            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#0c0d12cc",  
            expand=True,
            visible=False,
            alignment=ft.Alignment(0, 0),
        )

        self.consola_grid = ft.ResponsiveRow(controls=[], spacing=25, run_spacing=25)
        self.consola_column = ft.Column([
            ft.Row([
                ft.Text("Biblioteca", size=32, weight=ft.FontWeight.BOLD),
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
                alignment=ft.alignment.top_left
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
        # Para la lógica de existencia usamos la ruta física
        logo_fisico = artwork.obtener_ruta_logo_consola(emu["id"])
        has_logo = os.path.exists(logo_fisico)
        
        # Para mostrar en Flet usamos la ruta de assets
        logo_assets = artwork.obtener_ruta_logo_consola(emu["id"], flet_path=True)
        
        return ft.Container(
            content=ft.Stack([
                # Imagen de fondo (Logo de consola o icono)
                ft.Container(
                    content=ft.Image(
                        src=logo_assets,
                        fit=ft.ImageFit.CONTAIN,
                        opacity=0.4 if has_logo else 0.1,
                        width=120,
                        height=120,
                    ) if has_logo else ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=60, color=ft.Colors.BLUE_GREY_800),
                    alignment=ft.alignment.center,
                ),
                # Gradiente para legibilidad
                ft.Container(
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=[ft.Colors.TRANSPARENT, ft.Colors.BLACK87],
                    ),
                    border_radius=20,
                ),
                # Texto
                ft.Container(
                    content=ft.Column([
                        ft.Text(emu["console"], size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(emu["name"], size=11, color=ft.Colors.BLUE_200, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{count} Juegos", size=10, color=ft.Colors.GREY_500),
                    ], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    padding=15,
                )
            ]),
            width=180,
            height=180,
            bgcolor="#1a1c22",
            border_radius=20,
            on_click=lambda _: self.abrir_detalle_consola(emu),
            ink=True,
            border=ft.border.all(1, ft.Colors.WHITE10),
        )

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
            if self.biblioteca_main_area.page:
                self.biblioteca_main_area.update()
        elif self.consola_grid.page:
            self.consola_grid.update()
        
        self.bg_layer.gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#0c0d12", "#1a1c26"]
        )
        if self.bg_layer.page:
            self.bg_layer.update()

    def mostrar_vista_detalle(self, emu, juegos):
        self.current_emu_data = emu
        self.current_games_all = juegos
        self.search_field.value = "" # Reset search on entry

        hero_title = ft.Text(emu["console"], size=50, weight=ft.FontWeight.BOLD)
        hero_subtitle = ft.Text(emu["name"], size=20, color=ft.Colors.BLUE_200, weight=ft.FontWeight.W_500)
        hero_desc = ft.Text(emu.get("description", "Sin descripción disponible."), size=16, color=ft.Colors.GREY_300, width=600)

        
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
                hero_desc.value = f"Juego de {juego['consola']} ({juego['extension']})."
                # Creamos un nuevo contenedor para activar el AnimatedSwitcher
                self.bg_container = ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
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
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=base_colors
                    )
                )
                self.bg_layer.content = self.bg_container
            
            if self._page_ref:
                try:
                    hero_title.update()
                    hero_subtitle.update()
                    hero_desc.update()
                    self.bg_layer.update()
                except: pass
        
        self.hero_update_fn = update_hero
        self._actualizar_rejilla_juegos(juegos)

        game_boxes = []
        for j in juegos:
            caratula_path = artwork.obtener_ruta_caratula(j["ruta"])
            has_art = artwork.tiene_caratula(j["ruta"])
            
            # Imagen de la tarjeta
            if has_art:
                art_img = ft.Image(
                    src=caratula_path,
                    width=135,
                    height=180,
                    fit=ft.ImageFit.COVER,
                    border_radius=10,
                )
            else:
                art_img = ft.Container(
                    content=ft.Icon(ft.Icons.VIDEOGAME_ASSET_OUTLINED, size=40, color=ft.Colors.BLUE_200),
                    width=135,
                    height=180,
                    bgcolor="#252830",
                    border_radius=10,
                    alignment=ft.Alignment(0, 0)
                )

            # Botón de Play flotante
            play_btn = ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW_ROUNDED,
                    icon_color=ft.Colors.WHITE,
                    icon_size=40,
                    bgcolor=ft.Colors.BLUE_ACCENT_700,
                    on_click=lambda _, game=j: self._page_ref.run_task(self.lanzar_con_info, game),
                    style=ft.ButtonStyle(
                        shape=ft.CircleBorder(),
                    )
                ),
                opacity=0,
                animate_opacity=200,
                alignment=ft.alignment.center,
            )

            # Imagen con botón encima
            image_stack = ft.Stack([
                art_img,
                play_btn
            ], width=135, height=180)

            # Contenedor de la tarjeta de juego
            card_content = ft.Container(
                content=ft.Column([
                    image_stack,
                    ft.Container(
                        content=ft.Text(
                            j["nombre"], 
                            size=12, 
                            weight=ft.FontWeight.BOLD, 
                            max_lines=1, 
                            overflow=ft.TextOverflow.ELLIPSIS, 
                            text_align=ft.TextAlign.CENTER
                        ),
                        padding=ft.padding.only(left=5, right=5, bottom=5),
                        width=135
                    ),
                ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=8,
                border_radius=15,
                bgcolor="#1e2129",
                border=ft.border.all(1, ft.Colors.WHITE10),
                animate=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            )

            def handle_hover(e, container=card_content, game=j, btn=play_btn):
                is_hover = e.data == "true"
                container.scale = 1.05 if is_hover else 1.0
                container.border = ft.border.all(1, ft.Colors.BLUE_400) if is_hover else ft.border.all(1, ft.Colors.WHITE10)
                container.shadow = ft.BoxShadow(blur_radius=15, color="#000000") if is_hover else None
                btn.opacity = 1 if is_hover else 0
                btn.update()
                container.update()
                update_hero(game if is_hover else None)

            card_content.on_hover = handle_hover
            card_content.on_click = lambda _, game=j: self.mostrar_info_juego(game)
            card_content.mouse_cursor = ft.MouseCursor.CLICK

            game_boxes.append(
                ft.Card(
                    content=card_content,
                    elevation=10,
                    margin=0,
                    shape=ft.RoundedRectangleBorder(radius=15),
                )
            )

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
                        alignment=ft.alignment.bottom_right,
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
                            "ESCANEAR", 
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
                            "VOLVER", 
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
        
        self.biblioteca_main_area.update()
        update_hero()

    def _on_search_change(self, e):
        query = self.search_field.value.lower().strip()
        filtered = [
            j for j in self.current_games_all 
            if query in j["nombre"].lower()
        ]
        self._actualizar_rejilla_juegos(filtered)

    def _actualizar_rejilla_juegos(self, juegos):
        """Reconstruye los controles de la rejilla basándose en la lista proporcionada."""
        game_boxes = []
        
        if not juegos:
            self.game_grid_container.content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH_OFF, size=50, color=ft.Colors.GREY_700),
                    ft.Text("No se encontraron juegos", size=16, color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
            )
            if self.game_grid_container.page:
                self.game_grid_container.update()
            return

        self.game_grid_container.content = self.game_grid

        for j in juegos:
            caratula_path = artwork.obtener_ruta_caratula(j["ruta"])
            has_art = artwork.tiene_caratula(j["ruta"])
            
            # Imagen de la tarjeta
            if has_art:
                art_img = ft.Image(
                    src=caratula_path,
                    width=135,
                    height=180,
                    fit=ft.ImageFit.COVER,
                    border_radius=10,
                )
            else:
                art_img = ft.Container(
                    content=ft.Icon(ft.Icons.VIDEOGAME_ASSET_OUTLINED, size=40, color=ft.Colors.BLUE_200),
                    width=135,
                    height=180,
                    bgcolor="#252830",
                    border_radius=10,
                    alignment=ft.Alignment(0, 0)
                )

            # Botón de Play flotante
            play_btn = ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW_ROUNDED,
                    icon_color=ft.Colors.WHITE,
                    icon_size=40,
                    bgcolor=ft.Colors.BLUE_ACCENT_700,
                    on_click=lambda _, game=j: self._page_ref.run_task(self.lanzar_con_info, game),
                    style=ft.ButtonStyle(
                        shape=ft.CircleBorder(),
                    )
                ),
                opacity=0,
                animate_opacity=200,
                alignment=ft.alignment.center,
            )

            # Imagen con botón encima
            image_stack = ft.Stack([
                art_img,
                play_btn
            ], width=135, height=180)

            # Contenedor de la tarjeta de juego
            card_content = ft.Container(
                content=ft.Column([
                    image_stack,
                    ft.Container(
                        content=ft.Text(
                            j["nombre"], 
                            size=12, 
                            weight=ft.FontWeight.BOLD, 
                            max_lines=1, 
                            overflow=ft.TextOverflow.ELLIPSIS, 
                            text_align=ft.TextAlign.CENTER
                        ),
                        padding=ft.padding.only(left=5, right=5, bottom=5),
                        width=135
                    ),
                ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=8,
                border_radius=15,
                bgcolor="#1e2129",
                border=ft.border.all(1, ft.Colors.WHITE10),
                animate=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            )

            def handle_hover(e, container=card_content, game=j, btn=play_btn):
                is_hover = e.data == "true"
                container.scale = 1.05 if is_hover else 1.0
                container.border = ft.border.all(1, ft.Colors.BLUE_400) if is_hover else ft.border.all(1, ft.Colors.WHITE10)
                container.shadow = ft.BoxShadow(blur_radius=15, color="#000000") if is_hover else None
                btn.opacity = 1 if is_hover else 0
                try:
                    btn.update()
                    container.update()
                    if self.hero_update_fn:
                        self.hero_update_fn(game if is_hover else None)
                except: pass

            card_content.on_hover = handle_hover
            card_content.on_click = lambda _, game=j: self.mostrar_info_juego(game)
            card_content.mouse_cursor = ft.MouseCursor.CLICK

            game_boxes.append(
                ft.Card(
                    content=card_content,
                    elevation=10,
                    margin=0,
                    shape=ft.RoundedRectangleBorder(radius=15),
                )
            )
        
        self.game_grid.controls = game_boxes
        if self.game_grid_container.page:
            self.game_grid_container.update()

    def mostrar_info_juego(self, juego):
        def close_dlg(e):
            self._page_ref.close(self.info_dialog)
            self._page_ref.update()

        dlg = ft.AlertDialog(
            title=ft.Text(juego["nombre"]),
            content=ft.Column([
                ft.Text(f"Consola: {juego['consola']}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Extensión: {juego['extension']}"),
                ft.Text(f"Ruta: {juego['ruta']}", size=12, italic=True, color=ft.Colors.GREY_400),
            ], tight=True),
            actions=[
                ft.TextButton("Lanzar Juego", on_click=lambda _: self._page_ref.run_task(self.lanzar_con_info, juego)),
                ft.TextButton("Cerrar", on_click=close_dlg),
            ],
        )
        self.info_dialog = dlg
        self._page_ref.open(dlg)
        self._page_ref.update()

    async def lanzar_con_info(self, juego):
        if self.info_dialog:
            try: self._page_ref.close(self.info_dialog)
            except: pass
            self.info_dialog = None
        
        # Función interna para realizar el lanzamiento real
        async def ejecutar_lanzamiento(j):
            from core.constants import AVAILABLE_EMULATORS
            repo = next((emu["github"] for emu in AVAILABLE_EMULATORS if emu["id"] == j["id_emu"]), None)
            success, msg = await self.emu_manager.lanzar_juego(repo, j["ruta"], juego_obj=j)
            self._page_ref.open(ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN if success else ft.Colors.RED))
            self._page_ref.update()

        # Verificar si ya hay un emulador abierto
        if self.emu_manager.is_emulator_running():
            async def confirmar_y_lanzar(e):
                self._page_ref.close(confirm_dlg)
                self.emu_manager.terminar_proceso_actual()
                await asyncio.sleep(0.5) # Pausa para que el SO cierre el proceso
                await ejecutar_lanzamiento(juego)

            # Obtener nombre del juego actual para el mensaje
            actual = self.emu_manager.current_game
            nombre_actual = actual["nombre"] if actual else "Un juego"
            consola_actual = actual["consola"] if actual else "el emulador"

            confirm_dlg = ft.AlertDialog(
                title=ft.Row([ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_400), ft.Text("Cambiar de juego")], spacing=10),
                content=ft.Text(f"Actualmente estás jugando a '{nombre_actual}' en {consola_actual}.\n\n¿Quieres cerrarlo para empezar '{juego['nombre']}'?"),
                actions=[
                    ft.TextButton("Mantener actual", on_click=lambda _: self._page_ref.close(confirm_dlg)),
                    ft.ElevatedButton("Sí, cambiar juego", bgcolor=ft.Colors.RED_800, color=ft.Colors.WHITE, on_click=confirmar_y_lanzar),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self._page_ref.open(confirm_dlg)
            self._page_ref.update()
            return

        await ejecutar_lanzamiento(juego)

    async def refrescar_biblioteca(self, e, current_emu=None):
        if not self.emu_manager.roms_path:
            self._page_ref.open(ft.SnackBar(ft.Text("Configura la carpeta de ROMs en Ajustes.")))
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
            self.scan_overlay.update()
        
        def refrescar_vista():
            if current_emu:
                self.abrir_detalle_consola(current_emu)
            else:
                self.mostrar_consolas()

        if not juegos:
            refrescar_vista()
            return
        
        self.artwork_progress_bar.value = 0
        if self.artwork_overlay.page:
            self.artwork_overlay.visible = True
            self.artwork_overlay.update()
        
        refrescar_vista()
        
        def on_artwork_progress(actual, total, nombre_juego):
            self.artwork_progress_bar.value = actual / total
            nombre_corto = nombre_juego[:50] + "..." if len(nombre_juego) > 50 else nombre_juego
            self.artwork_progress_label.value = f"[{actual}/{total}] {nombre_corto}"
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
