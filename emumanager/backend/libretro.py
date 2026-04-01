from pathlib import Path
from typing import List, Dict, Optional

try:
    import mango_engine
except ImportError:
    mango_engine = None

from core.logger import EmuLog

# Base de datos de mapeo: Plataforma -> Lista de cores (id_interno, nombre_amigable)
CORE_DATABASE = {
    "snes": [
        ("snes9x", "Snes9x (SNES - Recomendado)"),
        ("bsnes", "bsnes (SNES - Precisión)"),
        ("mesen-s", "Mesen-S (SNES - Calidad)")
    ],
    "nes": [
        ("fceumm", "FCEUmm (NES - Recomendado)"),
        ("nestopia", "Nestopia (NES - Compatibilidad)"),
        ("mesen", "Mesen (NES - Precisión)")
    ],
    "gba": [
        ("mgba", "mGBA (GBA - Recomendado)"),
        ("vba_next", "VBA-Next (GBA - Rendimiento)")
    ],
    "n64": [
        ("mupen64plus_next", "Mupen64Plus-Next (N64 - Recomendado)"),
        ("parallel_n64", "ParaLLEl N64 (N64)")
    ],
    "ps1": [
        ("beetle_psx_hw", "Beetle PSX HW (PS1 - Recomendado)"),
        ("pcsx_rearmed", "PCSX ReARMed (PS1 - Low-end)")
    ],
    "ps2": [("pcsx2", "PCSX2 (PS2 - Alpha)")],
    "psp": [("ppsspp", "PPSSPP (PSP)")],
    "ds": [
        ("desmume", "DeSmuME (DS)"),
        ("melonds", "melonDS (DS)")
    ],
    "gc": [("dolphin", "Dolphin (GameCube/Wii)")],
    "wii": [("dolphin", "Dolphin (GameCube/Wii)")],
    "megadrive": [
        ("genesis_plus_gx", "Genesis Plus GX (Mega Drive)"),
        ("picodrive", "PicoDrive (Mega Drive/32X)")
    ],
    "dreamcast": [("flycast", "Flycast (Dreamcast)")],
    "gb": [("gambatte", "Gambatte (Game Boy)")],
    "gbc": [("gambatte", "Gambatte (Game Boy Color)")]
}

class LibretroManager:
    """Gestiona cores y configuraciones de Libretro para la emulación."""
    def __init__(self, emus_base_path: Path):
        self.base_emulators_path = emus_base_path
        self.retroarch_base_path = emus_base_path / "retroarch"

    @property
    def cores_path(self) -> Path:
        """Ruta global de cores compartida por todos los emuladores."""
        path = self.base_emulators_path / "cores"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def list_installed_cores(self) -> List[str]:
        """Devuelve una lista de los cores .dll/.so instalados (recursivo)."""
        if not self.cores_path.exists():
            return []
        
        import platform
        ext = ".dll" if platform.system() == "Windows" else ".so"
        return [f.stem for f in self.cores_path.rglob(f"*_libretro{ext}")]

    def get_core_for_platform(self, platform: str) -> Optional[str]:
        """Obtiene el ID del core sugerido para una plataforma."""
        cores = CORE_DATABASE.get(platform.lower(), [])
        return cores[0][0] if cores else None

    def fetch_filtered_cores(self, active_platforms: List[str]) -> List[Dict[str, str]]:
        """
        Obtiene la lista de cores disponibles, pero los filtra para mostrar solo los
        que corresponden a consolas que el usuario tiene juegos (active_platforms).
        Retorna una lista de dicts: {'id': 'snes9x', 'name': 'Snes9x (SNES)'}
        """
        if not mango_engine:
            return []
            
        try:
            available_raw = mango_engine.fetch_cores()
            filtered_results = []
            
            # Determinar extensión local
            import platform as py_platform
            is_win = py_platform.system() == "Windows"
            core_ext = ".dll" if is_win else ".so"
            
            # Buscamos en nuestra base de datos para las plataformas activas
            for platform in active_platforms:
                suggestions = CORE_DATABASE.get(platform.lower(), [])
                for core_id, display_name in suggestions:
                    # El core_id de Libretro suele terminar en _libretro en el buildbot
                    search_id = f"{core_id}_libretro"
                    if search_id in available_raw:
                        # Comprobar si ya existe físicamente en cores/PLATFORMA/arch_libretro.ext
                        core_file = self.cores_path / platform.lower() / f"{search_id}{core_ext}"
                        
                        filtered_results.append({
                            "id": search_id,
                            "name": display_name,
                            "platform": platform,
                            "isInstalled": core_file.exists()
                        })
            
            # Eliminar duplicados si una plataforma comparte cores (ej. GB y GBC)
            seen = set()
            unique_results = []
            for item in filtered_results:
                if item["id"] not in seen:
                    seen.add(item["id"])
                    unique_results.append(item)
                    
            return unique_results
            
        except Exception as e:
            EmuLog.error(f"Error filtrando cores: {e}")
            return []

    def _get_platform_for_core(self, core_id: str) -> str:
        """Busca a qué plataforma pertenece un core_id (limpio o con _libretro)."""
        clean_id = core_id.replace("_libretro", "")
        for platform, cores in CORE_DATABASE.items():
            if any(c[0] == clean_id for c in cores):
                return platform
        return "unknown"

    def download_core(self, core_name: str, progress_callback=None, status_callback=None) -> Optional[str]:
        """
        Descarga e instala un core usando M.A.N.G.O (Motor Nativo). 
        Ahora lo organiza en subcarpetas por consola.
        """
        if not mango_engine:
            return None
            
        try:
            # Determinar subcarpeta basada en la plataforma
            platform = self._get_platform_for_core(core_name)
            target_dir = self.cores_path / platform
            target_dir.mkdir(parents=True, exist_ok=True)
            
            EmuLog.info(f"M.A.N.G.O: Instalando core {core_name} en {target_dir}")
            return mango_engine.download_core(core_name, str(target_dir), progress_callback, status_callback)
        except Exception as e:
            EmuLog.error(f"Error downloading core {core_name}: {e}")
            return None

    def uninstall_core(self, core_name: str) -> bool:
        """Elimina el archivo del core del disco."""
        try:
            import platform as py_platform
            is_win = py_platform.system() == "Windows"
            core_ext = ".dll" if is_win else ".so"
            
            platform_id = self._get_platform_for_core(core_name)
            target_file = self.cores_path / platform_id / f"{core_name}{core_ext}"
            
            if target_file.exists():
                target_file.unlink()
                EmuLog.info(f"Core eliminado del disco: {target_file.name}")
                return True
            return False
        except Exception as e:
            EmuLog.error(f"Error al eliminar core {core_name}: {e}")
            return False
