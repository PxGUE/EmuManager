"""
settings.py — Bridge especializado en la gestión de configuración y rutas.

Este sub-bridge maneja:
1. Selección y apertura de rutas (Emuladores, ROMs).
2. Activación/desactivación de proveedores de metadatos (Scrapers).
3. Gestión de credenciales seguras (API Keys, Contraseñas).
"""

import os
import json
from PySide6.QtCore import QObject, Slot, Property, Signal, QUrl
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QDesktopServices

import core.logic.config as config
import core.security.security as security
from core.logic.metadata import get_providers_config

class SettingsBridge(QObject):
    """
    Gestiona la comunicación entre la pantalla de Ajustes de QML y el backend.
    """
    
    # Señal para notificar cambios en la configuración a la UI
    configDataChanged = Signal()

    def __init__(self, main_bridge):
        """
        Args:
            main_bridge (AppBridge): Referencia al bridge principal para emitir señales globales.
        """
        super().__init__()
        self.main = main_bridge
        self.emu_manager = main_bridge.emu_manager
        self.translator = main_bridge.translator

        # Vincular señal global con refresco local
        self.main.configUpdated.connect(self.configDataChanged)

    @Property(str, notify=configDataChanged)
    def installPath(self):
        """Ruta absoluta donde se instalan los emuladores."""
        return self.emu_manager.install_path or ""

    @Property(str, notify=configDataChanged)
    def romsPath(self):
        """Ruta absoluta donde se encuentran los juegos."""
        return self.emu_manager.roms_path or ""

    @Property(bool, notify=configDataChanged)
    def collectorMode(self):
        """Indica si el modo coleccionista está activo."""
        return getattr(self.emu_manager, "collector_mode", False)

    @Slot(bool)
    def setCollectorMode(self, enabled):
        """Activa o desactiva el modo coleccionista."""
        self.emu_manager.save_config(collector_mode=enabled)
        self.main.configUpdated.emit()

    @Slot()
    def browseInstallPath(self):
        """Abre un diálogo nativo para seleccionar la carpeta de emuladores."""
        path = QFileDialog.getExistingDirectory(None, self.translator.t("set_dlg_emus"), self.installPath)
        if path:
            self.emu_manager.install_path = path
            self.emu_manager.save_config()
            self.main.configUpdated.emit()

    @Slot()
    def browseRomsPath(self):
        """Abre un diálogo nativo para seleccionar la carpeta de ROMs."""
        path = QFileDialog.getExistingDirectory(None, self.translator.t("set_dlg_roms"), self.romsPath)
        if path:
            self.emu_manager.roms_path = path
            self.emu_manager.save_config()
            self.main.configUpdated.emit()

    @Slot()
    def openInstallFolder(self):
        """Abre la carpeta de emuladores en el explorador de archivos."""
        if self.installPath:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.installPath))

    @Slot()
    def openRomsFolder(self):
        """Abre la carpeta de ROMs en el explorador de archivos."""
        if self.romsPath:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.romsPath))

    @Property(list, notify=configDataChanged)
    def scraperProviders(self):
        """Lista de proveedores de metadatos configurables."""
        return get_providers_config()

    @Slot(str, bool)
    def toggleProvider(self, provider_id, enabled):
        """Activa o desactiva un proveedor de metadatos específico."""
        providers = get_providers_config()
        for p in providers:
            if p["id"] == provider_id:
                p["enabled"] = enabled
                break
        self._save_scrapers_config(providers)
        self.main.configUpdated.emit()

    def _save_scrapers_config(self, providers):
        """Guarda la configuración de scrapers (filtros y estado) en disco."""
        path = os.path.join("data", "scrapers_config.json")
        clean_data = []
        # No guardar secretos directamente en este JSON (por seguridad)
        secrets_blacklist = ["api_key", "user", "password"]
        for p in providers:
            clean_p = p.copy()
            for key in secrets_blacklist:
                if key in clean_p:
                    del clean_p[key]
            clean_data.append(clean_p)
            
        os.makedirs("data", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=2)

    @Slot(str, str, result=str)
    def getSecret(self, provider_id, key):
        """Recupera una credencial encriptada del sistema."""
        return security.get_secret(provider_id, key) or ""

    @Slot(str, str, str)
    def saveSecret(self, provider_id, key, value):
        """Guarda una credencial de forma segura usando el módulo security."""
        security.save_secret(provider_id, key, value)
        self.main.configUpdated.emit()

    @Slot(str)
    def clearSecrets(self, provider_id):
        """Elimina todas las credenciales guardadas de un proveedor."""
        security.clear_all_secrets(provider_id)
        self.main.configUpdated.emit()
