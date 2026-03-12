import asyncio
import aiohttp
import os
import json
import re
import difflib
from urllib.parse import quote
from typing import Optional, Dict, Any, List

# --- Motor de Similitud y Normalización ---

class ScraperEngine:
    @staticmethod
    def clean_name(name: str) -> str:
        """Limpia tags de ROMs para mejor búsqueda en web."""
        # Elimina (USA), [!], v1.2, etc.
        n = re.sub(r'\(.*?\)|\[.*?\]', '', name)
        n = re.sub(r'\bv\d+(\.\d+)*\b', '', n, flags=re.IGNORECASE)
        return n.strip()

    @staticmethod
    def get_ratio(str1: str, str2: str) -> float:
        """Calcula la similitud entre dos hilos de texto (0.0 a 1.0)."""
        if not str1 or not str2: return 0.0
        s1 = re.sub(r'[^a-z0-9]', '', str1.lower())
        s2 = re.sub(r'[^a-z0-9]', '', str2.lower())
        return difflib.SequenceMatcher(None, s1, s2).ratio()

# --- Scraper de Wikipedia (Gratis, sin API Key) ---

class WikipediaScraper:
    """Busca información en Wikipedia (MediaWiki API). No requiere Key."""
    API_URL = "https://en.wikipedia.org/w/api.php"

    async def fetch(self, session: aiohttp.ClientSession, query: str) -> Optional[Dict[str, Any]]:
        clean_q = ScraperEngine.clean_name(query)
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{clean_q} video game",
            "format": "json",
            "utf8": 1
        }
        try:
            async with session.get(self.API_URL, params=params, timeout=8) as resp:
                if resp.status != 200: return None
                data = await resp.json()
                results = data.get("query", {}).get("search", [])
                if not results: return None

                # El primer resultado suele ser el mejor, pero validamos con difflib
                best = None
                for res in results[:3]:
                    score = ScraperEngine.get_ratio(clean_q, res["title"])
                    if score > 0.45:
                        best = res
                        break
                
                if not best: return None

                # Obtener el extracto (resumen)
                content_params = {
                    "action": "query",
                    "prop": "extracts|revisions",
                    "exintro": 1,
                    "explaintext": 1,
                    "titles": best["title"],
                    "format": "json"
                }
                async with session.get(self.API_URL, params=content_params, timeout=8) as c_resp:
                    c_data = await c_resp.json()
                    pages = c_data.get("query", {}).get("pages", {})
                    page = next(iter(pages.values()))
                    
                    extract = page.get("extract", "")
                    if extract:
                        first_para = extract.split('\n')[0]
                        
                        return {
                            "description": first_para,
                            "year": self._extract_year(first_para) or "",
                            "developer": self._extract_developer(first_para) or "",
                            "publisher": self._extract_publisher(first_para) or "",
                            "genre": self._extract_genre(first_para) or "Classic Game",
                            "players": self._extract_players(first_para) or "",
                            "source": "Wikipedia"
                        }
        except: return None
        return None

    def _extract_year(self, text: str) -> Optional[str]:
        match = re.search(r'\b(19|20)\d{2}\b', text)
        return match.group(0) if match else None

    def _extract_developer(self, text: str) -> Optional[str]:
        # Patrón: "developed by [Name]"
        match = re.search(r'developed by\s+([^,.;]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).replace("and published by", "").strip()[:24]
        return None

    def _extract_publisher(self, text: str) -> Optional[str]:
        # Patrón: "published by [Name]"
        match = re.search(r'published by\s+([^,.;]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:24]
        return None

    def _extract_genre(self, text: str) -> Optional[str]:
        genres = ["platform", "racing", "role-playing", "action-adventure", "fighting", "shooter", "puzzle", "sports", "stealth"]
        for g in genres:
            if g in text.lower(): return g.capitalize()
        return None

    def _extract_players(self, text: str) -> Optional[str]:
        if "multiplayer" in text.lower(): return "Multiplayer"
        if "single-player" in text.lower(): return "Single-player"
        return None

# --- Motor de Metadatos ---

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

    wiki = WikipediaScraper()
    headers = {
        "User-Agent": "EmuManager/1.0 (https://github.com/chrispc/EmuManager; admin@example.com)"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        for i, juego in enumerate(juegos):
            ruta = juego.get("ruta", "")
            nombre = juego.get("nombre", "")
            
            # Si ya tenemos descripción, saltamos
            if ruta in cache and cache[ruta].get("description"):
                stats["skip"] += 1
            else:
                print(f"[METADATA] Scrapeando (Wikipedia): '{nombre}'...")
                res = await wiki.fetch(session, nombre)
                
                if res:
                    cache[ruta] = res
                    stats["ok"] += 1
                    print(f"[METADATA] ¡EXITO! Información recuperada de Wikipedia.")
                else:
                    cache[ruta] = cache.get(ruta, {}) # Mantener lo que hubiera o vacío
                    stats["fail"] += 1
            
            if on_progress: on_progress(i + 1, total, nombre)

    # Guardar cache final
    os.makedirs("data", exist_ok=True)
    with open(_METADATA_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    
    return stats

def get_providers_config():
    """Retorna la configuración de los scrapers desde el archivo JSON."""
    path = os.path.join("data", "scrapers_config.json")
    default = [
        {"id": "tgdb", "name": "TheGamesDB", "enabled": True, "priority": 1, "api_key": "legacy"},
        {"id": "rawg", "name": "RAWG.io", "enabled": True, "priority": 2, "api_key": "da1c12149b5c46bba8479e0a6d6545b7"},
        {"id": "screenscraper", "name": "ScreenScraper", "enabled": True, "priority": 3, "user": "paidex", "password": "Shiro347"},
        {"id": "steamgriddb", "name": "SteamGridDB", "enabled": True, "priority": 0, "api_key": "9dcc920d6a209a34802ce9463af6834f"}
    ]
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return default
