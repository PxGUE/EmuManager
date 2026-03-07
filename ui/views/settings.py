from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

class SettingsView(QWidget):
    def __init__(self, emu_manager, translator, on_update_dashboard, on_language_change):
        super().__init__()
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_dashboard = on_update_dashboard
        self.on_language_change_callback = on_language_change
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Titulo Principal
        title = QLabel(self.translator.t("set_title"))
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # --- SECCIÓN IDIOMA ---
        lang_group = QVBoxLayout()
        lang_lbl = QLabel(self.translator.t("set_lang_lbl"))
        lang_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        
        self.lang_cb = QComboBox()
        self.lang_cb.addItem("Español", "es")
        self.lang_cb.addItem("English", "en")
        self.lang_cb.setFixedWidth(200)
        self.lang_cb.setStyleSheet("""
            QComboBox {
                background-color: #1a1c24;
                color: white;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #15171e;
                color: white;
                selection-background-color: #4da6ff;
            }
        """)
        
        index = self.lang_cb.findData(self.emu_manager.language)
        if index >= 0:
            self.lang_cb.setCurrentIndex(index)
            
        self.lang_cb.currentIndexChanged.connect(self.on_lang_changed)
        
        lang_group.addWidget(lang_lbl)
        lang_group.addWidget(self.lang_cb)
        layout.addLayout(lang_group)
        
        # Separador
        hline = QFrame()
        hline.setFrameShape(QFrame.Shape.HLine)
        hline.setStyleSheet("color: #333333;")
        layout.addWidget(hline)
        
        # --- SECCIÓN RUTAS ---
        # Ruta Emuladores
        emus_group = QVBoxLayout()
        emus_title = QLabel(self.translator.t("set_emus_title"))
        emus_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        emus_sub = QLabel(self.translator.t("set_emus_sub"))
        emus_sub.setStyleSheet("font-size: 13px; color: #888888;")
        
        emus_path_layout = QHBoxLayout()
        self.install_path_input = QLineEdit(self.emu_manager.install_path or "")
        self.install_path_input.setStyleSheet("padding: 10px; border-radius: 6px; background-color: #1a1c24; color: white; border: 1px solid #333;")
        self.install_path_input.editingFinished.connect(self.auto_save_settings)
        
        btn_browse_install = QPushButton(self.translator.t("set_btn_select"))
        btn_browse_install.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_install.setStyleSheet("padding: 10px 15px; background-color: #1976d2; color: white; border-radius: 6px; font-weight: bold;")
        btn_browse_install.clicked.connect(self.browse_install_path)
        
        emus_path_layout.addWidget(self.install_path_input)
        emus_path_layout.addWidget(btn_browse_install)
        
        emus_group.addWidget(emus_title)
        emus_group.addWidget(emus_sub)
        emus_group.addLayout(emus_path_layout)
        layout.addLayout(emus_group)
        
        # Ruta ROMs
        roms_group = QVBoxLayout()
        roms_title = QLabel(self.translator.t("set_roms_title"))
        roms_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        roms_sub = QLabel(self.translator.t("set_roms_sub"))
        roms_sub.setStyleSheet("font-size: 13px; color: #888888;")
        
        roms_path_layout = QHBoxLayout()
        self.roms_path_input = QLineEdit(self.emu_manager.roms_path or "")
        self.roms_path_input.setStyleSheet("padding: 10px; border-radius: 6px; background-color: #1a1c24; color: white; border: 1px solid #333;")
        self.roms_path_input.editingFinished.connect(self.auto_save_settings)
        
        btn_browse_roms = QPushButton(self.translator.t("set_btn_select"))
        btn_browse_roms.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_roms.setStyleSheet("padding: 10px 15px; background-color: #1976d2; color: white; border-radius: 6px; font-weight: bold;")
        btn_browse_roms.clicked.connect(self.browse_roms_path)
        
        roms_path_layout.addWidget(self.roms_path_input)
        roms_path_layout.addWidget(btn_browse_roms)
        
        roms_group.addWidget(roms_title)
        roms_group.addWidget(roms_sub)
        roms_group.addLayout(roms_path_layout)
        layout.addLayout(roms_group)
        
        # Auto-save indicator
        auto_save_lbl = QLabel(self.translator.t("set_auto_save"))
        auto_save_lbl.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(auto_save_lbl)

        layout.addStretch()
        
        # --- SECCIÓN ACERCA DE ---
        about_group = QHBoxLayout()
        btn_about = QPushButton(self.translator.t("set_btn_about"))
        btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_about.setFixedWidth(200)
        btn_about.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                color: #a0c0ff; 
                border: 1px solid #a0c0ff;
                border-radius: 6px; 
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #152030;
            }
        """)
        btn_about.clicked.connect(self.show_about)
        about_group.addWidget(btn_about)
        about_group.addStretch()
        layout.addLayout(about_group)

    def on_lang_changed(self, index):
        new_lang = self.lang_cb.itemData(index)
        self.emu_manager.language = new_lang
        self.emu_manager.save_config()
        self.on_language_change_callback(new_lang)
        
    def browse_install_path(self):
        directory = QFileDialog.getExistingDirectory(self, self.translator.t("set_dlg_emus"), self.install_path_input.text())
        if directory:
            self.install_path_input.setText(directory)
            self.auto_save_settings()
            
    def browse_roms_path(self):
        directory = QFileDialog.getExistingDirectory(self, self.translator.t("set_dlg_roms"), self.roms_path_input.text())
        if directory:
            self.roms_path_input.setText(directory)
            self.auto_save_settings()
            
    def auto_save_settings(self):
        # We auto-save to EmuManager config when fields finish editing or files are browsed.
        old_install = self.emu_manager.install_path
        old_roms = self.emu_manager.roms_path
        
        new_install = self.install_path_input.text().strip()
        new_roms = self.roms_path_input.text().strip()
        
        if old_install != new_install or old_roms != new_roms:
            self.emu_manager.install_path = new_install
            self.emu_manager.roms_path = new_roms
            self.emu_manager.save_config()
            self.on_update_dashboard()
        
    def show_about(self):
        """Muestra un diálogo de 'Acerca de' con diseño premium."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
        from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
        from PyQt6.QtCore import QSize, QUrl
        import os

        dialog = QDialog(self)
        dialog.setWindowTitle(self.translator.t("set_about_title"))
        dialog.setFixedWidth(460)  # Aumentamos el ancho para que el texto respire
        dialog.setStyleSheet("background-color: #0c0d12; border: 1px solid #1a1c24; border-radius: 12px;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(18)

        # Icono Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("border: none; background: transparent;") # Sin fondo
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "media", "icon.svg")
        
        if os.path.exists(icon_path):
            pixmap = QIcon(icon_path).pixmap(QSize(90, 90))
            logo_label.setPixmap(pixmap)
        
        layout.addWidget(logo_label)

        # Nombre y Versión
        name_label = QLabel("EmuManager")
        name_label.setStyleSheet("font-size: 26px; font-weight: bold; color: white; border: none; background: transparent;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        ver_label = QLabel(self.translator.t("set_about_ver"))
        ver_label.setStyleSheet("font-size: 14px; color: #4da6ff; font-weight: bold; border: none; background: transparent;")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver_label)

        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #1a1c24; border: none;")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # Descripción
        desc_label = QLabel(self.translator.t("set_about_desc"))
        desc_label.setStyleSheet("font-size: 13px; color: #a0a0a0; border: none; background: transparent; line-height: 1.4;")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # Información de Licencia (Software Libre / GNU)
        license_box = QFrame()
        license_box.setStyleSheet("background-color: #15171e; border-radius: 10px; border: 1px solid #1a1c24;")
        license_layout = QVBoxLayout(license_box)
        license_layout.setContentsMargins(15, 15, 15, 15)
        license_layout.setSpacing(8)
        
        license_title = QLabel(self.translator.t("set_about_license_title"))
        license_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #10B981; border: none; background: transparent; text-transform: uppercase; letter-spacing: 1px;")
        license_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        license_text = QLabel(self.translator.t("set_about_license"))
        license_text.setStyleSheet("font-size: 12px; color: #e0e0e0; border: none; background: transparent;")
        license_text.setWordWrap(True)
        license_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Link de licencia estilizado
        license_link = QLabel(f'<a href="https://www.gnu.org/licenses/gpl-3.0.html" style="color: #4da6ff; text-decoration: none; font-weight: bold;">{self.translator.t("set_about_link")}</a>')
        license_link.setStyleSheet("font-size: 12px; border: none; background: transparent;")
        license_link.setOpenExternalLinks(True)
        license_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        license_layout.addWidget(license_title)
        license_layout.addWidget(license_text)
        license_layout.addWidget(license_link)
        layout.addWidget(license_box)

        # Copyright
        copy_label = QLabel(self.translator.t("set_about_copy"))
        copy_label.setStyleSheet("font-size: 11px; color: #555; border: none; background: transparent; margin-top: 5px;")
        copy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copy_label)

        # Botón Cerrar
        btn_close = QPushButton(self.translator.t("set_btn_close"))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedWidth(120)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #1a1c24;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #4da6ff;
                color: #000000;
                border: 1px solid #4da6ff;
            }
        """)
        btn_close.clicked.connect(dialog.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        dialog.exec()
