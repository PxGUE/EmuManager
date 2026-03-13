from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt

class ModernConfirmDialog(QDialog):
    """Diálogo de confirmación con diseño unificado (Premium)."""
    def __init__(self, title, message, translator, parent=None, is_question=True):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(title)
        self.setFixedWidth(400)
        self.setObjectName("modernConfirmDialog")
        self.is_question = is_question
        self.init_ui(title, message)

    def init_ui(self, title_text, message_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Título
        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)

        # Mensaje / Contenido en una caja sutil
        msg_box = QFrame()
        msg_box.setStyleSheet("background: rgba(255,255,255,0.03); border: 1px solid #252830; border-radius: 12px;")
        msg_layout = QVBoxLayout(msg_box)
        msg_layout.setContentsMargins(20, 20, 20, 20)

        msg_lbl = QLabel(message_text)
        msg_lbl.setStyleSheet("font-size: 14px; color: #a0a0a0; border: none;")
        msg_lbl.setWordWrap(True)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_layout.addWidget(msg_lbl)
        layout.addWidget(msg_box)

        # Botones
        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(15)

        if self.is_question:
            # Botón Cancelar (Secundario)
            cancel_btn = QPushButton(self.translator.t("dl_btn_cancel") if hasattr(self.translator, 't') else "Cancelar")
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setFixedHeight(40)
            cancel_btn.setStyleSheet("""
                QPushButton { background: transparent; color: #888; border: 1px solid #334155; border-radius: 8px; font-weight: bold; }
                QPushButton:hover { color: white; background: rgba(255,255,255,0.05); }
            """)
            cancel_btn.clicked.connect(self.reject)
            btns_layout.addWidget(cancel_btn)

        # Botón Aceptar (Primario/Acento)
        accept_lbl = "OK"
        if self.is_question:
            # Intentar obtener traducción de "Sí" o similar, si no "Aceptar"
            accept_lbl = self.translator.t("lib_yes_change") if hasattr(self.translator, 't') and self.is_question else "Aceptar"
            if not accept_lbl: accept_lbl = "Aceptar"

        accept_btn = QPushButton(accept_lbl)
        accept_btn.setFixedHeight(40)
        accept_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        accept_btn.setStyleSheet("""
            QPushButton { background: #4da6ff; color: #000000; border: none; border-radius: 8px; font-weight: bold; padding: 0 20px; }
            QPushButton:hover { background: #66b3ff; }
        """)
        accept_btn.clicked.connect(self.accept)
        btns_layout.addWidget(accept_btn, 1 if self.is_question else 0)

        layout.addLayout(btns_layout)

    @staticmethod
    def ask(parent, title, message, translator):
        dlg = ModernConfirmDialog(title, message, translator, parent, is_question=True)
        return dlg.exec() == QDialog.DialogCode.Accepted

    @staticmethod
    def inform(parent, title, message, translator):
        dlg = ModernConfirmDialog(title, message, translator, parent, is_question=False)
        return dlg.exec()
