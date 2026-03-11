"""
metadata.py — Scraper Hub V2.0 (Arquitectura de Proveedores)
Sistema flexible que soporta múltiples bases de datos configurables por el usuario.
"""

import asyncio
import aiohttp
import json
import os
import re
from typing import Optional, List, Dict, Any
from .normalization import normalize_title, get_search_variations
from .scraper_engine import ScraperEngine

# --- Proveedores Disponibles ---

class BaseProvider:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.priority = config.get("priority", 0)

    async def fetch(self, session: aiohttp.ClientSession, query: str, platform_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

class TGDBProvider(BaseProvider):
    URL = "https://api.thegamesdb.net/v1/Games/ByGameName"
    
    async def fetch(self, session: aiohttp.ClientSession, query: str, platform_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        api_key = self.config.get("api_key", "legacy")
        params = {
            "apikey": api_key,
            "name": query,
            "fields": "players,publishers,genres,overview,rating,release_date",
            "include": "boxart",
        }
        if platform_id: params["filter[platform]"] = platform_id
        
        headers = {"User-Agent": "EmuManager/2.0"}
        try:
            async with session.get(self.URL, params=params, headers=headers, timeout=10) as resp:
                if resp.status != 200: return None
                data = await resp.json()
                games = data.get("data", {}).get("games", [])
                if not games: return None
                
                best = ScraperEngine.select_best_object(query, games, lambda x: x.get("game_title", ""), min_ratio=0.45)
                if best:
                    # Parsea datos específicos de TGDB
                    best['_context'] = data
                    return self._parse(best)
        except: return None
        return None

    def _parse(self, g):
        inc = g.get('_context', {}).get("include", {})
        # Boxart
        box_meta = inc.get("boxart", {})
        base = box_meta.get("base_url", "https://cdn.thegamesdb.net/images/")
        box_url = ""
        for art in box_meta.get("data", {}).get(str(g.get("id")), []):
            if art.get("side") == "front":
                box_url = base + art.get("filename", "")
                break
        
        rel = g.get("release_date", "")
        return {
            "description": (g.get("overview") or "").strip(),
            "year": rel[:4] if len(rel) >= 4 else "",
            "company": inc.get("publishers", {}).get("data", {}).get(str(g.get("publishers", [0])[0]), {}).get("name", ""),
            "genre": "", # Requiere mapeo de IDs
            "rating": g.get("rating", ""),
            "boxart_url": box_url,
            "source": "TheGamesDB"
        }

class RAWGProvider(BaseProvider):
    URL = "https://api.rawg.io/api/games"
    
    async def fetch(self, session: aiohttp.ClientSession, query: str, platform_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        api_key = self.config.get("api_key", "da1c12149b5c46bba8479e0a6d6545b7")
        params = {"key": api_key, "search": query, "page_size": 5}
        
        try:
            async with session.get(self.URL, params=params, timeout=10) as resp:
                if resp.status != 200: return None
                data = await resp.json()
                results = data.get("results", [])
                best = ScraperEngine.select_best_object(query, results, lambda x: x.get("name", ""), min_ratio=0.40)
                if best: return self._parse(best)
        except: return None
        return None

    def _parse(self, g):
        rel = g.get("released") or ""
        return {
            "description": "Info de RAWG.io",
            "year": rel[:4] if len(rel) >= 4 else "",
            "company": "",
            "genre": ", ".join([gen.get("name", "") for gen in g.get("genres", [])]),
            "rating": str(g.get("rating", "")),
            "boxart_url": g.get("background_image") or "",
            "source": "RAWG.io"
        }

# --- Gestor de Metadatos ---

_METADATA_CACHE_PATH = os.path.join("data", "metadata.json")
_METADATA_MEM_CACHE: dict = {}

def get_providers_config() -> List[Dict]:
    """Carga la configuración de proveedores desde el disco."""
    path = os.path.join("data", "scrapers_config.json")
    default = [
        {"id": "tgdb", "name": "TheGamesDB", "enabled": True, "priority": 1, "api_key": "legacy"},
        {"id": "rawg", "name": "RAWG.io", "enabled": True, "priority": 2, "api_key": "da1c12149b5c46bba8479e0a6d6545b7"},
        {"id": "screenscraper", "name": "ScreenScraper", "enabled": False, "priority": 3, "user": "", "password": ""}
    ]
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except: pass
    return default

async def obtener_metadata(session: aiohttp.ClientSession, nombre: str, ruta: str, platform: Optional[str] = None) -> dict:
    configs = sorted(get_providers_config(), key=lambda x: x.get("priority", 99))
    providers = []
    for c in configs:
        if not c.get("enabled"): continue
        if c["id"] == "tgdb": providers.append(TGDBProvider(c))
        elif c["id"] == "rawg": providers.append(RAWGProvider(c))

    busquedas = get_search_variations(nombre)
    original_base = os.path.splitext(os.path.basename(ruta))[0]
    if original_base not in busquedas: busquedas.append(original_base)

    for query in busquedas:
        for p in providers:
            res = await p.fetch(session, query)
            if res: return res
    return {}

# --- Funciones de Caché ---

def _cargar_cache():
    global _METADATA_MEM_CACHE
    if _METADATA_MEM_CACHE: return _METADATA_MEM_CACHE
    try:
        if os.path.exists(_METADATA_CACHE_PATH):
            with open(_METADATA_CACHE_PATH, "r", encoding="utf-8") as f:
                _METADATA_MEM_CACHE = json.load(f)
    except: pass
    return _METADATA_MEM_CACHE

def obtener_metadata_local(ruta_rom: str) -> dict:
    return _cargar_cache().get(ruta_rom, {})

async def descargar_metadata_biblioteca(juegos: list, emu_map: dict, on_progress=None) -> dict:
    cache = _cargar_cache()
    stats = {"ok": 0, "skip": 0, "fail": 0}
    total = len(juegos)
    
    async with aiohttp.ClientSession() as session:
        for i, juego in enumerate(juegos):
            ruta = juego.get("ruta", "")
            nombre = juego.get("nombre", "")
            
            if ruta in cache and cache[ruta]:
                stats["skip"] += 1
            else:
                meta = await obtener_metadata(session, nombre, ruta)
                if meta:
                    cache[ruta] = meta
                    stats["ok"] += 1
                else:
                    cache[ruta] = {}
                    stats["fail"] += 1
            
            if on_progress: on_progress(i + 1, total, nombre)
            await asyncio.sleep(0.1)

    os.makedirs("data", exist_ok=True)
    with open(_METADATA_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    return stats
