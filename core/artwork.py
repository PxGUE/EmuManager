"""
artwork.py — Motor de Carátulas V2 (Fuzzy Match Index-Based)
Version: 0.1.1 alpha

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
from typing import Optional, Callable

# URL BASE del CDN de Libretro Thumbnails
LIBRETRO_CDN = "https://thumbnails.libretro.com"
THUMBNAIL_TYPE = "Named_Boxarts"

# Directorios para recursos estáticos del sistema
PROJECT_MEDIA = "media"
CONSOLES_DIR = os.path.join(PROJECT_MEDIA, "consolas")
EMULATORS_DIR = os.path.join(PROJECT_MEDIA, "emuladores")

# Memoria caché para evitar peticiones HTTP repetitivas al mismo índice en una sesión
_INDEX_CACHE = {}

def normalizar_nombre(nombre: str) -> str:
    """
    Limpia un nombre para compararlo de forma justa (Fuzzy Matching):
    - Quita paréntesis y corchetes.
    - Elimina caracteres especiales.
    - Convierte a minúsculas y quita espacios extra.
    """
    n = nombre.replace("_", " ")
    n = re.sub(r'[\(\[].*?[\)\]]', '', n) # Eliminar (USA), [Hack], etc.
    n = re.sub(r'[^a-zA-Z0-9\s]', '', n)  # Quedarse solo con letras y números
    return re.sub(r'\s+', ' ', n).strip().lower()

async def obtener_indice_plataforma(session: aiohttp.ClientSession, platform: str) -> list:
    """
    Descarga el índice HTML de una plataforma de Libretro y extrae los nombres de archivos .png
    """
    if platform in _INDEX_CACHE:
        return _INDEX_CACHE[platform]

    # Codificar la URL (ej: Nintendo - Game Boy Advance)
    platform_url = f"{LIBRETRO_CDN}/{urllib.parse.quote(platform)}/{THUMBNAIL_TYPE}/"
    nombres_disponibles = []

    try:
        async with session.get(platform_url, timeout=15) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                # Buscamos todas las etiquetas <a> que apuntan a imágenes
                links = soup.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    if href.endswith('.png'):
                        # Guardamos el nombre sin la extensión y decodificado
                        nombre_crudo = unquote(href[:-4])
                        nombres_disponibles.append(nombre_crudo)
                
                print(f"[ARTWORK] Índice cargado para {platform}: {len(nombres_disponibles)} portadas encontradas.")
                _INDEX_CACHE[platform] = nombres_disponibles
            else:
                print(f"[ARTWORK] Error {resp.status} - No se pudo cargar índice para {platform}.")
                _INDEX_CACHE[platform] = []
    except Exception as e:
        print(f"[ARTWORK] Excepción obteniendo índice para {platform}: {e}")
        _INDEX_CACHE[platform] = []

    return _INDEX_CACHE[platform]

def encontrar_mejor_coincidencia(nombre_buscado: str, lista_disponibles: list) -> Optional[str]:
    """
    Algoritmo de IA ligera para encontrar la carátula más parecida.
    Busca coincidencias en 3 niveles de rigor descendente.
    """
    norm_target = normalizar_nombre(nombre_buscado)
    
    # Crear un mapa local de nombres normalizados -> nombres originales
    mapa = {normalizar_nombre(orig): orig for orig in lista_disponibles}
    keys_norm = list(mapa.keys())
    
    # Nivel 1: Coincidencia perfecta (tras normalizar)
    if norm_target in mapa:
        return mapa[norm_target]
        
    # Nivel 2: Similitud estructural fuerte (80%)
    matches = difflib.get_close_matches(norm_target, keys_norm, n=1, cutoff=0.8)
    if matches:
        return mapa[matches[0]]
        
    # Nivel 3: Similitud flexible (70%) para nombres con variaciones ortográficas
    matches_relaxed = difflib.get_close_matches(norm_target, keys_norm, n=1, cutoff=0.7)
    if matches_relaxed:
         return mapa[matches_relaxed[0]]
         
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
    """Ruta del logo/imagen decorativa de la consola."""
    if flet_path: return f"/consolas/{id_emu}.png"
    return os.path.abspath(os.path.join(CONSOLES_DIR, f"{id_emu}.png"))

def obtener_ruta_logo_emulador(id_emu: str, flet_path: bool = False) -> str:
    """Ruta del logo del programa emulador."""
    if flet_path: return f"/emuladores/{id_emu}.png"
    return os.path.abspath(os.path.join(EMULATORS_DIR, f"{id_emu}.png"))

async def _descargar_archivo(session: aiohttp.ClientSession, url: str, ruta_destino: str) -> bool:
    """Descarga binaria de una imagen y guardado en disco."""
    try:
        async with session.get(url, timeout=15) as resp:
            if resp.status == 200:
                contenido = await resp.read()
                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                with open(ruta_destino, "wb") as f:
                    f.write(contenido)
                return True
    except: pass
    return False

async def descargar_caratula(session: aiohttp.ClientSession, platform: str, nombre_juego: str, ruta_rom: str) -> bool:
    """
    Lógica principal de descarga para un juego individual:
    1. Obtiene el índice de la consola.
    2. Busca el mejor 'match'.
    3. Descarga si hay éxito.
    """
    caratula_path = obtener_ruta_caratula(ruta_rom)
    if os.path.exists(caratula_path): return True

    lista_nombres = await obtener_indice_plataforma(session, platform)
    if not lista_nombres: return False

    # El nombre del archivo real es nuestro mejor candidato
    candidato_principal = os.path.splitext(os.path.basename(ruta_rom))[0]
    
    # Intentar búsqueda con el nombre del archivo
    mejor_match = encontrar_mejor_coincidencia(candidato_principal, lista_nombres)
    # Si falla, intentar con el nombre 'limpio' procesado por el escáner
    if not mejor_match:
        mejor_match = encontrar_mejor_coincidencia(nombre_juego, lista_nombres)

    if mejor_match:
        url = f"{LIBRETRO_CDN}/{urllib.parse.quote(platform)}/{THUMBNAIL_TYPE}/{urllib.parse.quote(mejor_match + '.png')}"
        ok = await _descargar_archivo(session, url, caratula_path)
        if ok:
            # Calcular ratio de similitud para el log
            ratio = int(difflib.SequenceMatcher(None, normalizar_nombre(candidato_principal), normalizar_nombre(mejor_match)).ratio()*100)
            print(f"[ARTWORK] ✓ Match al {ratio}%: '{candidato_principal}' -> '{mejor_match}'")
            return True
    return False

async def descargar_recursos_estaticos():
    """Asegura que el árbol de carpetas de media exista."""
    os.makedirs(CONSOLES_DIR, exist_ok=True)
    os.makedirs(EMULATORS_DIR, exist_ok=True)

async def predescargar_imagenes_consola(emu_map: dict, ruta_roms_base: str) -> int:
    """Inicialización de carpetas estáticas."""
    await descargar_recursos_estaticos()
    return 0

async def descargar_caratulas_biblioteca(
    juegos: list, emu_map: dict, ruta_roms_base: str = "", on_progress: Optional[Callable[[int, int, str], None]] = None
) -> dict:
    """
    Descarga masiva de carátulas para una lista de juegos con concurrencia controlada.
    Agrupa por plataforma para cargar los índices una sola vez.
    """
    stats = {"ok": 0, "skip": 0, "fail": 0}
    total = len(juegos)
    
    # Identificar qué plataformas necesitamos consultar
    plataformas_necesarias = list(set([emu_map.get(j.get("id_emu", "")) for j in juegos if emu_map.get(j.get("id_emu", ""))]))
    
    connector = aiohttp.TCPConnector(limit=10) # Límite de conexiones simultáneas
    async with aiohttp.ClientSession(connector=connector) as session:
        # 1. Pre-cargar índices de todas las consolas necesarias para ganar velocidad
        print(f"[ARTWORK] Preparando índices para {len(plataformas_necesarias)} plataformas...")
        await asyncio.gather(*[obtener_indice_plataforma(session, p) for p in plataformas_necesarias])

        # 2. Iniciar descargas con semáforo para no saturar el servidor
        semaforo = asyncio.Semaphore(5)

        async def _worker(idx, juego):
            async with semaforo:
                platform = emu_map.get(juego.get("id_emu", ""))
                nombre = juego.get("nombre", "")

                # Saltar si no hay plataforma asignada o ya tiene carátula
                if not platform or tiene_caratula(juego.get("ruta", "")):
                    stats["skip"] += 1
                    if on_progress: on_progress(idx + 1, total, nombre)
                    return

                ok = await descargar_caratula(session, platform, nombre, juego.get("ruta", ""))
                stats["ok" if ok else "fail"] += 1

                if on_progress: on_progress(idx + 1, total, nombre)

        # Ejecutar todos los workers en paralelo
        await asyncio.gather(*[_worker(i, j) for i, j in enumerate(juegos)])

    return stats
