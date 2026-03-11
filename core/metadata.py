"""
metadata.py — Scraper de Metadatos de Juegos V1.0

Descarga información de cada juego (descripción, año, desarrollador, género)
usando la API pública de TheGamesDB y la guarda en caché local.
"""

import asyncio
import aiohttp
import json
import os
import re
from typing import Optional, Callable

# ── API ──────────────────────────────────────────────────────────────
# TheGamesDB ofrece una API pública. Usamos el endpoint de búsqueda
# que devuelve resultados básicos sin necesitar API key para lectura.
TGDB_SEARCH_URL = "https://api.thegamesdb.net/v1/Games/ByGameName"
TGDB_GENRES_URL = "https://api.thegamesdb.net/v1/Genres"

# API key pública de demostración (funciona con rate limit ~100/day/IP)
# El usuario puede proveer la suya en configuración futura.
TGDB_API_KEY = "legacy"  # Clave de acceso legacy sin registro

# Ruta de caché local
_METADATA_CACHE_PATH = os.path.join("data", "metadata.json")

# Caché en memoria (evita recargar el JSON en cada consulta)
_METADATA_MEM_CACHE: dict = {}
_CACHE_LOADED = False

# Mapeo de nombre de plataforma Libretro → ID de plataforma TGDB
LIBRETRO_TO_TGDB_PLATFORM = {
    "Nintendo - Nintendo Entertainment System":           7,
    "Nintendo - Super Nintendo Entertainment System":     6,
    "Nintendo - Game Boy":                                4,
    "Nintendo - Game Boy Color":                          41,
    "Nintendo - Game Boy Advance":                        5,
    "Nintendo - Nintendo 64":                             3,
    "Nintendo - GameCube":                                2,
    "Nintendo - Wii":                                     9,
    "Nintendo - Nintendo 3DS":                            4911,
    "Nintendo - Nintendo Switch":                         4971,
    "Sony - PlayStation":                                 10,
    "Sony - PlayStation 2":                               11,
    "Sony - PlayStation 3":                               12,
    "Sony - PlayStation Portable":                        13,
    "Sega - Mega Drive - Genesis":                        18,
    "Sega - Master System - Mark III":                    35,
    "Sega - Game Gear":                                   21,
    "Microsoft - Xbox":                                   14,
    "NEC - PC Engine - TurboGrafx 16":                   34,
}

# Caché de géneros (id → nombre)
_GENRES_CACHE: dict = {}


def _metadata_cache_path() -> str:
    return _METADATA_CACHE_PATH


def _cargar_cache() -> dict:
    """Carga el JSON de metadatos desde disco (solo una vez por sesión)."""
    global _METADATA_MEM_CACHE, _CACHE_LOADED
    if _CACHE_LOADED:
        return _METADATA_MEM_CACHE
    try:
        if os.path.exists(_metadata_cache_path()):
            with open(_metadata_cache_path(), "r", encoding="utf-8") as f:
                _METADATA_MEM_CACHE = json.load(f)
    except Exception as e:
        print(f"[METADATA] Error cargando caché: {e}")
        _METADATA_MEM_CACHE = {}
    _CACHE_LOADED = True
    return _METADATA_MEM_CACHE


def _guardar_cache(cache: dict):
    """Guarda el diccionario de metadatos en disco."""
    try:
        os.makedirs("data", exist_ok=True)
        with open(_metadata_cache_path(), "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[METADATA] Error guardando caché: {e}")


def obtener_metadata_local(ruta_rom: str) -> dict:
    """
    Consulta el caché local para los metadatos de un juego.
    Devuelve un dict con: description, year, developer, genre, rating
    O un dict vacío si no hay datos.
    """
    cache = _cargar_cache()
    return cache.get(ruta_rom, {})


def _normalizar_busqueda(nombre: str) -> str:
    """Limpia el nombre para la búsqueda en TGDB."""
    n = re.sub(r'[\(\[].*?[\)\]]', '', nombre)
    n = re.sub(r'[-–—_]', ' ', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n


async def _cargar_generos(session: aiohttp.ClientSession) -> dict:
    """Descarga y cachea el mapa géneros id→nombre de TGDB."""
    global _GENRES_CACHE
    if _GENRES_CACHE:
        return _GENRES_CACHE
    try:
        async with session.get(
            TGDB_GENRES_URL,
            params={"apikey": TGDB_API_KEY},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                generos = data.get("data", {}).get("genres", {})
                _GENRES_CACHE = {str(k): v.get("name", "") for k, v in generos.items()}
    except Exception as e:
        print(f"[METADATA] Error cargando géneros: {e}")
    return _GENRES_CACHE


async def obtener_metadata(
    session: aiohttp.ClientSession,
    nombre_juego: str,
    ruta_rom: str,
    libretro_platform: Optional[str] = None
) -> dict:
    """
    Busca metadatos de un juego en TheGamesDB.
    Devuelve dict con: description, year, developer, genre, rating
    """
    nombre_limpio = _normalizar_busqueda(nombre_juego)
    if not nombre_limpio:
        return {}

    # Construir parámetros de búsqueda
    params = {
        "apikey": TGDB_API_KEY,
        "name": nombre_limpio,
        "fields": "players,publishers,genres,overview,rating,release_date",
        "include": "boxart",
        "filter[platform]": LIBRETRO_TO_TGDB_PLATFORM.get(libretro_platform, "")
    }
    if not params["filter[platform]"]:
        del params["filter[platform]"]

    try:
        async with session.get(
            TGDB_SEARCH_URL,
            params=params,
            timeout=aiohttp.ClientTimeout(total=12)
        ) as resp:
            if resp.status != 200:
                print(f"[METADATA] HTTP {resp.status} para '{nombre_limpio}'")
                return {}

            data = await resp.json(content_type=None)
            games = data.get("data", {}).get("games", [])
            if not games:
                print(f"[METADATA] ~ Sin resultados: '{nombre_limpio}'")
                return {}

            # Tomar el primer resultado (mejor coincidencia)
            g = games[0]

            # Géneros (pueden ser lista de IDs)
            genre_ids = g.get("genres", []) or []
            genre_cache = await _cargar_generos(session)
            genres_str = ", ".join(
                genre_cache.get(str(gid), "") for gid in genre_ids if str(gid) in genre_cache
            ) if genre_cache else ""

            # Año desde fecha de lanzamiento
            release_date = g.get("release_date", "") or ""
            year = release_date[:4] if len(release_date) >= 4 else ""

            # Desarrollador (publishers viene de include)
            publishers_data = data.get("include", {}).get("publishers", {}).get("data", {})
            publisher_ids = g.get("publishers", []) or []
            developer = ""
            if publisher_ids and publishers_data:
                pid = str(publisher_ids[0])
                developer = publishers_data.get(pid, {}).get("name", "")

            result = {
                "description": (g.get("overview") or "").strip(),
                "year": year,
                "developer": developer,
                "genre": genres_str,
                "rating": (g.get("rating") or "").strip(),
            }
            print(f"[METADATA] ✓ '{nombre_limpio}' → {result.get('year','?')} | {developer}")
            return result

    except asyncio.TimeoutError:
        print(f"[METADATA] ⏱ Timeout para '{nombre_limpio}'")
        return {}
    except Exception as e:
        print(f"[METADATA] ✗ Error para '{nombre_limpio}': {e}")
        return {}


async def descargar_metadata_biblioteca(
    juegos: list,
    emu_map: dict,
    on_progress: Optional[Callable[[int, int, str], None]] = None
) -> dict:
    """
    Descarga masiva de metadatos para todos los juegos de la biblioteca.
    Respeta el caché: solo consulta la API si el juego no tiene datos.
    """
    from core.artwork import get_platform_for_rom

    cache = _cargar_cache()
    stats = {"ok": 0, "skip": 0, "fail": 0}
    total = len(juegos)
    _cache_dirty = False

    connector = aiohttp.TCPConnector(limit=5)
    # TGDB es sensible al rate limiting — usamos semáforo conservador
    semaforo = asyncio.Semaphore(2)

    async with aiohttp.ClientSession(connector=connector) as session:
        # Pre-cargar géneros una sola vez
        await _cargar_generos(session)

        async def _worker(idx, juego):
            nonlocal _cache_dirty
            async with semaforo:
                ruta_rom = juego.get("ruta", "")
                nombre = juego.get("nombre", "")
                emu_id = juego.get("id_emu", "")

                # Si ya está en caché, saltar
                if ruta_rom in cache:
                    stats["skip"] += 1
                    if on_progress: on_progress(idx + 1, total, nombre)
                    return

                # Resolver plataforma
                default_plat = emu_map.get(emu_id)
                platform = get_platform_for_rom(emu_id, ruta_rom, default_plat)

                meta = await obtener_metadata(session, nombre, ruta_rom, platform)

                if meta:
                    cache[ruta_rom] = meta
                    _cache_dirty = True
                    stats["ok"] += 1
                else:
                    # Guardar entrada vacía para no reintentar en cada sesión
                    cache[ruta_rom] = {}
                    _cache_dirty = True
                    stats["fail"] += 1

                if on_progress: on_progress(idx + 1, total, nombre)
                # Pequeña pausa para no saturar la API
                await asyncio.sleep(0.3)

        await asyncio.gather(*[_worker(i, j) for i, j in enumerate(juegos)])

    # Guardar caché una sola vez al terminar
    if _cache_dirty:
        _guardar_cache(cache)

    return stats
