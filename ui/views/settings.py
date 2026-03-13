import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox, QFrame,
    QDialog, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
import core.artwork as artwork
import core.scanner as scanner
import core.security as security
from core.config import APP_VERSION

class CollapsibleSection(QWidget):
    """Contenedor simple para secciones desplegables con un arrow animado."""
    def __init__(self, title_key, translator, parent=None):
        super().__init__(parent)
        self.title_key = title_key
        self.translator = translator
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header (Botón)
        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #888;
                font-size: 11px;
                font-weight: 900;
                text-align: left;
                border: none;
                padding: 15px 0 10px 0;
                letter-spacing: 1px;
            }
            QPushButton:hover { color: #4da6ff; }
        """)
        self.toggle_btn.toggled.connect(self.set_content_visible)
        
        self.content_area = QWidget()
        self.content_area.setVisible(False)
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 0, 0, 15)
        self.content_layout.setSpacing(10)
        
        self.main_layout.addWidget(self.toggle_btn)
        self.main_layout.addWidget(self.content_area)
        
        self.retranslate_ui()

    def set_content_visible(self, visible):
        self.content_area.setVisible(visible)
        self.retranslate_ui()

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def retranslate_ui(self):
        arrow = "▼" if self.toggle_btn.isChecked() else "▶"
        title = self.translator.t(self.title_key).upper()
        self.toggle_btn.setText(f"{arrow}   {title}")

class SettingsView(QWidget):
    def __init__(self, emu_manager, translator, on_update_dashboard, on_language_change, parent=None):
        super().__init__(parent)
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_dashboard = on_update_dashboard
        self.on_language_change_callback = on_language_change
        
        self.init_ui()

    def save_provider_config(self):
        """Guarda la configuración de los proveedores en el disco (sin datos sensibles)."""
        path = os.path.join("data", "scrapers_config.json")
        try:
            # Crear una copia limpia para guardar sin secretos
            clean_data = []
            secrets_blacklist = ["api_key", "user", "password"]
            
            for p in self.providers_data:
                clean_p = p.copy()
                for key in secrets_blacklist:
                    if key in clean_p:
                        del clean_p[key]
                clean_data.append(clean_p)

            os.makedirs("data", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(clean_data, f, indent=2)
        except Exception as e:
            print(f"Error guardando scrapers_config: {e}")

    def show_about(self):
        """Muestra un diálogo de 'Acerca de' con diseño premium."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
        from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
        from PyQt6.QtCore import QSize, QUrl
        from core.config import APP_VERSION

        dialog = QDialog(self)
        dialog.setWindowTitle(self.translator.t("set_about_title"))
        dialog.setFixedWidth(460)
        dialog.setObjectName("aboutDialog")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(18)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setObjectName("aboutLogo")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "media", "icon.svg")
        
        if os.path.exists(icon_path):
            pixmap = QIcon(icon_path).pixmap(QSize(90, 90))
            logo_label.setPixmap(pixmap)
        
        layout.addWidget(logo_label)

        name_label = QLabel("EmuManager")
        name_label.setObjectName("aboutTitleText")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        ver_label = QLabel(self.translator.t("set_about_ver", APP_VERSION))
        ver_label.setObjectName("aboutVersionText")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("aboutSeparator")
        line.setFixedHeight(1)
        layout.addWidget(line)

        desc_label = QLabel(self.translator.t("set_about_desc"))
        desc_label.setObjectName("aboutDescText")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

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
        
        license_link = QLabel(f'<a href="https://www.gnu.org/licenses/gpl-3.0.html" style="color: #4da6ff; text-decoration: none; font-weight: bold;">{self.translator.t("set_about_link")}</a>')
        license_link.setObjectName("licenseLinkText")
        license_link.setOpenExternalLinks(True)
        license_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        license_layout.addWidget(license_title)
        license_layout.addWidget(license_text)
        license_layout.addWidget(license_link)
        layout.addWidget(license_box)

        # Sección de Privacidad (Nueva)
        privacy_box = QFrame()
        privacy_box.setObjectName("licenseBox")
        privacy_layout = QVBoxLayout(privacy_box)
        privacy_layout.setContentsMargins(15, 12, 15, 12)
        
        privacy_title = QLabel(self.translator.t("set_about_privacy_title"))
        privacy_title.setObjectName("licenseTitleText")
        privacy_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        privacy_text = QLabel(self.translator.t("set_about_privacy_desc"))
        privacy_text.setObjectName("licenseContentText")
        privacy_text.setWordWrap(True)
        privacy_text.setStyleSheet("font-size: 11px; line-height: 1.4;")
        
        privacy_layout.addWidget(privacy_title)
        privacy_layout.addWidget(privacy_text)
        layout.addWidget(privacy_box)

        copy_label = QLabel(self.translator.t("set_about_copy"))
        copy_label.setObjectName("copyText")
        copy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copy_label)

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
        self.scrapers_title = QLabel(self.translator.t("set_scrapers_title"))
        self.scrapers_title.setProperty("class", "sectionTitle")
        self.scrapers_sub = QLabel(self.translator.t("set_scrapers_sub"))
        self.scrapers_sub.setProperty("class", "sectionSubtitle")
        
        scrapers_group.addWidget(self.scrapers_title)
        scrapers_group.addWidget(self.scrapers_sub)
        scrapers_group.addSpacing(15)

        # Lista de Proveedores (Tarjetas)
        from core.metadata import get_providers_config
        self.providers_data = get_providers_config()
        self.provider_status_labels = [] # List of tuples (label, p_data)
        self.provider_config_btns = [] # List of buttons

        # Categorizar proveedores
        art_providers = [p for p in self.providers_data if p.get("type") == "artwork"]
        meta_providers = [p for p in self.providers_data if p.get("type") == "metadata"]

        def create_provider_card(p_data):
            card = QFrame()
            card.setObjectName("providerCard")
            card.setMinimumHeight(85)
            card.setStyleSheet("""
                QFrame#providerCard {
                    background: #16181f;
                    border: 1px solid #252830;
                    border-radius: 14px;
                }
                QFrame#providerCard:hover {
                    background: #1b1e2a;
                    border: 1px solid #4da6ff;
                }
            """)
            
            p_layout = QHBoxLayout(card)
            p_layout.setContentsMargins(20, 15, 20, 15)
            p_layout.setSpacing(15)

            # Icono representativo o círculo de color según tipo
            icon_circle = QLabel("●")
            clr = "#4da6ff" if p_data.get("type") == "artwork" else "#7c6ff7"
            icon_circle.setStyleSheet(f"color: {clr}; font-size: 14px; background: transparent; border: none;")
            p_layout.addWidget(icon_circle)

            # Info del proveedor
            v_info = QVBoxLayout()
            v_info.setSpacing(2)
            p_name = QLabel(p_data["name"])
            p_name.setStyleSheet("font-weight: 900; font-size: 14px; color: #ffffff; background: transparent; border: none;")
            
            p_status_text = self.translator.t("set_status_connected") if p_data.get("enabled") else self.translator.t("set_status_disconnected")
            p_status = QLabel(p_status_text)
            status_clr = "#4da6ff" if p_data.get("enabled") else "#555"
            p_status.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {status_clr}; background: transparent; border: none;")
            self.provider_status_labels.append((p_status, p_data))
            
            v_info.addWidget(p_name)
            v_info.addWidget(p_status)
            p_layout.addLayout(v_info)
            p_layout.addStretch()

            # Botón Configuración (Estilo minimalista y premium)
            has_config = p_data["id"] in ["tgdb", "rawg", "steamgriddb", "screenscraper"]
            if has_config:
                btn_cfg = QPushButton(self.translator.t("set_btn_configure"))
                btn_cfg.setFixedWidth(90)
                btn_cfg.setFixedHeight(28)
                btn_cfg.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_cfg.setStyleSheet("""
                    QPushButton {
                        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); 
                        border-radius: 6px; padding: 4px; font-size: 10px; font-weight: bold; color: #aaa;
                    }
                    QPushButton:hover { background: rgba(255,255,255,0.1); color: white; border-color: #4da6ff; }
                """)
                btn_cfg.clicked.connect(lambda checked, p=p_data: self.configure_provider(p))
                self.provider_config_btns.append(btn_cfg)
                p_layout.addWidget(btn_cfg)

            # Switch (Checkbox estilizado)
            cb = QCheckBox()
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            cb.setChecked(p_data.get("enabled", False))
            cb.stateChanged.connect(lambda state, p=p_data, s=p_status: self.toggle_provider(p, state, s))
            
            p_layout.addWidget(cb)
            return card

        # --- Subsección: ARTE ---
        self.art_section = CollapsibleSection("set_art_sources", self.translator)
        for p in art_providers:
            self.art_section.add_widget(create_provider_card(p))
        scrapers_group.addWidget(self.art_section)

        scrapers_group.addSpacing(5)

        # --- Subsección: INFORMACIÓN ---
        self.meta_section = CollapsibleSection("set_meta_sources", self.translator)
        for p in meta_providers:
            self.meta_section.add_widget(create_provider_card(p))
        scrapers_group.addWidget(self.meta_section)
        
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
        
        # Scrapers section
        self.scrapers_title.setText(self.translator.t("set_scrapers_title"))
        self.scrapers_sub.setText(self.translator.t("set_scrapers_sub"))
        
        self.art_section.retranslate_ui()
        self.meta_section.retranslate_ui()

        # Update provider cards
        for lbl, p_data in self.provider_status_labels:
            status_text = self.translator.t("set_status_connected") if p_data.get("enabled") else self.translator.t("set_status_disconnected")
            lbl.setText(status_text)
        
        for btn in self.provider_config_btns:
            btn.setText(self.translator.t("set_btn_configure"))
        
        # We need to refresh the provider cards too if they were dynamic, but since they are 
        # rebuild in init_ui, for now we just reload the view or update what we can.
        # Actually, let's just trigger a full sync if needed or keep it simple.
        self.on_update_dashboard() # This might help refresh some states
        
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
        status_label.setText(self.translator.t("set_status_connected") if enabled else self.translator.t("set_status_disconnected"))
        status_label.setStyleSheet("font-size: 11px; color: #4da6ff;" if enabled else "font-size: 11px; color: #777;")
        self.save_provider_config()

    def configure_provider(self, p):
        """Abre un diálogo para configurar el proveedor específico al estilo del Asistente Manual."""
        dialog = ScraperConfigDialog(p, self.translator, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.save_provider_config()
            # Ya no mostramos pop-up aquí, el diálogo interno da feedback o se asume el éxito.


class ScraperConfigDialog(QDialog):
    """Diálogo de configuración de scraper con el diseño premium de 'Instalación Manual'."""
    def __init__(self, provider, translator, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.translator = translator
        self.inputs = {}
        self.setWindowTitle(self.translator.t("set_dlg_config_title", provider['name']))
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(15)

        # Mensaje de estado con espacio reservado para evitar saltos en el layout
        self.status_msg = QLabel("")
        self.status_msg.setStyleSheet("color: #4da6ff; font-size: 11px; font-weight: bold;")
        self.status_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_msg.setFixedHeight(20) # Reservamos el espacio

        # Título
        title = QLabel(self.translator.t("set_dlg_config_title", self.provider['name']))
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f8f8ff;")
        layout.addWidget(title)

        # Información / Instrucciones
        info_box = QFrame()
        info_box.setStyleSheet("background: rgba(255,255,255,0.03); border: 1px solid #252830; border-radius: 8px;")
        info_layout = QVBoxLayout(info_box)
        
        info_title = QLabel(self.translator.t("set_dlg_config_for", self.provider['name']))
        info_title.setStyleSheet("font-weight: bold; color: #4da6ff; border: none;")
        
        info_desc = QLabel(self.translator.t("set_scrapers_sub")) # Reusamos subtitulo o info general
        info_desc.setStyleSheet("font-size: 11px; color: #aaaaaa; border: none;")
        info_desc.setWordWrap(True)

        info_layout.addWidget(info_title)
        info_layout.addWidget(info_desc)
        layout.addWidget(info_box)

        # Formulario de Configuración
        form_box = QFrame()
        form_box.setStyleSheet("background: rgba(255,255,255,0.03); border: 1px solid #252830; border-radius: 8px;")
        form_layout = QVBoxLayout(form_box)
        form_layout.setSpacing(15)

        # Renderizar campos según el proveedor (Ocultamos API Keys por seguridad)
        if self.provider["id"] in ["tgdb", "rawg", "steamgriddb"]:
            self._add_field(form_layout, self.translator.t("set_lbl_api_key"), "api_key", self.provider.get("api_key", ""), is_password=True)
        elif self.provider["id"] == "screenscraper":
            self._add_field(form_layout, self.translator.t("set_lbl_user"), "user", self.provider.get("user", ""))
            self._add_field(form_layout, self.translator.t("set_lbl_pass"), "password", self.provider.get("password", ""), is_password=True)

        layout.addWidget(form_box)

        # Botón de borrar (Control de usuario)
        clear_btn = QPushButton(self.translator.t("set_btn_clear"))
        clear_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; color: #ff4d4d; border: none; font-size: 11px; text-decoration: underline;
            }
            QPushButton:hover { color: #ff3333; }
        """)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setToolTip(self.translator.t("set_tip_clear", self.provider['name']))
        clear_btn.clicked.connect(self.on_clear)
        layout.addWidget(clear_btn, 0, Qt.AlignmentFlag.AlignLeft)

        layout.addSpacing(10)
        layout.addWidget(self.status_msg) # Espacio fijo aquí
        layout.addStretch()

        # Footer
        btns = QHBoxLayout()
        btns.setSpacing(12)
        
        cancel_btn = QPushButton(self.translator.t("dl_btn_cancel") if hasattr(self.translator, 't') else "Cancelar")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #888; border: 1px solid #334155; border-radius: 6px; padding: 8px; }
            QPushButton:hover { color: white; background: rgba(255,255,255,0.05); }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton(self.translator.t("set_btn_save"))
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton { 
                background: #4da6ff; color: #000000; font-weight: bold; border-radius: 6px; 
            }
            QPushButton:hover { background: #7abfff; }
        """)
        save_btn.clicked.connect(self.on_save)

        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn, 1)
        layout.addLayout(btns)

    def _add_field(self, layout, label_text, key, initial_value, is_password=False):
        v = QVBoxLayout()
        v.setSpacing(5)
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 11px; font-weight: 900; color: #4da6ff; border: none;")
        v.addWidget(lbl)
        
        # Contenedor del input (para el ojo)
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_container.setFixedHeight(34)
        input_container.setStyleSheet("""
            QFrame#inputContainer {
                background: #1a1c24; border: 1px solid #334155; border-radius: 6px;
            }
            QFrame#inputContainer:focus-within { border-color: #4da6ff; background: #1e202a; }
        """)
        h = QHBoxLayout(input_container)
        h.setContentsMargins(10, 0, 5, 0)
        h.setSpacing(5)
        
        edt = QLineEdit(str(initial_value))
        edt.setFrame(False)
        edt.setStyleSheet("background: transparent; color: #ffffff; border: none;")
        h.addWidget(edt)
        
        if is_password:
            edt.setEchoMode(QLineEdit.EchoMode.Password)
            toggle_btn = QPushButton("👁")
            toggle_btn.setFixedSize(24, 24)
            toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle_btn.setStyleSheet("""
                QPushButton { background: transparent; color: #888; border: none; font-size: 14px; }
                QPushButton:hover { color: #4da6ff; }
            """)
            
            def toggle_pass():
                if edt.echoMode() == QLineEdit.EchoMode.Password:
                    edt.setEchoMode(QLineEdit.EchoMode.Normal)
                    toggle_btn.setText("🔒")
                else:
                    edt.setEchoMode(QLineEdit.EchoMode.Password)
                    toggle_btn.setText("👁")
            
            toggle_btn.clicked.connect(toggle_pass)
            h.addWidget(toggle_btn)
            
        v.addWidget(input_container)
        layout.addLayout(v)
        self.inputs[key] = edt

    def on_save(self):
        for k, edt in self.inputs.items():
            val = edt.text().strip()
            if k in ["api_key", "user", "password"]:
                security.save_secret(self.provider["id"], k, val)
                self.provider[k] = val
            else:
                self.provider[k] = val
        
        # Mostrar feedback breve antes de cerrar
        self.status_msg.setText(self.translator.t("set_msg_saved_title"))
        QTimer.singleShot(800, self.accept)

    def on_clear(self):
        # Borrar de keyring sin preguntar (para menos clics)
        security.clear_all_secrets(self.provider["id"])
        # Limpiar memoria e inputs
        for k, edt in self.inputs.items():
            if k in ["api_key", "user", "password"]:
                edt.setText("")
                self.provider[k] = ""
        
        # Feedback en el label
        self.status_msg.setText(self.translator.t("set_msg_cleared"))
        # Ocultar mensaje después de 3 segundos (borrando el texto)
        QTimer.singleShot(3000, lambda: self.status_msg.setText(""))


