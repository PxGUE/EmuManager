"""
scanner.py — Motor de búsqueda de ROMs
Escanea el sistema de archivos y mantiene la base de datos local (library.json).
"""

import asyncio
import os
import json
import re
from dataclasses import dataclass, asdict
from typing import List
from .constants import AVAILABLE_EMULATORS

@dataclass
class Juego:
    """Modelo de datos para un videojuego."""
    id_emu: str    # ID del emulador asociado (ej: mgba)
    nombre: str    # Nombre limpio para mostrar en la interfaz
    ruta: str      # Ruta absoluta al archivo ROM
    consola: str   # Nombre de la consola (ej: Game Boy Advance)
    extension: str # Extensión del archivo (.gba)

def limpiar_nombre_juego(nombre_original: str) -> str:
    """
    Normaliza el nombre de un archivo ROM para que sea legible.
    Ej: "sonic_the_hedgehog_(usa)_(v1.1)" -> "Sonic The Hedgehog"
    """
    # 1. Eliminar contenido entre paréntesis () o corchetes []
    nombre = re.sub(r'\s*[\(\[][^()\[\]]*[\)\]]', '', nombre_original)
    
    # 2. Reemplazar guiones bajos y normales por espacios
    nombre = nombre.replace('_', ' ').replace('-', ' ')
    
    # 3. Colapsar espacios múltiples
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    
    # 4. Formatear cada palabra: "the hedgehog" -> "The Hedgehog"
    nombre = ' '.join(word.capitalize() for word in nombre.split())
    
    return nombre if nombre else nombre_original

async def escanear_roms(ruta_base: str, emu_id: str = None) -> List[Juego]:
    """
    Escanea la carpeta de ROMs organizada por subcarpetas de consola.
    Actualiza el archivo persistente data/library.json.
    """
    data_dir = "data"
    library_file = os.path.join(data_dir, "library.json")
    
    # Cargar juegos existentes para no borrar los de otras consolas en un escaneo parcial
    juegos_finales = []
    if emu_id:
        dict_existentes = cargar_biblioteca_cache()
        juegos_finales = [Juego(**j) for j in dict_existentes if j.get("id_emu") != emu_id]
    
    juegos_escaneados = []
    
    if not ruta_base or not os.path.exists(ruta_base):
        return juegos_finales

    # Filtrar: ¿Escaneamos todo o solo una consola específica?
    emus_procesar = [e for e in AVAILABLE_EMULATORS if e["id"] == emu_id] if emu_id else AVAILABLE_EMULATORS

    # Listar subcarpetas reales para búsqueda flexible
    try:
        subfolders = [f for f in os.listdir(ruta_base) if os.path.isdir(os.path.join(ruta_base, f))]
    except Exception as e:
        print(f"[SCANNER] Error listando ruta_base: {e}")
        return juegos_finales

    for emu in emus_procesar:
        target_folder = emu["folder"].lower()
        target_id = emu["id"].lower()
        target_console = emu["console"].lower()
        
        # Buscar carpetas que coincidan con folder, id o nombre de consola
        matched_folders = []
        for f in subfolders:
            f_low = f.lower()
            if f_low == target_folder or f_low == target_id or target_console in f_low or f_low in target_console:
                matched_folders.append(f)
        
        # Eliminar duplicados si varias coinciden (aunque es raro)
        matched_folders = list(set(matched_folders))
        
        for folder in matched_folders:
            console_path = os.path.join(ruta_base, folder)
            print(f"[SCANNER] Procesando carpeta: {folder} para emulador {emu['id']}")
            
            extensions = emu.get("extensions", [])
            for root, dirs, files in os.walk(console_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in extensions:
                        nombre_archivo = os.path.splitext(file)[0]
                        juegos_escaneados.append(
                            Juego(
                                id_emu=emu["id"],
                                nombre=limpiar_nombre_juego(nombre_archivo),
                                ruta=os.path.abspath(os.path.join(root, file)),
                                consola=emu["console"],
                                extension=ext
                            )
                        )
                await asyncio.sleep(0.01)
    
    # Unir resultados nuevos con los antiguos (si los hay)
    juegos_finales.extend(juegos_escaneados)
    
    # Guardar en JSON (Persistencia)
    try:
        os.makedirs(data_dir, exist_ok=True)
        with open(library_file, "w") as f:
            json.dump([asdict(j) for j in juegos_finales], f, indent=4)
        print(f"[SCANNER] Éxito: {len(juegos_finales)} juegos en biblioteca.")
    except Exception as e:
        print(f"[SCANNER] Error guardando JSON: {e}")
        
    return juegos_finales

def cargar_biblioteca_cache() -> List[dict]:
    """Lee la lista de juegos desde el archivo JSON de caché."""
    library_file = os.path.join("data", "library.json")
    if os.path.exists(library_file):
        try:
            with open(library_file, "r") as f:
                return json.load(f)
        except:
            return []
    return []


# ── SISTEMA DE FAVORITOS ──────────────────────────────────────────────

_FAVORITES_FILE = os.path.join("data", "favorites.json")
_favorites_cache: set = None


def cargar_favoritos() -> set:
    """Carga la lista de favoritos desde disco (caché en memoria por sesión)."""
    global _favorites_cache
    if _favorites_cache is not None:
        return _favorites_cache
    try:
        if os.path.exists(_FAVORITES_FILE):
            with open(_FAVORITES_FILE, "r", encoding="utf-8") as f:
                _favorites_cache = set(json.load(f))
        else:
            _favorites_cache = set()
    except Exception as e:
        print(f"[SCANNER] Error cargando favoritos: {e}")
        _favorites_cache = set()
    return _favorites_cache


def guardar_favoritos(favorites: set):
    """Persiste el conjunto de favoritos en disco."""
    global _favorites_cache
    _favorites_cache = favorites
    try:
        os.makedirs("data", exist_ok=True)
        with open(_FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(list(favorites), f, ensure_ascii=False)
    except Exception as e:
        print(f"[SCANNER] Error guardando favoritos: {e}")


def toggle_favorito(ruta_rom: str) -> bool:
    """Alterna el estado favorito de un juego. Devuelve True si ahora es favorito."""
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
    """Devuelve True si el juego está marcado como favorito."""
    return ruta_rom in cargar_favoritos()
