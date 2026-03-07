import asyncio
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QProgressBar, QMessageBox, QGridLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon
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
        self.setObjectName("emulatorCard")
        self.setStyleSheet(f"""
            QFrame#emulatorCard {{
                background-color: #1a1c24;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #2a2d3a;
            }}
            QFrame#emulatorCard:hover {{
                background-color: #242835;
                border: 1px solid {brand_color};
            }}
        """)
        self.setMinimumWidth(320)
        self.setMaximumWidth(450)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Logo
        logo_path = os.path.join(artwork.CONSOLES_DIR, f"{self.emu['id']}.png")
        if not os.path.exists(logo_path):
            logo_path = artwork.obtener_ruta_logo_emulador(self.emu["id"])
        
        icon_lbl = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_lbl.setPixmap(pixmap)
        else:
            icon_lbl.setText("🎮")
            icon_lbl.setStyleSheet("font-size: 50px; color: #444;")
            
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedWidth(80)
        
        # Titles + Descripton + Progress
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        content_layout.setSpacing(4)
        
        emu_lbl = QLabel(self.emu["name"])
        emu_lbl.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        
        content_layout.addWidget(emu_lbl)
        
        # Progress and status
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #888888; font-size: 11px;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        
        content_layout.addWidget(self.status_lbl)
        content_layout.addWidget(self.progress_bar)
        
        # Action button
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.action_btn = QPushButton()
        self.action_btn.setMinimumWidth(120)
        self.action_btn.setMinimumHeight(40)
        self.action_btn.clicked.connect(self.on_action_clicked)
        btn_layout.addWidget(self.action_btn)
        
        main_layout.addWidget(icon_lbl)
        main_layout.addLayout(content_layout)
        main_layout.addLayout(btn_layout)
        
    def update_ui_state(self):
        is_installed = self.emu_manager.esta_instalado(self.emu["github"])
        brand_color = self.emu.get("color", "#1976d2")
        if is_installed:
            self.action_btn.setText(self.translator.t("dl_btn_uninstall"))
            self.action_btn.setStyleSheet("""
                background-color: #d32f2f; color: white; border-radius: 6px; 
                font-weight: bold; border: none; padding: 10px;
            """)
        else:
            self.action_btn.setText(self.translator.t("dl_btn_install"))
            self.action_btn.setStyleSheet(f"""
                background-color: {brand_color}; color: white; border-radius: 6px; 
                font-weight: bold; border: none; padding: 10px;
            """)
            
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
                    self.status_lbl.setStyleSheet("color: red; font-size: 11px;")
                else:
                    self.status_lbl.setText(output_line)
                    
            if not error_occurred:
                self.status_lbl.setText(self.translator.t("dl_installed_ok"))
                self.status_lbl.setStyleSheet("color: #4CAF50; font-size: 11px;")
        else:
            # Uninstall
            self.action_btn.setText(self.translator.t("dl_uninstalling"))
            async for output_line in self.emu_manager.desinstalar_emulador(repo):
                self.status_lbl.setText(output_line[-50:])
            
            self.status_lbl.setText(self.translator.t("dl_uninstalled_ok"))
            self.status_lbl.setStyleSheet("color: #4CAF50; font-size: 11px;")
            
        self.update_ui_state()
        self.action_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Clear status message after 3 seconds
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
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        subtitle = QLabel(self.translator.t("dl_list_sub"))
        subtitle.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        layout.addWidget(subtitle)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background-color: transparent;")
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
            warning.setStyleSheet("background-color: #ffb300; color: black; padding: 10px; border-radius: 5px; font-weight: bold;")
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
        card_width = 450
        spacing = self.grid_layout.spacing()
        cols = max(1, width // (card_width + spacing))
        
        # Center the grid by applying left margin
        used_width = cols * card_width + (cols - 1) * spacing
        margin = max(0, (width - used_width) // 2)
        self.grid_layout.setContentsMargins(margin, 0, 0, 0)
        
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
