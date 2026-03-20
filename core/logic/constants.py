"""
constants.py Ã¢â‚¬â€ Diccionarios y configuraciones fijas del sistema
AquÃƒÂ­ se definen los emuladores soportados y sus metadatos de Libretro.
"""

import os
import json

def cargar_emuladores_config():
    """Carga la lista de emuladores desde el archivo JSON dinÃƒÂ¡mico."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 1. Intentar en la nueva ubicaciÃƒÂ³n de recursos (protegida de limpiezas del usuario)
    ruta_resources = os.path.join(base_dir, "resources", "emulators.json")
    # 2. Intentar en la antigua ubicaciÃƒÂ³n (retrocompatibilidad)
    ruta_data = os.path.join(base_dir, "data", "emulators.json")
    
    for ruta_json in [ruta_resources, ruta_data]:
        if os.path.exists(ruta_json):
            try:
                with open(ruta_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[CONSTANTS] Error cargando {ruta_json}: {e}")
    
    print("[CONSTANTS] CRÃƒÂTICO: No se encontrÃƒÂ³ emulators.json en ninguna ubicaciÃƒÂ³n.")
    return []

# La lista principal ahora es dinÃƒÂ¡mica
AVAILABLE_EMULATORS = cargar_emuladores_config()

# Otras constantes fijas del sistema podrÃƒÂ­an ir aquÃƒÂ­ en el futuro
# Ejemplo: APP_THEME_COLOR = "#7c6ff7"
