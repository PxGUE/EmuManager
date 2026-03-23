import keyring

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
