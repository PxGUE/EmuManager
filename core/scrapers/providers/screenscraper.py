import aiohttp
import urllib.parse
import os
from typing import Optional, Dict, Any
from core.scrapers.base import BaseScraper
from core.logic.scraper_engine import ScraperEngine

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
        # 🛡️ GUARD: No intentamos nada si faltan credenciales críticas
        user = str(self.user or "")
        pwd = str(self.password or "")
        dev = str(self.devid or "")
        if not user or not pwd or not dev or dev == "EMU_MANAGER_DEV":
            return None

        # ScreenScraper is very platform-sensitive
        platform_id = kwargs.get("ss_platform_id")
        
        rom_file = kwargs.get("rom_file", query)
        params = {
            "devid": str(self.devid or ""),
            "devpassword": str(self.devpassword or ""),
            "softname": str(self.softname or ""),
            "output": "json",
            "romtype": "rom",
            "romnom": str(rom_file or query or ""),
            "ssid": str(self.user or ""),
            "sspassword": str(self.password or "")
        }
        
        # ScreenScraper is very system-sensitive.
        if platform_id:
            params["systemeid"] = str(platform_id)

        try:
            # 🛡️ LIMPIEZA TOTAL: Evitar Error 431 y TypeErrors
            params = {k: str(v) if v is not None else "" for k, v in params.items()}
            headers = {"Connection": "close", "Cache-Control": "no-cache"}
            
            print(f"[SCREEN_SCRAPER] Buscando: {query} (ID Sistema: {platform_id or '?'})")
            
            data = None
            try:
                async with session.get(self.API_BASE, params=params, headers=headers, timeout=12) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                    elif resp.status == 404:
                        print(f"[SCREEN_SCRAPER] 404 No encontrado por ROM. Probando nombre: {query}")
                        # FALLBACK 1: Por nombre de juego directo
                        params["romtype"] = "nom"
                        params["romnom"] = str(query or "")
                        async with session.get(self.API_BASE, params=params, headers=headers, timeout=12) as retry_resp:
                            if retry_resp.status == 200:
                                data = await retry_resp.json()
                            elif retry_resp.status == 404:
                                print(f"[SCREEN_SCRAPER] 404 No encontrado por nombre. Probando búsqueda flexible...")
                                # FALLBACK 2: Búsqueda flexible
                                search_url = "https://www.screenscraper.fr/api2/jeuRecherche.php"
                                search_params = {
                                    "devid": params["devid"], "devpassword": params["devpassword"],
                                    "softname": params["softname"], "output": "json",
                                    "recherche": str(query or ""), "ssid": params["ssid"], "sspassword": params["sspassword"]
                                }
                                if platform_id: search_params["systemeid"] = str(platform_id)
                                
                                async with session.get(search_url, params=search_params, headers=headers, timeout=12) as search_resp:
                                    if search_resp.status == 200:
                                        search_data = await search_resp.json()
                                        results = search_data.get("response", {}).get("jeux", [])
                                        if results:
                                            print(f"[SCREEN_SCRAPER] {len(results)} Resultados en búsqueda flexible.")
                                            candidates_map = {} 
                                            for r in results:
                                                if not isinstance(r, dict): continue
                                                game_id = r.get("id")
                                                for nm in r.get("noms", []):
                                                    n_txt = nm.get("nom")
                                                    if n_txt: candidates_map[n_txt] = game_id
                                            
                                            best_match_name = ScraperEngine.find_best_match(query, list(candidates_map.keys()))
                                            best_id = candidates_map.get(best_match_name) if best_match_name else results[0].get("id")
                                            
                                            if best_id:
                                                print(f"[SCREEN_SCRAPER] Obteniendo detalles ID: {best_id}")
                                                info_params = params.copy()
                                                info_params["romtype"] = "id"
                                                info_params["romnom"] = str(best_id)
                                                async with session.get(self.API_BASE, params=info_params, headers=headers, timeout=12) as final_resp:
                                                    if final_resp.status == 200:
                                                        data = await final_resp.json()
                                                    else:
                                                        print(f"[SCREEN_SCRAPER] Error detalles ID {best_id} (Status {final_resp.status})")
                                    else:
                                        print(f"[SCREEN_SCRAPER] Error búsqueda flexible (Status {search_resp.status})")
                            else:
                                if retry_resp.status != 404:
                                    print(f"[SCREEN_SCRAPER] Error nombre {query} (Status {retry_resp.status})")
                    else:
                        print(f"[SCREEN_SCRAPER] Error ROM {query} (Status {resp.status})")
            except Exception as e_inner:
                print(f"[SCREEN_SCRAPER] Error en petición HTTP: {e_inner}")
                return None

            if not data:
                return None

            response = data.get("response", {})
            status = response.get("status")
            
            if status != "OK":
                err = response.get("errortext", status)
                print(f"[SCREEN_SCRAPER] Respuesta no OK: {err}")
                return None
                
            jeu = response.get("jeu", {})
            game_name_found = jeu.get("noms", [{}])[0].get("nom", "Desconocido")
            print(f"[SCREEN_SCRAPER] Juego encontrado: {game_name_found}")
            
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
            
            found_media_summary = []
            raw_media_logs = []
            
            for m in medias:
                m_type_orig = str(m.get("type", ""))
                m_type = m_type_orig.lower()
                m_region = str(m.get("region", "ss")).lower()
                m_url = m.get("url", "")
                
                if m_url:
                    raw_media_logs.append(f"{m_type_orig} ({m_region})")
                    
                    # Carátula 2D (Priorizamos box-2D-v para consolas verticales/handhelds)
                    if not boxart_url:
                        if m_type in ("box-2d", "box-2d-v", "box-2d-h"):
                            boxart_url = m_url
                            found_media_summary.append("2D")
                    
                    # Carátula 3D (Priorizamos box-3D-v que es el estándar GBA/Handheld en SS)
                    if not boxart_3d_url:
                        if m_type in ("box-3d", "box-3d-v", "box-3d-h"):
                            boxart_3d_url = m_url
                            found_media_summary.append("3D")

                    # Assets comunes
                    if "fanart" in m_type and not background_url:
                        background_url = m_url
                        found_media_summary.append("Fanart")
                    elif "logo" in m_type and not logo_url:
                        logo_url = m_url
                        found_media_summary.append("Logo")
                    elif ("manuel" in m_type or "manual" in m_type) and not manual_url:
                        manual_url = m_url
                        found_media_summary.append("Manual")

            if raw_media_logs:
                print(f"[SCREEN_SCRAPER] API Medias: {', '.join(raw_media_logs[:8])}{'...' if len(raw_media_logs) > 8 else ''}")
            
            if found_media_summary:
                print(f"[SCREEN_SCRAPER] Seleccionados: {', '.join(set(found_media_summary))}")
            else:
                print(f"[SCREEN_SCRAPER] No se encontraron medios compatibles en la respuesta de la API.")

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
