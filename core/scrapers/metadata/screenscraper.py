import aiohttp
import urllib.parse
from typing import Optional, Dict, Any
from core.scrapers.base import BaseScraper
from core.scraper_engine import ScraperEngine

class ScreenScraperScraper(BaseScraper):
    """
    Metadata scraper for ScreenScraper.fr API.
    A account is required for best results.
    """
    API_BASE = "https://www.screenscraper.fr/api2/jeuInfos.php"

    def __init__(self, user: str, password: str):
        super().__init__("ScreenScraper")
        self.user = user
        self.password = password
        # Dev credentials for the app (placeholders)
        self.devid = "demose"
        self.devpassword = "demosepassword"
        self.softname = "EmuManager"

    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        if not self.user or not self.password:
            return None

        # ScreenScraper is very platform-sensitive
        platform_id = kwargs.get("ss_platform_id")
        
        params = {
            "devid": self.devid,
            "devpassword": self.devpassword,
            "softname": self.softname,
            "output": "json",
            "romnome": query,
            "id": self.user,
            "password": self.password
        }
        
        if platform_id:
            params["systemeid"] = platform_id

        try:
            # Note: ScreenScraper prefers exact ROM name matches, but we can try search
            async with session.get(self.API_BASE, params=params, timeout=12) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                response = data.get("response", {})
                status = response.get("status")
                
                if status != "OK":
                    # If direct match fails, we can't easily do a 'search' with this specific endpoint
                    # without more sophisticated logic.
                    return None
                
                jeu = response.get("jeu", {})
                
                # Get description (prioritize Spanish, then English)
                textes = jeu.get("textes", [])
                desc = ""
                for t in textes:
                    if t.get("langue") == "es":
                        desc = t.get("text")
                    elif t.get("langue") == "en" and not desc:
                        desc = t.get("text")
                
                # Get Metadatos
                edit = jeu.get("editeur", {}).get("nom", "")
                dev = jeu.get("developpeur", {}).get("nom", "")
                genre = jeu.get("genres", [{}])[0].get("nom", "")
                year = jeu.get("dates", [{}])[0].get("date", "")[:4] if jeu.get("dates") else ""
                
                # Get Medias (Artwork)
                medias = jeu.get("medias", [])
                boxart_url = ""
                background_url = ""
                logo_url = ""
                
                for m in medias:
                    m_type = m.get("type", "")
                    m_url = m.get("url", "")
                    if not m_url: continue
                    
                    if m_type in ("box-2D", "box-3D", "box-2D-v", "box-2D-h") and not boxart_url:
                        boxart_url = m_url
                    elif m_type in ("fanart-64", "fanart-1080p", "fanart-720p") and not background_url:
                        background_url = m_url
                    elif m_type == "logo" and not logo_url:
                        logo_url = m_url

                return {
                    "description": desc[:500] if desc else "",
                    "year": year,
                    "developer": dev,
                    "publisher": edit,
                    "genre": genre,
                    "players": jeu.get("joueurs", "1"),
                    "boxart_url": boxart_url,
                    "background_url": background_url,
                    "logo_url": logo_url,
                    "source": self.name
                }
        except:
            pass
        return None
