"""
bridge.py — Capa de comunicación entre Python y QML.
Expone la lógica de EmuladorManager y el Traductor a la interfaz declarativa.
"""

from PySide6.QtCore import QObject, Slot, Property, Signal, QUrl
from core.i18n import TRANSLATIONS
import core.scanner as scanner
from core.constants import AVAILABLE_EMULATORS
import os
from core.artwork import obtener_ruta_caratula

class AppBridge(QObject):
    # Señales para notificar cambios a QML
    languageChanged = Signal(str)
    statsUpdated = Signal()
    configUpdated = Signal()
    downloadProgress = Signal(str, float) # url, progress
    downloadFinished = Signal(str, bool, str) # url, success, message
    scanProgress = Signal(float, str) # progress 0.0-1.0, current task/game name
    
    def __init__(self, emu_manager, translator):
        super().__init__()
        self.emu_manager = emu_manager
        self.translator = translator
        self._current_lang = emu_manager.language
        
        # Conectar señales del manager al bridge si existen, 
        # o inyectar callbacks en las funciones de descarga
        self._setup_manager_links()
        

    @Property(str, notify=languageChanged)
    def currentLanguage(self):
        return self._current_lang

    @Slot(str)
    def changeLanguage(self, lang):
        if lang != self._current_lang:
            self._current_lang = lang
            self.emu_manager.save_config(language=lang)
            self.translator.set_language(lang)
            self.languageChanged.emit(lang)

    @Slot(str, result=str)
    def translate(self, key):
        """Traduce una clave usando el motor actual."""
        return self.translator.t(key)

    @Slot(str, str, result=str)
    def translateWithArg(self, key, arg):
        """Traduce una clave con un argumento (ej: versión)."""
        return self.translator.t(key, str(arg))

    @Slot(str, list, result=str)
    def translateWithArgs(self, key, args):
        """Traduce una clave con múltiples argumentos."""
        return self.translator.t(key, *[str(a) for a in args])

    @Property(list, notify=statsUpdated)
    def allEmulators(self):
        """Lista de consolas únicas con sus emuladores asociados."""
        from core.constants import AVAILABLE_EMULATORS
        consoles = {}
        
        for emu in AVAILABLE_EMULATORS:
            c_id = emu["console_id"]
            is_installed = self.emu_manager.esta_instalado(emu["github"])
            
            if c_id not in consoles:
                consoles[c_id] = {
                    "id": c_id,
                    "name": emu["console"], # El nombre de la consola
                    "accentColor": emu.get("color", "#4da6ff"),
                    "emulators": []
                }
            
            consoles[c_id]["emulators"].append({
                "id": emu["id"],
                "name": emu["name"],
                "github": emu["github"],
                "isInstalled": is_installed,
                "description": emu["description"]
            })

        # Marcar la consola como instalada si al menos uno de sus emuladores lo está
        for c in consoles.values():
            c["isInstalled"] = any(e["isInstalled"] for e in c["emulators"])
            # Ordenar emuladores: instalados primero
            c["emulators"].sort(key=lambda x: x["isInstalled"], reverse=True)
            
        return list(consoles.values())

    def _setup_manager_links(self):
        """No longer needed as we'll handle the iteration in the slots."""
        pass

    @Slot(str)
    def installEmulator(self, github_url):
        print(f"[DEBUG] Slot installEmulator llamado para: {github_url}")
        import asyncio
        async def do_install():
            print(f"[DEBUG] Iniciando tarea do_install para: {github_url}")
            success = False
            message = "Error desconocido"
            try:
                # Iterar sobre el generador asíncrono del instalador
                async for step in self.emu_manager.instalar_emulador(github_url):
                    print(f"[DEBUG] Proceso instalación {github_url}: {step}")
                    
                    if step.startswith("PROGRESS:"):
                        try:
                            # Formato "PROGRESS:0.5|Mensaje"
                            partes = step.split("|")
                            prog_str = partes[0].split(":")[1]
                            prog_val = float(prog_str)
                            self.downloadProgress.emit(github_url, prog_val)
                            
                            # Si es el 100% o contiene éxito, marcar como éxito provisional
                            if len(partes) > 1:
                                msg_part = partes[1].lower()
                                if "éxito" in msg_part or "exitosa" in msg_part:
                                    success = True
                                    message = partes[1]
                                elif prog_val >= 1.0:
                                    success = True
                                    message = partes[1]
                        except: pass
                    elif step.startswith("ERROR:"):
                        message = step.split(":", 1)[1]
                        success = False
                    elif "éxito" in step.lower() or "exitosa" in step.lower():
                        success = True
                        message = step
                
                print(f"[DEBUG] Finalizado do_install {github_url}: {success} - {message}")
                self.downloadFinished.emit(github_url, success, message)
                if success:
                    self.statsUpdated.emit()
            except Exception as e:
                print(f"[DEBUG] Excepción en do_install {github_url}: {e}")
                self.downloadFinished.emit(github_url, False, str(e))
        
        asyncio.create_task(do_install())

    @Slot(str)
    def uninstallEmulator(self, github_url):
        print(f"[DEBUG] Slot uninstallEmulator llamado para: {github_url}")
        import asyncio
        async def do_uninstall():
            print(f"[DEBUG] Iniciando tarea do_uninstall para: {github_url}")
            success = False
            message = "Error al desinstalar"
            try:
                async for step in self.emu_manager.desinstalar_emulador(github_url):
                    print(f"[DEBUG] Proceso desinstalación {github_url}: {step}")
                    low_step = step.lower()
                    if "éxito" in low_step or "desinstalado" in low_step:
                        success = True
                        message = step
                    elif "error" in low_step:
                        success = False
                        message = step
                
                print(f"[DEBUG] Finalizado do_uninstall {github_url}: {success} - {message}")
                self.downloadFinished.emit(github_url, success, message)
                self.statsUpdated.emit()
            except Exception as e:
                print(f"[DEBUG] Excepción en do_uninstall {github_url}: {e}")
                self.downloadFinished.emit(github_url, False, str(e))

        asyncio.create_task(do_uninstall())

    @Slot(str)
    def openEmulatorFolder(self, github_url):
        info = self.emu_manager.installed_emus.get(github_url)
        if info:
            files = info.get("files", [])
            if files:
                path = os.path.dirname(files[0])
                from PySide6.QtGui import QDesktopServices
                from PySide6.QtCore import QUrl
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    @Slot(str, str)
    def manualInstall(self, github_url, file_path):
        import asyncio
        async def do_manual():
            emu = next((e for e in AVAILABLE_EMULATORS if e["github"] == github_url), None)
            if not emu:
                self.downloadFinished.emit(github_url, False, self.translator.t("dl_err_emu_not_found"))
                return
                
            success, msg = await self.emu_manager.instalar_manual(emu, file_path)
            self.downloadFinished.emit(github_url, success, msg)
            if success:
                self.statsUpdated.emit()
                
        asyncio.create_task(do_manual())

    @Slot(str)
    def openManualUrl(self, github_url):
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        emu = next((e for e in AVAILABLE_EMULATORS if e["github"] == github_url), None)
        if emu:
            url = emu.get("manual_url", emu.get("github"))
            QDesktopServices.openUrl(QUrl(url))

    # --- DATOS PARA DASHBOARD ---
    @Property(dict, notify=statsUpdated)
    def dashboardStats(self):
        biblioteca = scanner.cargar_biblioteca_cache()
        installed = sum(1 for emu in AVAILABLE_EMULATORS if self.emu_manager.esta_instalado(emu["github"]))
        total_seconds = sum(self.emu_manager.get_playtime(j.get("ruta", ""))[0] for j in biblioteca)
        total_hours = int(total_seconds // 3600)
        total_mins = int((total_seconds % 3600) // 60)
        
        # Formatear tiempo total localizado
        if total_hours > 0:
            time_display = self.translator.t("dash_hours_suffix", total_hours, total_mins)
        elif total_mins > 0:
            time_display = self.translator.t("dash_mins_suffix", total_mins)
        else:
            time_display = "0h"

        return {
            "installed": installed,
            "totalRoms": len(biblioteca),
            "totalConsoles": len(set(j.get("id_emu") for j in biblioteca)),
            "totalHours": total_hours,
            "totalTimeDisplay": time_display
        }

    @Property(list, notify=statsUpdated)
    def recentActivity(self):
        biblioteca = scanner.cargar_biblioteca_cache()
        juegos_con_tiempo = []
        for j in biblioteca:
            s, h, m = self.emu_manager.get_playtime(j.get("ruta", ""))
            if s > 0:
                emu = next((e for e in AVAILABLE_EMULATORS if e["id"] == j.get("id_emu")), {})
                color = emu.get("color", "#4da6ff")
                if h > 0: time_str = self.translator.t("dash_hours_suffix", h, m)
                elif m > 0: time_str = self.translator.t("dash_mins_suffix", m)
                else: time_str = self.translator.t("dash_less_min")
                
                juegos_con_tiempo.append({
                    "name": j["nombre"],
                    "console": j.get("consola", ""),
                    "playtime": time_str,
                    "color": color,
                    "seconds": s,
                    "path": j.get("ruta", ""),
                    "id_emu": j.get("id_emu", ""),
                    "cover": QUrl.fromLocalFile(obtener_ruta_caratula(j.get("ruta", ""))).toString() if os.path.exists(obtener_ruta_caratula(j.get("ruta", ""))) else ""
                })
        
        juegos_con_tiempo.sort(key=lambda x: x["seconds"], reverse=True)
        return juegos_con_tiempo[:10]

    @Property(dict, notify=statsUpdated)
    def systemStatus(self):
        emus_path = self.emu_manager.install_path
        roms_path = self.emu_manager.roms_path
        return {
            "emusPath": emus_path,
            "emusPathExists": os.path.exists(emus_path) if emus_path else False,
            "romsPath": roms_path,
            "romsPathExists": os.path.exists(roms_path) if roms_path else False,
            "installedEmus": [
                {
                    "name": emu["name"],
                    "console": self.translator.t(f"emu_{emu['id']}_console", emu.get("console", "SYSTEM")),
                    "color": emu.get("color", "#4da6ff")
                }
                for emu in AVAILABLE_EMULATORS 
                if self.emu_manager.esta_instalado(emu["github"])
            ]
        }

    @Slot()
    def refreshDashboard(self):
        self.statsUpdated.emit()

    # --- CONFIGURACIÓN (SETTINGS) ---
    @Property(str, notify=configUpdated)
    def installPath(self):
        return self.emu_manager.install_path or ""

    @Property(str, notify=configUpdated)
    def romsPath(self):
        return self.emu_manager.roms_path or ""

    @Slot()
    def browseInstallPath(self):
        from PySide6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(None, self.translator.t("set_dlg_emus"), self.installPath)
        if path:
            self.emu_manager.install_path = path
            self.emu_manager.save_config()
            self.configUpdated.emit()

    @Slot()
    def browseRomsPath(self):
        from PySide6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(None, self.translator.t("set_dlg_roms"), self.romsPath)
        if path:
            self.emu_manager.roms_path = path
            self.emu_manager.save_config()
            self.configUpdated.emit()

    @Slot()
    def openInstallFolder(self):
        if self.installPath:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.installPath))

    @Slot()
    def openRomsFolder(self):
        if self.romsPath:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.romsPath))

    @Slot(bool, bool, bool)
    def scanGames(self, dl_artwork=True, dl_backgrounds=True, dl_metadata=True):
        import asyncio
        import traceback
        from core.scanner import escanear_roms, asdict
        
        async def do_scan():
            try:
                print(f"[BRIDGE] Iniciando proceso de escaneo (Arte={dl_artwork}, Fondos={dl_backgrounds}, Meta={dl_metadata})")
                self.scanProgress.emit(0.0, self.translator.t("dl_scrap_scanning"))
                
                # 1. Escanear archivos
                juegos_obj = await escanear_roms(self.emu_manager.roms_path)
                library_dicts = [asdict(j) for j in juegos_obj]
                self.statsUpdated.emit()
                
                # 2. Fondos
                if dl_backgrounds:
                    self.scanProgress.emit(0.1, self.translator.t("lib_status_artwork"))
                    from core.artwork import descargar_fondos_consolas
                    def on_bg_progress(curr, total, name):
                        # 10% to 20% range for backgrounds
                        prog = 0.1 + (curr / total) * 0.1
                        self.scanProgress.emit(prog, self.translator.t("dl_status_bg", name))

                    stats_bg = await descargar_fondos_consolas(on_progress=on_bg_progress)
                    print(f"[BRIDGE] Fondos completados: {stats_bg}")
                    self.statsUpdated.emit()

                # 3. Artwork
                if dl_artwork:
                    self.scanProgress.emit(0.2, self.translator.t("lib_status_artwork"))
                    from core.artwork import descargar_caratulas_biblioteca
                    def on_art_progress(curr, total, name):
                        # 20% to 60% range for artwork
                        prog = 0.2 + (curr / total) * 0.4
                        self.scanProgress.emit(prog, self.translator.t("dl_status_art", name))
                    
                    emu_map = {e["id"]: e for e in AVAILABLE_EMULATORS}
                    stats_art = await descargar_caratulas_biblioteca(library_dicts, emu_map, on_progress=on_art_progress)
                    print(f"[BRIDGE] Artwork completado: {stats_art}")
                    self.statsUpdated.emit()

                # 4. Metadatos
                if dl_metadata:
                    self.scanProgress.emit(0.6, self.translator.t("lib_status_processing"))
                    from core.metadata import descargar_metadata_biblioteca
                    def on_meta_progress(curr, total, name):
                        # 60% to 100% range for metadata
                        prog = 0.6 + (curr / total) * 0.4
                        self.scanProgress.emit(prog, self.translator.t("dl_status_meta", name))

                    emu_map = {e["id"]: e for e in AVAILABLE_EMULATORS}
                    stats_meta = await descargar_metadata_biblioteca(library_dicts, emu_map, on_progress=on_meta_progress)
                    print(f"[BRIDGE] Metadatos completados: {stats_meta}")
                    self.statsUpdated.emit()
                
                print("[BRIDGE] Proceso de sincronización finalizado con éxito.")
                self.scanProgress.emit(1.0, self.translator.t("lib_status_complete"))
                self.statsUpdated.emit()
                
                # Reset progress after a short delay
                await asyncio.sleep(3)
                self.scanProgress.emit(0.0, "")
                
            except Exception as e:
                print(f"[BRIDGE] ERROR EN ESCANEO COMPLETO: {e}")
                self.scanProgress.emit(0.0, f"Error: {str(e)}")
                traceback.print_exc()
            
        asyncio.create_task(do_scan())

    @Property(list, notify=configUpdated)
    def scraperProviders(self):
        from core.metadata import get_providers_config
        return get_providers_config()

    @Slot(str, bool)
    def toggleProvider(self, provider_id, enabled):
        from core.metadata import get_providers_config
        providers = get_providers_config()
        for p in providers:
            if p["id"] == provider_id:
                p["enabled"] = enabled
                break
        self._save_scrapers_config(providers)
        self.configUpdated.emit()

    def _save_scrapers_config(self, providers):
        path = os.path.join("data", "scrapers_config.json")
        import json
        clean_data = []
        secrets_blacklist = ["api_key", "user", "password"]
        for p in providers:
            clean_p = p.copy()
            for key in secrets_blacklist:
                if key in clean_p: del clean_p[key]
            clean_data.append(clean_p)
        os.makedirs("data", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=2)

    @Slot(str, str, result=str)
    def getSecret(self, provider_id, key):
        import core.security as security
        return security.get_secret(provider_id, key) or ""

    @Slot(str, str, str)
    def saveSecret(self, provider_id, key, value):
        import core.security as security
        security.save_secret(provider_id, key, value)
        self.configUpdated.emit()

    @Slot(str)
    def clearSecrets(self, provider_id):
        import core.security as security
        security.clear_all_secrets(provider_id)
        # Notificar al sistema que los stats/config han cambiado para refrescar la UI
        self.configUpdated.emit()
        # Forzar refresco de la propiedad scraperProviders
        self.languageChanged.emit(self._current_lang) 

    # --- BIBLIOTECA (LIBRARY) ---
    @Property(list, notify=statsUpdated)
    def scannedConsoles(self):
        print("[BRIDGE] scannedConsoles: Checking installed systems...")
        lib = scanner.cargar_biblioteca_cache()
        if not lib:
            # Si no hay juegos escaneados, aún podemos mostrar sistemas instalados vacíos
            print("[BRIDGE] scannedConsoles: Library cache empty, checking for installed emus only.")
            
        result = []
        # Agrupar juegos por plataforma para contar rápido
        from collections import defaultdict
        game_counts = defaultdict(int)
        game_playtimes = defaultdict(float)
        for juego in lib:
            pid = juego.get("id_emu")
            if pid:
                game_counts[pid] += 1
                game_playtimes[pid] += float(juego.get("playtime_seconds", 0))

        for emu in AVAILABLE_EMULATORS:
            count = game_counts.get(emu["id"], 0)
            is_installed = self.emu_manager.esta_instalado(emu.get("github", "")) # Fallback safe
            
            if is_installed:
                total_s = game_playtimes.get(emu["id"], 0)
                
                from core.artwork import obtener_ruta_fondo_consola
                bg_raw = obtener_ruta_fondo_consola(emu)
                bg_url = QUrl.fromLocalFile(bg_raw).toString() if os.path.exists(bg_raw) else ""
                
                result.append({
                    "id": emu["id"],
                    "name": emu["console"],      # Title: Console Name
                    "emu_name": emu["name"],      # Subtitle: Emulator Name
                    "count": count,
                    "playtime": f"{int(total_s // 3600)}h {int((total_s % 3600) // 60)}m",
                    "color": emu.get("color", "#4da6ff"),
                    "background": bg_url
                })
        
        # Sort by count (filled consoles first)
        result.sort(key=lambda x: x["count"], reverse=True)
        found_names = [r["name"] for r in result]
        print(f"[BRIDGE] scannedConsoles: {len(result)} consoles found: {found_names}")
        return result

    @Slot(str, result=list)
    def getGamesForConsole(self, console_id):
        biblioteca = scanner.cargar_biblioteca_cache()
        from core.metadata import obtener_metadata_local
        
        games = []
        for j in biblioteca:
            if j.get("id_emu") == console_id:
                ruta = j.get("ruta", "")
                s, h, m = self.emu_manager.get_playtime(ruta)
                cover_raw = obtener_ruta_caratula(ruta)
                cover_url = QUrl.fromLocalFile(cover_raw).toString() if os.path.exists(cover_raw) else ""
                
                # Obtener metadatos locales (Scraped)
                meta = obtener_metadata_local(ruta)
                
                games.append({
                    "name": j["nombre"],
                    "title": meta.get("title") or j["nombre"],
                    "path": ruta,
                    "console": j.get("consola", ""),
                    "playtime": f"{h}h {m}m" if h > 0 else f"{m}m",
                    "cover": cover_url,
                    "id_emu": console_id,
                    "isFavorite": scanner.es_favorito(ruta),
                    
                    # Campos de Metadata Extras para el panel de info
                    "description": meta.get("description", ""),
                    "developer": meta.get("developer") or meta.get("publisher", "Desconocido"),
                    "year": meta.get("year", "N/A"),
                    "rating": float(meta.get("rating", 0)),
                    "genre": meta.get("genre", "General")
                })
        return games

    @Slot(str, str)
    def launchGame(self, game_path, emu_id):
        biblioteca = scanner.cargar_biblioteca_cache()
        game = next((j for j in biblioteca if j["ruta"] == game_path), None)
        if game:
            emu_info = next((e for e in AVAILABLE_EMULATORS if e["id"] == emu_id), None)
            if emu_info:
                async def do_launch():
                    success, msg = await self.emu_manager.lanzar_juego(emu_info["github"], game_path, game)
                    if success:
                        self.statsUpdated.emit()
                import asyncio
                asyncio.create_task(do_launch())

    @Slot(str, result=bool)
    def toggleFavorite(self, game_path):
        is_fav = scanner.toggle_favorito(game_path)
        self.statsUpdated.emit()
        return is_fav

    @Slot(str, result=bool)
    def isFavorite(self, game_path):
        return scanner.es_favorito(game_path)

    # --- CONTROL DE EJECUCIÓN ---
    @Property(bool, notify=statsUpdated)
    def isGameRunning(self):
        return self.emu_manager.is_emulator_running()

    @Property(str, notify=statsUpdated)
    def activeGameName(self):
        game = self.emu_manager.launcher.current_game
        return game.get("nombre", "") if game else ""

    @Slot(str, result=int)
    def checkLaunchState(self, game_path):
        """
        Retorna el estado de ejecución actual:
        0: No hay nada ejecutándose (Lanzamiento libre).
        1: Hay un juego DIFERENTE ejecutándose (Requiere advertencia).
        2: Es el MISMO juego que ya está abierto (Informar).
        """
        if not self.emu_manager.is_emulator_running():
            return 0
        
        current = self.emu_manager.launcher.current_game
        if current and current.get("ruta") == game_path:
            return 2
        return 1

    @Slot(str, str)
    def forceLaunchGame(self, game_path, emu_id):
        """Cierra lo que esté abierto y lanza el nuevo juego."""
        self.emu_manager.terminar_proceso_actual()
        self.launchGame(game_path, emu_id)

    # --- METADATOS BÁSICOS ---
    @Property(str, constant=True)
    def appVersion(self):
        from core.config import APP_VERSION
        return APP_VERSION

    @Property(str, constant=True)
    def appName(self):
        from core.config import APP_NAME
        return APP_NAME

    @Property(str, constant=True)
    def logoPath(self):
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_path, "media", "icon.svg")
        from PySide6.QtCore import QUrl
        return QUrl.fromLocalFile(path).toString()

    # --- AJUSTES DE EMULADOR (TWEAKS) ---
    @Slot(str, result=list)
    def getEmulatorTweaks(self, emu_id):
        """Retorna la lista de ajustes disponibles para un emulador."""
        return self.emu_manager.tweak_manager.get_tweaks_for_emu(emu_id)

    @Slot(str, str, "QVariant")
    def saveEmulatorTweak(self, emu_id, tweak_id, value):
        """Guarda un ajuste específico para un emulador."""
        self.emu_manager.tweak_manager.save_tweak(emu_id, tweak_id, value)
        # No es estrictamente necesario emitir statsUpdated a menos que queramos
        # refrescar algo visual inmediatamente en el dashboard.

    @Slot()
    def quit(self):
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.quit()
