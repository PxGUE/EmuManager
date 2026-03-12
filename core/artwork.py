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

def obtener_ruta_fondo_consola(emu) -> str:
    """Obtiene la ruta del fondo de la consola, prefiriendo console_id para compartir fondos."""
    if not emu: return ""
    
    # Manejar si pasan solo el string (id)
    if isinstance(emu, str):
        bg_id = emu
    else:
        # ID base para el fondo (usamos console_id si existe para que varios emus compartan)
        bg_id = emu.get("console_id", emu.get("id"))
    
    shared_path = os.path.abspath(os.path.join(get_consoles_bg_dir(), f"{bg_id}_bg.jpg"))
    if os.path.exists(shared_path):
        return shared_path
    
    # Fallback al id original del emu (si emu es dict)
    if not isinstance(emu, str):
        path_emu = os.path.abspath(os.path.join(get_consoles_bg_dir(), f"{emu.get('id')}_bg.jpg"))
        if os.path.exists(path_emu):
            return path_emu
    
    return shared_path

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
    """Descarga fondos de alta calidad para las consolas registradas."""
    stats = {"ok": 0, "skip": 0, "fail": 0}
    on_progress = kwargs.get("on_progress")
    
    # Lista de fondos a descargar (Id de consola -> URL)
    # Usamos console_id para que sea compartido
    FONDOS_MAP = {
        "switch": "https://images7.alphacoders.com/831/831411.jpg", 
        "ps2": "https://images7.alphacoders.com/109/1095345.jpg",
        "gc-wii": "https://images5.alphacoders.com/414/414761.jpg",
        "psp": "https://images.wallpapersden.com/image/download/sony-playstation-portable_a2VqZ2aUmZqaraWkpJRmbmdlrWZmZ2m5.jpg",
        "ps1": "https://images5.alphacoders.com/904/904910.jpg",
        "ps3": "https://images7.alphacoders.com/849/849615.jpg",
        "n64": "https://images.wallpapersden.com/image/download/nintendo-64-logo_a2VqZ2aUmZqaraWkpJRmbmdlrWZmZ2m5.jpg",
        "gba": "https://images8.alphacoders.com/493/493108.jpg",
        "nes": "https://images5.alphacoders.com/462/462499.jpg",
        "snes": "https://images.wallpapersden.com/image/download/nintendo-snes-controller_a2VqZ2aUmZqaraWkpJRmbmdlrWZmZ2m5.jpg",
        "wiiu": "https://images4.alphacoders.com/264/264639.jpg",
        "xbox": "https://images2.alphacoders.com/714/714247.jpg",
        "psvita": "https://images.wallpapersden.com/image/download/playstation-vita-logo_a2VqZ2aUmZqaraWkpJRmbmdlrWZmZ2m5.jpg",
        "multi": "https://wallpapercave.com/wp/wp4268688.jpg" # RetroArch style
    }

    total = len(FONDOS_MAP)
    dest_dir = get_consoles_bg_dir()
    os.makedirs(dest_dir, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        for i, (cid, url) in enumerate(FONDOS_MAP.items()):
            dest_path = os.path.join(dest_dir, f"{cid}_bg.jpg")
            
            if os.path.exists(dest_path):
                stats["skip"] += 1
            else:
                ok = await _descargar_archivo(session, url, dest_path)
                if ok: stats["ok"] += 1
                else: stats["fail"] += 1
            
            if on_progress:
                on_progress(i + 1, total, f"Fondo: {cid}")
                
    return stats
