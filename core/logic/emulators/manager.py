import os
import json
import time
from core.logic.constants import AVAILABLE_EMULATORS
from core.logic.config import resolve_path, normalize_path, DATA_DIR
from .installer import Installer
from .launcher import Launcher
from .tweaks.manager import TweakManager

class EmuladorManager:
    """
    Coordinador central para la gestiÃƒÂ³n de emuladores, ROMs y tiempo de juego.
    
    Esta clase orquestra el instalador, el lanzador y el gestor de 'tweaks'.
    Mantiene el estado de quÃƒÂ© emuladores estÃƒÂ¡n instalados y el registro de configuraciÃƒÂ³n.
    """
    def __init__(self):
        self.data_dir = DATA_DIR
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.installed_file = os.path.join(self.data_dir, "installed.json")
        self.playtime_file = os.path.join(self.data_dir, "playtime.json")
        self.cache_file = os.path.join(self.data_dir, "releases_cache.json")
        
        config = self._load_config()
        self.install_path = config.get("install_path", "")
        self.roms_path = config.get("roms_path", "")
        self.language = config.get("language", "es")
        self.collector_mode = config.get("collector_mode", False)
        
        self.installed_emus = self._load_installed()
        self.release_cache = self._load_cache()
        self.playtimes = self._load_playtime()
        self._is_installed_cache = {} # CachÃƒÂ© para evitar os.path.exists excesivos

        self.installer = Installer(self)
        self.tweak_manager = TweakManager(self.data_dir)
        self.launcher = Launcher(self)

        # No sincronizamos en el constructor para no bloquear el arranque de la UI
        # self._sync_with_disk()

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    # Resolver rutas al cargar
                    if "install_path" in data:
                        data["install_path"] = resolve_path(data["install_path"])
                    if "roms_path" in data:
                        data["roms_path"] = resolve_path(data["roms_path"])
                    return data
            except: return {}
        return {}

    def _load_installed(self):
        if os.path.exists(self.installed_file):
            try:
                with open(self.installed_file, "r") as f:
                    data = json.load(f)
                    # Resolver rutas en emuladores instalados
                    for repo, info in data.items():
                        if "path" in info:
                            info["path"] = resolve_path(info["path"])
                        if "files" in info:
                            info["files"] = [resolve_path(f) for f in info["files"]]
                    return data
            except: return {}
        return {}

    def _save_installed(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            # Normalizar rutas antes de guardar
            save_data = {}
            for repo, info in self.installed_emus.items():
                copy_info = info.copy()
                if "path" in copy_info:
                    copy_info["path"] = normalize_path(copy_info["path"])
                if "files" in copy_info:
                    copy_info["files"] = [normalize_path(f) for f in copy_info["files"]]
                save_data[repo] = copy_info

            with open(self.installed_file, "w") as f:
                json.dump(save_data, f, indent=4)
        except Exception as e:
            print(f"[EMU_MGR] Error al guardar {self.installed_file}: {e}")

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save_cache(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(self.release_cache, f, indent=4)
        except: pass

    def _load_playtime(self):
        if os.path.exists(self.playtime_file):
            try:
                with open(self.playtime_file, "r") as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save_playtime(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.playtime_file, "w") as f:
                json.dump(self.playtimes, f, indent=4)
        except: pass

    def _sync_with_disk(self, force=False):
        """VersiÃƒÂ³n interna sÃƒÂ­ncrona."""
        self._sync_logic(force)

    async def sync_with_disk_async(self, force=False):
        """VersiÃƒÂ³n asÃƒÂ­ncrona que no bloquea el event loop de Qt."""
        import asyncio
        await asyncio.to_thread(self._sync_logic, force)

    def _sync_logic(self, force=False):
        """LÃƒÂ³gica real de sincronizaciÃƒÂ³n (separada para ser llamada sÃƒÂ­ncrona o asÃƒÂ­ncronamente)."""
        if not self.install_path or not os.path.exists(self.install_path):
            return
        
        updated = False
        # 1. Limpiar entradas que ya no existen si forzamos
        if force:
            to_remove = []
            for repo, info in self.installed_emus.items():
                files = info.get("files", [])
                if not files or not os.path.exists(files[0]):
                    to_remove.append(repo)
            for repo in to_remove:
                del self.installed_emus[repo]
                updated = True

        # 2. Escanear nuevas carpetas
        try:
            for console_folder in os.listdir(self.install_path):
                console_path = os.path.join(self.install_path, console_folder)
                if os.path.isdir(console_path):
                    for f in os.listdir(console_path):
                        low_f = f.lower()
                        for emu in AVAILABLE_EMULATORS:
                            repo = emu["github"]
                            repo_name = repo.split("/")[-1].lower()
                            if repo_name in low_f and (low_f.endswith(".appimage") or low_f.endswith(".exe") or "linux" in low_f):
                                if repo not in self.installed_emus:
                                    self.installed_emus[repo] = {
                                        "path": os.path.abspath(console_path),
                                        "files": [os.path.abspath(os.path.join(console_path, f))],
                                        "install_date": "Auto-detectado en " + console_folder,
                                        "version": "detected"
                                    }
                                    updated = True
            if updated:
                self._save_installed()
                # Limpiar la cachÃƒÂ© de verificaciÃƒÂ³n fÃƒÂ­sica
                self._is_installed_cache = {}
        except: pass

    def save_config(self, install_path=None, roms_path=None, language=None, collector_mode=None):
        path_changed = False
        if install_path is not None and install_path != self.install_path:
            self.install_path = install_path
            path_changed = True
        if roms_path is not None:
            self.roms_path = roms_path
            self.crear_carpetas_roms()
        if language is not None:
            self.language = language
        if collector_mode is not None:
            self.collector_mode = collector_mode
            
        config = {
            "install_path": self.install_path,
            "roms_path": self.roms_path,
            "language": self.language,
            "collector_mode": self.collector_mode
        }
        
        try:
            # Normalizar rutas antes de guardar
            save_data = config.copy()
            if "install_path" in save_data:
                save_data["install_path"] = normalize_path(save_data["install_path"])
            if "roms_path" in save_data:
                save_data["roms_path"] = normalize_path(save_data["roms_path"])

            with open(self.config_file, "w") as f:
                json.dump(save_data, f, indent=4)
            if path_changed:
                self._sync_with_disk(force=True)
        except Exception as e:
            print(f"[EMU_MGR] Error al guardar configuraciÃƒÂ³n: {e}")

    def crear_carpetas_roms(self, repo_github=None):
        if not self.roms_path or not os.path.exists(self.roms_path): return
        
        folders_to_create = []
        if repo_github:
            emu = next((e for e in AVAILABLE_EMULATORS if e["github"] == repo_github), None)
            if emu: folders_to_create.append(emu["folder"])
        else:
            for emu in AVAILABLE_EMULATORS:
                folders_to_create.append(emu["folder"])
                    
        for folder in folders_to_create:
            path = os.path.join(self.roms_path, folder)
            if not os.path.exists(path):
                try: os.makedirs(path, exist_ok=True)
                except: pass

    def get_playtime(self, game_path):
        total_seconds = self.playtimes.get(game_path, 0)
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        return total_seconds, hours, minutes

    def update_playtime(self, game_obj, start_time):
        if game_obj and start_time > 0:
            elapsed = time.time() - start_time
            game_path = game_obj.get("ruta")
            if game_path:
                self.playtimes[game_path] = self.playtimes.get(game_path, 0) + elapsed
                self._save_playtime()

    def esta_instalado(self, repo_github: str) -> bool:
        """
        Consulta si un emulador estÃƒÂ¡ instalado con cachÃƒÂ© de verificaciÃƒÂ³n en disco.
        """
        if repo_github not in self.installed_emus:
            return False
        
        # 1. Devolver desde la cachÃƒÂ© de sesiÃƒÂ³n si ya se verificÃƒÂ³ antes
        if repo_github in self._is_installed_cache:
            return self._is_installed_cache[repo_github]
        
        # 2. ValidaciÃƒÂ³n real en disco (Solo ocurre una vez por sesiÃƒÂ³n o tras un cambio)
        info = self.installed_emus[repo_github]
        files = info.get("files", [])
        if not files: 
            self._is_installed_cache[repo_github] = False
            return False
        
        exists = os.path.exists(files[0])
        self._is_installed_cache[repo_github] = exists
        return exists

    # Delegated installer methods
    async def get_valid_emulators(self):
        return await self.installer.get_valid_emulators()

    def instalar_emulador(self, repo_github: str):
        return self.installer.instalar_emulador(repo_github)

    def desinstalar_emulador(self, repo_github: str):
        return self.installer.desinstalar_emulador(repo_github)

    async def instalar_manual(self, emu_info: dict, file_path: str):
        """VersiÃƒÂ³n simplificada para el bridge que retorna (success, msg)"""
        success = False
        last_msg = "Error desconocido"
        try:
            async for step in self.installer.instalar_emulador_local(emu_info["github"], file_path):
                if "ERROR:" in step:
                    return False, step.replace("ERROR:", "")
                if "Ã‚Â¡InstalaciÃƒÂ³n manual exitosa!" in step:
                    success = True
                last_msg = step.split("|")[-1] if "|" in step else step
            return success, last_msg
        except Exception as e:
            return False, str(e)

    # Delegated launcher methods
    async def lanzar_juego(self, repo_github: str, ruta_rom: str, juego_obj=None):
        return await self.launcher.lanzar_juego(repo_github, ruta_rom, juego_obj)

    def is_emulator_running(self):
        return self.launcher.is_emulator_running()

    def terminar_proceso_actual(self):
        return self.launcher.terminar_proceso_actual()
