import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox, QFrame, QSizePolicy,
    QDialog, QCheckBox, QProgressBar, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from qasync import asyncSlot
import core.artwork as artwork
import core.scanner as scanner
from core.constants import AVAILABLE_EMULATORS

class SettingsView(QWidget):
    def __init__(self, emu_manager, translator, on_update_dashboard, on_language_change, parent=None):
        super().__init__(parent)
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_dashboard = on_update_dashboard
        self.on_language_change_callback = on_language_change
        
        self.init_ui()
        
    def init_ui(self):
        # Layout principal de SettingsView
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area para evitar que se recorte el contenido
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("settingsScrollArea")
        
        # Widget que contendrá todo el contenido de configuración
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("settingsScrollContent")
        
        # Layout para el contenido (el layout original)
        layout = QVBoxLayout(self.scroll_content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Titulo Principal
        self.title = QLabel(self.translator.t("set_title"))
        self.title.setProperty("class", "pageTitle")
        layout.addWidget(self.title)
        
        # --- SECCIÓN IDIOMA ---
        lang_group = QVBoxLayout()
        self.lang_lbl = QLabel(self.translator.t("set_lang_lbl"))
        self.lang_lbl.setProperty("class", "sectionTitle")
        
        self.lang_cb = QComboBox()
        self.lang_cb.setProperty("class", "formSelect")
        self.lang_cb.addItem("Español", "es")
        self.lang_cb.addItem("English", "en")
        self.lang_cb.setFixedWidth(200)
        
        index = self.lang_cb.findData(self.emu_manager.language)
        if index >= 0:
            self.lang_cb.setCurrentIndex(index)
            
        self.lang_cb.currentIndexChanged.connect(self.on_lang_changed)
        
        lang_group.addWidget(self.lang_lbl)
        lang_group.addWidget(self.lang_cb)
        layout.addLayout(lang_group)
        
        # Separador
        hline = QFrame()
        hline.setFrameShape(QFrame.Shape.HLine)
        hline.setProperty("class", "separatorLine")
        layout.addWidget(hline)
        
        # --- SECCIÓN RUTAS ---
        # Ruta Emuladores
        emus_group = QVBoxLayout()
        self.emus_title = QLabel(self.translator.t("set_emus_title"))
        self.emus_title.setProperty("class", "sectionTitle")
        self.emus_sub = QLabel(self.translator.t("set_emus_sub"))
        self.emus_sub.setProperty("class", "sectionSubtitle")
        
        emus_path_layout = QHBoxLayout()
        self.install_path_input = QLineEdit(self.emu_manager.install_path or "")
        self.install_path_input.setProperty("class", "formInput")
        self.install_path_input.editingFinished.connect(self.auto_save_settings)
        
        self.btn_browse_install = QPushButton(self.translator.t("set_btn_select"))
        self.btn_browse_install.setProperty("class", "actionButton")
        self.btn_browse_install.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse_install.clicked.connect(self.browse_install_path)
        
        emus_path_layout.addWidget(self.install_path_input)
        emus_path_layout.addWidget(self.btn_browse_install)
        
        emus_group.addWidget(self.emus_title)
        emus_group.addSpacing(2)
        emus_group.addWidget(self.emus_sub)
        emus_group.addSpacing(12)
        emus_group.addLayout(emus_path_layout)
        layout.addLayout(emus_group)
        
        # Ruta ROMs
        roms_group = QVBoxLayout()
        self.roms_title = QLabel(self.translator.t("set_roms_title"))
        self.roms_title.setProperty("class", "sectionTitle")
        self.roms_sub = QLabel(self.translator.t("set_roms_sub"))
        self.roms_sub.setProperty("class", "sectionSubtitle")
        
        roms_path_layout = QHBoxLayout()
        self.roms_path_input = QLineEdit(self.emu_manager.roms_path or "")
        self.roms_path_input.setProperty("class", "formInput")
        self.roms_path_input.editingFinished.connect(self.auto_save_settings)
        
        self.btn_browse_roms = QPushButton(self.translator.t("set_btn_select"))
        self.btn_browse_roms.setProperty("class", "actionButton")
        self.btn_browse_roms.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse_roms.clicked.connect(self.browse_roms_path)
        
        roms_path_layout.addWidget(self.roms_path_input)
        roms_path_layout.addWidget(self.btn_browse_roms)
        
        roms_group.addWidget(self.roms_title)
        roms_group.addSpacing(2)
        roms_group.addWidget(self.roms_sub)
        roms_group.addSpacing(12)
        roms_group.addLayout(roms_path_layout)
        layout.addLayout(roms_group)
        
        # Auto-save indicator
        self.auto_save_lbl = QLabel(self.translator.t("set_auto_save"))
        self.auto_save_lbl.setProperty("class", "infoText")
        layout.addWidget(self.auto_save_lbl)

        # Separador
        hline2 = QFrame()
        hline2.setFrameShape(QFrame.Shape.HLine)
        hline2.setProperty("class", "separatorLine")
        layout.addWidget(hline2)

        # --- SECCIÓN BASES DE DATOS (Scrapers) ---
        scrapers_group = QVBoxLayout()
        self.scrapers_title = QLabel("CONFIGURACIÓN DE BASES DE DATOS")
        self.scrapers_title.setProperty("class", "sectionTitle")
        self.scrapers_sub = QLabel("Activa y configura las fuentes de información para tus juegos.")
        self.scrapers_sub.setProperty("class", "sectionSubtitle")
        
        scrapers_group.addWidget(self.scrapers_title)
        scrapers_group.addWidget(self.scrapers_sub)
        scrapers_group.addSpacing(15)

        # Lista de Proveedores (Tarjetas)
        from core.metadata import get_providers_config
        self.providers_data = get_providers_config()
        self.provider_widgets = []

        for p_data in self.providers_data:
            card = QFrame()
            card.setObjectName("providerCard")
            card.setMinimumHeight(70)
            card.setStyleSheet("""
                QFrame#providerCard {
                    background: rgba(255,255,255,0.03);
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 12px;
                }
                QFrame#providerCard:hover {
                    background: rgba(255,255,255,0.05);
                    border-color: rgba(77, 166, 255, 0.4);
                }
            """)
            
            p_layout = QHBoxLayout(card)
            p_layout.setContentsMargins(20, 10, 20, 10)

            # Info del proveedor
            v_info = QVBoxLayout()
            p_name = QLabel(p_data["name"])
            p_name.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
            p_status = QLabel("Conectado" if p_data.get("enabled") else "Desactivado")
            p_status.setStyleSheet("font-size: 11px; color: #4da6ff;" if p_data.get("enabled") else "font-size: 11px; color: #777;")
            v_info.addWidget(p_name)
            v_info.addWidget(p_status)
            p_layout.addLayout(v_info)
            p_layout.addStretch()

            # Botón Configuración
            btn_cfg = QPushButton("Configurar")
            btn_cfg.setFixedWidth(100)
            btn_cfg.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_cfg.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.08); border: none; 
                    border-radius: 6px; padding: 6px; font-size: 11px;
                }
                QPushButton:hover { background: rgba(255,255,255,0.15); }
            """)
            btn_cfg.clicked.connect(lambda checked, p=p_data: self.configure_provider(p))
            p_layout.addWidget(btn_cfg)

            # Switch (Checkbox estilizado)
            cb = QCheckBox()
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            cb.setChecked(p_data.get("enabled", False))
            cb.stateChanged.connect(lambda state, p=p_data, s=p_status: self.toggle_provider(p, state, s))
            p_layout.addWidget(cb)

            scrapers_group.addWidget(card)
        
        layout.addLayout(scrapers_group)

        # Separador final
        hline3 = QFrame()
        hline3.setFrameShape(QFrame.Shape.HLine)
        hline3.setProperty("class", "separatorLine")
        layout.addWidget(hline3)

        layout.addStretch()
        
        # --- SECCIÓN ACERCA DE ---
        about_group = QHBoxLayout()
        about_group.addStretch() # Añadir stretch a la izquierda para centrar
        self.btn_about = QPushButton(self.translator.t("set_btn_about"))
        self.btn_about.setProperty("class", "secondaryButton")
        self.btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about.setFixedWidth(240)
        self.btn_about.clicked.connect(self.show_about)
        about_group.addWidget(self.btn_about)
        about_group.addStretch() # Añadir stretch a la derecha para centrar
        layout.addLayout(about_group)
        layout.addSpacing(10) # Pequeño margen inferior

        # Configurar el scroll area con su contenido
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

    def on_lang_changed(self, index):
        new_lang = self.lang_cb.itemData(index)
        if new_lang == self.emu_manager.language:
            return
        self.emu_manager.language = new_lang
        self.emu_manager.save_config()
        self.on_language_change_callback(new_lang)

    def retranslate_ui(self):
        """Actualiza todos los textos de la vista al cambiar el idioma."""
        self.title.setText(self.translator.t("set_title"))
        self.lang_lbl.setText(self.translator.t("set_lang_lbl"))
        self.emus_title.setText(self.translator.t("set_emus_title"))
        self.emus_sub.setText(self.translator.t("set_emus_sub"))
        self.btn_browse_install.setText(self.translator.t("set_btn_select"))
        self.roms_title.setText(self.translator.t("set_roms_title"))
        self.roms_sub.setText(self.translator.t("set_roms_sub"))
        self.btn_browse_roms.setText(self.translator.t("set_btn_select"))
        self.auto_save_lbl.setText(self.translator.t("set_auto_save"))
        self.btn_about.setText(self.translator.t("set_btn_about"))
        
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
            
            # Actualizar ruta de arte dinámico
            import core.artwork as artwork
            if new_install:
                media_path = os.path.join(new_install, "media")
                artwork.set_base_media_path(media_path)
                
            self.on_update_dashboard()

    def toggle_provider(self, provider_data, state, status_label):
        enabled = (state == 2) # 2 es Checked en Qt
        provider_data["enabled"] = enabled
        status_label.setText("Conectado" if enabled else "Desactivado")
        status_label.setStyleSheet("font-size: 11px; color: #4da6ff;" if enabled else "font-size: 11px; color: #777;")
        self.save_provider_config()

    def configure_provider(self, p):
        """Abre un diálogo para configurar el proveedor específico."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Configurar {p['name']}")
        dialog.setFixedWidth(350)
        v = QVBoxLayout(dialog)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(10)

        v.addWidget(QLabel(f"<b>Configuración para {p['name']}</b>"))
        
        inputs = {}
        # Renderizar campos según el proveedor
        if p["id"] in ["tgdb", "rawg"]:
            v.addWidget(QLabel("API Key:"))
            edt = QLineEdit(p.get("api_key", ""))
            edt.setProperty("class", "formInput")
            v.addWidget(edt)
            inputs["api_key"] = edt
        elif p["id"] == "screenscraper":
            v.addWidget(QLabel("Usuario:"))
            u_edt = QLineEdit(p.get("user", ""))
            v.addWidget(u_edt)
            v.addWidget(QLabel("Contraseña:"))
            p_edt = QLineEdit(p.get("password", ""))
            p_edt.setEchoMode(QLineEdit.EchoMode.Password)
            v.addWidget(p_edt)
            inputs["user"] = u_edt
            inputs["password"] = p_edt

        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(dialog.accept)
        v.addWidget(btn_save)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            for k, edt in inputs.items():
                p[k] = edt.text()
            self.save_provider_config()
            QMessageBox.information(self, "Guardado", f"Configuración de {p['name']} actualizada.")

    def save_provider_config(self):
        """Guarda la configuración de los proveedores en el disco."""
        # Por ahora lo guardamos en un archivo separado para no romper el emu_manager config
        path = os.path.join("data", "scrapers_config.json")
        try:
            os.makedirs("data", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.providers_data, f, indent=2)
        except Exception as e:
            print(f"Error guardando scrapers_config: {e}")

    def show_about(self):
        """Muestra un diálogo de 'Acerca de' con diseño premium."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
        from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
        from PyQt6.QtCore import QSize, QUrl
        

        dialog = QDialog(self)
        dialog.setWindowTitle(self.translator.t("set_about_title"))
        dialog.setFixedWidth(460)  # Aumentamos el ancho para que el texto respire
        dialog.setObjectName("aboutDialog")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(18)

        # Icono Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setObjectName("aboutLogo")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "media", "icon.svg")
        
        if os.path.exists(icon_path):
            pixmap = QIcon(icon_path).pixmap(QSize(90, 90))
            logo_label.setPixmap(pixmap)
        
        layout.addWidget(logo_label)

        # Nombre y Versión
        name_label = QLabel("EmuManager")
        name_label.setObjectName("aboutTitleText")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        ver_label = QLabel(self.translator.t("set_about_ver"))
        ver_label.setObjectName("aboutVersionText")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver_label)

        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("aboutSeparator")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # Descripción
        desc_label = QLabel(self.translator.t("set_about_desc"))
        desc_label.setObjectName("aboutDescText")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # Información de Licencia (Software Libre / GNU)
        license_box = QFrame()
        license_box.setObjectName("licenseBox")
        license_layout = QVBoxLayout(license_box)
        license_layout.setContentsMargins(15, 15, 15, 15)
        license_layout.setSpacing(8)
        
        license_title = QLabel(self.translator.t("set_about_license_title"))
        license_title.setObjectName("licenseTitleText")
        license_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        license_text = QLabel(self.translator.t("set_about_license"))
        license_text.setObjectName("licenseContentText")
        license_text.setWordWrap(True)
        license_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Link de licencia estilizado
        license_link = QLabel(f'<a href="https://www.gnu.org/licenses/gpl-3.0.html" style="color: #4da6ff; text-decoration: none; font-weight: bold;">{self.translator.t("set_about_link")}</a>')
        license_link.setObjectName("licenseLinkText")
        license_link.setOpenExternalLinks(True)
        license_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        license_layout.addWidget(license_title)
        license_layout.addWidget(license_text)
        license_layout.addWidget(license_link)
        layout.addWidget(license_box)

        # Copyright
        copy_label = QLabel(self.translator.t("set_about_copy"))
        copy_label.setObjectName("copyText")
        copy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copy_label)

        # Botón Cerrar
        btn_close = QPushButton(self.translator.t("set_btn_close"))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedWidth(120)
        btn_close.setObjectName("aboutCloseBtn")
        btn_close.clicked.connect(dialog.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        dialog.exec()


