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
    # mesen
    ".nes":  "Nintendo - Nintendo Entertainment System",
    ".sfc":  "Nintendo - Super Nintendo Entertainment System",
    ".smc":  "Nintendo - Super Nintendo Entertainment System",
    # retroarch genérico
    ".gba":  "Nintendo - Game Boy Advance",
    ".gb":   "Nintendo - Game Boy",
    ".gbc":  "Nintendo - Game Boy Color",
    ".md":   "Sega - Mega Drive - Genesis",
    ".smd":  "Sega - Mega Drive - Genesis",
    ".gen":  "Sega - Mega Drive - Genesis",
    ".sms":  "Sega - Master System - Mark III",
    ".gg":   "Sega - Game Gear",
    ".pce":  "NEC - PC Engine - TurboGrafx 16",
    ".cue":  "Sony - PlayStation",
    ".bin":  "Sony - PlayStation",
    ".z64":  "Nintendo - Nintendo 64",
    ".n64":  "Nintendo - Nintendo 64",
    ".v64":  "Nintendo - Nintendo 64",
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
    """
    Limpia un nombre para compararlo (Fuzzy Matching).
    FIX: Preserva guiones y otros separadores válidos antes de eliminarlos,
    para evitar falsos negativos en títulos como "A Link to the Past".
    """
    n = nombre.replace("_", " ")
    # Eliminar etiquetas entre paréntesis/corchetes: (USA), [v1.1], etc.
    n = re.sub(r'[\(\[].*?[\)\]]', '', n)
    # Reemplazar guiones y puntos por espacios (en vez de eliminarlo)
    n = re.sub(r'[-–—.]', ' ', n)
    # Eliminar caracteres que no son letras, números o espacios
    n = re.sub(r'[^a-zA-Z0-9\s]', '', n)
    # Colapsar espacios múltiples
    return re.sub(r'\s+', ' ', n).strip().lower()


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
    Motor de busqueda fuzzy reescrito con uso completo de difflib:

    1. Coincidencia exacta tras normalizar (O(1) lookup)
    2. get_close_matches con cutoff 0.82 — rapido, alta precision
    3. Busqueda por subcadena: si el nombre buscado aparece DENTRO de algun titulo del indice
    4. SequenceMatcher.ratio() sobre todos los elementos si los pasos anteriores fallan,
       tomando el de mayor ratio siempre que supere 0.60. Esto aprovecha difflib al maximo
       en lugar de depender solo de get_close_matches.
    5. Coincidencia por palabras clave: si el nombre buscado tiene palabras significativas
       que aparecen en el titulo del indice.
    """
    norm_target = normalizar_nombre(nombre_buscado)
    if not norm_target:
        return None

    # Construir mapa normalizado -> original (una sola vez)
    mapa = {normalizar_nombre(orig): orig for orig in lista_disponibles}
    keys_norm = list(mapa.keys())

    # Nivel 1: Exacto
    if norm_target in mapa:
        return mapa[norm_target]

    # Nivel 2: get_close_matches rapido (cutoff alto — pocos falsos positivos)
    matches = difflib.get_close_matches(norm_target, keys_norm, n=3, cutoff=0.82)
    if matches:
        # Desempate: el de mayor ratio real
        best = max(matches, key=lambda m: difflib.SequenceMatcher(None, norm_target, m).ratio())
        return mapa[best]

    # Nivel 3: Subcadena — el nombre buscado aparece dentro del titulo del indice
    substr_hits = [k for k in keys_norm if norm_target in k or k in norm_target]
    if substr_hits:
        # Tomar el de mayor similitud entre los hits de subcadena
        best = max(substr_hits, key=lambda m: difflib.SequenceMatcher(None, norm_target, m).ratio())
        if difflib.SequenceMatcher(None, norm_target, best).ratio() >= 0.55:
            return mapa[best]

    # Nivel 4: SequenceMatcher exhaustivo (cutoff 0.62)
    # get_close_matches usa internamente SequenceMatcher pero con heuristicas que
    # pueden descartar buenos matches. Aqui calculamos el ratio directamente.
    best_ratio = 0.0
    best_key = None
    for k in keys_norm:
        ratio = difflib.SequenceMatcher(None, norm_target, k).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_key = k

    if best_ratio >= 0.62 and best_key:
        return mapa[best_key]

    # Nivel 5: Palabras clave (al menos 2 palabras significativas coinciden)
    stop_words = {"the", "a", "an", "of", "and", "in", "no", "de", "el", "la", "los"}
    target_words = [w for w in norm_target.split() if w not in stop_words and len(w) > 2]
    if len(target_words) >= 2:
        scored = []
        for k in keys_norm:
            k_words = set(k.split())
            hits = sum(1 for w in target_words if w in k_words)
            if hits >= 2:
                scored.append((hits, k))
        if scored:
            scored.sort(reverse=True)
            return mapa[scored[0][1]]

    return None


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
    for intento in range(retries + 1):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
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
    Lógica principal de descarga para un juego individual.
    """
    caratula_path = obtener_ruta_caratula(ruta_rom)
    if os.path.exists(caratula_path): return True

    lista_nombres = await obtener_indice_plataforma(session, platform)
    if not lista_nombres:
        return False

    candidato_principal = os.path.splitext(os.path.basename(ruta_rom))[0]

    mejor_match = encontrar_mejor_coincidencia(candidato_principal, lista_nombres)
    if not mejor_match:
        mejor_match = encontrar_mejor_coincidencia(nombre_juego, lista_nombres)

    if mejor_match:
        url = f"{LIBRETRO_CDN}/{urllib.parse.quote(platform)}/{THUMBNAIL_TYPE}/{urllib.parse.quote(mejor_match + '.png')}"
        ok = await _descargar_archivo(session, url, caratula_path)
        if ok:
            ratio = int(difflib.SequenceMatcher(
                None,
                normalizar_nombre(candidato_principal),
                normalizar_nombre(mejor_match)
            ).ratio() * 100)
            print(f"[ARTWORK] ✓ Match al {ratio}%: '{candidato_principal}' → '{mejor_match}'")
            return True
    else:
        print(f"[ARTWORK] ~ Sin coincidencia para '{candidato_principal}' en '{platform}'")
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

                if tiene_caratula(ruta_rom):
                    stats["skip"] += 1
                    if on_progress: on_progress(idx + 1, total, nombre)
                    return

                ok = await descargar_caratula(session, platform, nombre, ruta_rom)
                stats["ok" if ok else "fail"] += 1

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
