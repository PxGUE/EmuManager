import os
import asyncio
import aiohttp
from typing import Optional, Any
from . import metadata
from . import config
from core.scrapers.manager import ScraperManager

# --- UTILIDADES DE RUTAS (Usadas por el UI y otros módulos) ---

def obtener_ruta_caratula(ruta_rom: str, emu_id: str = "unknown", type: str = "2d") -> str:
    """Retorna la ruta absoluta para la carátula (2d o 3d)."""
    game_base_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(config.SCRAPED_DIR, emu_id, type, f"{game_base_name}.png")

def obtener_ruta_background(ruta_rom: str, emu_id: str = "unknown") -> str:
    game_base_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(config.SCRAPED_DIR, emu_id, "backgrounds", f"{game_base_name}.jpg")

def obtener_ruta_logo(ruta_rom: str, emu_id: str = "unknown") -> str:
    game_base_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(config.SCRAPED_DIR, emu_id, "logos", f"{game_base_name}.png")

def tiene_caratula(ruta_rom: str, emu_id: str = "unknown") -> bool:
    return os.path.exists(obtener_ruta_caratula(ruta_rom, emu_id, "2d"))

def obtener_ruta_logo_consola(id_emu: str) -> str:
    """Localiza el logo SVG o PNG de una consola."""
    base_path = os.path.join(config.MEDIA_DIR, "consolas", id_emu)
    for ext in (".svg", ".png"):
        full_path = os.path.abspath(base_path + ext)
        if os.path.exists(full_path):
            return full_path
    return os.path.abspath(base_path + ".png")

def obtener_ruta_fondo_consola(id_o_emu: Any) -> str:
    """Obtiene la ruta del fondo decorativo local para una consola."""
    bg_id = id_o_emu if isinstance(id_o_emu, str) else id_o_emu.get("console_id", id_o_emu.get("id"))
    bg_dir = os.path.join(config.BASE_DIR, "fondos_consolas")
    return os.path.abspath(os.path.join(bg_dir, f"{bg_id}.jpg"))

# --- MOTOR DE DESCARGA ---

async def descargar_caratulas_biblioteca(juegos: list, emu_map: dict, **kwargs) -> dict:
    """
    Descarga masiva de arte (2D y 3D) usando el ScraperManager unificado.
    """
    stats = {"ok": 0, "skip": 0, "fail": 0}
    fails_list = []
    on_progress = kwargs.get("on_progress")
    total = len(juegos)
    
    # Obtener configuración de proveedores
    configs = metadata.get_providers_config()

    # 🍪 USAMOS DummyCookieJar: Evita el Error 431 al no acumular cookies del servidor
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        manager = ScraperManager(session, configs)
        
        async def _worker(idx, juego):
            ruta = juego.get("ruta", "")
            nombre = juego.get("nombre", "")
            emu_id = juego.get("id_emu", "")
            emu_info = emu_map.get(emu_id, {})
            
            # 1. Scrapear (Screenscraper -> Libretro fallback)
            res = await manager.scrape_game(
                nombre,
                system_id=emu_info.get("screenscraper_id"),
                platform=emu_info.get("libretro_platform", emu_info.get("console", "")),
                rom_file=os.path.basename(ruta)
            )
            
            if res:
                exito_2d = False
                exito_3d = False
                
                # Descargar 2D (Prioridad sugerida por el usuario)
                if res.boxart_2d:
                    dest_2d = obtener_ruta_caratula(ruta, emu_id, "2d")
                    exito_2d = await _descargar_archivo(session, res.boxart_2d, dest_2d)
                
                # Descargar 3D (Si existe, se baja junto con la 2D)
                if res.boxart_3d:
                    dest_3d = obtener_ruta_caratula(ruta, emu_id, "3d")
                    exito_3d = await _descargar_archivo(session, res.boxart_3d, dest_3d)
                
                # Otros Assets
                if res.background:
                    await _descargar_archivo(session, res.background, obtener_ruta_background(ruta, emu_id))
                if res.logo:
                    await _descargar_archivo(session, res.logo, obtener_ruta_logo(ruta, emu_id))

                if exito_2d or exito_3d:
                    stats["ok"] += 1
                    info = "2D+3D" if (exito_2d and exito_3d) else ("3D" if exito_3d else "2D")
                    print(f"[ARTWORK] Exito: {nombre} ({info}) via {res.source_name}")
                else:
                    stats["fail"] += 1
                    fails_list.append(nombre)
            else:
                stats["fail"] += 1
                fails_list.append(nombre)
            
            if on_progress:
                on_progress(idx + 1, total, nombre)

        await asyncio.gather(*[_worker(i, j) for i, j in enumerate(juegos)])

    # --- REPORTE ---
    print("\n" + "="*45)
    print("🎨 RESUMEN DE ARTE Y CARÁTULAS")
    print(f"     Descargados: {stats['ok']}")
    print(f"   L Fallidos:    {stats['fail']}")
    print("="*45 + "\n")

    return stats

async def _descargar_archivo(session: aiohttp.ClientSession, url: str, destino: str) -> bool:
    """Helper seguro para descargar binarios."""
    if not url: return False
    try:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        async with session.get(url, timeout=15) as resp:
            if resp.status == 200:
                with open(destino, "wb") as f:
                    f.write(await resp.read())
                return True
    except:
        pass
    return False
