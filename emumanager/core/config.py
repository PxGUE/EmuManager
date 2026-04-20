import os
import json
import sys
import platform
from pathlib import Path
from typing import Optional

class AppConfig:
    APP_NAME = "EmuManager"
    APP_VERSION = "0.5.0 - alpha"
    MANGO_VERSION = "0.3.0 - alpha"
    IS_DEV_MODE = True 
    
    _is_frozen: bool = False
    _package_root: Path = None  
    _storage_root: Path = None  
    _config_cache: Optional[dict] = None

    @classmethod
    def initialize(cls):
        """
        Orquestador de Rutas: Resuelve el dilema Local-First vs AppData.
        """
        # 0. Raíz del Paquete (Donde vive el código / assets)
        cls._package_root = Path(__file__).resolve().parent.parent

        # 1. PRIORIDAD: MODO DESARROLLO
        # Si estamos programando, usamos la carpeta 'data' del repositorio local.
        if cls.IS_DEV_MODE:
            cls._storage_root = cls._package_root.parent
            cls._is_frozen = False
            return

        # 2. SEGUNDA OPCIÓN: MODO PORTABLE (Producción)
        # Intentamos usar la carpeta del ejecutable si tenemos permisos.
        exe_path = Path(sys.argv[0]).resolve()
        if exe_path.suffix.lower() != ".exe":
            exe_path = Path(sys.executable).resolve()
        
        exe_dir = exe_path.parent
        # Evitar carpetas temporales de Nuitka/PyInstaller
        if "temp" not in str(exe_dir).lower():
            try:
                test_dir = exe_dir / "data"
                test_dir.mkdir(parents=True, exist_ok=True)
                (test_dir / ".w").touch()
                (test_dir / ".w").unlink()
                cls._storage_root = exe_dir
                cls._is_frozen = True
                return
            except:
                pass # No hay permisos de escritura, ir a AppData

        # 3. TERCERA OPCIÓN: APPDATA (Instalado)
        cls._storage_root = cls._get_standard_appdata()
        cls._is_frozen = True

    @classmethod
    def _get_standard_appdata(cls) -> Path:
        if os.name == 'nt':
            appdata = os.getenv('APPDATA')
            base = Path(appdata).resolve() / cls.APP_NAME if appdata else Path.home() / "AppData" / "Roaming" / cls.APP_NAME
        else:
            base = Path.home() / ".local" / "share" / cls.APP_NAME
        base.mkdir(parents=True, exist_ok=True)
        return base

    @classmethod
    def get_package_root(cls) -> Path: return cls._package_root
    
    @classmethod
    def get_storage_root(cls) -> Path: return cls._storage_root

    @classmethod
    def get_asset_path(cls, *parts) -> Path:
        return cls._package_root.joinpath(*parts)

    @classmethod
    def get_app_data_dir(cls) -> Path:
        path = cls._storage_root / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_database_path(cls) -> Path:
        return cls.get_app_data_dir() / "db" / "emumanager.db"

    @classmethod
    def is_frozen(cls) -> bool: return cls._is_frozen

    # --- MÉTODOS DE CONFIGURACIÓN (RESTAURADOS) ---
    @classmethod
    def _get_config_file(cls) -> Path: return cls.get_app_data_dir() / "config.json"

    @classmethod
    def _load_config(cls):
        if cls._config_cache is None:
            config_file = cls._get_config_file()
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        cls._config_cache = json.load(f)
                except Exception: cls._config_cache = {}
            else: cls._config_cache = {}
        return cls._config_cache

    @classmethod
    def _save_config(cls):
        config_file = cls._get_config_file()
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(cls._config_cache, f, indent=4)

    @classmethod
    def get_roms_path(cls) -> str: return cls._load_config().get("roms_path", "")
    
    @classmethod
    def set_roms_path(cls, path: str):
        config = cls._load_config(); config["roms_path"] = str(path); cls._save_config()

    @classmethod
    def get_emulators_path(cls) -> str:
        config = cls._load_config()
        default = str(cls.get_app_data_dir() / "emulators")
        path = config.get("emulators_path", default)
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def set_emulators_path(cls, path: str):
        config = cls._load_config(); config["emulators_path"] = str(path); cls._save_config()

    @classmethod
    def get_language(cls) -> str: return cls._load_config().get("language", "es")
    
    @classmethod
    def set_language(cls, lang: str):
        config = cls._load_config(); config["language"] = str(lang); cls._save_config()

    @classmethod
    def get_gametdb_mode(cls) -> str: return cls._load_config().get("gametdb_mode", "web")
    
    @classmethod
    def set_gametdb_mode(cls, mode: str):
        config = cls._load_config(); config["gametdb_mode"] = str(mode); cls._save_config()

    @classmethod
    def get_discord_rpc_enabled(cls) -> bool: return cls._load_config().get("discord_rpc_enabled", True)
    
    @classmethod
    def set_discord_rpc_enabled(cls, enabled: bool):
        config = cls._load_config(); config["discord_rpc_enabled"] = bool(enabled); cls._save_config()

    @classmethod
    def get_discord_client_id(cls) -> str: return os.getenv("DISCORD_CLIENT_ID", "1225883652615147540")

    @classmethod
    def get_media_dir(cls, platform: str, media_type: str) -> Path:
        base = (cls.get_app_data_dir() / "media").resolve()
        media_dir = (base / platform.lower().lstrip('/') / media_type.lstrip('/')).resolve()
        try: media_dir.relative_to(base)
        except ValueError: raise ValueError("Path Traversal detected")
        media_dir.mkdir(parents=True, exist_ok=True)
        return media_dir

    @classmethod
    def get_screenscraper_user(cls) -> str: return cls._load_config().get("ss_user", "")
    
    @classmethod
    def set_screenscraper_user(cls, user: str):
        config = cls._load_config(); config["ss_user"] = str(user); cls._save_config()

    @classmethod
    def get_screenscraper_pass(cls) -> str:
        from core.security import CredentialsManager
        user = cls.get_screenscraper_user()
        return CredentialsManager.get_user_password("screenscraper", user) if user else ""

    @classmethod
    def set_screenscraper_pass(cls, pwd: str):
        from core.security import CredentialsManager
        user = cls.get_screenscraper_user()
        if user and pwd: CredentialsManager.save_user_password("screenscraper", user, pwd)
