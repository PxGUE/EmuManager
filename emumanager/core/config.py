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
        return config.get("cores_path", "")

    @classmethod
    def set_cores_path(cls, path: str):
        config = cls._load_config()
        config["cores_path"] = str(path)
        cls._save_config()

    @classmethod
    def get_database_path(cls) -> Path:
        return cls.get_app_data_dir() / "emumanager.db"

    @classmethod
    def get_covers_dir(cls) -> Path:
        covers_dir = cls.get_app_data_dir() / "covers"
        covers_dir.mkdir(parents=True, exist_ok=True)
        return covers_dir
