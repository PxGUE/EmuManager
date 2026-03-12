import aiohttp
import re
from typing import Optional, Dict, Any, List
from core.scrapers.base import BaseScraper
from core.scraper_engine import ScraperEngine
from core.normalization import normalize_title

class WikipediaScraper(BaseScraper):
    """
    Metadata scraper for Wikipedia (MediaWiki API).
    """
    API_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self):
        super().__init__("Wikipedia")

    async def _do_search(self, session: aiohttp.ClientSession, srsearch: str) -> List[Dict]:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": srsearch,
            "format": "json",
            "utf8": 1
        }
        try:
            async with session.get(self.API_URL, params=params, timeout=8) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("query", {}).get("search", [])
        except:
            pass
        return []

    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        try:
            # Estrategia Multibúsqueda:
            # 1. Búsqueda exacta del query (Wikipedia maneja bien acentos y redirecciones)
            # 2. Búsqueda con 'video game'
            # 3. Búsqueda con título normalizado
            
            search_queries = [
                query,
                f"{query} video game",
                f"{normalize_title(query)} video game"
            ]
            
            results = []
            for sq in search_queries:
                batch = await self._do_search(session, sq)
                if batch:
                    results.extend(batch)
                    if len(results) > 5: break # Suficientes candidatos
            
            if not results:
                return None

            # Deduplicar resultados por título
            seen = set()
            unique_results = []
            for r in results:
                if r["title"] not in seen:
                    unique_results.append(r)
                    seen.add(r["title"])

            candidates = [r["title"] for r in unique_results[:12]]
            best_title = ScraperEngine.find_best_match(query, candidates, min_ratio=0.30, require_significant=False)
            
            if not best_title:
                return None
            
            best = next(r for r in results if r["title"] == best_title)

            # Fetch extract
            params = {
                "action": "query",
                "prop": "extracts",
                "exintro": 1,
                "explaintext": 1,
                "titles": best["title"],
                "format": "json"
            }
            async with session.get(self.API_URL, params=params, timeout=8) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                pages = data.get("query", {}).get("pages", {})
                page = next(iter(pages.values()))
                
                extract = page.get("extract", "")
                if extract:
                    first_para = extract.split('\n')[0]
                    return {
                        "description": first_para,
                        "year": self._extract_year(first_para),
                        "developer": self._extract_developer(first_para),
                        "publisher": self._extract_publisher(first_para),
                        "genre": self._extract_genre(first_para),
                        "players": self._extract_players(first_para),
                        "source": self.name
                    }
        except:
            pass
        return None

    def _extract_year(self, text: str) -> str:
        match = re.search(r'\b(19|20)\d{2}\b', text)
        return match.group(0) if match else ""

    def _extract_developer(self, text: str) -> str:
        match = re.search(r'developed by\s+([^,.;]+)', text, re.IGNORECASE)
        return match.group(1).replace("and published by", "").strip()[:32] if match else ""

    def _extract_publisher(self, text: str) -> str:
        match = re.search(r'published by\s+([^,.;]+)', text, re.IGNORECASE)
        return match.group(1).strip()[:32] if match else ""

    def _extract_genre(self, text: str) -> str:
        genres = ["platform", "racing", "role-playing", "action-adventure", "fighting", "shooter", "puzzle", "sports", "stealth", "rhythm"]
        for g in genres:
            if g in text.lower():
                return g.capitalize()
        return "Classic Game"

    def _extract_players(self, text: str) -> str:
        if "multiplayer" in text.lower(): return "Multiplayer"
        if "single-player" in text.lower(): return "Single-player"
        return "Single-player"
