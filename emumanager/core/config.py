import os
from pathlib import Path

class AppConfig:
    APP_NAME = "EmuManager"
    
    @classmethod
    def get_app_data_dir(cls) -> Path:
        """
        Retorna el directorio de datos local de la aplicación (Local-First).
        En Windows: %LOCALAPPDATA%/EmuManager
        En Linux/macOS: ~/.local/share/EmuManager
        """
        if os.name == 'nt':
            base_dir = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~')))
        else:
            base_dir = Path(os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share')))
        
        app_dir = base_dir / cls.APP_NAME
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir

    @classmethod
    def get_database_path(cls) -> Path:
        return cls.get_app_data_dir() / "emumanager.db"

    @classmethod
    def get_covers_dir(cls) -> Path:
        covers_dir = cls.get_app_data_dir() / "covers"
        covers_dir.mkdir(parents=True, exist_ok=True)
        return covers_dir
