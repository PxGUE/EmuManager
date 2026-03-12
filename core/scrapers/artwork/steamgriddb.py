import aiohttp
import urllib.parse
import re
from typing import Optional, Dict, Any
from core.scrapers.base import BaseScraper
from core.scraper_engine import ScraperEngine

class SteamGridDBScraper(BaseScraper):
    """
    Scraper for SteamGridDB API v2.
    """
    URL_SEARCH = "https://www.steamgriddb.com/api/v2/search/autocomplete"
    URL_ASSETS = "https://www.steamgriddb.com/api/v2/{asset_type}/game/{game_id}"

    def __init__(self, api_key: str):
        super().__init__("SteamGridDB")
        self.api_key = api_key

    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None

        headers = {"Authorization": f"Bearer {self.api_key}"}
        # Clean query for search
        clean_query = re.sub(r'\(.*?\)|\[.*?\]', '', query).strip()
        
        try:
            # 1. Search for game ID
            search_url = f"{self.URL_SEARCH}/{urllib.parse.quote(clean_query)}"
            async with session.get(search_url, headers=headers, timeout=8) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                results = data.get("data", [])
                if not results:
                    return None
                
                candidates = [r["name"] for r in results]
                best_name = ScraperEngine.find_best_match(clean_query, candidates)
                if not best_name:
                    return None
                
                best_result = next(r for r in results if r["name"] == best_name)
                game_id = best_result["id"]
                
                # 2. Fetch specific asset types
                assets = {"source": self.name, "game_id": game_id}
                types = {
                    "grids": "boxart_url", 
                    "heroes": "background_url", 
                    "logos": "logo_url"
                }
                
                for a_type, key in types.items():
                    url = self.URL_ASSETS.format(asset_type=a_type, game_id=game_id)
                    async with session.get(url, headers=headers, timeout=5) as a_resp:
                        if a_resp.status == 200:
                            a_data = await a_resp.json()
                            a_list = a_data.get("data", [])
                            if a_list:
                                assets[key] = a_list[0]["url"]
                
                return assets if len(assets) > 2 else None
        except:
            pass
        return None
