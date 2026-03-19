"""
metadata.py — Motor de metadatos (Hub de Scrapers).

Este módulo coordina la obtención de información descriptiva de los juegos
(título, descripción, desarrollador, año, etc.) consultando múltiples 
fuentes externas de forma secuencial y manteniendo una caché local.
"""

import asyncio
import aiohttp
import os
import json
from typing import Optional, Dict, Any, List, Callable

from .scrapers.metadata.wikipedia import WikipediaScraper
from .scrapers.metadata.rawg import RAWGScraper
from .scrapers.metadata.tgdb import TGDBScraper
from .scrapers.metadata.screenscraper import ScreenScraperScraper
from .security import get_secret
from . import config

def obtener_metadata_local(ruta_rom: str) -> dict:
    """
    Obtiene los metadatos almacenados en la caché local para un juego específico.

    Args:
        ruta_rom (str): Ruta absoluta del archivo ROM.

    Returns:
        dict: Diccionario con los metadatos o vacío si no existe.
    """
    if not os.path.exists(config.METADATA_FILE):
        return {}
    try:
        # Normalizar para buscar en el JSON
        norm_ruta = config.normalize_path(ruta_rom)
        with open(config.METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get(norm_ruta, {})
    except:
        return {}

def guardar_metadata_local(ruta_rom: str, meta: dict):
    """
    Persiste o actualiza los metadatos de un juego en la caché local.

    Args:
        ruta_rom (str): Ruta absoluta del juego.
        meta (dict): Diccionario con la nueva información a guardar.
    """
    cache = {}
    if os.path.exists(config.METADATA_FILE):
        try:
            with open(config.METADATA_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except:
            pass
    
    # Normalizar ruta antes de guardar como clave
    norm_ruta = config.normalize_path(ruta_rom)
    cache[norm_ruta] = meta
    
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(config.METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

async def descargar_metadata_biblioteca(juegos: list, emu_map: dict, on_progress: Optional[Callable] = None) -> dict:
    """
    Proceso masivo de descarga de metadatos para una lista de juegos.
    Consulta proveedores activos según la configuración del usuario.

    Args:
        juegos (list): Lista de juegos (objetos Juego o dicts de library.json).
        emu_map (dict): Mapa de emuladores para obtener IDs específicos (ej: screenscraper_id).
        on_progress (callable, optional): Callback para reportar el progreso (actual, total, nombre).

    Returns:
        dict: Estadísticas del proceso (ok, skip, fail).
    """
    stats = {"ok": 0, "skip": 0, "fail": 0}
    total = len(juegos)
    
    # Cargar caché para evitar descargas duplicadas
    cache = {}
    if os.path.exists(config.METADATA_FILE):
        try:
            with open(config.METADATA_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except:
            pass

    # --- Inicialización de Proveedores (Solo si están activados) ---
    configs = get_providers_config()
    
    # 1. Wikipedia (Sin API Key, texto básico)
    wiki_cfg = next((c for c in configs if c["id"] == "wikipedia"), {"enabled": True})
    wiki = WikipediaScraper() if wiki_cfg.get("enabled") else None
    
    # 2. RAWG (Requiere API Key)
    rawg_cfg = next((c for c in configs if c["id"] == "rawg"), None)
    rawg_api_key = rawg_cfg["api_key"] if rawg_cfg and rawg_cfg.get("enabled") else None
    rawg = RAWGScraper(rawg_api_key) if rawg_api_key else None

    # 3. ScreenScraper (Requiere cuenta de usuario)
    ss_cfg = next((c for c in configs if c["id"] == "screenscraper"), None)
    ss_user = ss_cfg.get("user") if ss_cfg and ss_cfg.get("enabled") else None
    ss_pass = ss_cfg.get("password") if ss_cfg and ss_cfg.get("enabled") else None
    screenscraper = ScreenScraperScraper(ss_user, ss_pass) if (ss_user and ss_pass) else None

    headers = {
        "User-Agent": f"EmuManager/1.0 ({config.REPO_URL})"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        # Limitamos la concurrencia para evitar bloqueos por parte de las APIs
        semaphore = asyncio.Semaphore(3)
        
        async def _worker(idx, juego):
            async with semaphore:
                ruta = juego.get("ruta", "")
                nombre = juego.get("nombre", "")
                
                # Omitir si ya tiene descripción en caché
                if ruta in cache and cache[ruta].get("description"):
                    stats["skip"] += 1
                else:
                    res = None
                    # Intento secuencial por prioridad (ScreenScraper -> Wikipedia -> RAWG)
                    if screenscraper:
                        emu_id = juego.get("id_emu", "")
                        emu_info = emu_map.get(emu_id, {})
                        ss_id = emu_info.get("screenscraper_id")
                        res = await screenscraper.fetch(session, nombre, ss_platform_id=ss_id, rom_file=os.path.basename(ruta))

                    if not res and wiki:
                        print(f"[METADATA] Intentando fallback con Wikipedia para {nombre}")
                        res = await wiki.fetch(session, nombre)
                    
                    if not res and rawg:
                        print(f"[METADATA] Intentando fallback con RAWG para {nombre}")
                        res = await rawg.fetch(session, nombre)

                    if res:
                        print(f"[METADATA] ¡Éxito! Información encontrada desde {res.get('source', 'desconocido')}")
                        cache[ruta] = res
                        stats["ok"] += 1
                    else:
                        # Guardar objeto vacío para no re-intentar fallidos en la misma sesión
                        cache[ruta] = cache.get(ruta, {})
                        stats["fail"] += 1
                
                if on_progress:
                    on_progress(idx + 1, total, nombre)
                await asyncio.sleep(0.02)

        await asyncio.gather(*[_worker(i, j) for i, j in enumerate(juegos)])

    # Persistencia de los nuevos datos
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        # Normalizar todas las claves antes de guardar el cache masivo
        norm_cache = {config.normalize_path(k): v for k, v in cache.items()}
        with open(config.METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(norm_cache, f, ensure_ascii=False, indent=2)
    except:
        pass
    
    return stats

def get_providers_config() -> List[Dict]:
    """
    Obtiene la lista de proveedores de metadatos y arte configurados.
    Mezcla los valores por defecto con la configuración guardada y los secretos.

    Returns:
        List[Dict]: Lista de diccionarios con el estado y credenciales de cada scraper.
    """
    path = os.path.join(config.DATA_DIR, "scrapers_config.json")
    default = [
        {"id": "screenscraper", "name": "ScreenScraper", "enabled": True, "type": "metadata", "priority": 0, "user": "", "password": ""},
        {"id": "libretro", "name": "Libretro CDN", "enabled": True, "type": "artwork", "priority": 1},
        {"id": "steamgriddb", "name": "SteamGridDB", "enabled": True, "type": "artwork", "priority": 2, "api_key": ""},
        {"id": "wikipedia", "name": "Wikipedia", "enabled": True, "type": "metadata", "priority": 3},
        {"id": "tgdb", "name": "TheGamesDB", "enabled": True, "type": "metadata", "priority": 4, "api_key": ""},
        {"id": "rawg", "name": "RAWG.io", "enabled": True, "type": "metadata", "priority": 5, "api_key": ""},
    ]
    
    # 1. Cargar preferencias del usuario (Activado/Desactivado, Prioridad)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, list):
                    for d in default:
                        s = next((x for x in saved if x.get("id") == d["id"]), None)
                        if s:
                            for field in ["enabled", "priority"]:
                                if field in s:
                                    d[field] = s[field]
        except:
            pass
    
    # 2. Cargar credenciales desde el sistema de secretos
    for d in default:
        is_conf = True
        for field in ["api_key", "user", "password"]:
            if field in d:
                val = get_secret(d["id"], field)
                if val:
                    d[field] = val
                else:
                    is_conf = False
        d["is_configured"] = is_conf

    return default
