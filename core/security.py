"""
security.py — Gestión segura de credenciales usando el Almacén del Sistema
Utiliza la librería 'keyring' para guardar API Keys y contraseñas de forma segura.
"""

import keyring
from core.config import APP_NAME

def save_secret(service_id, key, value):
    """
    Guarda un secreto en el almacén del sistema.
    service_id: El ID del proveedor (ej: 'steamgriddb')
    key: El tipo de dato (ej: 'api_key', 'password')
    value: El contenido a guardar
    """
    if not value:
        # Si el valor es vacío, intentamos eliminar el registro anterior por limpieza
        delete_secret(service_id, key)
        return

    try:
        # El identificador del servicio será APP_NAME_serviceID (ej: EmuManager_steamgriddb)
        full_service_name = f"{APP_NAME}_{service_id}"
        keyring.set_password(full_service_name, key, value)
    except Exception as e:
        print(f"[SECURITY] Error al guardar secreto para {service_id}: {e}")

def get_secret(service_id, key):
    """
    Recupera un secreto del almacén del sistema.
    """
    try:
        full_service_name = f"{APP_NAME}_{service_id}"
        return keyring.get_password(full_service_name, key) or ""
    except Exception as e:
        print(f"[SECURITY] Error al recuperar secreto para {service_id}: {e}")
        return ""

def delete_secret(service_id, key):
    """
    Elimina un secreto del almacén del sistema.
    """
    try:
        full_service_name = f"{APP_NAME}_{service_id}"
        # Solo eliminamos si existe para evitar excepciones innecesarias
        if keyring.get_password(full_service_name, key):
            keyring.delete_password(full_service_name, key)
    except Exception:
        pass # Silencioso si no se puede borrar o no existe

def clear_all_secrets(service_id, keys=['api_key', 'user', 'password']):
    """
    Limpia todos los secretos asociados a un servicio específico.
    """
    for k in keys:
        delete_secret(service_id, k)
