import asyncio
import os
import json
import re
from dataclasses import dataclass, asdict
from typing import List
from .constants import AVAILABLE_EMULATORS

@dataclass
class Juego:
    id_emu: str
    nombre: str
    ruta: str
    consola: str
    extension: str

def limpiar_nombre_juego(nombre_original: str) -> str:
    """
    Limpia el nombre del juego eliminando versiones, regiones y formateando a Upper Camel Case.
    Ej: "sonic_the_hedgehog_(usa)_(v1.1)" -> "Sonic The Hedgehog"
    """
    # 1. Eliminar todo lo que esté entre paréntesis () o corchetes [] (regiones, versiones, etc)
    nombre = re.sub(r'\s*[\(\[][^()\[\]]*[\)\]]', '', nombre_original)
    
    # 2. Reemplazar guiones bajos y guiones por espacios
    nombre = nombre.replace('_', ' ').replace('-', ' ')
    
    # 3. Eliminar espacios múltiples
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    
    # 4. Convertir a Upper Camel Case (Title Case)
    # Usamos capitalize en cada palabra para que sea "The" y no "THE" o "the"
    nombre = ' '.join(word.capitalize() for word in nombre.split())
    
    return nombre if nombre else nombre_original

async def escanear_roms(ruta_base: str, emu_id: str = None) -> List[Juego]:
    """
    Escanea la ruta base buscando carpetas por consola (ej: GBA, N64).
    Si emu_id se especifica, solo escanea esa carpeta y actualiza la biblioteca persistente.
    """
    data_dir = "data"
    library_file = os.path.join(data_dir, "library.json")
    
    # Cargar juegos existentes si estamos haciendo un escaneo parcial
    juegos_finales = []
    if emu_id:
        dict_existentes = cargar_biblioteca_cache()
        # Preservar juegos de otras consolas
        juegos_finales = [Juego(**j) for j in dict_existentes if j.get("id_emu") != emu_id]
    
    juegos_escaneados = []
    
    if not ruta_base or not os.path.exists(ruta_base):
        print(f"[DEBUG SCANNER] Ruta base no válida: {ruta_base}")
        return juegos_finales

    print(f"[DEBUG SCANNER] Iniciando escaneo {'específico para ' + emu_id if emu_id else 'completo'} en: {ruta_base}")

    # Filtrar emuladores a escanear
    emus_procesar = [e for e in AVAILABLE_EMULATORS if e["id"] == emu_id] if emu_id else AVAILABLE_EMULATORS

    for emu in emus_procesar:
        # La carpeta esperada para esta consola (ej: Roms/GBA)
        folder_name = emu["folder"]
        console_path = os.path.join(ruta_base, folder_name)
        
        if os.path.exists(console_path) and os.path.isdir(console_path):
            print(f"[DEBUG SCANNER] Escaneando consola: {folder_name}")
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
                # Pequeña pausa para no bloquear el event loop en escaneos masivos
                await asyncio.sleep(0.01)
    
    # Fusionar resultados
    juegos_finales.extend(juegos_escaneados)
    
    # Guardar resultados en library.json
    try:
        os.makedirs(data_dir, exist_ok=True)
        with open(library_file, "w") as f:
            json.dump([asdict(j) for j in juegos_finales], f, indent=4)
        print(f"[DEBUG SCANNER] Biblioteca actualizada: {len(juegos_finales)} juegos totales.")
    except Exception as e:
        print(f"[DEBUG SCANNER] Error al guardar biblioteca: {e}")
        
    return juegos_finales

def cargar_biblioteca_cache() -> List[dict]:
    """Carga los juegos guardados en el último escaneo."""
    library_file = os.path.join("data", "library.json")
    if os.path.exists(library_file):
        try:
            with open(library_file, "r") as f:
                return json.load(f)
        except:
            return []
    return []
