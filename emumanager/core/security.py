import keyring
from pathlib import Path
from core.logger import EmuLog

class PathSecurity:
    @staticmethod
    def safe_join(base_path: Path, *parts: str) -> Path | None:
        """
        Une partes de una ruta de forma segura a una base, previniendo Path Traversal.
        Retorna la ruta absoluta si es segura, o None si se detecta un intento de escape.
        """
        try:
            base_resolved = base_path.resolve()
            # Unimos las partes asegurándonos de que no sean tratadas como rutas absolutas
            joined = base_resolved.joinpath(*(p.lstrip('/') for p in parts))
            joined_resolved = joined.resolve()

            # Verificamos si la ruta final sigue estando bajo la base
            if joined_resolved == base_resolved or base_resolved in joined_resolved.parents:
                return joined_resolved

            EmuLog.error(f"⚠️ Security Alert: Intento de acceso no autorizado bloqueado. Base: {base_resolved}, Partes: {parts}")
            return None
        except Exception as e:
            EmuLog.error(f"Error en validación de seguridad de ruta: {e}")
            return None

    @staticmethod
    def sanitize_id(identifier: str) -> str:
        """
        Limpia un identificador para eliminar caracteres peligrosos de rutas.
        """
        # Eliminamos saltos de directorio y separadores de ruta
        return identifier.replace("..", "").replace("/", "").replace("\\", "")

class CredentialsManager:
    @staticmethod
    def save_user_password(service: str, username: str, password: str) -> None:
        """
        Guarda la contraseña del usuario utilizando el keyring del sistema operativo local.
        """
        keyring.set_password(service, username, password)

    @staticmethod
    def get_user_password(service: str, username: str) -> str | None:
        """
        Recupera la contraseña del usuario utilizando el keyring del sistema operativo local.
        """
        return keyring.get_password(service, username)
