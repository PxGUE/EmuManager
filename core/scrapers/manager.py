import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from .models import ScrapedData
from .providers.screenscraper import ScreenScraperScraper
from .providers.libretro import LibretroScraper
from .providers.rawg import RAWGScraper
from .providers.tgdb import TGDBScraper

class ScraperManager:
    """
    Coordinates multiple providers to fetch the best possible metadata and artwork.
    """
    
    def __init__(self, session: aiohttp.ClientSession, configs: List[Dict[str, Any]]):
        self.session = session
        self.providers = self._init_providers(configs)
        # 1-second delay between requests to be safe (ScreenScraper limit)
        self.semaphore = asyncio.Semaphore(1) 

    def _init_providers(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        p = {}
        for c in configs:
            if not c.get("enabled"): continue
            pid = c["id"]
            if pid == "screenscraper":
                p[pid] = ScreenScraperScraper(c.get("user"), c.get("password"), c.get("devid"), c.get("devpassword"))
            elif pid == "libretro":
                p[pid] = LibretroScraper()
            elif pid == "rawg":
                p[pid] = RAWGScraper(c.get("api_key"))
            elif pid == "tgdb":
                p[pid] = TGDBScraper(c.get("api_key"))
        return p

    async def scrape_game(self, title: str, system_id: Optional[str] = None, **kwargs) -> Optional[ScrapedData]:
        """
        Executes the scraping flow for a single game.
        """
        async with self.semaphore:
            final_data = ScrapedData(title=title)
            
            # 1. ScreenScraper (Primary for everything)
            ss = self.providers.get("screenscraper")
            if ss:
                res = await ss.fetch(self.session, title, ss_platform_id=system_id, **kwargs)
                if res:
                    final_data.merge(res)
            
            # 2. Libretro (Fallback for 2D Boxart)
            if not final_data.boxart_2d:
                lib = self.providers.get("libretro")
                if lib and kwargs.get("platform"):
                    res = await lib.fetch(self.session, title, **kwargs)
                    if res:
                        print(f"[SCRAPER] Usando fallback Libretro para arte: {title}")
                        final_data.merge(res)
            
            # 3. TGDB / RAWG (Fallback for Metadata)
            # Only if description is missing
            if not final_data.description:
                for pid in ["tgdb", "rawg"]:
                    p = self.providers.get(pid)
                    if p:
                        res = await p.fetch(self.session, title, **kwargs)
                        if res:
                            final_data.merge(res)
                            if final_data.description: break
            
            # Wait a bit longer to prevent rate limiting (Status 431 prevention)
            await asyncio.sleep(1.2)
            
            # If we didn't get anything significant, return None
            if not final_data.boxart_2d and not final_data.description:
                return None
                
            return final_data
