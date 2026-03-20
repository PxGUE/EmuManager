import aiohttp
from typing import Optional, Dict, Any
from core.scrapers.base import BaseScraper
from core.logic.scraper_engine import ScraperEngine

class TGDBScraper(BaseScraper):
    """
    Metadata scraper for TheGamesDB.
    """
    API_SEARCH = "https://api.thegamesdb.net/v1/Games/ByGameName"
    API_DETAIL = "https://api.thegamesdb.net/v1/Games/ByGameID"

    def __init__(self, api_key: str):
        super().__init__("TheGamesDB")
        self.api_key = api_key

    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[ScrapedData]:
        if not self.api_key or self.api_key == "legacy":
            return None

        params = {"apikey": self.api_key, "name": query}
        try:
            async with session.get(self.API_SEARCH, params=params, timeout=12) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                games = data.get("data", {}).get("games", [])
                if not games:
                    return None

                # Matching logic
                candidates = [g["game_title"] for g in games]
                best_name = ScraperEngine.find_best_match(query, candidates)
                if not best_name:
                    return None

                best = next(g for g in games if g["game_title"] == best_name)
                
                # Format release date
                rdate = best.get("release_date", "")
                year = rdate.split("-")[0] if "-" in rdate else None

                return ScrapedData(
                    title=best["game_title"],
                    description=best.get("overview", ""),
                    release_date=year,
                    developer=str(best.get("developers", [{}])[0]) if best.get("developers") else None,
                    genre=str(best.get("genres", [{}])[0]) if best.get("genres") else None,
                    source_name=self.name
                )
        except Exception as e:
            print(f"[TGDB] Error en fetch ({query}): {e}")
        return None
