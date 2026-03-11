"""
artwork.py — Motor de Carátulas V2 (Fuzzy Match Index-Based)
Version: 0.2.0

Este módulo se encarga de:
1. Obtener la lista de carátulas disponibles en el servidor de Libretro.
2. Comparar el nombre de la ROM con la lista oficial usando algoritmos de similitud.
3. Descargar y guardar las imágenes localmente.
"""

import asyncio
import aiohttp
import os
import re
import urllib.parse
import difflib
from urllib.parse import unquote
from bs4 import BeautifulSoup
from typing import Optional, Callable, List
from .normalization import normalize_title
from .scraper_engine import ScraperEngine
import core.metadata as metadata

# URL BASE del CDN de Libretro Thumbnails
LIBRETRO_CDN = "https://thumbnails.libretro.com"
THUMBNAIL_TYPE = "Named_Boxarts"

# Directorios para recursos del sistema (Propios del proyecto)
PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_MEDIA_DIR = os.path.join(PROJECT_ROOT_DIR, "media")

# Directorios para recursos descargados (Configurables por el usuario)
USER_MEDIA_PATH = "media"  # Por defecto local, pero cambia dinámicamente

def set_base_media_path(new_path: str):
    """Actualiza la ruta base para los recursos multimedia descargables."""
    global USER_MEDIA_PATH
    USER_MEDIA_PATH = new_path

def get_consoles_bg_dir():
    """Donde se guardan los fondos de consola descargados."""
    return os.path.join(USER_MEDIA_PATH, "fondos_consolas")

def get_system_consoles_dir():
    """Iconos de consolas propios del proyecto."""
    return os.path.join(SYSTEM_MEDIA_DIR, "consolas")

def get_system_emulators_dir():
    """Iconos de emuladores propios del proyecto."""
    return os.path.join(SYSTEM_MEDIA_DIR, "emuladores")

# Memoria caché para evitar peticiones HTTP repetitivas al mismo índice en una sesión
_INDEX_CACHE = {}

# URLs base para descargar fondos (Ecosistema Batocera/EmulationStation - Carbon Theme)
CARBON_BG_BASE_URL = "https://raw.githubusercontent.com/fabricecaruso/es-theme-carbon/master/art/background/"

FONDO_CONSOLA_MAPPING = {
    "retroarch": "retrobat.jpg",
    "dolphin": "gc.jpg",
    "pcsx2": "ps2.jpg",
    "rpcs3": "ps3.jpg",
    "ppsspp": "psp.jpg",
    "duckstation": "psx.jpg",
    "xemu": "xbox.jpg",
    "mgba": "gba.jpg",
    "rmg": "n64.jpg",
    "mesen": "nes.jpg",
    "snes9x": "snes.jpg",
    "lime3ds": "3ds.jpg",
    "switch": "switch.jpg"
}

# ──────────────────────────────────────────────────────────────
# FIX #1: Plataformas por extensión para emuladores multi-sistema
# ──────────────────────────────────────────────────────────────
# Para emuladores que cubren varias consolas (mesen, retroarch),
# usamos la extensión del archivo para deducir la plataforma correcta.
EXTENSION_PLATFORM_MAP = {
    # Nintendo
    ".nes":  "Nintendo - Nintendo Entertainment System",
    ".sfc":  "Nintendo - Super Nintendo Entertainment System",
    ".smc":  "Nintendo - Super Nintendo Entertainment System",
    ".gba":  "Nintendo - Game Boy Advance",
    ".gb":   "Nintendo - Game Boy",
    ".gbc":  "Nintendo - Game Boy Color",
    ".n64":  "Nintendo - Nintendo 64",
    ".z64":  "Nintendo - Nintendo 64",
    ".v64":  "Nintendo - Nintendo 64",
    ".wbfs": "Nintendo - Wii",
    ".rvz":  "Nintendo - GameCube",
    # Sony
    ".cue":  "Sony - PlayStation",
    ".bin":  "Sony - PlayStation",
    ".chd":  "Sony - PlayStation 2", 
    # Sega
    ".md":   "Sega - Mega Drive - Genesis",
    ".smd":  "Sega - Mega Drive - Genesis",
    ".gen":  "Sega - Mega Drive - Genesis",
    ".sms":  "Sega - Master System - Mark III",
    ".gg":   "Sega - Game Gear",
    ".ms":   "Sega - Master System - Mark III",
    # NEC
    ".pce":  "NEC - PC Engine - TurboGrafx 16",
}

def get_platform_for_rom(emu_id: str, ruta_rom: str, default_platform: Optional[str]) -> Optional[str]:
    """
    FIX #2: Devuelve la plataforma correcta para un ROM dado.
    Para emuladores multi-sistema (mesen, retroarch), usa la extensión del archivo.
    Para el resto, devuelve el platform estándar del emulador.
    """
    if default_platform is not None:
        # La mayoría de emuladores ya tienen platform correcto
        # Pero mesen cubre NES+SNES — su platform por defecto es solo NES
        if emu_id == "mesen":
            ext = os.path.splitext(ruta_rom)[1].lower()
            return EXTENSION_PLATFORM_MAP.get(ext, default_platform)
        return default_platform

    # FIX #2b: Emuladores con platform = None (retroarch, switch, rpcs3)
    if emu_id in ("retroarch",):
        ext = os.path.splitext(ruta_rom)[1].lower()
        guessed = EXTENSION_PLATFORM_MAP.get(ext)
        if guessed:
            return guessed
        print(f"[ARTWORK] ⚠ Retroarch: extensión '{ext}' sin plataforma conocida. Saltando.")
        return None

    print(f"[ARTWORK] ⚠ Emulador '{emu_id}' sin plataforma Libretro asignada. Saltando.")
    return None


# ──────────────────────────────────────────────────────────────
# FIX #3: normalizar_nombre mejorado
# ──────────────────────────────────────────────────────────────
def normalizar_nombre(nombre: str) -> str:
    """Delegates to unified normalization utility."""
    return normalize_title(nombre)


async def obtener_indice_plataforma(session: aiohttp.ClientSession, platform: str) -> list:
    """
    Descarga el índice HTML de una plataforma de Libretro y extrae los nombres de archivos .png
    """
    if platform in _INDEX_CACHE:
        return _INDEX_CACHE[platform]

    platform_url = f"{LIBRETRO_CDN}/{urllib.parse.quote(platform)}/{THUMBNAIL_TYPE}/"
    nombres_disponibles = []

    try:
        async with session.get(platform_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                links = soup.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    if href.endswith('.png'):
                        nombre_crudo = unquote(href[:-4])
                        nombres_disponibles.append(nombre_crudo)

                print(f"[ARTWORK] Índice cargado para '{platform}': {len(nombres_disponibles)} portadas.")
                _INDEX_CACHE[platform] = nombres_disponibles
            else:
                print(f"[ARTWORK] ✗ Error HTTP {resp.status} al cargar índice de '{platform}'.")
                _INDEX_CACHE[platform] = []
    except Exception as e:
        print(f"[ARTWORK] ✗ Excepción obteniendo índice de '{platform}': {e}")
        _INDEX_CACHE[platform] = []

    return _INDEX_CACHE[platform]


def encontrar_mejor_coincidencia(nombre_buscado: str, lista_disponibles: list) -> Optional[str]:
    """
    Motor de busqueda fuzzy unificado via ScraperEngine.
    """
    return ScraperEngine.find_best_match(nombre_buscado, lista_disponibles)


def obtener_ruta_caratula(ruta_rom: str) -> str:
    """Devuelve la ruta absoluta donde DEBERÍA estar guardada la carátula de un juego."""
    rom_dir = os.path.dirname(ruta_rom)
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(rom_dir, "media", f"{game_name}.png")

def tiene_caratula(ruta_rom: str) -> bool:
    """Verifica la existencia física del archivo de carátula."""
    return os.path.exists(obtener_ruta_caratula(ruta_rom))

def obtener_ruta_logo_consola(id_emu: str, flet_path: bool = False) -> str:
    if flet_path: return f"/consolas/{id_emu}.png"
    return os.path.abspath(os.path.join(get_system_consoles_dir(), f"{id_emu}.png"))

def obtener_ruta_fondo_consola(id_emu: str) -> str:
    return os.path.abspath(os.path.join(get_consoles_bg_dir(), f"{id_emu}_bg.jpg"))

def obtener_ruta_logo_emulador(id_emu: str, flet_path: bool = False) -> str:
    if flet_path: return f"/emuladores/{id_emu}.png"
    return os.path.abspath(os.path.join(get_system_emulators_dir(), f"{id_emu}.png"))


# ──────────────────────────────────────────────────────────────
# FIX #4: Retry logic en descarga de archivos
# ──────────────────────────────────────────────────────────────
async def _descargar_archivo(session: aiohttp.ClientSession, url: str, ruta_destino: str,
                              retries: int = 2) -> bool:
    """Descarga binaria con reintentos automáticos ante fallos de red."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for intento in range(retries + 1):
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    contenido = await resp.read()
                    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                    with open(ruta_destino, "wb") as f:
                        f.write(contenido)
                    return True
                else:
                    print(f"[ARTWORK] ✗ HTTP {resp.status} para {url}")
                    return False
        except asyncio.TimeoutError:
            if intento < retries:
                print(f"[ARTWORK] ⏱ Timeout ({intento+1}/{retries}), reintentando...")
                await asyncio.sleep(1)
        except Exception as e:
            print(f"[ARTWORK] ✗ Error descargando '{url}': {e}")
            if intento < retries:
                await asyncio.sleep(1)
    return False


async def descargar_caratula(session: aiohttp.ClientSession, platform: str, nombre_juego: str,
                             ruta_rom: str) -> bool:
    """
    Descarga la carátula de un juego con lógica de múltiples fuentes.
    1. Intenta Libretro CDN (Alta calidad).
    2. Intenta URL de Boxart de Metadata (TGDB) si está disponible.
    """
    caratula_path = obtener_ruta_caratula(ruta_rom)
    lista_nombres = await obtener_indice_plataforma(session, platform)
    
    candidato_principal = os.path.splitext(os.path.basename(ruta_rom))[0]
    
    # --- FUENTE 1: Libretro CDN ---
    mejor_match = encontrar_mejor_coincidencia(candidato_principal, lista_nombres)
    if not mejor_match:
        mejor_match = encontrar_mejor_coincidencia(nombre_juego, lista_nombres)

    if mejor_match:
        url = f"{LIBRETRO_CDN}/{urllib.parse.quote(platform)}/{THUMBNAIL_TYPE}/{urllib.parse.quote(mejor_match + '.png')}"
        ok = await _descargar_archivo(session, url, caratula_path)
        if ok:
            ratio = int(difflib.SequenceMatcher(None, normalize_title(candidato_principal), normalize_title(mejor_match)).ratio() * 100)
            # print(f"[ARTWORK] ✓ Libretro match {ratio}%: '{mejor_match}'")
            return True

    # --- FUENTE 2: Metadata / TGDB (Fallback) ---
    meta = metadata.obtener_metadata_local(ruta_rom)
    tgdb_url = meta.get("boxart_url")
    if tgdb_url:
        # print(f"[ARTWORK] ~ Intentando fallback TGDB para '{candidato_principal}'...")
        ok = await _descargar_archivo(session, tgdb_url, caratula_path)
        if ok:
            print(f"[ARTWORK] ✓ TGDB match para '{candidato_principal}'")
            return True

    return False


async def descargar_recursos_estaticos():
    """Asegura que el árbol de carpetas de media de usuario exista."""
    os.makedirs(get_consoles_bg_dir(), exist_ok=True)
    os.makedirs(get_system_consoles_dir(), exist_ok=True)
    os.makedirs(get_system_emulators_dir(), exist_ok=True)




async def descargar_caratulas_biblioteca(
    juegos: list, emu_map: dict, ruta_roms_base: str = "",
    on_progress: Optional[Callable[[int, int, str], None]] = None
) -> dict:
    """
    Descarga masiva de carátulas con concurrencia controlada.
    FIX: Usa get_platform_for_rom() para resolver plataformas multi-sistema y nulas.
    """
    stats = {"ok": 0, "skip": 0, "fail": 0}
    total = len(juegos)

    # Calcular plataformas reales necesarias (con resolución por extensión)
    plataformas_necesarias = set()
    for j in juegos:
        emu_id = j.get("id_emu", "")
        default_plat = emu_map.get(emu_id)
        real_plat = get_platform_for_rom(emu_id, j.get("ruta", ""), default_plat)
        if real_plat:
            plataformas_necesarias.add(real_plat)

    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Pre-cargar índices de todas las consolas necesarias
        print(f"[ARTWORK] Preparando índices para {len(plataformas_necesarias)} plataformas...")
        await asyncio.gather(*[obtener_indice_plataforma(session, p) for p in plataformas_necesarias])

        semaforo = asyncio.Semaphore(5)

        async def _worker(idx, juego):
            async with semaforo:
                emu_id = juego.get("id_emu", "")
                ruta_rom = juego.get("ruta", "")
                nombre = juego.get("nombre", "")

                # FIX: Resolver la plataforma correcta por emulador+extensión
                default_plat = emu_map.get(emu_id)
                platform = get_platform_for_rom(emu_id, ruta_rom, default_plat)

                if not platform:
                    stats["skip"] += 1
                    if on_progress: on_progress(idx + 1, total, nombre)
                    return

                # Intentar descargar siempre para asegurar "carátulas correctas" como pidió el usuario
                # (aunque ya exista, si encontramos un mejor match o fuente, se actualizará)
                ok = await descargar_caratula(session, platform, nombre, ruta_rom)
                if ok:
                    stats["ok"] += 1
                else:
                    if tiene_caratula(ruta_rom):
                        stats["skip"] += 1
                    else:
                        stats["fail"] += 1

                if on_progress: on_progress(idx + 1, total, nombre)

        await asyncio.gather(*[_worker(i, j) for i, j in enumerate(juegos)])

    return stats


async def descargar_fondos_consolas(
    on_progress: Optional[Callable[[int, int, str], None]] = None,
    emus_a_descargar: Optional[List[str]] = None
) -> dict:
    """Descarga concurrente de fondos de pantalla para el carrusel de consolas."""
    import core.constants as constants
    stats = {"ok": 0, "skip": 0, "fail": 0}

    await descargar_recursos_estaticos()

    connector = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        semaforo = asyncio.Semaphore(3)

        emus_to_download = [emu for emu in constants.AVAILABLE_EMULATORS if emu["id"] in FONDO_CONSOLA_MAPPING]
        if emus_a_descargar is not None:
            emus_to_download = [emu for emu in emus_to_download if emu["id"] in emus_a_descargar]

        total = len(emus_to_download)
        if total == 0:
            return stats

        async def _worker(idx, emu):
            async with semaforo:
                id_emu = emu["id"]
                filename = FONDO_CONSOLA_MAPPING[id_emu]
                url = f"{CARBON_BG_BASE_URL}{filename}"
                ruta_destino = obtener_ruta_fondo_consola(id_emu)

                if os.path.exists(ruta_destino):
                    stats["skip"] += 1
                    if on_progress: on_progress(idx + 1, total, f"Fondo {emu['name']}")
                    return

                headers = {'User-Agent': 'Mozilla/5.0'}
                try:
                    async with session.get(url, headers=headers,
                                           timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        if resp.status == 200:
                            contenido = await resp.read()
                            os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                            with open(ruta_destino, "wb") as f:
                                f.write(contenido)
                            stats["ok"] += 1
                            print(f"[ARTWORK] ✓ Fondo descargado: {emu['name']}")
                        else:
                            print(f"[ARTWORK] ✗ HTTP {resp.status} para fondo de {emu['name']}")
                            stats["fail"] += 1
                except Exception as e:
                    print(f"[ARTWORK] ✗ Error descargando fondo de {emu['name']}: {e}")
                    stats["fail"] += 1

                if on_progress: on_progress(idx + 1, total, f"Fondo {emu['name']}")

        await asyncio.gather(*[_worker(i, e) for i, e in enumerate(emus_to_download)])

    return stats
