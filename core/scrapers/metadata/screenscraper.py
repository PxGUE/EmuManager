import aiohttp
import urllib.parse
import os
from typing import Optional, Dict, Any
from core.scrapers.base import BaseScraper
from core.scraper_engine import ScraperEngine

class ScreenScraperScraper(BaseScraper):
    """
    Metadata scraper for ScreenScraper.fr API.
    A account is required for best results.
    """
    API_BASE = "https://www.screenscraper.fr/api2/jeuInfos.php"

    def __init__(self, user: str, password: str, dev_id: str = None, dev_password: str = None):
        super().__init__("ScreenScraper")
        self.user = user
        self.password = password
        
        # 🛡️ SEGURIDAD (COMPILACIÓN):
        try:
            from core import _secrets
        except (ImportError, ModuleNotFoundError):
            _secrets = None

        final_dev_id = dev_id or (getattr(_secrets, "SS_DEV_ID", None) if _secrets else None) or os.getenv("SS_DEV_ID", "EMU_MANAGER_DEV")
        final_dev_pass = dev_password or (getattr(_secrets, "SS_DEV_PASSWORD", None) if _secrets else None) or os.getenv("SS_DEV_PASSWORD", "EMU_MANAGER_PASS")

        self.devid = final_dev_id
        self.devpassword = final_dev_pass
        self.softname = "EmuManager"

    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        # 🛡️ GUARD: No intentamos nada si faltan credenciales críticas o son los placeholders por defecto
        if not self.user or not self.password or self.devid in (None, "", "EMU_MANAGER_DEV"):
            # Omitimos log para no saturar si es lo esperado (sin configuración)
            return None

        # ScreenScraper is very platform-sensitive
        platform_id = kwargs.get("ss_platform_id")
        
        rom_file = kwargs.get("rom_file", query)
        params = {
            "devid": self.devid,
            "devpassword": self.devpassword,
            "softname": self.softname,
            "output": "json",
            "romtype": "rom",
            "romnom": rom_file,
            "ssid": self.user,
            "sspassword": self.password
        }
        
        # ScreenScraper is very system-sensitive.
        if platform_id:
            params["systemeid"] = platform_id

        try:
            print(f"[SCREEN_SCRAPER] Buscando: {query} (ID Sistema: {platform_id})")
            # Note: ScreenScraper prefers exact ROM name matches, but we can try search
            async with session.get(self.API_BASE, params=params, timeout=12) as resp:
                if resp.status != 200:
                    err_txt = await resp.text()
                    if resp.status == 403:
                        print(f"[SCREEN_SCRAPER] Error 403: Se requiere registrar un 'devid' de desarrollador en screenscraper.fr para usar esta API.")
                    else:
                        print(f"[SCREEN_SCRAPER] Error HTTP: {resp.status} - {err_txt}")
                    return None
                
                data = await resp.json()
                response = data.get("response", {})
                status = response.get("status")
                
                if status != "OK":
                    print(f"[SCREEN_SCRAPER] Respuesta no OK: {status}")
                    # If direct match fails, we can't easily do a 'search' with this specific endpoint
                    # without more sophisticated logic.
                    return None
                
                print(f"[SCREEN_SCRAPER] Juego encontrado: {response.get('jeu', {}).get('noms', [{}])[0].get('nom', 'Desconocido')}")
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
                boxart_3d_url = ""
                background_url = ""
                logo_url = ""
                manual_url = ""
                
                for m in medias:
                    m_type = m.get("type", "")
                    m_url = m.get("url", "")
                    if not m_url: continue
                    
                    if m_type in ("box-2D", "box-2D-v", "box-2D-h") and not boxart_url:
                        boxart_url = m_url
                    elif m_type == "box-3D" and not boxart_3d_url:
                        boxart_3d_url = m_url
                    elif m_type in ("fanart-64", "fanart-1080p", "fanart-720p") and not background_url:
                        background_url = m_url
                    elif m_type == "logo" and not logo_url:
                        logo_url = m_url
                    elif m_type == "manuel" and not manual_url:
                        manual_url = m_url

                return {
                    "description": desc[:500] if desc else "",
                    "year": year,
                    "developer": dev,
                    "publisher": edit,
                    "genre": genre,
                    "players": jeu.get("joueurs", "1"),
                    "boxart_url": boxart_url,
                    "boxart_3d_url": boxart_3d_url,
                    "background_url": background_url,
                    "logo_url": logo_url,
                    "manual_url": manual_url,
                    "source": self.name
                }
        except Exception as e:
            print(f"[SCREEN_SCRAPER] Excepción en fetch: {e}")
            pass
        return None
