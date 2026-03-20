"""
config.py â€” ConfiguraciÃ³n global y metadatos del sistema
"""

import os
import json
import sys

# Metadatos de la AplicaciÃ³n
APP_NAME = "EmuManager"
APP_VERSION = "0.1.20-alpha"
PORTABLE_MODE = True
REPO_URL = "https://github.com/PxGUE/EmuManager"

# Rutas del Proyecto
# RESOURCE_DIR: Directorio de recursos internos (QML, recursos por defecto)
# DATA_DIR: Directorio de datos persistentes (biblioteca, config, artwork descargado)

if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    # Si es un ejecutable (distribuido)
    # Ruta de los archivos incluidos en el paquete (bundle)
    RESOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Ruta para datos persistentes (junto al ejecutable si es portable)
    if os.getenv("APPIMAGE"):
        # En AppImage, el ejecutable estÃ¡ en el monte, pero queremos los datos
        # junto al archivo .AppImage real (o en el HOME si se prefiere)
        # Para modo portable extremo, usamos el directorio del archivo .AppImage
        DATA_BASE_DIR = os.path.dirname(os.getenv("APPIMAGE"))
    else:
        DATA_BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si corre como script de Python
    RESOURCE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_BASE_DIR = RESOURCE_DIR

BASE_DIR = RESOURCE_DIR # Retrocompatibilidad
DATA_DIR = os.path.join(DATA_BASE_DIR, "data")
MEDIA_DIR = os.path.join(DATA_BASE_DIR, "media")

# Archivos de Datos
SETTINGS_FILE = os.path.join(DATA_DIR, "config.json")
EMULATORS_FILE = os.path.join(RESOURCE_DIR, "resources", "emulators.json")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
FAVORITES_FILE = os.path.join(DATA_DIR, "favorites.json")
SCRAPED_DIR = os.path.join(DATA_DIR, "scraped")

def get_resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso."""
    return os.path.join(BASE_DIR, relative_path)

def normalize_path(path):
    """
    Si la ruta estÃ¡ dentro del BASE_DIR, la convierte en relativa.
    Esto permite la portabilidad si se mueve la carpeta del proyecto.
    """
    if not path: return ""
    abs_path = os.path.abspath(path)
    if abs_path.startswith(BASE_DIR):
        return os.path.relpath(abs_path, BASE_DIR)
    return abs_path

def resolve_path(path):
    """
    Si la ruta es relativa, la resuelve respecto al BASE_DIR.
    Si es absoluta, la devuelve tal cual.
    """
    if not path: return ""
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(BASE_DIR, path))

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                # Resolver rutas al cargar
                if "install_path" in settings:
                    settings["install_path"] = resolve_path(settings["install_path"])
                if "roms_path" in settings:
                    settings["roms_path"] = resolve_path(settings["roms_path"])
                return settings
        except:
            pass
    return {}

def save_settings(settings):
    os.makedirs(DATA_DIR, exist_ok=True)
    # Normalizar rutas antes de guardar
    settings_to_save = settings.copy()
    if "install_path" in settings_to_save:
        settings_to_save["install_path"] = normalize_path(settings_to_save["install_path"])
    if "roms_path" in settings_to_save:
        settings_to_save["roms_path"] = normalize_path(settings_to_save["roms_path"])
        
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings_to_save, f, indent=4)
