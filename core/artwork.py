"""
artwork.py — Artwork Hub V3 (Modular Provider Based)
"""

import asyncio
import aiohttp
import os
import urllib.parse
from typing import Optional, Callable, List, Dict

from .normalization import normalize_title
from .scrapers.artwork.libretro import LibretroScraper
from .scrapers.artwork.steamgriddb import SteamGridDBScraper
import core.metadata as metadata

# --- Hub de Carátulas ---

class ArtworkHub:
    def __init__(self, session: aiohttp.ClientSession, configs: List[Dict]):
        self.session = session
        
        # Initialize Providers based on enabled status
        libretro_cfg = next((c for c in configs if c["id"] == "libretro"), {"enabled": True})
        self.libretro = LibretroScraper() if libretro_cfg.get("enabled") else None
        
        sgdb_cfg = next((c for c in configs if c["id"] == "steamgriddb"), None)
        sgdb_key = sgdb_cfg.get("api_key") if sgdb_cfg and sgdb_cfg.get("enabled") else None
        self.sgdb = SteamGridDBScraper(sgdb_key) if sgdb_key else None

    async def download_for_game(self, platform: str, game_name: str, rom_path: str) -> bool:
        """
        Coordinates downloading artwork from multiple providers.
        """
        caratula_path = obtener_ruta_caratula(rom_path)
        
        # 1. Try Libretro (Primary for Boxarts)
        if self.libretro:
            res = await self.libretro.fetch(self.session, game_name, platform=platform)
            if res and res.get("boxart_url"):
                ok = await _descargar_archivo(self.session, res["boxart_url"], caratula_path)
                if ok:
                    return True
        
        # 2. Try SteamGridDB (Boxart, Hero, Logo)
        if self.sgdb:
            # Try by ROM name first, then game name
            clean_name = os.path.splitext(os.path.basename(rom_path))[0]
            res = await self.sgdb.fetch(self.session, clean_name)
            if not res:
                res = await self.sgdb.fetch(self.session, game_name)
            
            if res:
                # Download Boxart if not already fetched
                if res.get("boxart_url") and not os.path.exists(caratula_path):
                    await _descargar_archivo(self.session, res["boxart_url"], caratula_path)
                
                # Download Background (Hero)
                if res.get("background_url"):
                    bg_path = obtener_ruta_background(rom_path)
                    if not os.path.exists(bg_path):
                        await _descargar_archivo(self.session, res["background_url"], bg_path)
                
                # Download Logo
                if res.get("logo_url"):
                    logo_path = obtener_ruta_logo(rom_path)
                    if not os.path.exists(logo_path):
                        await _descargar_archivo(self.session, res["logo_url"], logo_path)
                
                return os.path.exists(caratula_path)
        
        return os.path.exists(caratula_path)


# Directorios y Utilerías de Rutas (Se mantienen del original para compatibilidad)

PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_MEDIA_DIR = os.path.join(PROJECT_ROOT_DIR, "media")
USER_MEDIA_PATH = "media"

def set_base_media_path(new_path: str):
    global USER_MEDIA_PATH
    USER_MEDIA_PATH = new_path

def get_consoles_bg_dir():
    return os.path.join(USER_MEDIA_PATH, "fondos_consolas")

def get_system_consoles_dir():
    return os.path.join(SYSTEM_MEDIA_DIR, "consolas")

def get_system_emulators_dir():
    return os.path.join(SYSTEM_MEDIA_DIR, "emuladores")

def obtener_ruta_caratula(ruta_rom: str) -> str:
    rom_dir = os.path.dirname(ruta_rom)
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(rom_dir, "media", f"{game_name}.png")

def obtener_ruta_background(ruta_rom: str) -> str:
    rom_dir = os.path.dirname(ruta_rom)
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(rom_dir, "media", f"{game_name}_bg.jpg")

def obtener_ruta_logo(ruta_rom: str) -> str:
    rom_dir = os.path.dirname(ruta_rom)
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(rom_dir, "media", f"{game_name}_logo.png")

def tiene_caratula(ruta_rom: str) -> bool:
    return os.path.exists(obtener_ruta_caratula(ruta_rom))

def obtener_ruta_logo_consola(id_emu: str, flet_path: bool = False) -> str:
    if flet_path: return f"/consolas/{id_emu}.png"
    return os.path.abspath(os.path.join(get_system_consoles_dir(), f"{id_emu}.png"))

def obtener_ruta_fondo_consola(id_emu: str) -> str:
    return os.path.abspath(os.path.join(get_consoles_bg_dir(), f"{id_emu}_bg.jpg"))

async def _descargar_archivo(session: aiohttp.ClientSession, url: str, ruta_destino: str, retries: int = 1) -> bool:
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
            if attempt < retries: await asyncio.sleep(1)
    return False

# Mapeos de Consolas y Fondos (Se mantienen)
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
    ext = os.path.splitext(ruta_rom)[1].lower()
    if emu_id in ("mesen", "retroarch"):
        return EXTENSION_PLATFORM_MAP.get(ext, default_platform)
    return default_platform

async def descargar_caratulas_biblioteca(juegos: list, emu_map: dict, **kwargs) -> dict:
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
                plat = get_platform_for_rom(emu_id, ruta, emu_map.get(emu_id))
                
                if not plat:
                    stats["skip"] += 1
                else:
                    ok = await hub.download_for_game(plat, nombre, ruta)
                    if ok: stats["ok"] += 1
                    else: stats["fail"] += 1
                
                if on_progress: on_progress(idx + 1, total, nombre)

        await asyncio.gather(*[_worker(i, j) for i, j in enumerate(juegos)])
    return stats

async def descargar_fondos_consolas(**kwargs) -> dict:
    # Logic for downloading console backgrounds (Carbon Theme)
    # Keeping it simple for the refactor hub
    return {"ok": 0, "skip": 0, "fail": 0}
