from PySide6.QtCore import QObject, Slot, Signal
from core.logic.emulators.updater import check_all_updates
from core.logic.constants import AVAILABLE_EMULATORS

class MaintenanceBridge(QObject):
    """
    Bridge especializado en utilidades del sistema (actualizaciones).
    """
    
    updatesDiscoveryFinished = Signal(dict) # {emu_id: info}
    
    def __init__(self, main_bridge):
        super().__init__(main_bridge)
        self.main = main_bridge
        self.emu_mgr = main_bridge.emu_manager


    @Slot()
    def checkUpdates(self):
        """
        Verifica actualizaciones de forma asíncrona para todos los emuladores.
        Emite updatesDiscoveryFinished al terminar.
        """
        import asyncio
        
        async def _async_task():
            try:
                # El emu_mgr mantiene la lista de instalados y AVAILABLE_EMULATORS es global
                results = await check_all_updates(self.emu_mgr.installed_emus, AVAILABLE_EMULATORS)
                self.updatesDiscoveryFinished.emit(results)
            except Exception as e:
                print(f"[MAINTENANCE] Error en checkUpdates: {e}")
                self.updatesDiscoveryFinished.emit({})
            
        asyncio.create_task(_async_task())

