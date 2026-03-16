import platform
import subprocess
import os
import time
from core.constants import AVAILABLE_EMULATORS

class Launcher:
    def __init__(self, manager):
        self.manager = manager
        self.current_process = None
        self.current_game = None
        self.current_game_start = 0

    def is_emulator_running(self):
        """Devuelve True si hay un proceso de emulador activo."""
        if self.current_process:
            is_running = self.current_process.poll() is None
            if not is_running and self.current_game:
                # El emulador se cerró, guardar tiempo final
                self.manager.update_playtime(self.current_game, self.current_game_start)
                self.current_game = None
                self.current_game_start = 0
            return is_running
        return False

    def terminar_proceso_actual(self):
        """Cierra el proceso del emulador actual y todos sus hijos."""
        if self.is_emulator_running():
            try:
                import psutil
                parent = psutil.Process(self.current_process.pid)
                # Obtenemos todos los hijos recursivamente
                children = parent.children(recursive=True)
                for child in children:
                    try:
                        child.terminate()
                    except:
                        pass
                
                # Terminamos el proceso padre
                parent.terminate()
                
                # Esperamos un momento y forzamos si siguen vivos
                gone, alive = psutil.wait_procs(children + [parent], timeout=3)
                for p in alive:
                    try:
                        p.kill()
                    except:
                        pass
                
                print(f"[DEBUG] Proceso {self.current_process.pid} y sus hijos terminados.")
                self.current_process = None
                return True
            except Exception as e:
                print(f"[DEBUG] Error al terminar proceso con psutil: {e}")
                # Fallback al método estándar si psutil falla
                try:
                    self.current_process.terminate()
                    self.current_process = None
                    return True
                except:
                    pass
        return False

    async def lanzar_juego(self, repo_github: str, ruta_rom: str, juego_obj=None):
        """Lanza un juego usando el emulador correspondiente."""
        print(f"[DEBUG v2] lanzar_juego llamado para: {juego_obj.get('nombre') if juego_obj else 'Solo emulador'}")
        
        if repo_github not in self.manager.installed_emus:
            return False, "El emulador no está instalado."

        # Si hay ruta, verificar que exista. Si está vacío, es para abrir solo el emulador.
        if ruta_rom and not os.path.exists(ruta_rom):
            return False, "El archivo del juego no existe."

        try:
            info = self.manager.installed_emus[repo_github]
            files = info.get("files", [])
            
            # Buscar el ejecutable principal (AppImage, exe) o binario linux
            executable = self._encontrar_ejecutable(files)

            if not executable:
                return False, "No se encontró el ejecutable. ¿Se extrajo correctamente?"

            print(f"[DEBUG LAUNCH] Lanzando: {executable} con {'ROM' if ruta_rom else 'Interfaz'}")
            
            # 1. Base executable
            args = [executable]
            
            # 2. Add Tweaks (Flags) BEFORE the ROM path
            emu_id = next((e["id"] for e in AVAILABLE_EMULATORS if e["github"] == repo_github), "default")
            
            # Load user settings to debug
            user_settings = self.manager.tweak_manager.user_prefs.get(emu_id, {})
            print(f"[DEBUG TWEAKS] User settings for {emu_id}: {user_settings}")
            
            # Pass the current args (with executable) so handler knows the context
            args = self.manager.tweak_manager.apply_tweaks(emu_id, args, ruta_rom)
            
            # 3. Add ROM path at the end (standard for most CLIs)
            if ruta_rom and ruta_rom not in args:
                args.append(ruta_rom)

            print(f"[DEBUG TWEAKS] Argumentos finales: {args}")

            # Usar el directorio del ejecutable como CWD es crucial en Linux para encontrar librerías locales
            cwd = os.path.dirname(executable)

            if platform.system() == "Linux":
                # start_new_session=True evita que el emulador muera si cerramos la app
                self.current_process = subprocess.Popen(args, cwd=cwd, start_new_session=True)
            else:
                # shell=False es necesario para psutil.terminate()
                self.current_process = subprocess.Popen(args, cwd=cwd, shell=False)
                
            self.current_game = juego_obj
            self.current_game_start = time.time()
            return True, "¡Abierto correctamente!"
        except Exception as e:
            print(f"[DEBUG LAUNCH] Error: {e}")
            return False, f"Error al lanzar: {e}"

    def _encontrar_ejecutable(self, files):
        executable = None
        archive_exts = (".zip", ".7z", ".rar", ".tar", ".gz", ".xz")
        
        # 1. Priorizar versiones "Premium" (Qt, GUI) sobre SDL o No-GUI
        # Buscamos ejecutables que NO tengan sdl, nogui, console en el nombre primero
        execs = [f for f in files if f.lower().endswith((".appimage", ".exe")) and not any(x in f.lower() for x in ["installer", "setup", "unins"])]
        
        if execs:
            # Intentar encontrar uno que sea "puro" (ej: mgba.exe vs mgba-sdl.exe)
            puros = [f for f in execs if not any(x in os.path.basename(f).lower() for x in ["-sdl", "sdl", "console", "nogui"])]
            if puros:
                return puros[0]
            return execs[0]
        
        # 2. Si no hay exe, intentar linux binario
        if platform.system() == "Linux":
            for f in files:
                name = os.path.basename(f).lower()
                if "." not in name and not any(x in name for x in archive_exts):
                    return f

        # 3. Fallback
        for f in files:
            if not f.lower().endswith(archive_exts):
                return f
                
        return None
