from PySide6.QtCore import QObject, Signal, Slot, QTimer
from PySide6.QtQml import QmlElement
from core.logger import EmuLog

QML_IMPORT_NAME = "EmuManager.Gamepad"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class GamepadController(QObject):
    """
    Controlador que recibe eventos de mando desde Rust y los traduce a señales de QML.
    """
    buttonPressed = Signal(str) # "A", "B", "X", "Y", "UP", "DOWN", "LEFT", "RIGHT", "START", "SELECT"
    connected = Signal(str)     # Nombre del mando
    disconnected = Signal()
    devicesChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_active = False
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(150) # Evitar ráfagas de input
        self._last_key = None
        self._devices = []
        from core.config import AppConfig
        self._deadzone = AppConfig.get_deadzone()

    @Slot()
    def start_monitoring(self):
        if self._is_active:
            return
            
        try:
            import mango_engine
            mango_engine.start_gamepad_monitor(self._on_rust_input)
            self._is_active = True
            EmuLog.info("Gamepad: Monitoreo activado.")
        except Exception as e:
            EmuLog.error(f"Gamepad: Error al iniciar monitor: {e}")

    @Slot()
    def stop_monitoring(self):
        try:
            import mango_engine
            mango_engine.stop_gamepad_monitor()
            self._is_active = False
            EmuLog.info("Gamepad: Monitoreo detenido.")
        except: pass

    def _on_rust_input(self, key):
        """Callback llamado desde el hilo de Rust."""
        if key.startswith("CONNECT:"):
            name = key.replace("CONNECT:", "")
            if name not in self._devices:
                self._devices.append(name)
            self.connected.emit(name)
            self.devicesChanged.emit()
            EmuLog.info(f"Gamepad: {name} conectado.")
            return

        if key == "DISCONNECT":
            if self._devices:
                name = self._devices.pop() # Simplificación para un solo mando por ahora
                self.disconnected.emit()
                self.devicesChanged.emit()
                EmuLog.info(f"Gamepad: Desconectado.")
            return

        if not self._debounce_timer.isActive():
            self.buttonPressed.emit(key)
            self._debounce_timer.start()
            EmuLog.debug(f"Gamepad Input: {key}")

    @Slot(result=list)
    def get_devices(self):
        return self._devices

    @Slot(float)
    def set_deadzone(self, val):
        self._deadzone = val
        from core.config import AppConfig
        AppConfig.set_deadzone(val)
        EmuLog.info(f"Gamepad: Deadzone actualizada a {val}")

    @Slot(result=float)
    def get_deadzone(self):
        return self._deadzone
