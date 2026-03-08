import asyncio
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QProgressBar, QMessageBox, QGridLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor
from qasync import asyncSlot
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork

class EmulatorCard(QFrame):
    def __init__(self, emu, emu_manager, translator, on_update_library_bg, parent=None):
        super().__init__(parent)
        self.emu = emu
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_library_bg = on_update_library_bg
        
        self.init_ui()
        self.update_ui_state()
        
    def init_ui(self):
        brand_color = self.emu.get("color", "#4da6ff")
        self.setProperty("class", "premiumCardStore")
        self.setFixedSize(260, 340) # Tamaño fijo tipo Store
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. BANNER SUPERIOR CON DOBLE DEGRADADO
        self.banner = QFrame()
        self.banner.setFixedHeight(120)
        self.banner.setProperty("class", "storeCardBanner")
        
        # El degradado se aplica en el paintEvent o vía inline style con linear-gradient
        # Usaremos inline style para los dos colores (brand color y uno más oscuro)
        darker_brand = QColor(brand_color).darker(150).name()
        self.banner.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {brand_color}, stop:1 {darker_brand});
                border-top-left-radius: 12px; 
                border-top-right-radius: 12px;
            }}
        """)
        
        banner_layout = QVBoxLayout(self.banner)
        banner_layout.setContentsMargins(0, 20, 0, 0)
        banner_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        # Logo dentro del banner
        logo_path = artwork.obtener_ruta_logo_consola(self.emu["id"]).replace(".png", ".svg")
        if not os.path.exists(logo_path):
            logo_path = artwork.obtener_ruta_logo_consola(self.emu["id"])
        if not os.path.exists(logo_path):
            logo_path = artwork.obtener_ruta_logo_emulador(self.emu["id"]).replace(".png", ".svg")
        if not os.path.exists(logo_path):
            logo_path = artwork.obtener_ruta_logo_emulador(self.emu["id"])
            
        icon_lbl = QLabel()
        if os.path.exists(logo_path):
            if logo_path.endswith(".svg"):
                pixmap = QIcon(logo_path).pixmap(QSize(90, 90))
            else:
                pixmap = QPixmap(logo_path).scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_lbl.setPixmap(pixmap)
        else:
            icon_lbl.setText("🎮")
            icon_lbl.setProperty("class", "emulatorCardIconEmpty")
            
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner_layout.addWidget(icon_lbl)
        
        # 2. SECCIÓN DE CONTENIDO BLANCA/OSCURA
        content_frame = QFrame()
        content_frame.setProperty("class", "storeCardContent")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 25, 20, 20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        content_layout.setSpacing(8)
        
        emu_lbl = QLabel(self.emu["name"])
        emu_lbl.setProperty("class", "emulatorCardTitleStore")
        emu_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emu_lbl.setWordWrap(True)
        
        # Subtítulo (Consola)
        console_lbl = QLabel(self.emu.get("console", "Emulador"))
        console_lbl.setProperty("class", "emulatorCardSubtitleStore")
        console_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_lbl = QLabel("")
        self.status_lbl.setProperty("class", "emulatorCardStatusStoreSmall")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setMinimumHeight(35) # Darle algo más de espacio para centrado visual
        
        content_layout.addWidget(emu_lbl)
        content_layout.addWidget(console_lbl)
        content_layout.addWidget(self.status_lbl)
        content_layout.addStretch()
        
        # 3. BOTÓN Y PROGRESO INTEGRADOS BOTTOM
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(15, 0, 15, 15)
        bottom_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        
        self.action_btn = QPushButton()
        self.action_btn.setProperty("class", "storeCardButton")
        self.action_btn.setFixedHeight(45)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_btn.clicked.connect(self.on_action_clicked)
        
        bottom_layout.addWidget(self.progress_bar)
        bottom_layout.addWidget(self.action_btn)
        
        main_layout.addWidget(self.banner)
        main_layout.addWidget(content_frame)
        main_layout.addLayout(bottom_layout)
        
    def update_ui_state(self, keep_status=False):
        is_installed = self.emu_manager.esta_instalado(self.emu["github"])
        if is_installed:
            self.action_btn.setText(self.translator.t("dl_btn_uninstall"))
            self.action_btn.setProperty("class", "storeCardButton danger")
            if not keep_status:
                self.status_lbl.setText("")
                self.status_lbl.setProperty("class", "emulatorCardStatusStoreSmall")
        else:
            self.action_btn.setText(self.translator.t("dl_btn_install"))
            self.action_btn.setProperty("class", "storeCardButton primary")
            if not keep_status:
                self.status_lbl.setText("")
                self.status_lbl.setProperty("class", "emulatorCardStatusStoreSmall")
            
        self.action_btn.style().unpolish(self.action_btn)
        self.action_btn.style().polish(self.action_btn)
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)
            
    @asyncSlot()
    async def on_action_clicked(self):
        is_installed = self.emu_manager.esta_instalado(self.emu["github"])
        repo = self.emu["github"]
        
        self.action_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        if not is_installed:
            # Install
            self.action_btn.setText(self.translator.t("dl_installing"))
            error_occurred = False
            async for output_line in self.emu_manager.instalar_emulador(repo):
                if output_line.startswith("PROGRESS:"):
                    try:
                        parts = output_line.replace("PROGRESS:", "").split("|")
                        val = float(parts[0]) * 100
                        msg = parts[1] if len(parts) > 1 else self.translator.t("lib_status_processing")
                        self.progress_bar.setValue(int(val))
                        self.status_lbl.setText(msg)
                    except:
                        self.status_lbl.setText(output_line)
                elif output_line.startswith("ERROR:") or "Error" in output_line:
                    error_occurred = True
                    clean_msg = output_line.replace("ERROR:", "").strip()
                    self.status_lbl.setText(clean_msg)
                    self.status_lbl.setProperty("class", "emulatorCardStatusErrorStoreSmall")
                    self.status_lbl.style().unpolish(self.status_lbl)
                    self.status_lbl.style().polish(self.status_lbl)
                else:
                    self.status_lbl.setText(output_line[-60:])
                    
            if not error_occurred:
                self.status_lbl.setText(self.translator.t("dl_installed_ok"))
                self.status_lbl.setProperty("class", "emulatorCardStatusSuccessStoreSmall")
                self.status_lbl.style().unpolish(self.status_lbl)
                self.status_lbl.style().polish(self.status_lbl)
        else:
            # Uninstall
            self.action_btn.setText(self.translator.t("dl_uninstalling"))
            async for output_line in self.emu_manager.desinstalar_emulador(repo):
                self.status_lbl.setText(output_line[-50:])
            
            self.status_lbl.setText(self.translator.t("dl_uninstalled_ok"))
            self.status_lbl.setProperty("class", "emulatorCardStatusStoreSmall")
            self.status_lbl.style().unpolish(self.status_lbl)
            self.status_lbl.style().polish(self.status_lbl)
            
        self.update_ui_state(keep_status=True)
        self.action_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Ocultar el estado temporal (sea de éxito, desinstalación o error) después de 3 segundos
        QTimer.singleShot(3000, lambda: self.status_lbl.setText(""))
            
        if self.on_update_library_bg:
            self.on_update_library_bg()

class DownloadsView(QWidget):
    def __init__(self, emu_manager, translator, on_update_library_bg):
        super().__init__()
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_library_bg = on_update_library_bg
        
        self.init_ui()
        self.load_emulators()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel(self.translator.t("dl_title"))
        title.setProperty("class", "pageTitle")
        layout.addWidget(title)
        
        subtitle = QLabel(self.translator.t("dl_list_sub"))
        subtitle.setProperty("class", "sectionSubtitle")
        layout.addWidget(subtitle)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setProperty("class", "transparentScrollArea")
        
        self.grid_container = QWidget()
        self.grid_container.setProperty("class", "transparentBg")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll_area.setWidget(self.grid_container)
        layout.addWidget(self.scroll_area)
        
    def load_emulators(self):
        path_emus = self.emu_manager.install_path
        path_roms = self.emu_manager.roms_path
        
        emus_ok = bool(path_emus and os.path.exists(path_emus))
        roms_ok = bool(path_roms and os.path.exists(path_roms))
        paths_configured = emus_ok and roms_ok
        
        if not paths_configured:
            warning = QLabel(self.translator.t("dl_warn_paths"))
            warning.setProperty("class", "warningBox")
            self.grid_layout.addWidget(warning, 0, 0, 1, 3)
            return
            
        # Draw cards
        for emu in AVAILABLE_EMULATORS:
            card = EmulatorCard(emu, self.emu_manager, self.translator, self.on_update_library_bg)
            self.grid_layout.addWidget(card)
            
        # Force reflow calculation once UI is ready
        QTimer.singleShot(50, lambda: self.resizeEvent(None))
 
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, lambda: self.resizeEvent(None))
 
    def resizeEvent(self, event):
        if event:
            super().resizeEvent(event)
        if not hasattr(self, 'grid_layout') or self.grid_layout.count() == 0:
            return
            
        width = self.scroll_area.viewport().width()
        card_width = 260 # Tamaño alineado a la nueva tarjeta vertical
        spacing = self.grid_layout.spacing()
        cols = max(1, width // (card_width + spacing))
        
        # Center the grid by applying left margin
        used_width = cols * card_width + (cols - 1) * spacing
        margin = max(0, (width - used_width) // 2)
        self.grid_layout.setContentsMargins(margin, 20, margin, 20)
        
        if getattr(self, '_current_cols', 0) != cols:
            self._current_cols = cols
            self._rearrange_grid(cols)
            
    def _rearrange_grid(self, cols):
        widgets = []
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                widgets.append(item.widget())
                
        for w in widgets:
            self.grid_layout.removeWidget(w)
            
        row = 0
        col = 0
        for w in widgets:
            if isinstance(w, QLabel): # Warning label
                self.grid_layout.addWidget(w, row, 0, 1, cols)
                row += 1
                col = 0
            else:
                self.grid_layout.addWidget(w, row, col)
                col += 1
                if col >= cols:
                    col = 0
                    row += 1
