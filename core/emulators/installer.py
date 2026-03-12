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
        self.linux_distro = self._get_linux_distro()

    def _get_linux_distro(self):
        """Detecta la distribución de Linux de forma básica."""
        if platform.system() != "Linux":
            return None
        try:
            # Intentar con la API moderna de Python 3.10+
            if hasattr(platform, "freedesktop_os_release"):
                info = platform.freedesktop_os_release()
                return info.get("ID", "generic").lower()
            
            # Fallback manual leyendo /etc/os-release
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            return line.split("=")[1].strip().strip('"').lower()
        except Exception as e:
            print(f"[DEBUG] Error detectando distro: {e}")
        return "generic"

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

        # Prioridad 1: Coincidencia exacta de arquitectura + extensión preferida
        if sys_name == "Windows":
            # Extensiones preferidas para Windows (portables)
            valid_exts = (".zip", ".7z", ".exe")
            
            # 1.1 Intentar buscar x64 portable
            for asset in assets:
                name = asset["name"].lower()
                # Saltar instaladores
                if any(x in name for x in ["installer", "setup", "msi"]): continue
                # Saltar otras plataformas
                if any(x in name for x in ["linux", "macos", "android", "appimage", "flatpak"]): continue
                
                if name.endswith(valid_exts):
                    if is_x64 and any(x in name for x in ["x64", "64", "amd64", "win64"]): return asset
            
            # 1.2 Intentar buscar cualquier portable para la plataforma
            for asset in assets:
                name = asset["name"].lower()
                if any(x in name for x in ["installer", "setup", "msi"]): continue
                if any(x in name for x in ["linux", "macos", "android", "appimage"]): continue
                if name.endswith(valid_exts):
                    if "win" in name or "windows" in name: return asset

        elif sys_name == "Linux":
            # 1.1 Intentar buscar AppImage (es lo más universal)
            for asset in assets:
                name = asset["name"].lower()
                if name.endswith(".appimage") and "libretro" not in name:
                    if is_x64 and any(x in name for x in ["x86_64", "amd64", "x64"]): return asset
                    if is_arm and any(x in name for x in ["arm64", "aarch64"]): return asset

            # 1.2 Priorizar por distribución (Debian/Ubuntu son comunes)
            distro_keywords = {
                "ubuntu": ["ubuntu", "debian", "pop", "mint"],
                "debian": ["debian", "ubuntu"],
                "arch": ["arch", "manjaro"],
                "fedora": ["fedora", "redhat", "suse"]
            }
            
            # Si detectamos una distro específica, buscar keywords relacionadas
            search_keywords = distro_keywords.get(self.linux_distro, [self.linux_distro])
            
            for asset in assets:
                name = asset["name"].lower()
                if any(ext in name for ext in [".tar.gz", ".tar.xz", ".7z", ".zip", ".deb"]):
                    if "libretro" in name or "core" in name or "windows" in name or "exe" in name: continue
                    # Comprobar arquitectura
                    if is_x64 and not any(x in name for x in ["x86_64", "amd64", "x64", "linux"]): continue
                    
                    # Si coincide con la distro detectada
                    if any(k in name for k in search_keywords):
                        return asset

            # 1.3 Buscar binarios comprimidos genéricos de Linux
            for asset in assets:
                name = asset["name"].lower()
                if any(ext in name for ext in [".tar.gz", ".tar.xz", ".7z", ".zip"]):
                    if "libretro" in name or "core" in name: continue
                    if "windows" in name or "win64" in name or "exe" in name: continue
                    if is_x64 and any(x in name for x in ["x86_64", "amd64", "x64", "linux"]): return asset

        # Fallback genérico: el primero que parezca portable y no sea de otra arquitectura
        for asset in assets:
            name = asset["name"].lower()
            if is_x64 and any(x in name for x in ["arm64", "aarch64", "armv7"]): continue
            if sys_name == "Windows" and any(x in name for x in ["linux", "macos", "appimage"]): continue
            if sys_name == "Linux" and any(x in name for x in ["windows", "win64", "win32", ".exe"]): continue
            
            if sys_name == "Windows" and name.endswith((".zip", ".7z")): return asset
            if sys_name == "Linux" and (name.endswith(".appimage") or ".tar" in name): return asset
            
        return None

    async def instalar_emulador(self, repo_github: str):
        if not self.manager.install_path:
            yield "ERROR:No se ha configurado una ruta de instalación."
            return
            
        self.manager.install_path = os.path.abspath(self.manager.install_path)
        os.makedirs(self.manager.install_path, exist_ok=True)

        emu_info = next((e for e in AVAILABLE_EMULATORS if e["github"] == repo_github), None)
        
        # Determinar el repo real según plataforma
        target_repo = repo_github
        if emu_info:
            if platform.system() == "Windows" and emu_info.get("github_win"):
                target_repo = emu_info["github_win"]
            elif platform.system() == "Linux" and emu_info.get("github_linux"):
                target_repo = emu_info["github_linux"]

        yield "PROGRESS:0.05|Buscando versiones en GitHub..."
        releases_data = await asyncio.to_thread(self._fetch_release_data, target_repo)
        
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
                if emu["github"] == repo_github:
                    # Intentar fallback específico por OS
                    if platform.system() == "Windows" and emu.get("fallback_win"):
                        download_url = emu["fallback_win"]
                    elif platform.system() == "Linux" and emu.get("fallback_linux"):
                        download_url = emu["fallback_linux"]
                    else:
                        download_url = emu.get("fallback_url")
                        
                    if download_url:
                        filename = download_url.split("/")[-1]
                        yield "PROGRESS:0.1|Usando descarga de repuesto..."
                    break

        emu_info = next((e for e in AVAILABLE_EMULATORS if e["github"] == repo_github), None)
        subfolder = emu_info["folder"] if emu_info else "Otros"
        
        full_install_path = os.path.abspath(os.path.join(self.manager.install_path, subfolder))
        os.makedirs(full_install_path, exist_ok=True)

        if not download_url:
            sys_info = f"{platform.system()} ({platform.machine()})"
            if platform.system() == "Linux":
                sys_info += f" - Distro: {self.linux_distro}"
            
            yield f"ERROR:No se encontró una versión compatible para {sys_info}."
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

    async def instalar_emulador_local(self, repo_github: str, local_zip_path: str):
        """Instala un emulador desde un archivo local proporcionado por el usuario."""
        if not self.manager.install_path:
            yield "ERROR:No se ha configurado una ruta de instalación."
            return

        emu_info = next((e for e in AVAILABLE_EMULATORS if e["github"] == repo_github), None)
        subfolder = emu_info["folder"] if emu_info else "Otros"
        full_install_path = os.path.abspath(os.path.join(self.manager.install_path, subfolder))
        os.makedirs(full_install_path, exist_ok=True)

        filename = os.path.basename(local_zip_path)
        target_file = os.path.join(full_install_path, filename)

        yield f"PROGRESS:0.2|Copiando archivo {filename}..."
        try:
            await asyncio.to_thread(shutil.copy2, local_zip_path, target_file)
        except Exception as e:
            yield f"ERROR:Error al copiar archivo: {e}"
            return

        yield "PROGRESS:0.5|Extrayendo archivos..."
        success_ext, installed_files = await self._ejecutar_extraccion(target_file, filename, full_install_path)

        if not success_ext:
            yield "ERROR:Falla en la extracción manual."
            return

        self.manager.installed_emus[repo_github] = {
            "installed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": installed_files,
            "version": "manual"
        }
        self.manager._save_installed()
        self.manager.crear_carpetas_roms(repo_github)
        yield "PROGRESS:1.0|¡Instalación manual exitosa!"

    async def _ejecutar_extraccion(self, target_file, filename, full_install_path):
        """Lógica común de extracción."""
        installed_files = [target_file]

        def _extract():
            try:
                if filename.lower().endswith(".zip"):
                    with zipfile.ZipFile(target_file, 'r') as zip_ref:
                        zip_ref.extractall(full_install_path)
                elif filename.lower().endswith((".tar.gz", ".tar.xz")):
                    with tarfile.open(target_file, 'r:*') as tar_ref:
                        tar_ref.extractall(full_install_path)
                elif filename.lower().endswith(".7z"):
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
                            # Windows sometimes has tar even if binary not in paths
                            subprocess.run(["tar", "-axf", target_file, "-C", full_install_path], check=True)
                            extracted = True
                        except: pass

                    if not extracted:
                        try:
                            import py7zr
                            with py7zr.SevenZipFile(target_file, mode='r') as archive:
                                archive.extractall(path=full_install_path)
                        except Exception as e:
                            print(f"[DEBUG] Fallo 7z local: {e}")
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

        success = await asyncio.to_thread(_extract)
        return success, installed_files

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
