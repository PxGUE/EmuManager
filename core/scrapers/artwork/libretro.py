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

        url = f"{self.CDN_URL}/{urllib.parse.quote(platform)}/{self.THUMBNAIL_TYPE}/"
        try:
            async with session.get(url, timeout=15) as resp:
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
                    self._index_cache[platform] = names
                    return names
        except:
            pass
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
