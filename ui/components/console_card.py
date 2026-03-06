import flet as ft
import os
import core.artwork as artwork

def create_console_card(emu, count, translator, on_click):
    logo_fisico = artwork.obtener_ruta_logo_consola(emu["id"])
    has_logo = os.path.exists(logo_fisico)
    logo_assets = f"consolas/{emu['id']}.png"
    
    return ft.Container(
        content=ft.Stack([
            # Imagen de fondo (Logo de consola o icono)
            ft.Container(
                content=ft.Image(
                    src=logo_assets,
                    fit=ft.BoxFit.CONTAIN,
                    opacity=0.4 if has_logo else 0.1,
                    width=120,
                    height=120,
                ) if has_logo else ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=60, color=ft.Colors.BLUE_GREY_800),
                alignment=ft.Alignment.CENTER,
            ),
            # Gradiente para legibilidad
            ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_CENTER,
                    end=ft.Alignment.BOTTOM_CENTER,
                    colors=[ft.Colors.TRANSPARENT, ft.Colors.BLACK87],
                ),
                border_radius=20,
            ),
            # Texto
            ft.Container(
                content=ft.Column([
                    ft.Text(emu["console"], size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(emu["name"], size=11, color=ft.Colors.BLUE_200, text_align=ft.TextAlign.CENTER),
                    ft.Text(translator.t("lib_games_count", count), size=10, color=ft.Colors.GREY_500),
                ], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=15,
            )
        ]),
        width=180,
        height=180,
        bgcolor="#1a1c22",
        border_radius=20,
        on_click=lambda _: on_click(emu),
        ink=True,
        border=ft.Border(
            top=ft.BorderSide(1, ft.Colors.WHITE10),
            right=ft.BorderSide(1, ft.Colors.WHITE10),
            bottom=ft.BorderSide(1, ft.Colors.WHITE10),
            left=ft.BorderSide(1, ft.Colors.WHITE10),
        ),
    )
