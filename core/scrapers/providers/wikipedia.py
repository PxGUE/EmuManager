import aiohttp
import re
import unicodedata
from typing import Optional, Dict, Any, List
from core.scrapers.base import BaseScraper
from core.logic.scraper_engine import ScraperEngine
from core.logic.normalization import normalize_title, get_search_variations

class WikipediaScraper(BaseScraper):
    """
    Metadata scraper for Wikipedia (MediaWiki API).
    """
    # Soporte multi-idioma para ampliar cobertura (English y Spanish)
    API_URLS = {
        "en": "https://en.wikipedia.org/w/api.php",
        "es": "https://es.wikipedia.org/w/api.php"
    }

    def __init__(self):
        super().__init__("Wikipedia")

    async def _do_search(self, session: aiohttp.ClientSession, srsearch: str, lang: str = "en") -> List[Dict]:
        url = self.API_URLS.get(lang, self.API_URLS["en"])
        params = {
            "action": "query",
            "list": "search",
            "srsearch": srsearch,
            "format": "json",
            "utf8": 1
        }
        try:
            async with session.get(url, params=params, timeout=8) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("query", {}).get("search", [])
        except:
            pass
        return []

    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        # Estrategia: Probar idiomas (EN, ES) y recursividad (pop-back)
        for lang, url in self.API_URLS.items():
            base_search = query
            attempts = 0 # Máximo 2 intentos recursivos (quitando palabras del final)
            
            while attempts < 3:
                try:
                    # 1. Preparar variaciones
                    variations = get_search_variations(base_search)
                    search_queries = [base_search]
                    for v in variations[:2]:
                        if v not in search_queries: search_queries.append(v)
                        tag = "video game" if lang == "en" else "videojuego"
                        search_queries.append(f"{v} {tag}")
                    
                    # 2. Realizar búsquedas
                    results = []
                    for sq in search_queries:
                        batch = await self._do_search(session, sq, lang=lang)
                        if batch:
                            results.extend(batch)
                            if len(results) > 5: break
                    
                    if not results:
                        # Recursividad: Quitar la última palabra e intentar de nuevo
                        words = base_search.split()
                        if len(words) > 1:
                            base_search = " ".join(words[:-1])
                            attempts += 1
                            continue
                        else:
                            break # No se puede recortar más

                    # 3. Procesar Candidatos
                    seen = set()
                    unique_results = []
                    for r in results:
                        if r["title"] not in seen:
                            unique_results.append(r)
                            seen.add(r["title"])

                    candidates = [r["title"] for r in unique_results[:12]]
                    best_title = ScraperEngine.find_best_match(query, candidates, min_ratio=0.30, require_significant=False)
                    
                    if not best_title:
                        # Si no hay match bueno, probar acortando el nombre de búsqueda
                        words = base_search.split()
                        if len(words) > 1:
                            base_search = " ".join(words[:-1])
                            attempts += 1
                            continue
                        else:
                            break
                    
                    best = next(r for r in unique_results if r["title"] == best_title)

                    # 4. Obtener contenido (Extract)
                    params = {
                        "action": "query",
                        "prop": "extracts",
                        "exintro": 1,
                        "explaintext": 1,
                        "titles": best["title"],
                        "format": "json"
                    }
                    async with session.get(url, params=params, timeout=8) as resp:
                        if resp.status == 200:
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
                                    "source": f"{self.name} ({lang.upper()})"
                                }
                    break # Salir del while si procesamos candidatos pero sin retorno final
                except Exception:
                    attempts += 1
                    continue
        return None

    def _extract_year(self, text: str) -> str:
        match = re.search(r'\b(19|20)\d{2}\b', text)
        return match.group(0) if match else ""

    def _extract_developer(self, text: str) -> str:
        match = re.search(r'developed by\s+([^,.;]+)', text, re.IGNORECASE)
        # Fallback para español
        if not match:
            match = re.search(r'desarrollado por\s+([^,.;]+)', text, re.IGNORECASE)
        return match.group(1).replace("and published by", "").strip()[:32] if match else ""

    def _extract_publisher(self, text: str) -> str:
        match = re.search(r'published by\s+([^,.;]+)', text, re.IGNORECASE)
        if not match:
            match = re.search(r'publicado por\s+([^,.;]+)', text, re.IGNORECASE)
        return match.group(1).strip()[:32] if match else ""

    def _extract_genre(self, text: str) -> str:
        genres = ["platform", "racing", "role-playing", "action-adventure", "fighting", "shooter", "puzzle", "sports", "stealth", "rhythm", "plataformas", "carreras", "rol"]
        for g in genres:
            if g in text.lower():
                return g.capitalize()
        return "Classic Game"

    def _extract_players(self, text: str) -> str:
        t_low = text.lower()
        if "multiplayer" in t_low or "multijugador" in t_low: return "Multiplayer"
        if "single-player" in t_low or "un jugador" in t_low: return "Single-player"
        return "Single-player"
