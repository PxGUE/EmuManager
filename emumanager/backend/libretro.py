from typing import List, Dict, Optional
from pathlib import Path

class LibretroManager:
    """Gestiona cores y configuraciones de Libretro para la emulación."""
    def __init__(self, cores_path: Path):
        self.cores_path = cores_path

    def list_installed_cores(self) -> List[str]:
        """Devuelve una lista de los cores .dll/.so instalados."""
        if not self.cores_path.exists():
            return []
        return [f.stem for f in self.cores_path.glob("*_libretro.*")]

    def get_core_for_platform(self, platform: str) -> Optional[str]:
        """Mapea plataformas a cores sugeridos de libretro."""
        platform_map = {
            "N64": "mupen64plus_next",
            "SNES": "snes9x",
            "PS1": "beetle_psx_hw",
            "GC": "dolphin"
        }
        return platform_map.get(platform)
