import aiohttp
import urllib.parse
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
from core.scrapers.base import BaseScraper
from core.scraper_engine import ScraperEngine
from core.normalization import normalize_title

class LibretroScraper(BaseScraper):
    """
    Scraper for Libretro Thumbnails CDN.
    """
    CDN_URL = "https://thumbnails.libretro.com"
    THUMBNAIL_TYPE = "Named_Boxarts"

    def __init__(self):
        super().__init__("Libretro")
        self._index_cache = {}

    async def _get_index(self, session: aiohttp.ClientSession, platform: str) -> List[str]:
        if platform in self._index_cache:
            return self._index_cache[platform]

        # Variantes de búsqueda (Espacios, Guiones, etc.) para evitar el Error 404
        search_variations = [
            platform,                            # "Nintendo - Game Boy Advance"
            platform.replace(" ", "_"),          # "Nintendo_-_Game_Boy_Advance"
            platform.replace(" - ", " - "),      # Normalizar espacios en el guion
            platform.replace(" - ", "-")         # "Nintendo-Game Boy Advance"
        ]
        
        # Eliminar duplicados manteniendo orden
        search_variations = list(dict.fromkeys(search_variations))

        for plat_atempt in search_variations:
            url = f"{self.CDN_URL}/{urllib.parse.quote(plat_atempt)}/{self.THUMBNAIL_TYPE}/"
            try:
                async with session.get(url, timeout=12) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        links = soup.find_all('a')
                        names = []
                        for link in links:
                            href = link.get('href', '')
                            if href.endswith('.png'):
                                name = urllib.parse.unquote(href[:-4])
                                names.append(name)
                        
                        if names:
                            self._index_cache[platform] = names
                            print(f"[LIBRETRO] Índice cargado para '{plat_atempt}' (Intento exitoso): {len(names)} juegos.")
                            return names
                    elif resp.status == 404:
                        # Silencioso, intentamos la siguiente variante
                        continue
                    else:
                        print(f"[LIBRETRO] Error HTTP {resp.status} al cargar el índice de '{plat_atempt}'")
            except Exception as e:
                print(f"[LIBRETRO] Excepción en _get_index para '{plat_atempt}': {e}")
        
        return []

    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        platform = kwargs.get("platform")
        if not platform:
            return None

        candidates = await self._get_index(session, platform)
        if not candidates:
            return None

        best_match = ScraperEngine.find_best_match(query, candidates)
        if best_match:
            url = f"{self.CDN_URL}/{urllib.parse.quote(platform)}/{self.THUMBNAIL_TYPE}/{urllib.parse.quote(best_match + '.png')}"
            return {
                "boxart_url": url,
                "source": self.name,
                "match_name": best_match
            }
        return None
