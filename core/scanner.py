"""
scanner.py — Motor de búsqueda y gestión de biblioteca (ROMs).

Este módulo se encarga de:
1. Escanear el sistema de archivos buscando ROMs compatibles.
2. Normalizar nombres de archivos para la interfaz.
3. Gestionar la agrupación de juegos multi-disco (.m3u).
4. Mantener el sistema de favoritos y la persistencia de la biblioteca.
"""

import asyncio
import os
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set

from .constants import AVAILABLE_EMULATORS
from . import config

_library_cache: Optional[List[dict]] = None

@dataclass
class Juego:
    """
    Representa un videojuego detectado en el sistema.
    
    Attributes:
        id_emu (str): ID del emulador asignado (según emulators.json).
        nombre (str): Nombre limpio para mostrar en la UI.
        ruta (str): Ruta absoluta al archivo físico.
        consola (str): Nombre descriptivo de la plataforma.
        extension (str): Extensión del archivo original.
    """
    id_emu: str
    nombre: str
    ruta: str
    consola: str
    extension: str

def limpiar_nombre_juego(nombre_original: str) -> str:
    """
    Normaliza el nombre de un archivo ROM para una presentación limpia.
    
    Ejemplo: "Sonic_Hedgehog_(USA)_[!]" -> "Sonic Hedgehog"

    Args:
        nombre_original (str): El nombre base del archivo.

    Returns:
        str: El nombre formateado y capitalizado.
    """
    # 1. Eliminar contenido entre paréntesis o corchetes (regiones, versiones, etc.)
    nombre = re.sub(r'\s*[\(\[][^()\[\]]*[\)\]]', '', nombre_original)
    
    # 2. Reemplazar caracteres de unión por espacios
    nombre = nombre.replace('_', ' ').replace('-', ' ')
    
    # 3. Eliminar espacios múltiples resultantes
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    
    # 4. Capitalización: "the legend" -> "The Legend"
    nombre = ' '.join(word.capitalize() for word in nombre.split())
    
    return nombre if nombre else nombre_original

async def escanear_roms(ruta_base: str, emu_id: Optional[str] = None) -> List[Juego]:
    """
    Escanea el directorio de ROMs y actualiza la base de datos local.

    Args:
        ruta_base (str): Carpeta raíz donde se encuentran las ROMs por subcarpetas.
        emu_id (str, optional): Si se especifica, solo escanea esta consola/emulador.

    Returns:
        List[Juego]: Lista actualizada de todos los juegos en la biblioteca.
    """
    library_file = config.METADATA_FILE.replace("metadata.json", "library.json") # TODO: Mover a config de forma explícita
    # Nota: Usamos la carpeta de datos configurada en config.py
    
    juegos_finales = []
    
    # Si es un escaneo parcial (una consola), preservamos el resto de la biblioteca
    if emu_id:
        dict_existentes = cargar_biblioteca_cache()
        juegos_finales = [Juego(**j) for j in dict_existentes if j.get("id_emu") != emu_id]
    
    juegos_escaneados = []
    
    if not ruta_base or not os.path.exists(ruta_base):
        return juegos_finales

    # Decidir qué emuladores/carpetas procesar
    emus_procesar = [e for e in AVAILABLE_EMULATORS if e["id"] == emu_id] if emu_id else AVAILABLE_EMULATORS

    try:
        subfolders = [f for f in os.listdir(ruta_base) if os.path.isdir(os.path.join(ruta_base, f))]
    except Exception as e:
        print(f"[SCANNER] Error de acceso a '{ruta_base}': {e}")
        return juegos_finales

    for emu in emus_procesar:
        target_folder = emu["folder"].lower()
        target_id = emu["id"].lower()
        target_console = emu["console"].lower()
        
        # Búsqueda difusa de carpetas (puede ser por ID, nombre de carpeta o consola)
        matched_folders = []
        for f in subfolders:
            f_low = f.lower()
            if f_low == target_folder or f_low == target_id or target_console in f_low or f_low in target_console:
                matched_folders.append(f)
        
        matched_folders = list(set(matched_folders)) # Evitar procesar dos veces la misma carpeta
        
        for folder in matched_folders:
            console_path = os.path.join(ruta_base, folder)
            extensions = emu.get("extensions", [])
            
            # 1. Recopilar archivos candidatos basados en extensiones configuradas
            archivos_candidatos = []
            for root, dirs, files in os.walk(console_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in extensions:
                        archivos_candidatos.append((root, file, ext))
            
            # 2. Gestión de Multi-Disco: Leer archivos .m3u para ocultar archivos referenciados
            # Esto evita que aparezca "Disc 1", "Disc 2" en la UI si el M3U ya los agrupa.
            rutas_a_ignorar: Set[str] = set()
            for root, file, ext in archivos_candidatos:
                if ext == ".m3u":
                    try:
                        m3u_path = os.path.join(root, file)
                        with open(m3u_path, "r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                # Ignorar líneas vacías y comentarios de M3U
                                if line and not line.startswith("#"):
                                    ref_path = os.path.abspath(os.path.join(root, line))
                                    rutas_a_ignorar.add(ref_path)
                    except: pass

            # 3. Crear objetos Juego filtrando los ignorados
            for root, file, ext in archivos_candidatos:
                ruta_completa = os.path.abspath(os.path.join(root, file))
                if ruta_completa in rutas_a_ignorar:
                    continue
                
                nombre_archivo = os.path.splitext(file)[0]
                juegos_escaneados.append(
                    Juego(
                        id_emu=emu["id"],
                        nombre=limpiar_nombre_juego(nombre_archivo),
                        ruta=ruta_completa,
                        consola=emu["console"],
                        extension=ext
                    )
                )
            # Pequeña pausa para no bloquear el loop de eventos en escaneos masivos
            await asyncio.sleep(0.01)
    
    juegos_finales.extend(juegos_escaneados)
    juegos_finales.sort(key=lambda x: x.nombre.lower())
    
    # Limpiar caché para forzar recarga
    global _library_cache
    _library_cache = None
    
    # 4. Persistencia en library.json
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        lib_path = os.path.join(config.DATA_DIR, "library.json")
        
        # Normalizar rutas antes de guardar
        data_to_save = []
        for j in juegos_finales:
            j_dict = asdict(j)
            j_dict["ruta"] = config.normalize_path(j_dict["ruta"])
            data_to_save.append(j_dict)
            
        with open(lib_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        print(f"[SCANNER] Biblioteca actualizada: {len(juegos_finales)} juegos totales.")
    except Exception as e:
        print(f"[SCANNER] Error al guardar biblioteca: {e}")
        
    return juegos_finales

def cargar_biblioteca_cache() -> List[dict]:
    """
    Carga la lista de juegos desde el JSON persistente resolviendo rutas.
    Utiliza caché en memoria para evitar lecturas de disco repetitivas.
    """
    global _library_cache
    if _library_cache is not None:
        return _library_cache

    lib_path = os.path.join(config.DATA_DIR, "library.json")
    if os.path.exists(lib_path):
        try:
            with open(lib_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Resolver rutas al cargar
                for j in data:
                    if "ruta" in j:
                        j["ruta"] = config.resolve_path(j["ruta"])
                _library_cache = data
                return data
        except:
            return []
    _library_cache = []
    return []


# ── SISTEMA DE FAVORITOS ──────────────────────────────────────────────

_favorites_cache: Optional[Set[str]] = None

def cargar_favoritos() -> Set[str]:
    """
    Obtiene el conjunto de rutas marcadas como favoritas.
    Utiliza un sistema de caché en memoria para accesos rápidos en la misma sesión.
    
    Returns:
        Set[str]: Un conjunto (set) de rutas absolutas de ROMs.
    """
    global _favorites_cache
    if _favorites_cache is not None:
        return _favorites_cache
    try:
        if os.path.exists(config.FAVORITES_FILE):
            with open(config.FAVORITES_FILE, "r", encoding="utf-8") as f:
                raw_favs = json.load(f)
                # Resolver rutas al cargar
                _favorites_cache = set(config.resolve_path(p) for p in raw_favs)
        else:
            _favorites_cache = set()
    except Exception as e:
        print(f"[SCANNER] Error cargando favoritos: {e}")
        _favorites_cache = set()
    return _favorites_cache


def guardar_favoritos(favorites: Set[str]):
    """
    Guarda el conjunto de favoritos en el archivo JSON correspondiente.

    Args:
        favorites (Set[str]): Conjunto de rutas a persistir.
    """
    global _favorites_cache
    _favorites_cache = favorites
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        # Normalizar rutas antes de guardar
        normalized_favs = [config.normalize_path(p) for p in favorites]
        with open(config.FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(normalized_favs, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[SCANNER] Error guardando favoritos: {e}")


def toggle_favorito(ruta_rom: str) -> bool:
    """
    Añade o quita un juego de la lista de favoritos.

    Args:
        ruta_rom (str): Ruta absoluta del juego.

    Returns:
        bool: True si el juego terminó como favorito, False si se quitó.
    """
    favs = cargar_favoritos()
    if ruta_rom in favs:
        favs.discard(ruta_rom)
        is_fav = False
    else:
        favs.add(ruta_rom)
        is_fav = True
    guardar_favoritos(favs)
    return is_fav


def es_favorito(ruta_rom: str) -> bool:
    """
    Consulta si un juego específico es favorito.

    Args:
        ruta_rom (str): Ruta absoluta del juego.

    Returns:
        bool: True si es favorito.
    """
    return ruta_rom in cargar_favoritos()
