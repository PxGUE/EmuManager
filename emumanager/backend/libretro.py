import os
import platform
from pathlib import Path

try:
    import mango_engine
except ImportError:
    mango_engine = None

from core.logger import EmuLog
from core.security import PathSecurity

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

def _build_core_platform_map() -> dict[str, str]:
    """Crea un mapeo inverso core_id -> plataforma optimizado."""
    mapping = {}
    for plat_name, cores in CORE_DATABASE.items():
        for core_id, _ in cores:
            if core_id not in mapping:
                mapping[core_id] = plat_name
    return mapping

_CORE_PLATFORM_MAP = _build_core_platform_map()

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

    def list_installed_cores(self) -> list[str]:
        """Devuelve una lista de los cores .dll/.so instalados (recursivo)."""
        if not self.cores_path.exists():
            return []
        
        ext = ".dll" if platform.system() == "Windows" else ".so"
        return [f.stem for f in self.cores_path.rglob(f"*_libretro{ext}")]

    def get_core_for_platform(self, platform: str) -> str | None:
        """Obtiene el ID del core sugerido para una plataforma."""
        cores = CORE_DATABASE.get(platform.lower(), [])
        return cores[0][0] if cores else None

    def fetch_filtered_cores(self, active_platforms: list[str]) -> list[dict[str, str]]:
        """
        Obtiene la lista de cores disponibles, pero los filtra para mostrar solo los
        que corresponden a consolas que el usuario tiene juegos (active_platforms).
        Retorna una lista de dicts: {'id': 'snes9x', 'name': 'Snes9x (SNES)'}
        """
        if not mango_engine:
            return []
            
        try:
            available_raw = mango_engine.fetch_cores()
            available_set = set(available_raw)
            
            # Determinar extensión local
            system = platform.system()
            if system == "Windows":
                core_ext = ".dll"
            elif system == "Darwin":
                core_ext = ".dylib"
            else:
                core_ext = ".so"

            # Optimización: Pre-escanear cores instalados usando os.scandir para máximo rendimiento
            installed_set = set()
            cores_path_str = str(self.cores_path)

            if os.path.isdir(cores_path_str):
                valid_exts = (".dll", ".so", ".dylib")
                with os.scandir(cores_path_str) as it1:
                    for entry1 in it1:
                        if entry1.is_dir():
                            p_name = entry1.name.lower()
                            with os.scandir(entry1.path) as it2:
                                for entry2 in it2:
                                    if entry2.is_file() and entry2.name.lower().endswith(valid_exts):
                                        # Guardamos en minúsculas para búsqueda case-insensitive
                                        installed_set.add(f"{p_name}/{entry2.name.lower()}")

            unique_results = []
            seen_ids = set()
            
            # Buscamos en nuestra base de datos para las plataformas activas
            for plat_name in active_platforms:
                platform_lower = plat_name.lower()
                suggestions = CORE_DATABASE.get(platform_lower, [])

                for core_id, display_name in suggestions:
                    # El core_id de Libretro suele terminar en _libretro en el buildbot
                    search_id = f"{core_id}_libretro"

                    # Evitar procesar el mismo core varias veces (de-duplicación temprana)
                    if search_id in seen_ids:
                        continue

                    if search_id in available_set:
                        # Comprobar si ya existe físicamente usando el caché del escaneo (case-insensitive)
                        core_rel_path = f"{platform_lower}/{search_id}{core_ext}".lower()
                        is_installed = core_rel_path in installed_set
                        
                        seen_ids.add(search_id)
                        unique_results.append({
                            "id": search_id,
                            "name": display_name,
                            "platform": plat_name,
                            "isInstalled": is_installed
                        })
                    
            return unique_results
            
        except Exception as e:
            EmuLog.error(f"Error filtrando cores: {e}")
            return []

    def _get_platform_for_core(self, core_id: str) -> str:
        """Busca a qué plataforma pertenece un core_id (limpio o con _libretro)."""
        clean_id = core_id.replace("_libretro", "")
        return _CORE_PLATFORM_MAP.get(clean_id, "unknown")

    def download_core(self, core_name: str, progress_callback=None, status_callback=None) -> str | None:
        """
        Descarga e instala un core usando M.A.N.G.O (Motor Nativo). 
        Ahora lo organiza en subcarpetas por consola.
        """
        if not mango_engine:
            return None
            
        try:
            # Determinar subcarpeta basada en la plataforma
            platform_id = self._get_platform_for_core(core_name)
            target_dir = PathSecurity.safe_join(self.cores_path, platform_id)

            # Verificación de seguridad: asegurar que el directorio está dentro de cores_path
            if not target_dir:
                return None

            target_dir.mkdir(parents=True, exist_ok=True)
            
            EmuLog.info(f"M.A.N.G.O: Instalando core {core_name} en {target_dir}")
            return mango_engine.download_core(core_name, str(target_dir), progress_callback, status_callback)
        except Exception as e:
            EmuLog.error(f"Error downloading core {core_name}: {e}")
            return None

    def uninstall_core(self, core_name: str) -> bool:
        """Elimina el archivo del core del disco."""
        try:
            is_win = platform.system() == "Windows"
            core_ext = ".dll" if is_win else ".so"
            
            platform_id = self._get_platform_for_core(core_name)
            target_file = PathSecurity.safe_join(self.cores_path, platform_id, f"{core_name}{core_ext}")
            
            # Verificación de seguridad: asegurar que el archivo está dentro de cores_path
            if not target_file:
                return False

            if target_file.exists():
                target_file.unlink()
                EmuLog.info(f"Core eliminado del disco: {target_file.name}")
                return True
            return False
        except Exception as e:
            EmuLog.error(f"Error al eliminar core {core_name}: {e}")
            return False
