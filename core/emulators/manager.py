import os
import json
import time
from core.constants import AVAILABLE_EMULATORS
from .installer import Installer
from .launcher import Launcher

class EmuladorManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        
        self.data_dir = "data"
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.installed_file = os.path.join(self.data_dir, "installed.json")
        self.playtime_file = os.path.join(self.data_dir, "playtime.json")
        self.cache_file = os.path.join(self.data_dir, "releases_cache.json")
        
        config = self._load_config()
        self.install_path = config.get("install_path", "")
        self.roms_path = config.get("roms_path", "")
        self.language = config.get("language", "es")
        
        self.installed_emus = self._load_installed()
        self.release_cache = self._load_cache()
        self.playtimes = self._load_playtime()

        self.installer = Installer(self)
        self.launcher = Launcher(self)

        self._sync_with_disk()

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except: return {}
        return {}

    def _load_installed(self):
        if os.path.exists(self.installed_file):
            try:
                with open(self.installed_file, "r") as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save_installed(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.installed_file, "w") as f:
                json.dump(self.installed_emus, f, indent=4)
        except Exception as e:
            print(f"[DEBUG] Error al guardar {self.installed_file}: {e}")

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

    def _sync_with_disk(self):
        if not self.install_path or not os.path.exists(self.install_path):
            return
        
        updated = False
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
                                        "install_date": "Auto-detectado en " + console_folder
                                    }
                                    updated = True
            if updated:
                self._save_installed()
        except: pass

    def save_config(self, install_path=None, roms_path=None, language=None):
        config = self._load_config()
        if install_path is not None:
            config["install_path"] = install_path
            self.install_path = install_path
        if roms_path is not None:
            config["roms_path"] = roms_path
            self.roms_path = roms_path
            self.crear_carpetas_roms()
        if language is not None:
            config["language"] = language
            self.language = language
            
        with open(self.config_file, "w") as f:
            json.dump(config, f)

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
        return repo_github in self.installed_emus

    # Delegated installer methods
    async def get_valid_emulators(self):
        return await self.installer.get_valid_emulators()

    def instalar_emulador(self, repo_github: str):
        return self.installer.instalar_emulador(repo_github)

    def desinstalar_emulador(self, repo_github: str):
        return self.installer.desinstalar_emulador(repo_github)

    # Delegated launcher methods
    async def lanzar_juego(self, repo_github: str, ruta_rom: str, juego_obj=None):
        return await self.launcher.lanzar_juego(repo_github, ruta_rom, juego_obj)

    def is_emulator_running(self):
        return self.launcher.is_emulator_running()

    def terminar_proceso_actual(self):
        return self.launcher.terminar_proceso_actual()
