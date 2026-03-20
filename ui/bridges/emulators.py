"""
emulators.py â€” Bridge especializado en la gestiÃ³n de emuladores.

Este sub-bridge maneja:
1. InstalaciÃ³n de emuladores (desde GitHub o manual).
2. DesinstalaciÃ³n de emuladores.
3. Apertura de carpetas de instalaciÃ³n.
4. GestiÃ³n de 'tweaks' (ajustes especÃ­ficos por emulador).
"""

import os
import asyncio
from PySide6.QtCore import QObject, Slot, Signal, QUrl
from PySide6.QtGui import QDesktopServices

from core.logic.constants import AVAILABLE_EMULATORS

class EmulatorsBridge(QObject):
    """
    Gestiona las operaciones fÃ­sicas sobre los emuladores instalados.
    """
    def __init__(self, main_bridge):
        """
        Args:
            main_bridge (AppBridge): Referencia para emitir seÃ±ales de progreso globales.
        """
        super().__init__()
        self.main = main_bridge
        self.emu_manager = main_bridge.emu_manager
        self.translator = main_bridge.translator

    @Slot(str)
    def installEmulator(self, github_url):
        """
        Inicia la descarga e instalaciÃ³n automÃ¡tica de un emulador.
        
        Args:
            github_url (str): URL del repositorio para identificar el emulador.
        """
        async def do_install():
            success = False
            message = "Error desconocido"
            try:
                async for step in self.emu_manager.instalar_emulador(github_url):
                    if step.startswith("PROGRESS:"):
                        try:
                            # Formato esperado: PROGRESS:valor|mensaje
                            partes = step.split("|")
                            prog_str = partes[0].split(":")[1]
                            prog_val = float(prog_str)
                            # Encontrar ID corto
                            emu_id_prog = github_url
                            for e in AVAILABLE_EMULATORS:
                                if e.get("github") == github_url or e.get("github_win") == github_url or e.get("github_linux") == github_url:
                                    emu_id_prog = e["id"]
                                    break
                            self.main.downloadProgress.emit(emu_id_prog, prog_val)
                            
                            if len(partes) > 1:
                                msg_part = partes[1].lower()
                                if "Ã©xito" in msg_part or "exitosa" in msg_part or prog_val >= 1.0:
                                    success = True
                                    message = partes[1]
                        except: pass
                    elif step.startswith("ERROR:"):
                        message = step.split(":", 1)[1]
                        success = False
                    elif "Ã©xito" in step.lower() or "exitosa" in step.lower():
                        success = True
                        message = step
                
                if success:
                    print(f"[BRIDGE] InstalaciÃ³n finalizada: {github_url}")
                    self.main.statsUpdated.emit()
                
                # Intentamos encontrar el ID corto para facilitar la lÃ³gica de la UI
                emu_id = github_url
                for e in AVAILABLE_EMULATORS:
                    if e.get("github") == github_url or e.get("github_win") == github_url or e.get("github_linux") == github_url:
                        emu_id = e["id"]
                        break
                        
                self.main.downloadFinished.emit(emu_id, success, message)
            except Exception as e:
                print(f"[BRIDGE] Fallo en instalaciÃ³n {github_url}: {e}")
                
                emu_id = github_url
                for e in AVAILABLE_EMULATORS:
                    if e.get("github") == github_url or e.get("github_win") == github_url or e.get("github_linux") == github_url:
                        emu_id = e["id"]
                        break
                self.main.downloadFinished.emit(emu_id, False, str(e))
        
        asyncio.create_task(do_install())

    @Slot(str)
    def uninstallEmulator(self, github_url):
        """
        Elimina los archivos de un emulador instalado.
        """
        async def do_uninstall():
            success = False
            message = "Error al desinstalar"
            try:
                async for step in self.emu_manager.desinstalar_emulador(github_url):
                    low_step = step.lower()
                    if "Ã©xito" in low_step or "desinstalado" in low_step:
                        success = True
                        message = step
                    elif "error" in low_step:
                        success = False
                        message = step
                
                if success:
                    print(f"[BRIDGE] DesinstalaciÃ³n finalizada: {github_url}")
                
                emu_id = github_url
                for e in AVAILABLE_EMULATORS:
                    if e.get("github") == github_url or e.get("github_win") == github_url or e.get("github_linux") == github_url:
                        emu_id = e["id"]
                        break
                        
                self.main.downloadFinished.emit(emu_id, success, message)
                self.main.statsUpdated.emit()
            except Exception as e:
                print(f"[BRIDGE] Fallo en desinstalaciÃ³n {github_url}: {e}")
                
                emu_id = github_url
                for e in AVAILABLE_EMULATORS:
                    if e.get("github") == github_url or e.get("github_win") == github_url or e.get("github_linux") == github_url:
                        emu_id = e["id"]
                        break
                self.main.downloadFinished.emit(emu_id, False, str(e))

        asyncio.create_task(do_uninstall())

    @Slot(str)
    def openEmulatorFolder(self, github_url):
        """Abre la carpeta de instalaciÃ³n del emulador en el explorador de archivos."""
        info = self.emu_manager.installed_emus.get(github_url)
        if info:
            files = info.get("files", [])
            if files:
                path = os.path.dirname(files[0])
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    @Slot(str, str)
    def manualInstall(self, github_url, file_path):
        """
        Instala un emulador usando un archivo local proporcionado por el usuario.
        
        Args:
            github_url (str): Emulador destino.
            file_path (str): Ruta al archivo ZIP/EXE.
        """
        async def do_manual():
            emu = next((e for e in AVAILABLE_EMULATORS if e["github"] == github_url), None)
            if not emu:
                self.main.downloadFinished.emit(github_url, False, self.main.translator.t("dl_err_emu_not_found"))
                return
                
            success, msg = await self.emu_manager.instalar_manual(emu, file_path)
            self.main.downloadFinished.emit(github_url, success, msg)
            if success:
                self.main.statsUpdated.emit()
                
        asyncio.create_task(do_manual())

    @Slot(str)
    def openManualUrl(self, github_url):
        """Abre la pÃ¡gina oficial de descarga del emulador."""
        emu = next((e for e in AVAILABLE_EMULATORS if e["github"] == github_url), None)
        if emu:
            url = emu.get("manual_url", emu.get("github"))
            QDesktopServices.openUrl(QUrl(url))

    @Slot(str, result=list)
    def getEmulatorTweaks(self, emu_id):
        """Obtiene la lista de ajustes configurables para un emulador."""
        return self.emu_manager.tweak_manager.get_tweaks_for_emu(emu_id)

    @Slot(str, str, "QVariant")
    def saveEmulatorTweak(self, emu_id, tweak_id, value):
        """Guarda un ajuste especÃ­fico."""
        self.emu_manager.tweak_manager.save_tweak(emu_id, tweak_id, value)
