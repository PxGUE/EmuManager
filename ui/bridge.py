"""
bridge.py â€” Puente principal de comunicaciÃ³n entre Python y QML.

Este mÃ³dulo define la clase AppBridge, que actÃºa como el "Hub" central.
Organiza la lÃ³gica mediante sub-bridges especializados (Library, Settings, Emulators)
y gestiona el estado global (idioma, procesos en ejecuciÃ³n, metadatos de la app).
"""

import os
import sys
from collections import OrderedDict
import psutil
import asyncio
from PySide6.QtCore import QObject, Slot, Property, Signal, QUrl

from core.logic.constants import AVAILABLE_EMULATORS
import core.logic.config as config
from ui.bridges.library import LibraryBridge
from ui.bridges.settings import SettingsBridge
from ui.bridges.emulators import EmulatorsBridge
from ui.bridges.maintenance import MaintenanceBridge

class AppBridge(QObject):
    """
    Clase principal expuesta al motor QML.
    
    Proporciona acceso a todas las funcionalidades del backend mediante seÃ±ales,
    slots y propiedades. Utiliza una arquitectura de sub-objetos para mantener
    el cÃ³digo organizado y escalable.
    """
    
    # --- SeÃ±ales Globales (Notificaciones a la UI) ---
    languageChanged = Signal()
    statsUpdated = Signal()
    systemResourcesChanged = Signal()
    configUpdated = Signal()
    downloadProgress = Signal(str, float)  # (emu_id, porcentaje)
    downloadFinished = Signal(str, bool, str)  # (emu_id, Ã©xito, mensaje)
    scanProgress = Signal(float, str)  # (porcentaje, nombre_actual)
    bridgeStateChanged = Signal()
    isReadyChanged = Signal()
    loadingMessageChanged = Signal()

    def __init__(self, emu_manager, translator):
        """
        Inicializa el bridge y conecta los sub-objetos.

        Args:
            emu_manager (EmuManager): El controlador lÃ³gico central de la app.
            translator (Translator): El motor de traducciones i18n.
        """
        super().__init__()
        self.emu_manager = emu_manager
        self.translator = translator
        # VersiÃ³n y nombre hardcoded preventivamente por si config no carga
        self._app_version = config.APP_VERSION
        self._app_name = config.APP_NAME
        self._is_fullscreen = False
        self._is_ready = False
        self._loading_message = ""
        self._cpu_usage = 0.0
        self._ram_usage = 0.0

        # Inicializar sub-bridges (Modularidad)
        self._library = LibraryBridge(self)
        self._settings = SettingsBridge(self)
        self._emulators = EmulatorsBridge(self)
        self._maintenance = MaintenanceBridge(self)

    async def _initialize_async(self):
        """Tarea asÃ­ncrona para cargar datos pesados sin bloquear la UI."""
        import asyncio
        import core.logic.scanner as scanner

        # 1. Verificando configuraciÃ³n
        self._set_loading_msg(self.translator.t("loading_config"))
        await asyncio.sleep(0.4) # Simulado para que sea legible
        
        # 2. Sincronizar emuladores
        self._set_loading_msg(self.translator.t("loading_emus"))
        await self.emu_manager.sync_with_disk_async()
        
        # 3. Precargar biblioteca (CachÃ©)
        self._set_loading_msg(self.translator.t("loading_library"))
        # Esto forzarÃ¡ que cargar_biblioteca_cache llene el _library_cache
        await asyncio.to_thread(scanner.cargar_biblioteca_cache)
        
        # 4. Finalizando
        self._set_loading_msg(self.translator.t("loading_ready"))
        await asyncio.sleep(0.4)
        
        # Marcar como listo. La Splash Screen se ocultarÃ¡.
        self._is_ready = True
        self.isReadyChanged.emit()
        
        # 5. Iniciar monitor de recursos ligero
        asyncio.create_task(self._monitor_resources())

    async def _monitor_resources(self):
        """Actualiza estadÃ­sticas del PC sin bloquear nunca la interfaz."""
        import psutil
        while True:
            # interval=None hace que no bloquee, usa la diferencia desde la Ãºltima llamada
            self._cpu_usage = psutil.cpu_percent(interval=None)
            self._ram_usage = psutil.virtual_memory().percent
            self.systemResourcesChanged.emit()
            await asyncio.sleep(3) # Cada 3 segundos es suficiente y suave

    def _set_loading_msg(self, msg):
        self._loading_message = msg
        self.loadingMessageChanged.emit()

    @Property(str, notify=loadingMessageChanged)
    def loadingMessage(self):
        return self._loading_message

    @Property(bool, notify=isReadyChanged)
    def isReady(self):
        return self._is_ready

    # --- PROPIEDADES DE SUB-BRIDGES ---
    # Permite acceder desde QML como: app.lib.nombreMetodo()
    
    @Property(QObject, constant=True)
    def lib(self):
        """Bridge especializado en la biblioteca de juegos."""
        return self._library
    
    @Property(QObject, constant=True)
    def set(self):
        """Bridge especializado en ajustes y configuraciÃ³n."""
        return self._settings
    
    @Property(QObject, constant=True)
    def emu(self):
        """Bridge especializado en la gestiÃ³n fÃ­sica de emuladores."""
        return self._emulators
        
    @Property(QObject, constant=True)
    def maint(self):
        """Bridge especializado en mantenimiento y utilidades (Backups, Updates)."""
        return self._maintenance

    # --- GestiÃ³n de Idioma (i18n) ---
    
    @Property(str, notify=languageChanged)
    def currentLanguage(self):
        """CÃ³digo del idioma actual (ej: 'es')."""
        return self.translator.lang

    @Slot(str)
    def changeLanguage(self, lang_code):
        """Cambia el idioma de la app y notifica a toda la UI para refrescar textos."""
        self.translator.set_language(lang_code)
        self.languageChanged.emit()
        self.statsUpdated.emit()
        self.configUpdated.emit()

    @Slot(str, result=str)
    def translate(self, key):
        """Traduce una clave directamente desde QML."""
        return self.translator.t(key)

    @Slot(str, list, result=str)
    def translateWithArgs(self, key, args):
        """Traduce una clave inyectando argumentos (ej: "{0} juegos")."""
        return self.translator.t(key, *args)

    def _sanitize_emu(self, emu):
        """
        Normaliza un diccionario de emulador para que QML siempre reciba
        las mismas claves, evitando errores de 'undefined'.
        """
        safe = emu.copy()
        template = {
            "id": "", "name": "", "console": "", "console_id": "", "description": "",
            "folder": "", "github": "", "manual_url": "", "extensions": [],
            "libretro_platform": "", "fallback_url": "", "fallback_win": "",
            "fallback_linux": "", "screenscraper_id": "", "color": "#7c6ff7",
            "github_win": "", "github_linux": ""
        }
        for k, default in template.items():
            if k not in safe or safe[k] is None:
                safe[k] = default
        return safe

    @Property(list, constant=True)
    def allEmulators(self):
        """
        Retorna la lista de todos los emuladores agrupados por consola.
        Ideal para vistas tipo cuadrÃ­cula o Dashboard.
        """
        groups = OrderedDict()
        
        for emu in AVAILABLE_EMULATORS:
            c_id = emu.get("console_id", "misc")
            if c_id not in groups:
                groups[c_id] = {
                    "id": c_id,
                    "name": emu.get("console", "Otros"),
                    "accentColor": emu.get("color", "#7c6ff7"),
                    "emulators": []
                }
            
            is_inst = self.emu_manager.esta_instalado(emu["github"])
            safe_emu = self._sanitize_emu(emu)
            groups[c_id]["emulators"].append({
                **safe_emu,
                "isInstalled": is_inst
            })
            
        result = []
        for g in groups.values():
            # El grupo se marca como instalado si tiene al menos un emulador listo
            g["isInstalled"] = any(e["isInstalled"] for e in g["emulators"])
            result.append(g)
            
        return result

    @Property(dict, notify=systemResourcesChanged)
    def systemStatus(self):
        """
        Estado dinÃ¡mico del PC y la configuraciÃ³n de rutas.
        Utilizado principalmente en el panel lateral o Dashboard.
        """
        return {
            "cpu": self._cpu_usage,
            "ram": self._ram_usage,
            "running": self.emu_manager.is_emulator_running(),
            "emusPath": self.emu_manager.install_path or "No configurado",
            "romsPath": self.emu_manager.roms_path or "No configurado",
            "emusPathExists": os.path.exists(self.emu_manager.install_path) if self.emu_manager.install_path else False,
            "romsPathExists": os.path.exists(self.emu_manager.roms_path) if self.emu_manager.roms_path else False,
            "installedEmus": [
                {**self._sanitize_emu(emu), "isInstalled": True} 
                for emu in AVAILABLE_EMULATORS 
                if self.emu_manager.esta_instalado(emu.get("github", ""))
            ]
        }

    @Property(bool, notify=statsUpdated)
    def isGameRunning(self):
        """Indica si hay un proceso de emulador activo."""
        return self.emu_manager.is_emulator_running()

    @Property(str, notify=statsUpdated)
    def activeGameName(self):
        """Retorna el nombre del juego que se estÃ¡ ejecutando actualmente."""
        current = self.emu_manager.launcher.current_game
        return current.get("nombre", "") if current else ""

    @Property(str, constant=True)
    def appVersion(self):
        """VersiÃ³n de la aplicaciÃ³n."""
        return config.APP_VERSION

    @Property(str, constant=True)
    def appName(self):
        """Nombre de la aplicaciÃ³n."""
        return config.APP_NAME

    @Property(str, constant=True)
    def logoPath(self):
        """Ruta al logo principal (SVG) en formato QUrl."""
        media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")
        logo = os.path.join(media_dir, "icon.svg")
        return QUrl.fromLocalFile(logo).toString()

    @Slot()
    def refreshDashboard(self):
        """Dispara manualmente la actualizaciÃ³n de estadÃ­sticas en la UI."""
        self.statsUpdated.emit()

    @Property(bool, notify=bridgeStateChanged)
    def isFullScreen(self):
        """Estado de pantalla completa (Cinema Mode)."""
        return self._is_fullscreen

    @Slot()
    def toggleFullScreen(self):
        """Alterna el modo de pantalla completa."""
        self._is_fullscreen = not self._is_fullscreen
        self.bridgeStateChanged.emit()

    @Slot()
    def quit(self):
        """Cierra de forma segura emuladores activos y sale de la aplicaciÃ³n."""
        self.emu_manager.terminar_proceso_actual()
        sys.exit(0)
