import aiohttp
from typing import Optional, Dict, Any
from core.scrapers.base import BaseScraper
from core.scraper_engine import ScraperEngine

class RAWGScraper(BaseScraper):
    """
    Metadata scraper for RAWG.io API.
    """
    API_SEARCH = "https://api.rawg.io/api/games"

    def __init__(self, api_key: str):
        super().__init__("RAWG.io")
        self.api_key = api_key

    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None

        params = {"search": query, "key": self.api_key, "page_size": 5}
        try:
            async with session.get(self.API_SEARCH, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                results = data.get("results", [])
                if not results:
                    return None

                candidates = [r["name"] for r in results]
                best_name = ScraperEngine.find_best_match(query, candidates, min_ratio=0.45, require_significant=False)
                
                if not best_name:
                    return None
                
                best = next(r for r in results if r["name"] == best_name)
                
                # Fetch detailed description
                detail_url = f"{self.API_SEARCH}/{best['id']}"
                async with session.get(detail_url, params={"key": self.api_key}, timeout=8) as d_resp:
                    if d_resp.status == 200:
                        d = await d_resp.json()
                        desc = d.get("description_raw") or d.get("description") or ""
                        # Sanitize description (split by newline and take first relevant para)
                        clean_desc = desc.split('\n')[0][:500] if desc else ""
                        
                        return {
                            "description": clean_desc,
                            "year": (d.get("released") or "")[:4],
                            "developer": d.get("developers", [{}])[0].get("name", "") if d.get("developers") else "",
                            "publisher": d.get("publishers", [{}])[0].get("name", "") if d.get("publishers") else "",
                            "genre": d.get("genres", [{}])[0].get("name", "") if d.get("genres") else "",
                            "players": "Multiplayer" if any(p['name'].lower() == 'multiplayer' for p in d.get('tags', [])) else "Single-player",
                            "source": self.name
                        }
        except:
            pass
        return None
