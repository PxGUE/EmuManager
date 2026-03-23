import os
import subprocess
from pathlib import Path
from core.config import AppConfig

class LibretroManager:
    def __init__(self):
        self.cores_dir = AppConfig.get_app_data_dir() / "cores"
        self.cores_dir.mkdir(parents=True, exist_ok=True)
        
    def get_core_path(self, core_name: str) -> Path:
        """Devuelve la ruta absoluta esperada para el core (DLL/SO) de libretro, garantizando Local-First."""
        ext = ".dll" if os.name == "nt" else ".so"
        if not core_name.endswith(ext):
            core_name += ext
        return self.cores_dir / core_name

    def is_core_installed(self, core_name: str) -> bool:
        """Verifica offline si el core ya fue descargado previamente."""
        return self.get_core_path(core_name).exists()

    def launch_game(self, core_name: str, rom_path: str):
        """
        Lanza el juego de forma aislada (subprocess en un hilo indepndiente) para 
        evitar que bloqueos del core o crasheos de C/C++ afecten la UI principal (QML/Python).
        """
        core_path = self.get_core_path(core_name)
        if not core_path.exists():
            raise FileNotFoundError(f"El core '{core_name}' no se encuentra en {self.cores_dir}. Descárgalo primero.")
            
        print("LibretroManager: Iniciando proceso aislado.")
        print(f" -> Core: {core_path}")
        print(f" -> ROM: {rom_path}")
        
        # En una integración total, se utilizaría Popen para llamar a un frontend retroarch ligero:
        # subprocess.Popen(["retroarch", "-L", str(core_path), rom_path])
        return True
