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

    for emu in emus_procesar:
        folder_name = emu["folder"]
        console_path = os.path.join(ruta_base, folder_name)
        
        if os.path.exists(console_path) and os.path.isdir(console_path):
            print(f"[SCANNER] Escaneando: {folder_name}...")
            extensions = emu.get("extensions", [])
            
            # Recorrido recursivo de archivos en la carpeta de la consola
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
                # Pausa técnica para dejar que el hilo de la UI respire
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
