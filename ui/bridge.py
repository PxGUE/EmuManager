"""
bridge.py — Capa de comunicación entre Python y QML.
Expone la lógica de EmuladorManager y el Traductor a la interfaz declarativa.
"""

from PySide6.QtCore import QObject, Slot, Property, Signal
from core.i18n import TRANSLATIONS
import core.scanner as scanner
from core.constants import AVAILABLE_EMULATORS
import os

class AppBridge(QObject):
    # Señales para notificar cambios a QML
    languageChanged = Signal(str)
    statsUpdated = Signal()
    downloadProgress = Signal(str, float) # url, progress
    downloadFinished = Signal(str, bool, str) # url, success, message
    
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
        return self.translator.t(key, arg)

    def _setup_manager_links(self):
        """Sobrescribe o extiende métodos del manager para capturar progreso."""
        # Esto es un poco hacky pero efectivo para no modificar el core
        original_download = self.emu_manager.instalar_emulador
        
        async def wrapped_download(github_url, on_progress=None):
            def progress_hook(p):
                self.downloadProgress.emit(github_url, p)
                if on_progress: on_progress(p)
            
            return await original_download(github_url, on_progress=progress_hook)
        
        self.emu_manager.instalar_emulador = wrapped_download

    @Property(list, notify=statsUpdated)
    def allEmulators(self):
        """Lista completa de emuladores con estado de instalación."""
        result = []
        for emu in AVAILABLE_EMULATORS:
            is_installed = self.emu_manager.esta_instalado(emu["github"])
            result.append({
                "id": emu["id"],
                "name": emu["name"],
                "console": emu["console"],
                "consoleId": emu["console_id"],
                "description": emu["description"],
                "github": emu["github"],
                "isInstalled": is_installed,
                "color": emu.get("color", "#4da6ff"),
                "hasManual": "manual_url" in emu
            })
        return result

    @Slot(str)
    def installEmulator(self, github_url):
        import asyncio
        async def do_install():
            success, msg = await self.emu_manager.instalar_emulador(github_url)
            self.downloadFinished.emit(github_url, success, msg)
            if success:
                self.statsUpdated.emit()
        
        asyncio.create_task(do_install())

    @Slot(str)
    def uninstallEmulator(self, github_url):
        success = self.emu_manager.desinstalar_emulador(github_url)
        self.downloadFinished.emit(github_url, success, "Uninstalled" if success else "Error")
        self.statsUpdated.emit()

    @Slot(str, str)
    def manualInstall(self, github_url, file_path):
        import asyncio
        async def do_manual():
            emu = next((e for e in AVAILABLE_EMULATORS if e["github"] == github_url), None)
            if not emu:
                self.downloadFinished.emit(github_url, False, "Emu not found")
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
        
        return {
            "installed": installed,
            "totalRoms": len(biblioteca),
            "totalConsoles": len(set(j.get("id_emu") for j in biblioteca)),
            "totalHours": total_hours
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
                if h > 0: time_str = f"{h}h {m}m"
                elif m > 0: time_str = f"{m}m"
                else: time_str = "< 1m"
                
                juegos_con_tiempo.append({
                    "name": j["nombre"],
                    "console": j.get("consola", ""),
                    "playtime": time_str,
                    "color": color,
                    "seconds": s
                })
        
        juegos_con_tiempo.sort(key=lambda x: x["seconds"], reverse=True)
        return juegos_con_tiempo[:7]

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
            ][:6]
        }

    @Slot()
    def refreshDashboard(self):
        self.statsUpdated.emit()

    # --- CONFIGURACIÓN (SETTINGS) ---
    @Property(str, notify=statsUpdated)
    def installPath(self):
        return self.emu_manager.install_path or ""

    @Property(str, notify=statsUpdated)
    def romsPath(self):
        return self.emu_manager.roms_path or ""

    @Slot()
    def browseInstallPath(self):
        from PySide6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(None, self.translator.t("set_dlg_emus"), self.installPath)
        if path:
            self.emu_manager.install_path = path
            self.emu_manager.save_config()
            self.statsUpdated.emit()

    @Slot()
    def browseRomsPath(self):
        from PySide6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(None, self.translator.t("set_dlg_roms"), self.romsPath)
        if path:
            self.emu_manager.roms_path = path
            self.emu_manager.save_config()
            self.statsUpdated.emit()

    @Property(list, notify=statsUpdated)
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
        self.statsUpdated.emit()

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

    @Slot(str, str, str)
    def saveSecret(self, provider_id, key, value):
        import core.security as security
        security.save_secret(provider_id, key, value)
        self.statsUpdated.emit()

    @Slot(str)
    def clearSecrets(self, provider_id):
        import core.security as security
        security.clear_all_secrets(provider_id)
        self.statsUpdated.emit()

    # --- BIBLIOTECA (LIBRARY) ---
    @Property(list, notify=statsUpdated)
    def scannedConsoles(self):
        biblioteca = scanner.cargar_biblioteca_cache()
        console_ids = set(j.get("id_emu") for j in biblioteca)
        result = []
        for emu in AVAILABLE_EMULATORS:
            if emu["id"] in console_ids:
                count = sum(1 for j in biblioteca if j.get("id_emu") == emu["id"])
                total_s = sum(self.emu_manager.get_playtime(j.get("ruta", ""))[0] for j in biblioteca if j.get("id_emu") == emu["id"])
                result.append({
                    "id": emu["id"],
                    "name": emu["name"],
                    "count": count,
                    "playtime": total_s,
                    "color": emu.get("color", "#4da6ff")
                })
        return result

    @Slot(str, result=list)
    def getGamesForConsole(self, console_id):
        biblioteca = scanner.cargar_biblioteca_cache()
        games = []
        for j in biblioteca:
            if j.get("id_emu") == console_id:
                s, h, m = self.emu_manager.get_playtime(j.get("ruta", ""))
                cover_path = self.emu_manager.get_cover_path(j)
                games.append({
                    "name": j["nombre"],
                    "path": j["ruta"],
                    "console": j.get("consola", ""),
                    "playtime": f"{h}h {m}m" if h > 0 else f"{m}m",
                    "cover": cover_path if os.path.exists(cover_path) else "",
                    "id_emu": console_id
                })
        return games

    @Slot(str, str)
    def launchGame(self, game_path, emu_id):
        biblioteca = scanner.cargar_biblioteca_cache()
        game = next((j for j in biblioteca if j["ruta"] == game_path), None)
        if game:
            async def do_launch():
                await self.emu_manager.lanzar_juego(game)
            import asyncio
            asyncio.create_task(do_launch())

    # --- METADATOS BÁSICOS ---
    @Property(str, constant=True)
    def appVersion(self):
        from core.config import APP_VERSION
        return APP_VERSION

    @Property(str, constant=True)
    def appName(self):
        from core.config import APP_NAME
        return APP_NAME

    @Slot()
    def quit(self):
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.quit()
