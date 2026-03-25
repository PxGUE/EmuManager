import os
import json
from pathlib import Path
from typing import Optional

class AppConfig:
    APP_NAME = "EmuManager"
    _config_cache: Optional[dict] = None

    @classmethod
    def get_app_data_dir(cls) -> Path:
        """
        Retorna el directorio de datos local de la aplicación.
        Ahora centralizado en la carpeta 'data/' en la raíz del proyecto.
        """
        # Obtenemos la raíz del proyecto (un nivel arriba de emumanager/core)
        project_root = Path(__file__).resolve().parent.parent.parent
        data_dir = project_root / "data"
        
        # Aseguramos que la carpeta exista
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @classmethod
    def _get_config_file(cls) -> Path:
        return cls.get_app_data_dir() / "config.json"

    @classmethod
    def _load_config(cls):
        if cls._config_cache is None:
            config_file = cls._get_config_file()
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        cls._config_cache = json.load(f)
                except Exception:
                    cls._config_cache = {}
            else:
                cls._config_cache = {}
        return cls._config_cache

    @classmethod
    def _save_config(cls):
        config_file = cls._get_config_file()
        with open(config_file, 'w') as f:
            json.dump(cls._config_cache, f, indent=4)

    @classmethod
    def get_roms_path(cls) -> str:
        config = cls._load_config()
        return config.get("roms_path", "")

    @classmethod
    def set_roms_path(cls, path: str):
        config = cls._load_config()
        config["roms_path"] = str(path)
        cls._save_config()

    @classmethod
    def get_cores_path(cls) -> str:
        config = cls._load_config()
        default_path = str(cls.get_app_data_dir() / "cores")
        path = config.get("cores_path", default_path)
        # Aseguramos que el directorio exista
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def set_cores_path(cls, path: str):
        config = cls._load_config()
        config["cores_path"] = str(path)
        cls._save_config()

    @classmethod
    def get_runner_path(cls) -> str:
        """Retorna la ruta del ejecutable de RetroArch o el emulador global."""
        config = cls._load_config()
        return config.get("runner_path", "retroarch") # Por defecto asume que está en el PATH

    @classmethod
    def set_runner_path(cls, path: str):
        config = cls._load_config()
        config["runner_path"] = str(path)
        cls._save_config()

    @classmethod
    def get_screenscraper_user(cls) -> str:
        return cls._load_config().get("ss_user", "")

    @classmethod
    def set_screenscraper_user(cls, user: str):
        config = cls._load_config()
        config["ss_user"] = str(user)
        cls._save_config()

    @classmethod
    def get_screenscraper_pass(cls) -> str:
        """
        Recupera la contraseña desde el almacén seguro del SO (Keyring)
        Evita almacenar contraseñas en texto plano en config.json
        """
        from core.security import CredentialsManager
        user = cls.get_screenscraper_user()
        if not user:
            return ""
        return CredentialsManager.get_user_password("screenscraper", user) or ""

    @classmethod
    def set_screenscraper_pass(cls, pwd: str):
        """
        Guarda la contraseña en el almacén seguro del SO (Keyring)
        Elimina cualquier rastro anterior del JSON plano.
        """
        from core.security import CredentialsManager
        user = cls.get_screenscraper_user()
        if user and pwd:
            CredentialsManager.save_user_password("screenscraper", user, pwd)
            
            # Limpieza: Aseguramos que NO exista en el JSON
            config = cls._load_config()
            if "ss_pass" in config:
                del config["ss_pass"]
                cls._save_config()

    @classmethod
    def get_database_path(cls) -> Path:

        return cls.get_app_data_dir() / "emumanager.db"

    @classmethod
    def get_media_dir(cls, platform: str, media_type: str) -> Path:
        """
        Retorna y asegura la existencia del directorio de medios dinámico.
        Ejemplo: data/media/gba/covers/2d
        """
        media_dir = cls.get_app_data_dir() / "media" / platform.lower() / media_type
        media_dir.mkdir(parents=True, exist_ok=True)
        return media_dir
