import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QMovie

class LoadingOverlay(QWidget):
    """
    Capa semitransparente bloqueadora que se superpone sobre la aplicación 
    o un widget específico para indicar que hay lógica pesada corriendo.
    """
    def __init__(self, parent=None, text="Cargando..."):
        super().__init__(parent)
        self.text = text
        self.init_ui()
        
    def init_ui(self):
        self.setObjectName("loadingOverlayBg")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Loader animado o Emoji fallback
        self.lbl_spinner = QLabel()
        self.lbl_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Opcional: Podrías usar un GIF. Aquí usamos un texto grande animado como fallback premium
        self.lbl_spinner.setText("⏳")
        self.lbl_spinner.setObjectName("loadingSpinner")
        
        self.lbl_text = QLabel(self.text)
        self.lbl_text.setObjectName("loadingText")
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.lbl_spinner)
        layout.addWidget(self.lbl_text)
        
        # Efecto de fundido (Opacidad)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        self.hide()

    def show_loading(self, message=None):
        if message:
            self.lbl_text.setText(message)
            
        if self.parent():
            self.resize(self.parent().size())
            
        self.show()
        self.raise_() # Asegurar que esté encima de todo
        
        # Animación Fade-in
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(250)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()
        
    def hide_loading(self):
        # Animación Fade-out
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.finished.connect(self.hide)
        self.anim.start()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.resize(self.parent().size())

