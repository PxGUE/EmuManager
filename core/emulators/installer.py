import os
import time
import asyncio
import aiohttp
import requests
import zipfile
import tarfile
import shutil
import platform
from core.constants import AVAILABLE_EMULATORS

class Installer:
    def __init__(self, manager):
        self.manager = manager
        self.headers = {"User-Agent": "EmuManager-App"}
        self.cache_duration = 3600

    def _fetch_release_data(self, repo_github: str):
        now = time.time()
        if repo_github in self.manager.release_cache:
            cache_time, data = self.manager.release_cache[repo_github]
            if now - cache_time < self.cache_duration:
                return data

        try:
            res = requests.get(f"https://api.github.com/repos/{repo_github}/releases", headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                self.manager.release_cache[repo_github] = [now, data]
                self.manager._save_cache()
                return data
        except Exception as e:
            print(f"[DEBUG] Error al buscar releases de {repo_github}: {e}")
        
        return None

    async def check_github_repo(self, repo: str) -> bool:
        def _check():
            try:
                response = requests.get(f"https://api.github.com/repos/{repo}", headers=self.headers, timeout=5)
                if response.status_code in [200, 403, 429]:
                    return True
                return False
            except:
                return True
        return await asyncio.to_thread(_check)

    async def get_valid_emulators(self) -> list:
        try:
            tasks = [self.check_github_repo(emu["github"]) for emu in AVAILABLE_EMULATORS]
            results = await asyncio.gather(*tasks)
            valid_emus = [emu for emu, is_valid in zip(AVAILABLE_EMULATORS, results) if is_valid]
            return valid_emus if valid_emus else AVAILABLE_EMULATORS
        except Exception as e:
            print(f"Error en get_valid_emulators: {e}")
            return AVAILABLE_EMULATORS

    def _get_best_asset(self, assets):
        sys_name = platform.system()
        arch = platform.machine().lower()
        
        is_x64 = any(x in arch for x in ["x86_64", "amd64", "x64"])
        is_arm = any(x in arch for x in ["arm64", "aarch64"])

        if sys_name == "Windows":
            for asset in assets:
                name = asset["name"].lower()
                if any(x in name for x in ["installer", "setup", "msi", ".exe"]): continue
                if name.endswith(".zip") and not any(x in name for x in ["linux", "macos", "android"]):
                    if is_x64 and any(x in name for x in ["x64", "64", "amd64"]): return asset
                    return asset
            
            for asset in assets:
                name = asset["name"].lower()
                if any(x in name for x in ["installer", "setup", "msi", ".exe"]): continue
                if any(name.endswith(ext) for ext in [".7z", ".rar"]): return asset

            for asset in assets:
                name = asset["name"].lower()
                if any(x in name for x in ["installer", "setup", "msi"]): continue
                if name.endswith(".exe") and not any(x in name for x in ["linux", "macos"]): return asset
                
            for asset in assets:
                name = asset["name"].lower()
                if name.endswith(".exe") and not any(x in name for x in ["linux", "macos"]): return asset

        elif sys_name == "Linux":
            for asset in assets:
                name = asset["name"].lower()
                if name.endswith(".appimage") and "libretro" not in name:
                    if is_x64 and any(x in name for x in ["x86_64", "amd64", "x64"]): return asset
                    if is_arm and any(x in name for x in ["arm64", "aarch64"]): return asset
                    return asset
            
            for asset in assets:
                name = asset["name"].lower()
                if any(x in name for x in ["linux", "ubuntu", "debian", "tar.gz", "tar.xz"]):
                    if "libretro" in name or "core" in name: continue
                    return asset
        return None

    async def instalar_emulador(self, repo_github: str):
        if not self.manager.install_path:
            yield "ERROR:No se ha configurado una ruta de instalación."
            return
            
        self.manager.install_path = os.path.abspath(self.manager.install_path)
        os.makedirs(self.manager.install_path, exist_ok=True)

        yield "PROGRESS:0.05|Buscando versiones en GitHub..."
        releases_data = await asyncio.to_thread(self._fetch_release_data, repo_github)
        
        download_url = None
        filename = None

        if releases_data and isinstance(releases_data, list):
            for release in releases_data[:3]:
                if "assets" in release and release["assets"]:
                    asset = self._get_best_asset(release["assets"])
                    if asset:
                        download_url = asset["browser_download_url"]
                        filename = asset["name"]
                        break
        elif releases_data and isinstance(releases_data, dict):
            if "assets" in releases_data:
                asset = self._get_best_asset(releases_data["assets"])
                if asset:
                    download_url = asset["browser_download_url"]
                    filename = asset["name"]

        if not download_url:
            for emu in AVAILABLE_EMULATORS:
                if emu["github"] == repo_github and emu.get("fallback_url"):
                    download_url = emu["fallback_url"]
                    filename = download_url.split("/")[-1]
                    yield "PROGRESS:0.1|Usando descarga de repuesto..."
                    break

        emu_info = next((e for e in AVAILABLE_EMULATORS if e["github"] == repo_github), None)
        subfolder = emu_info["folder"] if emu_info else "Otros"
        
        full_install_path = os.path.abspath(os.path.join(self.manager.install_path, subfolder))
        os.makedirs(full_install_path, exist_ok=True)

        if not download_url:
            yield "ERROR:No se encontró descarga disponible."
            return

        target_file = os.path.abspath(os.path.join(full_install_path, filename))
        yield f"PROGRESS:0.15|Iniciando descarga..."

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url, headers=self.headers, timeout=300) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    with open(target_file, 'wb') as f:
                        async for chunk in r.content.iter_chunked(64 * 1024):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = 0.2 + (downloaded / total_size * 0.7)
                                yield f"PROGRESS:{progress:.2f}|Descargando... {int((downloaded/total_size)*100)}%"
        except Exception as e:
            yield f"ERROR:Falla en descarga: {str(e)}"
            return

        yield "PROGRESS:0.95|Configurando emulador..."
        installed_files = [target_file]
        
        def _extract():
            try:
                if filename.endswith(".zip"):
                    with zipfile.ZipFile(target_file, 'r') as zip_ref:
                        zip_ref.extractall(full_install_path)
                elif filename.endswith((".tar.gz", ".tar.xz")):
                    with tarfile.open(target_file, 'r:*') as tar_ref:
                        tar_ref.extractall(full_install_path)
                elif filename.endswith(".7z"):
                    binary = self._find_7z_binary()
                    extracted = False
                    if binary:
                        try:
                            import subprocess
                            subprocess.run([binary, "x", target_file, f"-o{full_install_path}", "-y"], check=True)
                            extracted = True
                        except: pass
                    
                    if not extracted and platform.system() == "Windows":
                        try:
                            import subprocess
                            subprocess.run(["tar", "-xf", target_file, "-C", full_install_path], check=True)
                            extracted = True
                        except: pass
                    
                    if not extracted:
                        try:
                            import py7zr
                            with py7zr.SevenZipFile(target_file, mode='r') as archive:
                                archive.extractall(path=full_install_path)
                        except Exception as e:
                            print(f"[DEBUG] Fallo 7z: {e}")
                            return False

                for root, dirs, files in os.walk(full_install_path):
                    for f in files:
                        installed_files.append(os.path.join(root, f))
                
                if platform.system() == "Linux":
                    for path in installed_files:
                        low_f = os.path.basename(path).lower()
                        if low_f.endswith(".appimage") or "linux" in low_f or ".x86_64" in low_f or "retroarch" in low_f:
                            try: os.chmod(path, 0o755)
                            except: pass
                return True
            except Exception as e:
                print(f"[DEBUG] Error en extracción: {e}")
                return False

        success_ext = await asyncio.to_thread(_extract)
        if not success_ext:
            yield "ERROR:Falla en la configuración local."
            return
        
        self.manager.installed_emus[repo_github] = {
            "installed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": installed_files,
            "version": releases_data[0]["tag_name"] if isinstance(releases_data, list) and releases_data else "latest"
        }
        self.manager._save_installed()
        self.manager.crear_carpetas_roms(repo_github)
        
        if os.path.exists(target_file):
            yield "PROGRESS:1.0|¡Instalación exitosa!"
        else:
            yield "ERROR:No se encontró el archivo instalado."

    def _find_7z_binary(self):
        paths = ["7z", r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe"]
        import subprocess
        for p in paths:
            try:
                subprocess.run([p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return p
            except: continue
        return None

    async def desinstalar_emulador(self, repo_github: str):
        if repo_github not in self.manager.installed_emus:
            yield "ERROR:El emulador no está registrado."
            return

        yield f"Desinstalando {repo_github}..."
        
        def _delete():
            try:
                info = self.manager.installed_emus[repo_github]
                install_dir = info.get("path")
                if install_dir and os.path.exists(install_dir):
                    shutil.rmtree(install_dir)
                else:
                    files = info.get("files", [])
                    for path in sorted(files, reverse=True):
                        if os.path.isfile(path) or os.path.islink(path):
                            try: os.remove(path)
                            except: pass
                        elif os.path.isdir(path):
                            try: os.rmdir(path)
                            except: pass
                return True
            except Exception as e:
                return False

        success = await asyncio.to_thread(_delete)
        if success:
            del self.manager.installed_emus[repo_github]
            self.manager._save_installed()
            yield f"[ÉXITO] Emulador desinstalado."
        else:
            yield "Error parcial durante la desinstalación."
