import os
import requests
import json
import asyncio
import time
import platform
import zipfile
import tarfile
import shutil
import subprocess
from pathlib import Path
import aiohttp
from .constants import AVAILABLE_EMULATORS

class EmuladorManager:
    def __init__(self):
        # Crear carpeta de datos si no existe
        os.makedirs("data", exist_ok=True)
        
        self.data_dir = "data"
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.installed_file = os.path.join(self.data_dir, "installed.json")
        self.cache_file = os.path.join(self.data_dir, "releases_cache.json")
        
        config = self._load_config()
        self.install_path = config.get("install_path", "")
        self.roms_path = config.get("roms_path", "")
        
        self.installed_emus = self._load_installed()
        self.headers = {"User-Agent": "EmuManager-App"}
        self.release_cache = self._load_cache() # {repo: (timestamp, data)}
        self.cache_duration = 3600 # 1 hora
        self.current_process = None # Para rastrear el emulador activo
        self.current_game = None # Información del juego en ejecución
        self._sync_with_disk()

    def _load_installed(self):
        if os.path.exists(self.installed_file):
            try:
                with open(self.installed_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_installed(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.installed_file, "w") as f:
                json.dump(self.installed_emus, f, indent=4)
            print(f"[DEBUG] Guardado exitoso en {self.installed_file}")
        except Exception as e:
            print(f"[DEBUG] Error al guardar {self.installed_file}: {e}")

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(self.release_cache, f, indent=4)
        except:
            pass

    def _sync_with_disk(self):
        """Escanea la carpeta de instalación para auto-detectar emuladores ya descargados."""
        if not self.install_path or not os.path.exists(self.install_path):
            return
        
        updated = False
        try:
            # Escanear subcarpetas (consolas)
            for console_folder in os.listdir(self.install_path):
                console_path = os.path.join(self.install_path, console_folder)
                if os.path.isdir(console_path):
                    for f in os.listdir(console_path):
                        low_f = f.lower()
                        # Buscar coincidencia con emuladores conocidos
                        for emu in AVAILABLE_EMULATORS:
                            repo = emu["github"]
                            repo_name = repo.split("/")[-1].lower()
                            
                            # Si coincide el nombre del archivo con el repo y es ejecutable/appimage
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
        except Exception as e:
            print(f"[DEBUG] Error en sync_with_disk: {e}")

    def esta_instalado(self, repo_github: str) -> bool:
        """Verifica si el emulador está registrado como instalado."""
        return repo_github in self.installed_emus

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self, install_path=None, roms_path=None):
        config = self._load_config()
        if install_path is not None:
            config["install_path"] = install_path
            self.install_path = install_path
        if roms_path is not None:
            config["roms_path"] = roms_path
            self.roms_path = roms_path
            # Al cambiar la ruta de roms, creamos carpetas para los emuladores ya instalados
            self.crear_carpetas_roms()
            
        with open(self.config_file, "w") as f:
            json.dump(config, f)

    def crear_carpetas_roms(self, repo_github=None):
        """Crea las carpetas de ROMs correspondientes en la ruta de juegos."""
        if not self.roms_path or not os.path.exists(self.roms_path):
            return
        
        folders_to_create = []
        if repo_github:
            emu = next((e for e in AVAILABLE_EMULATORS if e["github"] == repo_github), None)
            if emu:
                folders_to_create.append(emu["folder"])
        else:
            # Si no se especifica repo, creamos para todos los emuladores definidos
            # o podrías limitarlo a los instalados: for repo in self.installed_emus:
            for emu in AVAILABLE_EMULATORS:
                folders_to_create.append(emu["folder"])
                    
        for folder in folders_to_create:
            path = os.path.join(self.roms_path, folder)
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                    print(f"[DEBUG] Carpeta de ROMs creada: {path}")
                except Exception as e:
                    print(f"Error creando carpeta {path}: {e}")

    def _fetch_release_data(self, repo_github: str):
        # Revisar caché primero
        now = time.time()
        if repo_github in self.release_cache:
            cache_time, data = self.release_cache[repo_github]
            if now - cache_time < self.cache_duration:
                return data

        # Si no hay caché o expiró, intentar obtener de GitHub
        try:
            # Primero intentar obtener la lista de releases (más robusto que 'latest')
            res = requests.get(f"https://api.github.com/repos/{repo_github}/releases", headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                self.release_cache[repo_github] = [now, data]
                self._save_cache()
                return data
        except Exception as e:
            print(f"[DEBUG] Error al buscar releases de {repo_github}: {e}")
        
        return None

    async def check_github_repo(self, repo: str) -> bool:
        """Verifica si el repositorio de GitHub existe y es accesible."""
        def _check():
            print(f"[DEBUG FROM check_github_repo] Verificando {repo}...")
            try:
                response = requests.get(f"https://api.github.com/repos/{repo}", headers=self.headers, timeout=5)
                # Si recibimos 200, existe. 
                # Si recibimos 403 o 429 (Límite de API), asumimos que existe 
                # para no esconder la lista por error de conexión/límites.
                if response.status_code in [200, 403, 429]:
                    return True
                return False
            except:
                # En caso de error de red, mejor mostrarlo que esconderlo
                return True
        return await asyncio.to_thread(_check)

    async def get_valid_emulators(self) -> list:
        """Devuelve solo los emuladores cuyos repositorios existan."""
        try:
            tasks = [self.check_github_repo(emu["github"]) for emu in AVAILABLE_EMULATORS]
            results = await asyncio.gather(*tasks)
            
            valid_emus = []
            for emu, is_valid in zip(AVAILABLE_EMULATORS, results):
                if is_valid:
                    valid_emus.append(emu)
            
            # Si por alguna razón la lista queda vacía, devolvemos todos 
            # para no romper la experiencia del usuario.
            return valid_emus if valid_emus else AVAILABLE_EMULATORS
        except Exception as e:
            print(f"Error en get_valid_emulators: {e}")
            return AVAILABLE_EMULATORS

    def _get_best_asset(self, assets):
        """Selecciona el mejor asset según el sistema operativo y arquitectura."""
        sys_name = platform.system()
        arch = platform.machine().lower() # e.g. 'x86_64', 'arm64'
        
        # Mapeo de términos comunes de arquitectura
        is_x64 = "x86_64" in arch or "amd64" in arch or "x64" in arch
        is_arm = "arm64" in arch or "aarch64" in arch

        if sys_name == "Linux":
            # 1. Buscar AppImage prioritariamente coincidiendo con arquitectura
            for asset in assets:
                name = asset["name"].lower()
                # IGNORAR archivos libretro o cores (son para RetroArch, no standalone)
                if "libretro" in name or "core" in name:
                    continue
                if name.endswith(".appimage"):
                    if is_x64 and any(x in name for x in ["x86_64", "amd64", "x64"]):
                        return asset
                    if is_arm and any(x in name for x in ["arm64", "aarch64"]):
                        return asset
            
            # 2. Buscar cualquier binario de Linux (tar.gz, zip, etc.)
            for asset in assets:
                name = asset["name"].lower()
                if "libretro" in name or "core" in name:
                    continue
                if any(x in name for x in ["linux", "ubuntu", "debian", "appimage"]):
                    if is_x64 and any(x in name for x in ["x86_64", "amd64", "x64"]):
                        return asset
                    if not any(x in name for x in ["arm", "aarch", "win", "macos"]):
                        return asset # Fallback general para Linux x64
            
            # 3. Último recurso: cualquier AppImage que no sea core
            for asset in assets:
                name = asset["name"].lower()
                if name.endswith(".appimage") and "libretro" not in name:
                    return asset

        elif sys_name == "Windows":
            # Preferir zip o exe con 'win' o 'x64'
            for asset in assets:
                name = asset["name"].lower()
                if name.endswith(".zip") and ("win" in name or ("x64" in name if is_x64 else True)):
                    return asset
                if name.endswith(".exe") and ("installer" not in name):
                    return asset
        return None

    async def instalar_emulador(self, repo_github: str):
        """Descarga e instala el emulador real desde GitHub."""
        if not self.install_path:
            yield "ERROR:No se ha configurado una ruta de instalación."
            return
            
        # Forzar ruta absoluta
        self.install_path = os.path.abspath(self.install_path)
        os.makedirs(self.install_path, exist_ok=True)

        yield "PROGRESS:0.05|Buscando versiones en GitHub..."
        releases_data = await asyncio.to_thread(self._fetch_release_data, repo_github)
        
        download_url = None
        filename = None

        if releases_data and isinstance(releases_data, list):
            # Buscar en los últimos 3 releases por si el más nuevo no tiene assets (ej: Dolphin)
            for release in releases_data[:3]:
                if "assets" in release and release["assets"]:
                    asset = self._get_best_asset(release["assets"])
                    if asset:
                        download_url = asset["browser_download_url"]
                        filename = asset["name"]
                        break
        elif releases_data and isinstance(releases_data, dict):
            # Fallback si solo obtuvimos un objeto (el latest)
            if "assets" in releases_data:
                asset = self._get_best_asset(releases_data["assets"])
                if asset:
                    download_url = asset["browser_download_url"]
                    filename = asset["name"]

        # Si falla el API, intentar con fallback hardcoded si existe
        if not download_url:
            for emu in AVAILABLE_EMULATORS:
                if emu["github"] == repo_github and emu.get("fallback_url"):
                    download_url = emu["fallback_url"]
                    filename = download_url.split("/")[-1]
                    yield "PROGRESS:0.1|Usando de descarga de repuesto..."
                    break

        # Obtener información del emulador para la subcarpeta
        emu_info = next((e for e in AVAILABLE_EMULATORS if e["github"] == repo_github), None)
        subfolder = emu_info["folder"] if emu_info else "Otros"
        
        full_install_path = os.path.abspath(os.path.join(self.install_path, subfolder))
        os.makedirs(full_install_path, exist_ok=True)

        if not download_url:
            yield "ERROR:No se encontró descarga disponible."
            return

        target_file = os.path.abspath(os.path.join(full_install_path, filename))
        yield f"PROGRESS:0.15|Iniciando descarga..."

        # Descarga usando aiohttp para progreso real
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
                                progress = 0.2 + (downloaded / total_size * 0.7) # De 20% a 90%
                                yield f"PROGRESS:{progress:.2f}|Descargando... {int((downloaded/total_size)*100)}%"
        except Exception as e:
            yield f"ERROR:Falla en descarga: {str(e)}"
            return

        yield "PROGRESS:0.95|Configurando emulador..."
        
        # Lista para rastrear archivos instalados
        installed_files = [target_file]
        
        def _extract():
            try:
                # Si es un AppImage o ejecutable directo, solo mover (ya está en destino) y dar permisos
                if filename.endswith(".appimage") or filename.endswith(".exe"):
                    print(f"[DEBUG] No requiere extracción: {filename}")
                elif filename.endswith(".zip"):
                    print(f"[DEBUG] Extrayendo ZIP: {filename}")
                    with zipfile.ZipFile(target_file, 'r') as zip_ref:
                        for member in zip_ref.namelist():
                            full_path = os.path.join(full_install_path, member)
                            installed_files.append(full_path)
                        zip_ref.extractall(full_install_path)
                elif filename.endswith((".tar.gz", ".tar.xz")):
                    print(f"[DEBUG] Extrayendo TAR: {filename}")
                    with tarfile.open(target_file, 'r:*') as tar_ref:
                        for member in tar_ref.getnames():
                            full_path = os.path.join(full_install_path, member)
                            installed_files.append(full_path)
                        tar_ref.extractall(full_install_path)
                elif filename.endswith(".7z"):
                    print(f"[DEBUG] Extrayendo 7Z: {filename}")
                    try:
                        import subprocess
                        subprocess.run(["7z", "x", target_file, f"-o{full_install_path}", "-y"], check=True)
                        # Nota: 7z no devuelve lista de archivos fácilmente por subprocess sin parsear, se asume exito
                    except Exception as e:
                        print(f"[DEBUG] Error al extraer 7z (¿Está instalado 7zip?): {e}")
                        return False
                
                # Permisos de ejecución en Linux
                if platform.system() == "Linux":
                    # Dar permisos a todo lo que parezca ejecutable en la carpeta
                    for root, dirs, files in os.walk(full_install_path):
                        for f in files:
                            path = os.path.join(root, f)
                            low_f = f.lower()
                            if low_f.endswith(".appimage") or "linux" in low_f or ".x86_64" in low_f or "retroarch" in low_f:
                                try:
                                    os.chmod(path, 0o755)
                                    print(f"[DEBUG] Permiso +x dado a: {path}")
                                except:
                                    pass
                return True
            except Exception as e:
                print(f"[DEBUG] Error en extracción: {e}")
                return False

        success_ext = await asyncio.to_thread(_extract)
        if not success_ext:
            yield "ERROR:Falla en la configuración local."
            return
        
        # Guardar en el registro de instalados
        self.installed_emus[repo_github] = {
            "installed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": installed_files,
            "version": releases_data[0]["tag_name"] if isinstance(releases_data, list) and releases_data else "latest"
        }
        self._save_installed()
        
        # Crear carpeta de ROMs para este emulador recién instalado
        self.crear_carpetas_roms(repo_github)
        
        if os.path.exists(target_file):
            yield "PROGRESS:1.0|¡Instalación exitosa!"
        else:
            yield "ERROR:No se encontró el archivo instalado."

    async def desinstalar_emulador(self, repo_github: str):
        """Elimina los archivos del emulador basado en el registro."""
        if repo_github not in self.installed_emus:
            yield "ERROR:El emulador no está registrado."
            return

        yield f"Desinstalando {repo_github}..."
        
        def _delete():
            try:
                info = self.installed_emus[repo_github]
                install_dir = info.get("path")
                
                if install_dir and os.path.exists(install_dir):
                    print(f"[DEBUG] Borrando carpeta completa: {install_dir}")
                    shutil.rmtree(install_dir)
                else:
                    # Fallback por si no tiene 'path' (instalaciones viejas)
                    files = info.get("files", [])
                    for path in sorted(files, reverse=True):
                        if os.path.isfile(path) or os.path.islink(path):
                            try:
                                os.remove(path)
                            except:
                                pass
                        elif os.path.isdir(path):
                            try:
                                os.rmdir(path)
                            except:
                                pass
                return True
            except Exception as e:
                print(f"[DEBUG] Error al borrar: {e}")
                return False

        success = await asyncio.to_thread(_delete)
        if success:
            del self.installed_emus[repo_github]
            self._save_installed()
            yield f"[ÉXITO] Emulador {repo_github} desinstalado."
        else:
            yield "Error parcial durante la desinstalación."

    def is_emulator_running(self):
        """Devuelve True si hay un proceso de emulador activo."""
        if self.current_process:
            return self.current_process.poll() is None
        return False

    def terminar_proceso_actual(self):
        """Cierra el proceso del emulador actual."""
        if self.is_emulator_running():
            try:
                self.current_process.terminate()
                # Esperar un poco a que cierre
                return True
            except Exception as e:
                print(f"[DEBUG] Error al terminar proceso: {e}")
                try:
                    self.current_process.kill()
                    return True
                except:
                    pass
        return False

    async def lanzar_juego(self, repo_github: str, ruta_rom: str, juego_obj=None):
        """Lanza un juego usando el emulador correspondiente."""
        print(f"[DEBUG v2] lanzar_juego llamado para: {juego_obj.get('nombre') if juego_obj else 'Solo emulador'}")
        if repo_github not in self.installed_emus:
            return False, "El emulador no está instalado."

        # Si hay ruta, verificar que exista. Si está vacío, es para abrir solo el emulador.
        if ruta_rom and not os.path.exists(ruta_rom):
            return False, "El archivo del juego no existe."

        try:
            info = self.installed_emus[repo_github]
            files = info.get("files", [])
            
            # Buscar el ejecutable principal (AppImage o exe)
            executable = None
            for f in files:
                low_f = f.lower()
                if low_f.endswith((".appimage", ".exe")) or ("linux" in low_f and "." not in low_f.split("/")[-1]):
                    executable = f
                    break
            
            if not executable and files:
                executable = files[0] # Fallback al primer archivo

            if not executable:
                return False, "No se encontró el ejecutable del emulador."

            print(f"[DEBUG LAUNCH] Lanzando: {executable} con {'ROM' if ruta_rom else 'Interfaz'}")
            
            # Lanzamiento no bloqueante según OS
            args = [executable]
            if ruta_rom:
                args.append(ruta_rom)

            if platform.system() == "Linux":
                self.current_process = subprocess.Popen(args, start_new_session=True)
            else:
                # En Windows, usar shell=True para mayor compatibilidad con rutas
                self.current_process = subprocess.Popen(args, shell=True)
                
            self.current_game = juego_obj
            return True, "¡Abierto correctamente!"
        except Exception as e:
            print(f"[DEBUG LAUNCH] Error: {e}")
            return False, f"Error al lanzar: {e}"

