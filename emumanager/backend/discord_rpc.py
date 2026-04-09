import time
from core.logger import EmuLog
from core.config import AppConfig

try:
    from pypresence import Presence
    PYPRESENCE_AVAILABLE = True
except ImportError:
    PYPRESENCE_AVAILABLE = False

class DiscordRPCManager:
    """
    Gestiona la conexión y actualización del estado de Discord Rich Presence.
    """

    def __init__(self):
        self.rpc = None
        self._is_connected = False
        self._enabled = False

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        if not enabled:
            self.clear_presence()

    def connect(self):
        if not PYPRESENCE_AVAILABLE: return False
        if not self._enabled: return False
        if self._is_connected: return True
        
        try:
            client_id = AppConfig.get_discord_client_id()
            self.rpc = Presence(client_id)
            self.rpc.connect()
            self._is_connected = True
            EmuLog.info("Discord RPC: Conectado con éxito.")
            return True
        except Exception as e:
            EmuLog.debug(f"Discord RPC: No se pudo conectar (¿Discord cerrado?): {e}")
            self._is_connected = False
            return False

    def update_presence(self, game_name, platform):
        if not PYPRESENCE_AVAILABLE: return
        if not self._enabled: return
        
        if not self._is_connected:
            if not self.connect(): return

        try:
            # Mapeo de iconos (Opcional si tenemos assets en el portal de Discord)
            large_image = platform.lower() if platform else "logo"
            
            self.rpc.update(
                state=f"En {platform.upper()}" if platform else "Jugando",
                details=game_name,
                start=time.time(),
                large_image=large_image,
                large_text="EmuManager",
                small_image="logo",
                small_text="Viviendo la nostalgia"
            )
            EmuLog.info(f"Discord RPC: Estado actualizado -> {game_name}")
        except Exception as e:
            EmuLog.error(f"Discord RPC: Error al actualizar estado: {e}")
            self._is_connected = False

    def clear_presence(self):
        if not PYPRESENCE_AVAILABLE: return
        if self.rpc and self._is_connected:
            try:
                self.rpc.clear()
                EmuLog.info("Discord RPC: Estado limpiado.")
            except Exception as e:
                EmuLog.debug(f"Discord RPC: Error al limpiar estado: {e}")

    def disconnect(self):
        """Cierra la conexión con Discord de forma definitiva."""
        if not PYPRESENCE_AVAILABLE: return
        if self.rpc and self._is_connected:
            try:
                self.rpc.close()
                EmuLog.info("Discord RPC: Desconectado.")
            except Exception as e:
                EmuLog.debug(f"Discord RPC: Error al cerrar conexión: {e}")
        self._is_connected = False
        self.rpc = None
