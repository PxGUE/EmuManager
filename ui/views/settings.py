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
    def __init__(self, emu_manager, translator, on_update_dashboard, on_language_change):
        super().__init__()
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
        title = QLabel(self.translator.t("set_title"))
        title.setProperty("class", "pageTitle")
        layout.addWidget(title)
        
        # --- SECCIÓN IDIOMA ---
        lang_group = QVBoxLayout()
        lang_lbl = QLabel(self.translator.t("set_lang_lbl"))
        lang_lbl.setProperty("class", "sectionTitle")
        
        self.lang_cb = QComboBox()
        self.lang_cb.setProperty("class", "formSelect")
        self.lang_cb.addItem("Español", "es")
        self.lang_cb.addItem("English", "en")
        self.lang_cb.setFixedWidth(200)
        
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
        hline.setProperty("class", "separatorLine")
        layout.addWidget(hline)
        
        # --- SECCIÓN RUTAS ---
        # Ruta Emuladores
        emus_group = QVBoxLayout()
        emus_title = QLabel(self.translator.t("set_emus_title"))
        emus_title.setProperty("class", "sectionTitle")
        emus_sub = QLabel(self.translator.t("set_emus_sub"))
        emus_sub.setProperty("class", "sectionSubtitle")
        
        emus_path_layout = QHBoxLayout()
        self.install_path_input = QLineEdit(self.emu_manager.install_path or "")
        self.install_path_input.setProperty("class", "formInput")
        self.install_path_input.editingFinished.connect(self.auto_save_settings)
        
        btn_browse_install = QPushButton(self.translator.t("set_btn_select"))
        btn_browse_install.setProperty("class", "actionButton")
        btn_browse_install.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_install.clicked.connect(self.browse_install_path)
        
        emus_path_layout.addWidget(self.install_path_input)
        emus_path_layout.addWidget(btn_browse_install)
        
        emus_group.addWidget(emus_title)
        emus_group.addSpacing(2)
        emus_group.addWidget(emus_sub)
        emus_group.addSpacing(12)
        emus_group.addLayout(emus_path_layout)
        layout.addLayout(emus_group)
        
        # Ruta ROMs
        roms_group = QVBoxLayout()
        roms_title = QLabel(self.translator.t("set_roms_title"))
        roms_title.setProperty("class", "sectionTitle")
        roms_sub = QLabel(self.translator.t("set_roms_sub"))
        roms_sub.setProperty("class", "sectionSubtitle")
        
        roms_path_layout = QHBoxLayout()
        self.roms_path_input = QLineEdit(self.emu_manager.roms_path or "")
        self.roms_path_input.setProperty("class", "formInput")
        self.roms_path_input.editingFinished.connect(self.auto_save_settings)
        
        btn_browse_roms = QPushButton(self.translator.t("set_btn_select"))
        btn_browse_roms.setProperty("class", "actionButton")
        btn_browse_roms.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_roms.clicked.connect(self.browse_roms_path)
        
        roms_path_layout.addWidget(self.roms_path_input)
        roms_path_layout.addWidget(btn_browse_roms)
        
        roms_group.addWidget(roms_title)
        roms_group.addSpacing(2)
        roms_group.addWidget(roms_sub)
        roms_group.addSpacing(12)
        roms_group.addLayout(roms_path_layout)
        layout.addLayout(roms_group)
        
        # Auto-save indicator
        auto_save_lbl = QLabel(self.translator.t("set_auto_save"))
        auto_save_lbl.setProperty("class", "infoText")
        layout.addWidget(auto_save_lbl)

        # Separador
        hline2 = QFrame()
        hline2.setFrameShape(QFrame.Shape.HLine)
        hline2.setProperty("class", "separatorLine")
        layout.addWidget(hline2)
        
        # --- SECCIÓN SCRAPING ---
        scrap_group = QVBoxLayout()
        scrap_title = QLabel(self.translator.t("set_scraping_title"))
        scrap_title.setProperty("class", "sectionTitle")
        scrap_sub = QLabel(self.translator.t("set_scraping_sub"))
        scrap_sub.setProperty("class", "sectionSubtitle")
        
        self.btn_scraping = QPushButton(self.translator.t("set_btn_scraping"))
        self.btn_scraping.setProperty("class", "primaryButton")
        self.btn_scraping.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scraping.clicked.connect(self.open_scraping_dialog)
        self.btn_scraping.setFixedWidth(250) # Limitar ancho para que no se estire
        
        scrap_group.addWidget(scrap_title)
        scrap_group.addWidget(scrap_sub)
        scrap_group.addWidget(self.btn_scraping)
        
        emus_path_layout.setContentsMargins(0, 10, 0, 10)
        roms_path_layout.setContentsMargins(0, 10, 0, 10)
        
        layout.addLayout(scrap_group)
        layout.addStretch()
        
        # --- SECCIÓN ACERCA DE ---
        about_group = QHBoxLayout()
        about_group.addStretch() # Añadir stretch a la izquierda para centrar
        btn_about = QPushButton(self.translator.t("set_btn_about"))
        btn_about.setProperty("class", "secondaryButton")
        btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_about.setFixedWidth(240)
        btn_about.clicked.connect(self.show_about)
        about_group.addWidget(btn_about)
        about_group.addStretch() # Añadir stretch a la derecha para centrar
        layout.addLayout(about_group)
        layout.addSpacing(10) # Pequeño margen inferior

        # Configurar el scroll area con su contenido
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

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
            
            # Actualizar ruta de arte dinámico
            import core.artwork as artwork
            if new_install:
                media_path = os.path.join(new_install, "media")
                artwork.set_base_media_path(media_path)
                
            self.on_update_dashboard()
        
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

    def open_scraping_dialog(self):
        """Abre el diálogo de scraping personalizado."""
        dialog = ScrapingDialog(self.emu_manager, self.translator, self)
        dialog.exec()

class ScrapingDialog(QDialog):
    def __init__(self, emu_manager, translator, parent=None):
        super().__init__(parent)
        self.emu_manager = emu_manager
        self.translator = translator
        self.selections = {} # {id_emu: {"covers": QCheckBox, "bg": QCheckBox}}
        self.is_running = False
        
        self.init_ui()
        
    def init_ui(self):
        from PyQt6.QtWidgets import QGridLayout
        
        self.setWindowTitle(self.translator.t("set_scrap_dlg_title"))
        self.setFixedWidth(550)
        self.setMinimumHeight(450)
        self.setObjectName("scrapingDialog")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Titulo
        title = QLabel(self.translator.t("set_scrap_dlg_title").upper())
        title.setObjectName("scrapingDialogTitle")
        layout.addWidget(title)
        
        desc = QLabel(self.translator.t("set_scrap_dlg_select"))
        desc.setObjectName("scrapingDialogDesc")
        layout.addWidget(desc)

        # Controles Maestros
        master_layout = QHBoxLayout()
        self.cb_all_covers = QCheckBox("Todas las Carátulas")
        self.cb_all_covers.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_all_covers.setChecked(True)
        self.cb_all_covers.toggled.connect(lambda checked: self.toggle_all_column(checked, "covers"))
        
        self.cb_all_bgs = QCheckBox("Todos los Fondos")
        self.cb_all_bgs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_all_bgs.setChecked(False)
        self.cb_all_bgs.toggled.connect(lambda checked: self.toggle_all_column(checked, "bg"))
        
        master_layout.addWidget(self.cb_all_covers)
        master_layout.addWidget(self.cb_all_bgs)
        master_layout.addStretch()
        layout.addLayout(master_layout)
        
        # Área Scrolleable de Consolas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("consolesScroll")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("consolesScrollContent")
        
        # Usamos Grid para la tabla granular
        grid = QGridLayout(scroll_content)
        grid.setSpacing(10)
        grid.setColumnStretch(0, 1) # Nombre Consola toma el espacio sobrante
        
        # Cabeceras de tabla
        lbl_col_name = QLabel("CONSOLA")
        lbl_col_name.setStyleSheet("font-weight: bold; color: #8a8d98; font-size: 11px;")
        lbl_col_cover = QLabel("CARÁTULAS")
        lbl_col_cover.setStyleSheet("font-weight: bold; color: #8a8d98; font-size: 11px;")
        lbl_col_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_col_bg = QLabel("FONDOS")
        lbl_col_bg.setStyleSheet("font-weight: bold; color: #8a8d98; font-size: 11px;")
        lbl_col_bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        grid.addWidget(lbl_col_name, 0, 0)
        grid.addWidget(lbl_col_cover, 0, 1)
        grid.addWidget(lbl_col_bg, 0, 2)
        
        # Filas dinámicas (Solo consolas instaladas)
        row = 1
        for emu in AVAILABLE_EMULATORS:
            if not self.emu_manager.esta_instalado(emu["github"]):
                continue
                
            console_key = f"emu_{emu['id']}_console"
            translated_console = self.translator.t(console_key)
            name_lbl = QLabel(f"{emu['name']} ({translated_console})")
            
            cb_cov = QCheckBox()
            cb_cov.setCursor(Qt.CursorShape.PointingHandCursor)
            cb_cov.setChecked(True) # Por defecto bajamos caratulas
            # Centrar el checkbox visualmente
            cov_container = QWidget()
            cov_layout = QHBoxLayout(cov_container)
            cov_layout.setContentsMargins(0,0,0,0)
            cov_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cov_layout.addWidget(cb_cov)
            
            cb_bg = QCheckBox()
            cb_bg.setCursor(Qt.CursorShape.PointingHandCursor)
            # Solo bajar fondos estéticamente pesados si se pide explícitamente, o dejar unchecked por defecto
            cb_bg.setChecked(False) 
            bg_container = QWidget()
            bg_layout = QHBoxLayout(bg_container)
            bg_layout.setContentsMargins(0,0,0,0)
            bg_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bg_layout.addWidget(cb_bg)
            
            grid.addWidget(name_lbl, row, 0)
            grid.addWidget(cov_container, row, 1)
            grid.addWidget(bg_container, row, 2)
            
            self.selections[emu["id"]] = {"covers": cb_cov, "bg": cb_bg}
            row += 1
            
        # Añadir un espaciador al final del grid para empujar filas arriba si hay espacio libre
        grid.setRowStretch(row, 1)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Info de estado y Barra de Progreso
        self.status_lbl = QLabel(self.translator.t("set_scrap_status_idle"))
        self.status_lbl.setObjectName("scrapingStatusLabel")
        layout.addWidget(self.status_lbl)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setObjectName("scrapingProgressBar")
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Botones de Acción
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_start = QPushButton(self.translator.t("set_scrap_btn_start"))
        self.btn_start.setProperty("class", "actionButton")
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.setFixedHeight(42)
        self.btn_start.setFixedWidth(180)
        self.btn_start.clicked.connect(self.run_scraping)
        
        self.btn_close = QPushButton(self.translator.t("set_scrap_btn_close"))
        self.btn_close.setProperty("class", "secondaryButton")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setFixedHeight(42)
        self.btn_close.setFixedWidth(180)
        self.btn_close.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_close)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_start)
        layout.addLayout(btn_layout)

    def toggle_all_column(self, checked, col_key):
        """Marca o desmarca todos los checkboxes de una columna (covers o bg)."""
        for emu_id, dict_cbs in self.selections.items():
            dict_cbs[col_key].setChecked(checked)

    @asyncSlot()
    async def run_scraping(self):
        """Ejecuta el proceso de scraping para las consolas y tareas seleccionadas."""
        if self.is_running: return
        
        # Analizar selecciones
        covers_targets = [eid for eid, cbs in self.selections.items() if cbs["covers"].isChecked()]
        bg_targets = [eid for eid, cbs in self.selections.items() if cbs["bg"].isChecked()]
        
        if not covers_targets and not bg_targets:
            QMessageBox.information(self, "Aviso", "No has seleccionado tareas a procesar.")
            return
            
        if covers_targets and not self.emu_manager.roms_path:
            QMessageBox.warning(self, "Error", self.translator.t("lib_missing_roms"))
            return

        self.is_running = True
        self.btn_start.setEnabled(False)
        self.btn_close.setEnabled(False)
        
        try:
            # 1. Descarga individual de Fondos primero (rápido)
            if bg_targets:
                self.status_lbl.setText("Descargando Fondos de Consolas (Artwork)...")
                self.progress_bar.setRange(0, 0)
                
                def bg_progress(actual, total, nombre):
                    if self.progress_bar.maximum() == 0:
                        self.progress_bar.setRange(0, total)
                    self.progress_bar.setValue(actual)
                    self.status_lbl.setText(f"Fondos: [ {actual}/{total} ] {nombre}")
                    
                await artwork.descargar_fondos_consolas(bg_progress, emus_a_descargar=bg_targets)

            # 2. Descarga de Carátulas (lento, escaneo ROMS)
            if covers_targets:
                total_covers = len(covers_targets)
                emu_platform_map = {emu["id"]: emu.get("libretro_platform") for emu in AVAILABLE_EMULATORS}
                
                for i, emu_id in enumerate(covers_targets):
                    emu_name = next(e["name"] for e in AVAILABLE_EMULATORS if e["id"] == emu_id)
                    self.status_lbl.setText(f"[{i+1}/{total_covers}] {emu_name}: Escaneando ROMs...")
                    self.progress_bar.setRange(0, 0) # Indeterminado
                    
                    juegos = await scanner.escanear_roms(self.emu_manager.roms_path, emu_id=emu_id)
                    if not juegos:
                        continue
                    
                    self.status_lbl.setText(f"[{i+1}/{total_covers}] {emu_name}: Descargando imágenes...")
                    self.progress_bar.setRange(0, len(juegos))
                    self.progress_bar.setValue(0)
                    
                    j_dict = [j if isinstance(j, dict) else j.__dict__ for j in juegos]
                    
                    def cv_progress(actual, total, nombre):
                        self.progress_bar.setValue(actual)
                        msg = f"[{i+1}/{total_covers}] {emu_name}: {actual}/{total} - {nombre if nombre else '...'}"
                        self.status_lbl.setText(msg)
                    
                    await artwork.descargar_caratulas_biblioteca(
                        j_dict, emu_platform_map, self.emu_manager.roms_path, cv_progress
                    )
            
            self.status_lbl.setText(self.translator.t("lib_status_complete"))
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo durante el scraping: {e}")
            self.status_lbl.setText(f"Error: {e}")
        finally:
            self.is_running = False
            self.btn_start.setEnabled(True)
            self.btn_close.setEnabled(True)
            self.btn_close.setText(self.translator.t("set_btn_close"))

