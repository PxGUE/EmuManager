"""
backups.py — Motor de copias de seguridad de partidas guardadas.

Este módulo se encarga de localizar las carpetas de saves/states de los emuladores
y comprimirlas en archivos ZIP fechados dentro de la carpeta 'backups' del proyecto.
"""

import os
import zipfile
from datetime import datetime
from . import config

def crear_backup_emulador(emu_id: str, emu_name: str, install_path: str, save_dirs: list) -> tuple:
    """
    Crea un archivo ZIP con las carpetas de guardado de un emulador.
    
    Args:
        emu_id (str): ID del emulador.
        emu_name (str): Nombre amigable para el nombre del archivo.
        install_path (str): Ruta absoluta donde está instalado el emulador.
        save_dirs (list): Lista de subcarpetas (relativas a install_path) a respaldar.
        
    Returns:
        tuple: (éxito: bool, mensaje: str)
    """
    if not install_path or not os.path.exists(install_path):
        return False, f"Ruta de instalación no válida para {emu_name}."
    
    if not save_dirs:
        return False, f"No hay carpetas de guardado configuradas para {emu_name}."

    # Crear carpeta de backups en el raíz del proyecto si no existe
    backup_root = os.path.join(config.BASE_DIR, "backups")
    os.makedirs(backup_root, exist_ok=True)
    
    # Nombre del archivo: EmuName_YYYYMMDD_HHMMSS.zip
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = "".join(c if c.isalnum() else "_" for c in emu_name)
    filename = f"backup_{clean_name}_{timestamp}.zip"
    dest_path = os.path.join(backup_root, filename)
    
    try:
        with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            found_any = False
            for sdir in save_dirs:
                # Resolvemos la ruta de la carpeta de guardado
                abs_sdir = os.path.join(install_path, sdir)
                if os.path.exists(abs_sdir):
                    found_any = True
                    # Añadir carpeta al zip conservando estructura relativa al emulador
                    for root, dirs, files in os.walk(abs_sdir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # La ruta dentro del zip será relativa a install_path (ej: saves/rom.srm)
                            arcname = os.path.relpath(file_path, install_path)
                            zipf.write(file_path, arcname)
            
            if not found_any:
                # Si no encontramos nada físico, cerramos y borramos el zip vacío
                zipf.close()
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                return False, f"No se encontraron carpetas de guardado para {emu_name} en las rutas configuradas."
                
        return True, f"Copia de seguridad creada: {filename}"
        
    except Exception as e:
        # Limpieza en caso de error
        if os.path.exists(dest_path):
            try: os.remove(dest_path)
            except: pass
        return False, f"Error al crear backup: {str(e)}"

def listar_backups() -> list:
    """
    Obtiene la lista de backups disponibles en la carpeta de respaldos.
    
    Returns:
        list: Lista de diccionarios con metadatos de los archivos ZIP.
    """
    backup_root = os.path.join(config.BASE_DIR, "backups")
    if not os.path.exists(backup_root):
        return []
    
    backups = []
    try:
        for f in os.listdir(backup_root):
            if f.endswith(".zip") and f.startswith("backup_"):
                path = os.path.join(backup_root, f)
                stats = os.stat(path)
                backups.append({
                    "filename": f,
                    "size_mb": round(stats.st_size / (1024 * 1024), 2),
                    "date": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
    except Exception as e:
        print(f"[BACKUPS] Error al listar archivos: {e}")
        
    # Ordenar por fecha descendente (más recientes primero)
    return sorted(backups, key=lambda x: x['date'], reverse=True)
