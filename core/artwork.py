"""
artwork.py — Hub de Arte y Carátulas.

Este módulo gestiona la descarga y localización de recursos visuales:
1. Carátulas (Boxarts).
2. Fondos (Fanart/Backdrops).
3. Logos de juegos y consolas.
Coordina múltiples proveedores (Libretro, SteamGridDB, ScreenScraper).
"""

import asyncio
import aiohttp
import os
import urllib.parse
from typing import Optional, Callable, List, Dict, Any

from .normalization import normalize_title
from .scrapers.artwork.libretro import LibretroScraper
from .scrapers.artwork.steamgriddb import SteamGridDBScraper
from .scrapers.metadata.screenscraper import ScreenScraperScraper
from . import metadata
from . import config

class ArtworkHub:
    """
    Coordina la descarga de arte desde múltiples proveedores.
    """
    def __init__(self, session: aiohttp.ClientSession, configs: List[Dict]):
        """
        Inicializa los scrapers de arte según la configuración.

        Args:
            session (aiohttp.ClientSession): Sesión HTTP compartida.
            configs (List[Dict]): Configuración de proveedores (desde metadata.get_providers_config).
        """
        self.session = session
        
        # 1. Libretro (CDN Gratuito de carátulas)
        libretro_cfg = next((c for c in configs if c["id"] == "libretro"), {"enabled": True})
        self.libretro = LibretroScraper() if libretro_cfg.get("enabled") else None
        
        # 2. SteamGridDB (Excelente para fondos y logos)
        sgdb_cfg = next((c for c in configs if c["id"] == "steamgriddb"), None)
        sgdb_key = sgdb_cfg.get("api_key") if sgdb_cfg and sgdb_cfg.get("enabled") else None
        self.sgdb = SteamGridDBScraper(sgdb_key) if sgdb_key else None

        # 3. ScreenScraper (El más completo, requiere cuenta)
        ss_cfg = next((c for c in configs if c["id"] == "screenscraper"), None)
        ss_user = ss_cfg.get("user") if ss_cfg and ss_cfg.get("enabled") else None
        ss_pass = ss_cfg.get("password") if ss_cfg and ss_cfg.get("enabled") else None
        self.ss = ScreenScraperScraper(ss_user, ss_pass) if (ss_user and ss_pass) else None

    async def download_for_game(self, platform: str, game_name: str, rom_path: str, **kwargs) -> bool:
        """
        Busca y descarga todo el arte disponible para un juego.

        Args:
            platform (str): Nombre de la plataforma para Libretro/SS.
            game_name (str): Nombre limpio del juego.
            rom_path (str): Ruta absoluta del archivo ROM.
            **kwargs: Parámetros extra como ss_platform_id.

        Returns:
            bool: True si al menos la carátula principal fue descargada con éxito.
        """
        caratula_path = obtener_ruta_caratula(rom_path)
        
        # --- 1. Intento con Libretro (Rápido y fiable para Boxarts) ---
        if self.libretro:
            res = await self.libretro.fetch(self.session, game_name, platform=platform)
            if res and res.get("boxart_url"):
                ok = await _descargar_archivo(self.session, res["boxart_url"], caratula_path)
                if ok:
                    return True

        # --- 2. Intento con SteamGridDB (Fondos y Logos Premium) ---
        if self.sgdb:
            # Primero intentamos por nombre de archivo (más preciso), luego por nombre limpio
            clean_name = os.path.splitext(os.path.basename(rom_path))[0]
            res = await self.sgdb.fetch(self.session, clean_name)
            if not res:
                res = await self.sgdb.fetch(self.session, game_name)
            
            if res:
                # Descargar Carátula
                if res.get("boxart_url") and not os.path.exists(caratula_path):
                    await _descargar_archivo(self.session, res["boxart_url"], caratula_path)
                
                # Descargar Fondo (Hero)
                if res.get("background_url"):
                    bg_path = obtener_ruta_background(rom_path)
                    if not os.path.exists(bg_path):
                        await _descargar_archivo(self.session, res["background_url"], bg_path)
                
                # Descargar Logo
                if res.get("logo_url"):
                    logo_path = obtener_ruta_logo(rom_path)
                    if not os.path.exists(logo_path):
                        await _descargar_archivo(self.session, res["logo_url"], logo_path)
                
                return os.path.exists(caratula_path)

        # --- 3. Intento con ScreenScraper (El último recurso) ---
        if self.ss:
            ss_id = kwargs.get("ss_platform_id")
            res = await self.ss.fetch(self.session, game_name, ss_platform_id=ss_id)
            if res:
                if res.get("boxart_url") and not os.path.exists(caratula_path):
                    await _descargar_archivo(self.session, res["boxart_url"], caratula_path)
                
                if res.get("background_url"):
                    bg_path = obtener_ruta_background(rom_path)
                    if not os.path.exists(bg_path):
                        await _descargar_archivo(self.session, res["background_url"], bg_path)
                
                if res.get("logo_url"):
                    logo_path = obtener_ruta_logo(rom_path)
                    if not os.path.exists(logo_path):
                        await _descargar_archivo(self.session, res["logo_url"], logo_path)
                
                return os.path.exists(caratula_path)

        return os.path.exists(caratula_path)


# ── UTILIDADES DE RUTAS ──────────────────────────────────────────────

def obtener_ruta_caratula(ruta_rom: str) -> str:
    """Retorna la ruta donde debe guardarse/leerse la carátula de un juego."""
    rom_dir = os.path.dirname(ruta_rom)
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(rom_dir, "media", f"{game_name}.png")

def obtener_ruta_background(ruta_rom: str) -> str:
    """Retorna la ruta para el fondo (fanart) de un juego."""
    rom_dir = os.path.dirname(ruta_rom)
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(rom_dir, "media", f"{game_name}_bg.jpg")

def obtener_ruta_logo(ruta_rom: str) -> str:
    """Retorna la ruta para el logo (marquee) de un juego."""
    rom_dir = os.path.dirname(ruta_rom)
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(rom_dir, "media", f"{game_name}_logo.png")

def tiene_caratula(ruta_rom: str) -> bool:
    """Verifica si existe el archivo de carátula para un juego."""
    return os.path.exists(obtener_ruta_caratula(ruta_rom))

def obtener_ruta_logo_consola(id_emu: str) -> str:
    """
    Localiza el logo SVG o PNG de una consola en la carpeta de recursos del sistema.
    """
    base_path = os.path.join(config.MEDIA_DIR, "consolas", id_emu)
    for ext in (".svg", ".png"):
        full_path = os.path.abspath(base_path + ext)
        if os.path.exists(full_path):
            return full_path
    return os.path.abspath(base_path + ".png")

def obtener_ruta_fondo_consola(id_o_emu: Any) -> str:
    """
    Obtiene la ruta del fondo decorativo local para una consola.
    """
    bg_id = id_o_emu if isinstance(id_o_emu, str) else id_o_emu.get("console_id", id_o_emu.get("id"))
    bg_dir = os.path.join(config.BASE_DIR, "fondos_consolas")
    return os.path.abspath(os.path.join(bg_dir, f"{bg_id}.jpg"))

async def _descargar_archivo(session: aiohttp.ClientSession, url: str, ruta_destino: str, retries: int = 1) -> bool:
    """
    Función interna para descargar un binario y guardarlo en disco.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(retries + 1):
        try:
            async with session.get(url, headers=headers, timeout=15) as resp:
                if resp.status == 200:
                    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                    with open(ruta_destino, "wb") as f:
                        f.write(await resp.read())
                    return True
        except:
            if attempt < retries:
                await asyncio.sleep(1)
    return False

# Mapeos de Consolas para scrapers externos
EXTENSION_PLATFORM_MAP = {
    ".nes": "Nintendo - Nintendo Entertainment System",
    ".sfc": "Nintendo - Super Nintendo Entertainment System",
    ".smc": "Nintendo - Super Nintendo Entertainment System",
    ".gba": "Nintendo - Game Boy Advance",
    ".gb":  "Nintendo - Game Boy",
    ".gbc": "Nintendo - Game Boy Color",
    ".n64": "Nintendo - Nintendo 64",
    ".z64": "Nintendo - Nintendo 64",
    ".v64": "Nintendo - Nintendo 64",
    ".wbfs": "Nintendo - Wii",
    ".rvz": "Nintendo - GameCube",
    ".cue": "Sony - PlayStation",
    ".bin": "Sony - PlayStation",
    ".chd": "Sony - PlayStation 2",
    ".md":  "Sega - Mega Drive - Genesis",
    ".pce": "NEC - PC Engine - TurboGrafx 16",
}

def get_platform_for_rom(emu_id: str, ruta_rom: str, default_platform: Optional[str]) -> Optional[str]:
    """
    Resuelve el nombre de plataforma exacto requerido por Libretro basándose en la extensión.
    """
    ext = os.path.splitext(ruta_rom)[1].lower()
    if emu_id in ("mesen", "retroarch"):
        return EXTENSION_PLATFORM_MAP.get(ext, default_platform)
    return default_platform

async def descargar_caratulas_biblioteca(juegos: list, emu_map: dict, **kwargs) -> dict:
    """
    Descarga masiva de arte para la biblioteca del usuario.

    Args:
        juegos (list): Lista de diccionarios de juegos.
        emu_map (dict): Mapa de configuración de emuladores.
        **kwargs: on_progress callback.

    Returns:
        dict: Estadísticas (ok, skip, fail).
    """
    stats = {"ok": 0, "skip": 0, "fail": 0}
    configs = metadata.get_providers_config()
    on_progress = kwargs.get("on_progress")
    total = len(juegos)

    async with aiohttp.ClientSession() as session:
        hub = ArtworkHub(session, configs)
        semaphore = asyncio.Semaphore(5)

        async def _worker(idx, juego):
            async with semaphore:
                emu_id = juego.get("id_emu", "")
                ruta = juego.get("ruta", "")
                nombre = juego.get("nombre", "")
                
                # Resolver plataforma técnica
                emu_info = emu_map.get(emu_id, {})
                libretro_p = emu_info.get("libretro_platform", emu_info.get("console", ""))
                plat = get_platform_for_rom(emu_id, ruta, libretro_p)
                ss_id = emu_info.get("screenscraper_id")
                
                if not plat:
                    stats["skip"] += 1
                else:
                    ok = await hub.download_for_game(plat, nombre, ruta, ss_platform_id=ss_id)
                    if ok: stats["ok"] += 1
                    else: stats["fail"] += 1
                
                if on_progress:
                    on_progress(idx + 1, total, nombre)

        await asyncio.gather(*[_worker(i, j) for i, j in enumerate(juegos)])
    return stats
