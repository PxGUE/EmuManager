import asyncio
import aiohttp
import os
import json
from typing import Optional, Dict, Any, List

from .scrapers.metadata.wikipedia import WikipediaScraper
from .scrapers.metadata.rawg import RAWGScraper
from .scrapers.metadata.tgdb import TGDBScraper

# --- Motor de Metadatos (Hub) ---

_METADATA_CACHE_PATH = os.path.join("data", "metadata.json")

def obtener_metadata_local(ruta_rom: str) -> dict:
    if not os.path.exists(_METADATA_CACHE_PATH): return {}
    try:
        with open(_METADATA_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get(ruta_rom, {})
    except: return {}

async def descargar_metadata_biblioteca(juegos: list, emu_map: dict, on_progress=None) -> dict:
    stats = {"ok": 0, "skip": 0, "fail": 0}
    total = len(juegos)
    
    # Cargar cache
    cache = {}
    if os.path.exists(_METADATA_CACHE_PATH):
        try:
            with open(_METADATA_CACHE_PATH, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except: pass

    # Inicializar Scrapers basados en estado 'enabled'
    configs = get_providers_config()
    
    # Wikipedia
    wiki_cfg = next((c for c in configs if c["id"] == "wikipedia"), {"enabled": True})
    wiki = WikipediaScraper() if wiki_cfg.get("enabled") else None
    
    # RAWG
    rawg_cfg = next((c for c in configs if c["id"] == "rawg"), None)
    rawg_api_key = rawg_cfg["api_key"] if rawg_cfg and rawg_cfg.get("enabled") else None
    rawg = RAWGScraper(rawg_api_key) if rawg_api_key else None

    headers = {
        "User-Agent": "EmuManager/1.0 (https://github.com/chrispc/EmuManager; admin@example.com)"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        semaphore = asyncio.Semaphore(3)
        
        async def _worker(idx, juego):
            async with semaphore:
                ruta = juego.get("ruta", "")
                nombre = juego.get("nombre", "")
                
                if ruta in cache and cache[ruta].get("description"):
                    stats["skip"] += 1
                else:
                    res = None
                    if wiki:
                        res = await wiki.fetch(session, nombre)
                    
                    if not res and rawg:
                        res = await rawg.fetch(session, nombre)

                    if res:
                        cache[ruta] = res
                        stats["ok"] += 1
                    else:
                        cache[ruta] = cache.get(ruta, {})
                        stats["fail"] += 1
                
                if on_progress: on_progress(idx + 1, total, nombre)
                await asyncio.sleep(0.02)

        await asyncio.gather(*[_worker(i, j) for i, j in enumerate(juegos)])

    # Guardar cache final
    os.makedirs("data", exist_ok=True)
    with open(_METADATA_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    
    return stats

def get_providers_config() -> List[Dict]:
    """Retorna la configuración de los scrapers mezclando los defaults con lo guardado."""
    path = os.path.join("data", "scrapers_config.json")
    default = [
        {"id": "libretro", "name": "Libretro CDN", "enabled": True, "type": "artwork", "priority": 0},
        {"id": "steamgriddb", "name": "SteamGridDB", "enabled": True, "type": "artwork", "priority": 1, "api_key": "9dcc920d6a209a34802ce9463af6834f"},
        {"id": "wikipedia", "name": "Wikipedia", "enabled": True, "type": "metadata", "priority": 0},
        {"id": "tgdb", "name": "TheGamesDB", "enabled": True, "type": "metadata", "priority": 1, "api_key": "legacy"},
        {"id": "rawg", "name": "RAWG.io", "enabled": True, "type": "metadata", "priority": 2, "api_key": "da1c12149b5c46bba8479e0a6d6545b7"},
        {"id": "screenscraper", "name": "ScreenScraper", "enabled": True, "type": "metadata", "priority": 3, "user": "paidex", "password": "Shiro347"}
    ]
    
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Migración: Si 'saved' es una lista, actualizamos los defaults con los valores guardados
                if isinstance(saved, list):
                    for d in default:
                        s = next((x for x in saved if x.get("id") == d["id"]), None)
                        if s:
                            # Preservar valores del usuario pero mantener la estructura nueva
                            for field in ["enabled", "api_key", "user", "password", "priority"]:
                                if field in s:
                                    d[field] = s[field]
                return default
        except Exception as e:
            print(f"[METADATA] Error cargando config: {e}")
            
    return default
