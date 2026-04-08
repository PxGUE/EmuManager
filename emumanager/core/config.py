import os
import json
from pathlib import Path
from typing import Optional

class AppConfig:
    APP_NAME = "EmuManager"
    APP_VERSION = "0.3.5 - alpha"
    MANGO_VERSION = "0.2.1 - alpha"
    IS_DEV_MODE = True # Desarrollo activo: Bypass de comprobaciones reales
    _config_cache: Optional[dict] = None
    _app_root: Optional[Path] = None

    @classmethod
    def set_app_root(cls, root: Path):
        cls._app_root = root

    @classmethod
    def get_asset_path(cls, *parts) -> Path:
        """Retorna una ruta absoluta a un recurso/activo del proyecto."""
        if cls._app_root:
            return cls._app_root.joinpath(*parts)
        # Fallback para casos donde no se inicializó
        return Path(__file__).resolve().parent.parent.joinpath(*parts)

    @classmethod
    def get_app_data_dir(cls) -> Path:
        """
        Retorna el directorio de datos local de la aplicación.
        Usa rutas estándar del sistema en modo empaquetado para evitar errores de solo lectura.
        """
        import sys
        
        # Detección Robusta (Igual que en app.py)
        _exe_name = os.path.basename(sys.executable).lower()
        _is_python = _exe_name in ["python.exe", "pythonw.exe", "python", "python3"]
        is_frozen = not _is_python or getattr(sys, 'frozen', False) or '__nuitka_binary__' in sys.modules
        
        if is_frozen:
            if os.name == 'nt':
                # Windows: C:\Users\Nombre\AppData\Roaming\EmuManager
                appdata = os.getenv('APPDATA')
                base_dir = Path(appdata).resolve() / "EmuManager" if appdata else Path.home() / "AppData" / "Roaming" / "EmuManager"
            else:
                # Linux: /home/usuario/.local/share/EmuManager
                base_dir = Path.home() / ".local" / "share" / "EmuManager"
            
            data_dir = base_dir / "data"
        else:
            # Desarrollo: una carpeta 'data' en la raíz del proyecto
            # Asumimos que core/config.py está en emumanager/core/
            project_root = Path(__file__).resolve().parent.parent.parent
            data_dir = project_root / "data"

        
        # Aseguramos que la carpeta exista (en la ruta de usuario, no en el AppImage)
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
                    with open(config_file, 'r', encoding='utf-8') as f:
                        cls._config_cache = json.load(f)
                except Exception:
                    cls._config_cache = {}
            else:
                cls._config_cache = {}
        return cls._config_cache

    @classmethod
    def _save_config(cls):
        config_file = cls._get_config_file()
        with open(config_file, 'w', encoding='utf-8') as f:
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
    def get_emulators_path(cls) -> str:
        config = cls._load_config()
        default_path = str(cls.get_app_data_dir() / "emulators")
        path = config.get("emulators_path", default_path)
        # Aseguramos que el directorio exista
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def set_emulators_path(cls, path: str):
        config = cls._load_config()
        config["emulators_path"] = str(path)
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
    def get_language(cls) -> str:
        return cls._load_config().get("language", "es")

    @classmethod
    def set_language(cls, lang: str):
        config = cls._load_config()
        config["language"] = str(lang)
        cls._save_config()

    @classmethod
    def get_database_path(cls) -> Path:
        return cls.get_app_data_dir() / "db" / "emumanager.db"

    @classmethod
    def get_gametdb_mode(cls) -> str:
        """Retorna 'web' o 'local' para GameTDB."""
        return cls._load_config().get("gametdb_mode", "web")

    @classmethod
    def set_gametdb_mode(cls, mode: str):
        config = cls._load_config()
        config["gametdb_mode"] = str(mode)
        cls._save_config()

    @classmethod
    def get_media_dir(cls, platform: str, media_type: str) -> Path:
        """
        Retorna y asegura la existencia del directorio de medios dinámico.
        Ejemplo: data/media/gba/covers/2d
        """
        # Sanitización de seguridad contra Path Traversal
        # Evitamos que se usen rutas absolutas o saltos de directorio (..)
        # platform y media_type pueden contener subdirectorios legítimos (ej: covers/2d)

        base_media_dir = (cls.get_app_data_dir() / "media").resolve()

        # Unimos las partes de forma segura
        # Al usar platform.lstrip('/') nos aseguramos de que no sea tratada como ruta absoluta por Path()
        media_dir = (base_media_dir / platform.lower().lstrip('/') / media_type.lstrip('/')).resolve()

        # Verificación: El path resultante debe ser estrictamente un hijo de base_media_dir
        try:
            media_dir.relative_to(base_media_dir)
        except ValueError:
            raise ValueError(f"Intento de Path Traversal detectado: {platform}/{media_type}")

        media_dir.mkdir(parents=True, exist_ok=True)
        return media_dir

    @classmethod
    def get_discord_rpc_enabled(cls) -> bool:
        return cls._load_config().get("discord_rpc_enabled", True)

    @classmethod
    def set_discord_rpc_enabled(cls, enabled: bool):
        config = cls._load_config()
        config["discord_rpc_enabled"] = bool(enabled)
        cls._save_config()

    @classmethod
    def get_discord_client_id(cls) -> str:
        """Retorna el Client ID de Discord, priorizando variable de entorno."""
        return os.getenv("DISCORD_CLIENT_ID", "1225883652615147540")
