import aiohttp
import urllib.parse
import os
from typing import Optional, Dict, Any
from core.scrapers.base import BaseScraper
from core.logic.scraper_engine import ScraperEngine
from core.scrapers.models import ScrapedData

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
        self.softname = "EmuManagerApp"

    async def fetch(self, session: aiohttp.ClientSession, query: str, **kwargs) -> Optional[ScrapedData]:
        # 🛡️ GUARD: Solo bloqueamos si el usuario no tiene cuenta SS básica
        if not self.user or not self.password:
            return None

        platform_id = kwargs.get("ss_platform_id")
        rom_file = kwargs.get("rom_file", query)
        
        # 🛡️ CABECERAS MINIMALISTAS (Evitar Error 431)
        headers = {
            "User-Agent": "EmuManager/0.1.20 (Scraping Engine; Windows)",
            "Accept": "application/json",
            "Cookie": "" # Forzar limpieza absoluta
        }
        
        base_params = {
            "devid": self.devid,
            "devpassword": self.devpassword,
            "softname": self.softname,
            "output": "json"
        }
        # Solo añadir credenciales de usuario si existen
        if self.user: base_params["ssid"] = str(self.user)
        if self.password: base_params["sspassword"] = str(self.password)
        
        if platform_id: base_params["systemeid"] = str(platform_id)

        print(f"[SCREEN_SCRAPER] Buscando: {query} (ID Sistema: {platform_id or '?'})")
        
        data = None
        try:
            # ETAPA 1: Búsqueda por ROM (Checksum o nombre exacto de archivo)
            params = base_params.copy()
            params.update({"romtype": "rom", "romnom": str(rom_file or query)})
            async with session.get(self.API_BASE, params=params, headers=headers, timeout=12) as resp:
                if resp.status == 200:
                    data = await resp.json()
                elif resp.status == 404:
                    # ETAPA 2: Búsqueda por Nombre de Juego Directo
                    print(f"[SCREEN_SCRAPER] 404 por ROM. Probando nombre: {query}")
                    params.update({"romtype": "nom", "romnom": str(query)})
                    async with session.get(self.API_BASE, params=params, headers=headers, timeout=12) as retry_resp:
                        if retry_resp.status == 200:
                            data = await retry_resp.json()
                        elif retry_resp.status == 404:
                            # ETAPA 3: Búsqueda Flexible
                            print(f"[SCREEN_SCRAPER] 404 por nombre. Iniciando búsqueda flexible...")
                            search_url = "https://www.screenscraper.fr/api2/jeuRecherche.php"
                            search_params = base_params.copy()
                            search_params["recherche"] = str(query)
                            async with session.get(search_url, params=search_params, headers=headers, timeout=12) as s_resp:
                                if s_resp.status == 200:
                                    s_data = await s_resp.json()
                                    jeux = s_data.get("response", {}).get("jeux", [])
                                    if jeux:
                                        print(f"[SCREEN_SCRAPER] {len(jeux)} resultados en búsqueda flexible.")
                                        cand_map = {}
                                        for j in jeux:
                                            jid = j.get("id")
                                            for n in j.get("noms", []):
                                                if n.get("nom"): cand_map[n.get("nom")] = jid
                                        
                                        best_name = ScraperEngine.find_best_match(query, list(cand_map.keys()))
                                        best_id = cand_map.get(best_name) if best_name else jeux[0].get("id")
                                        
                                        if best_id:
                                            print(f"[SCREEN_SCRAPER] Resolviendo ID: {best_id}")
                                            params.update({"romtype": "id", "romnom": str(best_id)})
                                            async with session.get(self.API_BASE, params=params, headers=headers, timeout=12) as f_resp:
                                                if f_resp.status == 200:
                                                    data = await f_resp.json()
                elif resp.status != 200:
                    print(f"[SCREEN_SCRAPER] Error HTTP {resp.status} para: {query}")

            if not data or data.get("response", {}).get("status") != "OK":
                return None

            jeu = data["response"].get("jeu", {})
            
            # --- PARSEO DE DATOS ---
            scraped = ScrapedData(source_name=self.name)
            scraped.title = jeu.get("noms", [{}])[0].get("nom", query)
            
            # Textos (Descripción)
            for t in jeu.get("textes", []):
                if t.get("langue") == "es":
                    scraped.description = t.get("text")
                    break
            if not scraped.description:
                for t in jeu.get("textes", []):
                    if t.get("langue") == "en":
                        scraped.description = t.get("text")
                        break

            # Metadatos básicos
            scraped.developer = jeu.get("developpeur", {}).get("nom", "")
            scraped.publisher = jeu.get("editeur", {}).get("nom", "")
            scraped.genre = jeu.get("genres", [{}])[0].get("nom", "")
            if jeu.get("dates"):
                d = jeu["dates"][0].get("date", "")
                scraped.release_date = d[:4] if d else None
            scraped.players = str(jeu.get("joueurs", "1"))
            
            # --- PARSEO DE MEDIAS (ARTE) ---
            medias = jeu.get("medias", [])
            raw_logs = []
            
            for m in medias:
                m_type = str(m.get("type", "")).lower()
                m_url = m.get("url", "")
                m_reg = str(m.get("region", "ss")).lower()
                if not m_url: continue

                raw_logs.append(f"{m_type}({m_reg})")

                # Boxart 2D (Prioridad: v > h > normal)
                if m_type in ("box-2d-v", "box-2d-h", "box-2d"):
                    if not scraped.boxart_2d: scraped.boxart_2d = m_url
                
                # Boxart 3D (Prioridad: v > h > normal)
                elif m_type in ("box-3d-v", "box-3d-h", "box-3d"):
                    if not scraped.boxart_3d: scraped.boxart_3d = m_url

                # Background / Logo / Manual
                elif "fanart" in m_type and not scraped.background:
                    scraped.background = m_url
                elif "logo" in m_type and not scraped.logo:
                    scraped.logo = m_url
                elif ("manuel" in m_type or "manual" in m_type) and not scraped.manual:
                    scraped.manual = m_url

            found_types = []
            if scraped.boxart_2d: found_types.append("2D")
            if scraped.boxart_3d: found_types.append("3D")
            
            print(f"[SCREEN_SCRAPER] Encontrado: {scraped.title} [{', '.join(found_types)}]")
            return scraped

        except Exception as e:
            print(f"[SCREEN_SCRAPER] Excepción en fetch para {query}: {e}")
            return None
