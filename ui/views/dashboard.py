from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

class DashboardView(QWidget):
    def __init__(self, emu_manager, translator):
        super().__init__()
        self.emu_manager = emu_manager
        self.translator = translator
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome Title
        title = QLabel(self.translator.t("dash_welcome_title"))
        title.setStyleSheet("font-size: 42px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel(self.translator.t("dash_welcome_subtitle"))
        subtitle.setStyleSheet("font-size: 18px; color: #a0c0ff;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Status Section
        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        
        route_status = QLabel(self.translator.t("dash_route_status"))
        route_status.setStyleSheet("font-size: 12px; color: #888888;")
        route_status.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_layout.addWidget(route_status)
        
        self.status_emus_lbl = QLabel()
        self.status_roms_lbl = QLabel()
        
        status_icons_layout = QHBoxLayout()
        status_icons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_icons_layout.addWidget(self.status_emus_lbl)
        status_icons_layout.addWidget(self.status_roms_lbl)
        
        status_layout.addLayout(status_icons_layout)
        layout.addLayout(status_layout)
        
        self.update_dashboard_status()
        
    def update_dashboard_status(self):
        import os
        def get_status_text(path, label):
            if not path:
                return f"❌ {label}: {self.translator.t('dash_missing')}"
            if not os.path.exists(path):
                return f"⚠️ {label}: {self.translator.t('dash_path_missing')}"
            return f"✅ {label}: {self.translator.t('dash_configured')}"
            
        self.status_emus_lbl.setText(get_status_text(self.emu_manager.install_path, self.translator.t("dash_status_emus")))
        self.status_roms_lbl.setText(get_status_text(self.emu_manager.roms_path, self.translator.t("dash_status_roms")))
