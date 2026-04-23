from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement
from core.logger import EmuLog

QML_IMPORT_NAME = "EmuManager.Chameleon"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class ChameleonController(QObject):
    """
    Controlador especializado en la gestión de la estética adaptativa.
    Extrae colores de carátulas y los propaga a la UI.
    """
    colorChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_color = "#025E73" # Default Theme._p1
        self._cache = {}

    @Property(str, notify=colorChanged)
    def currentColor(self):
        return self._current_color

    @Slot(str)
    def adapt_to_image(self, image_path):
        """
        Extrae el color dominante de una imagen y actualiza el estado global.
        """
        if not image_path:
            EmuLog.debug("Chameleon: No image path provided.")
            return

        EmuLog.info(f"Chameleon: Adaptando a {image_path}")

        if image_path in self._cache:
            self._update_color(self._cache[image_path])
            return

        try:
            import mango_engine
            # La ruta viene como file:/// o absoluta. Normalizamos para Rust.
            clean_path = image_path.replace("file:///", "").replace("/", "\\")
            if clean_path.startswith("\\"): # Caso /F:/... -> F:\...
                 clean_path = clean_path[1:]
            
            EmuLog.debug(f"Chameleon: Ruta limpia para Rust: {clean_path}")
            
            rgb = mango_engine.extract_accent_color(clean_path)
            hex_color = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
            
            EmuLog.info(f"Chameleon: Color extraído: {hex_color}")
            
            self._cache[image_path] = hex_color
            self._update_color(hex_color)
            
        except Exception as e:
            EmuLog.error(f"Chameleon: Error al extraer color de {image_path}: {e}")

    def _update_color(self, hex_color):
        if self._current_color != hex_color:
            self._current_color = hex_color
            EmuLog.info(f"Chameleon: Emitiendo señal de cambio de color -> {hex_color}")
            self.colorChanged.emit() # Notificar al sistema de propiedades de Qt
            EmuLog.debug(f"Chameleon: Estética adaptada a {hex_color}")

    @Slot()
    def reset_to_default(self):
        self._update_color("#025E73")
