from typing import List, Dict, Optional
from pathlib import Path

try:
    import mango_engine
except ImportError:
    mango_engine = None

from core.logger import EmuLog

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
            "snes": "snes9x",
            "nes": "fceumm",
            "gba": "mgba",
            "gb": "gambatte",
            "gbc": "gambatte",
            "n64": "mupen64plus_next",
            "ps1": "beetle_psx_hw",
            "ps2": "pcsx2",
            "psp": "ppsspp",
            "ds": "desmume",
            "megadrive": "genesis_plus_gx",
            "dreamcast": "flycast"
        }
        return platform_map.get(platform.lower())

    def fetch_available_cores(self) -> List[str]:
        """Obtiene la lista de cores disponibles en el buildbot usando M.A.N.G.O (Rust)."""
        if not mango_engine:
            EmuLog.warning("M.A.N.G.O engine no está disponible para fetch_available_cores")
            return []
        try:
            return mango_engine.fetch_cores()
        except Exception as e:
            EmuLog.error(f"Error fetching cores: {e}")
            return []

    def download_core(self, core_name: str, progress_callback=None) -> Optional[str]:
        """Descarga e instala un core usando M.A.N.G.O (Rust). El callback recibe el progreso (0.0 a 1.0)."""
        if not mango_engine:
            EmuLog.warning("M.A.N.G.O engine no está disponible para download_core")
            return None
        try:
            return mango_engine.download_core(core_name, str(self.cores_path), progress_callback)
        except Exception as e:
            EmuLog.error(f"Error downloading core {core_name}: {e}")
            return None
