"""
artwork.py — Descargador de carátulas usando el CDN de Libretro Thumbnails.

CDN Base: https://thumbnails.libretro.com/{platform}/Named_Boxarts/{game}.png
No requiere API key ni cuenta de usuario.

Estrategia de matching aproximado (agresiva):
1. Nombre normalizado (underscores → espacios, espacios dobles → uno)
2. Sin tags regionales (USA), (Europe), (Rev X), etc.
3. Solo la parte base antes del primer paréntesis o corchete
4. Primera palabra significativa + segunda palabra (para franquicias como Pokemon)
5. Solo la primera palabra (último recurso)
"""

import asyncio
import aiohttp
import os
import re
import urllib.parse
from typing import Optional, Callable

LIBRETRO_CDN = "https://thumbnails.libretro.com"
THUMBNAIL_TYPE = "Named_Boxarts"

# Tags regionales y de versión a eliminar
_REGION_TAGS = re.compile(
    r'\s*[\(\[](USA|Europe|Japan|World|En|Fr|De|Es|It|Pt|'
    r'Rev \w+|Rev\w+|v\d[\d.]*|Beta|Demo|Proto|Sample|'
    r'En,\w+|[A-Z]{2}(?:,[A-Z]{2})+)[)\]]\s*',
    re.IGNORECASE
)

# Caracteres inválidos para Libretro CDN (El ampersand & es válido en Libretro)
_INVALID_CHARS = re.compile(r'[*/:<>\\|]')

# Carpetas de medios del proyecto (El usuario coloca aquí sus imágenes manualmente)
PROJECT_MEDIA = "media"
CONSOLES_DIR = os.path.join(PROJECT_MEDIA, "consolas")
EMULATORS_DIR = os.path.join(PROJECT_MEDIA, "emuladores")


def _normalizar_nombre(nombre: str) -> str:
    """
    Normalización agresiva del nombre del ROM:
    - Reemplaza underscores por espacios
    - Colapsa espacios múltiples
    - Elimina caracteres inválidos de Libretro
    - Quita el punto final si lo hay
    """
    nombre = nombre.replace("_", " ")
    nombre = _INVALID_CHARS.sub(' ', nombre)
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    nombre = nombre.rstrip('.')
    return nombre


def _generar_variantes(nombre: str) -> list:
    """
    Genera variantes mínimas basadas en el nombre y regiones.
    """
    variantes = []
    seen = set()

    def add(v: str):
        v = v.strip().replace("  ", " ").rstrip('.')
        if v and v not in seen:
            seen.add(v)
            variantes.append(v)

    def add_con_regiones(base: str):
        add(base)
        for region in ["(USA)", "(USA, Europe)", "(Europe)", "(World)", "(Japan)"]:
            add(f"{base} {region}")

    # 1. Normalización y limpieza de tags
    nombre = _normalizar_nombre(nombre)
    nombre_limpio = _REGION_TAGS.sub('', nombre).strip()
    nombre_limpio = re.split(r'[\(\[]', nombre_limpio)[0].strip()
    
    # 2. Intentar nombre limpio tal cual
    add_con_regiones(nombre_limpio)

    # 3. Variante: Mover ", The" al principio si existe (ej: "Legend of Zelda, The" -> "The Legend of Zelda")
    if ", The" in nombre_limpio:
        base_the = "The " + nombre_limpio.replace(", The", "").strip()
        add_con_regiones(base_the)
        
        # Intentar insertar el guion separador después de ", The" si hay más texto
        # "Legend of Zelda, The A Link..." -> "Legend of Zelda, The - A Link..."
        partes = nombre_limpio.split(", The")
        if len(partes) > 1 and partes[1].strip():
            base_dash = f"{partes[0]}, The - {partes[1].strip()}"
            add_con_regiones(base_dash)
    elif nombre_limpio.startswith("The "):
        base_no_the = nombre_limpio.replace("The ", "").strip() + ", The"
        add_con_regiones(base_no_the)
    
    # 4. Variantes de caracteres especiales
    if "&" in nombre_limpio:
        add_con_regiones(nombre_limpio.replace("&", "and"))
    if "," in nombre_limpio:
        add_con_regiones(nombre_limpio.replace(",", ""))

    # 5. Variante por palabras (primeras 3 o 2)
    palabras = nombre_limpio.split()
    if len(palabras) >= 3:
        add_con_regiones(f"{palabras[0]} {palabras[1]} {palabras[2]}")
    elif len(palabras) >= 2:
        add_con_regiones(f"{palabras[0]} {palabras[1]}")

    return variantes


def _construir_url(platform: str, nombre_juego: str) -> str:
    """Construye la URL thumbnail en el CDN de Libretro."""
    platform_enc = urllib.parse.quote(platform)
    game_enc = urllib.parse.quote(nombre_juego + ".png")
    return f"{LIBRETRO_CDN}/{platform_enc}/{THUMBNAIL_TYPE}/{game_enc}"


def obtener_ruta_caratula(ruta_rom: str) -> str:
    """
    Devuelve la ruta donde se guarda la carátula de un ROM.
    Ubicación: [carpeta_del_rom]/media/[nombre_sin_ext].png
    """
    rom_dir = os.path.dirname(ruta_rom)
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(rom_dir, "media", f"{game_name}.png")


def obtener_ruta_imagen_consola(ruta_roms_base: str, id_emu: str) -> str:
    """
    Devuelve la ruta de la imagen representativa de una consola.
    Ubicación: [ruta_roms_base]/.console_art/[id_emu].png
    """
    return os.path.join(ruta_roms_base, ".console_art", f"{id_emu}.png")


def tiene_caratula(ruta_rom: str) -> bool:
    """Verifica si ya existe una carátula descargada para este ROM."""
    return os.path.exists(obtener_ruta_caratula(ruta_rom))


def obtener_ruta_logo_consola(id_emu: str, flet_path: bool = False) -> str:
    """Ruta del logo de la consola. flet_path=True devuelve ruta relativa para assets."""
    if flet_path:
        return f"/consolas/{id_emu}.png"
    return os.path.abspath(os.path.join(CONSOLES_DIR, f"{id_emu}.png"))

def obtener_ruta_logo_emulador(id_emu: str, flet_path: bool = False) -> str:
    """Ruta del logo del emulador. flet_path=True devuelve ruta relativa para assets."""
    if flet_path:
        return f"/emuladores/{id_emu}.png"
    return os.path.abspath(os.path.join(EMULATORS_DIR, f"{id_emu}.png"))

def tiene_logo_consola(id_emu: str) -> bool:
    return os.path.exists(obtener_ruta_logo_consola(id_emu))

def tiene_logo_emulador(id_emu: str) -> bool:
    return os.path.exists(obtener_ruta_logo_emulador(id_emu))


async def _intentar_descarga(session: aiohttp.ClientSession, url: str, ruta_destino: str) -> bool:
    """Intenta descargar una imagen y guardarla. Retorna True si tuvo éxito."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                contenido = await resp.read()
                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                print(f"[ARTWORK] Descarga exitosa: {url}")
                with open(ruta_destino, "wb") as f:
                    f.write(contenido)
                return True
            else:
                print(f"[ARTWORK] Error {resp.status} al descargar: {url}")
    except Exception as e:
        print(f"[ARTWORK] Excepción al descargar {url}: {e}")
    return False


async def descargar_caratula(
    session: aiohttp.ClientSession,
    platform: str,
    nombre_juego: str,
    ruta_rom: str
) -> bool:
    """
    Descarga la carátula de un juego probando múltiples variantes del nombre.
    Prioriza el nombre real del archivo como variante principal.
    """
    caratula_path = obtener_ruta_caratula(ruta_rom)
    if os.path.exists(caratula_path):
        return True

    # Candidatos a probar
    candidatos = []
    seen = set()

    def add_c(v: str):
        v = v.strip()
        if v and v not in seen:
            seen.add(v)
            candidatos.append(v)

    # 1. Prioridad: Nombre real del archivo (limpiando underscores)
    filename = os.path.splitext(os.path.basename(ruta_rom))[0]
    filename_clean = filename.replace("_", " ")
    add_c(filename_clean)
    add_c(filename_clean.title()) # Probar también con mayúsculas tipo título

    # 2. Variantes generadas
    for v in _generar_variantes(nombre_juego):
        add_c(v)
        add_c(v.title()) # Probar capitalización para cada variante

    # Probar candidatos
    for variante in candidatos:
        url = _construir_url(platform, variante)
        ok = await _intentar_descarga(session, url, caratula_path)
        if ok:
            print(f"[ARTWORK] ✓ '{nombre_juego}' → coincidencia con: '{variante}'")
            return True

    return False


async def descargar_recursos_estaticos():
    """Asegura que existan las carpetas para que el usuario ponga sus imágenes."""
    os.makedirs(CONSOLES_DIR, exist_ok=True)
    os.makedirs(EMULATORS_DIR, exist_ok=True)


async def predescargar_imagenes_consola(emu_map: dict, ruta_roms_base: str) -> int:
    """
    (Lógica de descarga automática eliminada)
    Solo asegura la creación de carpetas de medios.
    """
    await descargar_recursos_estaticos()
    return 0


async def descargar_caratulas_biblioteca(
    juegos: list,
    emu_map: dict,
    ruta_roms_base: str = "",
    on_progress: Optional[Callable[[int, int, str], None]] = None
) -> dict:
    """
    Descarga carátulas para todos los juegos con concurrencia controlada (5 simultáneas).
    Returns: estadísticas {'ok': int, 'skip': int, 'fail': int}
    """
    stats = {"ok": 0, "skip": 0, "fail": 0}
    total = len(juegos)
    semaforo = asyncio.Semaphore(5)

    async def _worker(session, idx, juego):
        async with semaforo:
            platform = emu_map.get(juego.get("id_emu", ""))
            nombre = juego.get("nombre", "")

            if not platform:
                stats["skip"] += 1
                if on_progress:
                    on_progress(idx + 1, total, nombre)
                return

            if tiene_caratula(juego.get("ruta", "")):
                stats["skip"] += 1
                if on_progress:
                    on_progress(idx + 1, total, nombre)
                return

            ok = await descargar_caratula(session, platform, nombre, juego.get("ruta", ""))
            stats["ok" if ok else "fail"] += 1

            if on_progress:
                on_progress(idx + 1, total, nombre)
            await asyncio.sleep(0.05)

    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        await asyncio.gather(*[_worker(session, i, j) for i, j in enumerate(juegos)])

    return stats
