import platform
import subprocess
import os
import time
from core.logic.constants import AVAILABLE_EMULATORS

class Launcher:
    """
    Gestiona la ejecuciÃ³n y el monitoreo de procesos de emuladores.
    
    Se encarga de encontrar el ejecutable correcto, aplicar argumentos (tweaks)
    y rastrear el tiempo de juego.
    """
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
                # El emulador se cerrÃ³, guardar tiempo final
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
                
                # Limpiar referencias

                self.current_process = None
                return True
            except Exception as e:
                print(f"[LAUNCHER] Error al terminar proceso con psutil: {e}")
                # Fallback al mÃ©todo estÃ¡ndar si psutil falla
                try:
                    self.current_process.terminate()
                    self.current_process = None
                    return True
                except:
                    pass
        return False

    async def lanzar_juego(self, repo_github: str, ruta_rom: str, juego_obj=None):
        """Lanza un juego de forma asÃ­ncrona sin bloquear la UI."""
        import asyncio
        return await asyncio.to_thread(self._lanzar_juego_sync, repo_github, ruta_rom, juego_obj)

    def _lanzar_juego_sync(self, repo_github: str, ruta_rom: str, juego_obj=None):
        """LÃ³gica sÃ­ncrona de lanzamiento (para ejecutar en hilo separado)."""
        if repo_github not in self.manager.installed_emus:
            return False, "El emulador no estÃ¡ instalado."

        if ruta_rom and not os.path.exists(ruta_rom):
            return False, "El archivo del juego no existe."

        try:
            info = self.manager.installed_emus[repo_github]
            files = info.get("files", [])
            executable = self._encontrar_ejecutable(files)

            if not executable:
                return False, "No se encontrÃ³ el ejecutable. Â¿Se extrajo correctamente?"
            
            args = [executable]
            emu_id = next((e["id"] for e in AVAILABLE_EMULATORS if e["github"] == repo_github), "default")
            args = self.manager.tweak_manager.apply_tweaks(emu_id, args, ruta_rom)
            
            if ruta_rom and ruta_rom not in args:
                args.append(ruta_rom)

            print(f"[LAUNCHER] Ejecutando: {' '.join(args)}")
            cwd = os.path.dirname(executable)

            if platform.system() == "Linux":
                self.current_process = subprocess.Popen(args, cwd=cwd, start_new_session=True)
            else:
                self.current_process = subprocess.Popen(args, cwd=cwd, shell=False)
                
            self.current_game = juego_obj
            self.current_game_start = time.time()
            return True, "Â¡Abierto correctamente!"
        except Exception as e:
            print(f"[LAUNCHER] Error al lanzar: {e}")
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
