import flet as ft
import core.artwork as artwork

def create_game_card(game, on_launch, hero_update_fn=None):
    W, H = 140, 200
    
    # 1. Ícono de Play
    play_icon = ft.Icon(ft.Icons.PLAY_CIRCLE_FILL, color=ft.Colors.WHITE, size=50)
    
    # 2. Capa de sombra/play (se usará absoluta dentro del Stack)
    shadow = ft.Container(
        content=play_icon,
        alignment=ft.Alignment.CENTER,
        bgcolor="black54",
        opacity=0.0,
        animate_opacity=150,
        border_radius=10,
        width=W,
        height=H,
    )

    # 3. Imagen o fondo
    if artwork.tiene_caratula(game["ruta"]):
        bg_image = ft.Image(
            src=artwork.obtener_ruta_caratula(game["ruta"]),
            fit="cover", width=W, height=H, border_radius=10
        )
    else:
        bg_image = ft.Container(
            content=ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=40, color="blue200"),
            bgcolor="#252830", width=W, height=H, border_radius=10, alignment=ft.Alignment.CENTER
        )

    # 4. Texto inferior
    text_footer = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=["transparent", "black87"]
        ),
        padding=10, alignment=ft.Alignment.BOTTOM_CENTER, border_radius=10, width=W, height=H,
        content=ft.Text(game["nombre"], size=10, weight="bold", color="white", text_align="center", max_lines=2)
    )

    # 5. CONTENEDOR VISUAL (Manejamos HOVER aquí porque es más estable)
    card_content = ft.Container(
        content=ft.Stack([bg_image, text_footer, shadow]),
        width=W, height=H,
        border_radius=12,
        bgcolor="#1a1c23",
        scale=1.0, 
        border=ft.Border.all(2, ft.Colors.TRANSPARENT),
        animate_scale=ft.Animation(100, ft.AnimationCurve.DECELERATE),
        animate=100,
    )

    def set_hover_style(hovered):
        card_content.scale = 1.05 if hovered else 1.0
        card_content.border = ft.Border.all(2, ft.Colors.BLUE_400) if hovered else ft.Border.all(2, ft.Colors.TRANSPARENT)
        shadow.opacity = 1.0 if hovered else 0.0
        card_content.update()

    def handle_hover(e):
        set_hover_style(str(e.data).lower() == "true")

    card_content.on_hover = handle_hover

    def handle_down(e):
        card_content.scale = 0.92
        card_content.update()

    def handle_up(e):
        card_content.scale = 1.05
        card_content.update()
        on_launch(game)

    # 6. GESTURE DETECTOR (Solo para el click intuitivo)
    return ft.GestureDetector(
        content=card_content,
        on_tap_down=handle_down,
        on_tap_up=handle_up,
        on_tap_cancel=lambda _: set_hover_style(False),
        mouse_cursor=ft.MouseCursor.CLICK
    )
