"""
constants.py — Diccionarios y configuraciones fijas del sistema
Aquí se definen los emuladores soportados y sus metadatos de Libretro.
"""

import os
import json

def cargar_emuladores_config():
    """Carga la lista de emuladores desde el archivo JSON dinámico."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 1. Intentar en la nueva ubicación de recursos (protegida de limpiezas del usuario)
    ruta_resources = os.path.join(base_dir, "resources", "emulators.json")
    # 2. Intentar en la antigua ubicación (retrocompatibilidad)
    ruta_data = os.path.join(base_dir, "data", "emulators.json")
    
    for ruta_json in [ruta_resources, ruta_data]:
        if os.path.exists(ruta_json):
            try:
                with open(ruta_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[CONSTANTS] Error cargando {ruta_json}: {e}")
    
    print("[CONSTANTS] CRÍTICO: No se encontró emulators.json en ninguna ubicación.")
    return []

# La lista principal ahora es dinámica
AVAILABLE_EMULATORS = cargar_emuladores_config()

# Otras constantes fijas del sistema podrían ir aquí en el futuro
# Ejemplo: APP_THEME_COLOR = "#7c6ff7"