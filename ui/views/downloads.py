"""
downloads.py — Vista de Descarga e Instalación de Emuladores
Diseño premium: nombre de consola como elemento principal, color único, filtros.
"""

import asyncio
import os
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QProgressBar, QGridLayout, QSizePolicy, QGraphicsDropShadowEffect, QCheckBox, QDialog, QDialogButtonBox, QApplication, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt, QTimer, QSize, QUrl
from PyQt6.QtGui import QPixmap, QIcon, QColor, QDesktopServices
from qasync import asyncSlot
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork
import core.scanner as scanner
import core.metadata as metadata

ACCENT = "#4da6ff"
ACCENT_HOVER = "#7abfff"
CARD_DARK = "#13151c"
CARD_BG = "#16181f"
CARD_BG_HOVER = "#1b1e2a"


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL INSTALL DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class ManualInstallDialog(QDialog):
    def __init__(self, emu, translator, parent=None):
        super().__init__(parent)
        self.emu = emu
        self.translator = translator
        self.selected_file = None
        self.setWindowTitle(f"Asistente: {emu['name']}")
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Title
        title = QLabel("Instalación Manual")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f8f8ff;")
        layout.addWidget(title)

        # Step 1: Link
        step1_box = QFrame()
        step1_box.setStyleSheet("background: rgba(255,255,255,0.03); border: 1px solid #252830; border-radius: 8px;")
        s1_layout = QVBoxLayout(step1_box)
        
        s1_title = QLabel("1. Descarga el paquete")
        s1_title.setStyleSheet("font-weight: bold; color: #4da6ff; border: none;")
        
        info = QLabel("Descarga la versión portable (.zip, .7z) de la web oficial:")
        info.setStyleSheet("font-size: 11px; color: #aaaaaa; border: none;")
        info.setWordWrap(True)

        url_btn = QPushButton("Abrir Página de Descarga")
        url_btn.setFixedHeight(34)
        url_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        url_btn.setStyleSheet("""
            QPushButton { 
                background: #1e293b; color: #ffffff; border: 1px solid #334155; border-radius: 6px; font-weight: bold; 
            }
            QPushButton:hover { background: #334155; }
        """)
        url_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.emu.get("manual_url", self.emu.get("github")))))

        s1_layout.addWidget(s1_title)
        s1_layout.addWidget(info)
        s1_layout.addWidget(url_btn)
        layout.addWidget(step1_box)

        # Step 2: File Pick
        step2_box = QFrame()
        step2_box.setStyleSheet("background: rgba(255,255,255,0.03); border: 1px solid #252830; border-radius: 8px;")
        s2_layout = QVBoxLayout(step2_box)

        s2_title = QLabel("2. Selecciona el archivo")
        s2_title.setStyleSheet("font-weight: bold; color: #4da6ff; border: none;")

        self.file_lbl = QLabel("No se ha seleccionado archivo")
        self.file_lbl.setStyleSheet("font-size: 10px; color: #888888; border: none;")
        self.file_lbl.setWordWrap(True)

        pick_btn = QPushButton("Seleccionar ZIP / 7Z / EXE")
        pick_btn.setFixedHeight(34)
        pick_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pick_btn.setStyleSheet("""
            QPushButton { 
                background: #064e3b; color: #34d399; border: 1px solid #065f46; border-radius: 6px; font-weight: bold; 
            }
            QPushButton:hover { background: #065f46; }
        """)
        pick_btn.clicked.connect(self.on_pick_file)

        s2_layout.addWidget(s2_title)
        s2_layout.addWidget(self.file_lbl)
        s2_layout.addWidget(pick_btn)
        layout.addWidget(step2_box)

        # Footer
        btns = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        self.install_btn = QPushButton("Finalizar Instalación")
        self.install_btn.setEnabled(False)
        self.install_btn.setFixedHeight(40)
        self.install_btn.setStyleSheet("""
            QPushButton:disabled { background: #1a1c24; color: #444455; }
            QPushButton:enabled { background: #4da6ff; color: #000000; font-weight: bold; }
        """)
        self.install_btn.clicked.connect(self.accept)

        btns.addWidget(cancel_btn)
        btns.addWidget(self.install_btn, 1)
        layout.addLayout(btns)

    def on_pick_file(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar emulador", "",
            "Archivos de emulador (*.zip *.7z *.tar.gz *.tar.xz *.exe *.AppImage)"
        )
        if f:
            self.selected_file = f
            self.file_lbl.setText(os.path.basename(f))
            self.file_lbl.setStyleSheet("font-size: 10px; color: #4ade80; border: none; font-weight: bold;")
            self.install_btn.setEnabled(True)

# ─────────────────────────────────────────────────────────────────────────────
# EMULATOR CARD
# ─────────────────────────────────────────────────────────────────────────────

class EmulatorCard(QFrame):
    """Tarjeta de consola unificada. Permite elegir entre varios emuladores si están disponibles."""

    def __init__(self, emus, emu_manager, translator, on_update_library_bg, parent=None):
        super().__init__(parent)
        self.emus = emus
        # El emu actual es el primero de la lista por defecto, o el primero instalado
        self.emu = next((e for e in emus if emu_manager.esta_instalado(e["github"])), emus[0])
        
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_library_bg = on_update_library_bg

        self.init_ui()
        self.update_ui_state()

    # ── Layout ────────────────────────────────────────────────────────────────

    def init_ui(self):
        self.setFixedSize(240, 320)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self._base_style = """
            QFrame {
                background-color: #16181f;
                border-radius: 16px;
                border: 1px solid #252830;
            }
        """
        self._hover_style = f"""
            QFrame {{
                background-color: {CARD_BG_HOVER};
                border-radius: 16px;
                border: 1px solid {ACCENT};
            }}
        """
        self.setStyleSheet(self._base_style)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 110))
        self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── BANNER ────────────────────────────────────────────────────────
        banner = QFrame(self)
        banner.setFixedHeight(100)
        banner.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a2035, stop:1 {CARD_DARK}
                );
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }}
        """)

        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(0, 14, 0, 10)
        banner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Installed badge
        self.installed_badge = QLabel("✓ INSTALADO", banner)
        self.installed_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.installed_badge.setStyleSheet(f"""
            background: rgba(34, 197, 94, 0.18);
            color: #4ade80;
            font-size: 9px; font-weight: bold; letter-spacing: 1px;
            border-radius: 8px; padding: 2px 8px;
            border: 1px solid rgba(74, 222, 128, 0.3);
        """)
        self.installed_badge.setFixedHeight(18)
        self.installed_badge.setVisible(False)

        # Logo small
        self.logo_lbl = QLabel(banner)
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_lbl.setStyleSheet("background: transparent; border: none;")
        self._update_logo()

        banner_layout.addWidget(self.installed_badge, 0, Qt.AlignmentFlag.AlignCenter)
        banner_layout.addWidget(self.logo_lbl)

        # ── CONTENT ───────────────────────────────────────────────────────
        content = QFrame(self)
        content.setStyleSheet("background: transparent; border: none;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(16, 14, 16, 8)
        c_layout.setSpacing(6)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Console Title
        self.console_lbl = QLabel(self.emu.get("console", "EL SISTEMA").upper(), content)
        self.console_lbl.setStyleSheet("""
            font-size: 15px; font-weight: 900; color: #f8f8ff;
            background: transparent; border: none; letter-spacing: 0.5px;
        """)
        self.console_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Emulator Selector (Visible if more than 1)
        self.selector_box = QtWidgets.QComboBox(content)
        self.selector_box.setFixedHeight(28)
        self.selector_box.setStyleSheet(f"""
            QComboBox {{
                background: #1a1c24; color: #aaaabb;
                border: 1px solid #252830; border-radius: 6px;
                padding-left: 8px; font-size: 11px; font-weight: bold;
            }}
            QComboBox:hover {{ border-color: {ACCENT}; color: #ffffff; }}
        """)
        for e in self.emus:
            self.selector_box.addItem(e["name"], e["id"])
        
        # Set selection
        idx = self.selector_box.findData(self.emu["id"])
        if idx >= 0: self.selector_box.setCurrentIndex(idx)
        self.selector_box.currentIndexChanged.connect(self._on_emu_changed)
        self.selector_box.setVisible(len(self.emus) > 1)

        # If only one emu, show its name in a simple label
        self.single_emu_name = QLabel(self.emu["name"], content)
        self.single_emu_name.setStyleSheet("font-size: 11px; color: #666688; font-weight: bold;")
        self.single_emu_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.single_emu_name.setVisible(len(self.emus) == 1)

        # Status text
        self.status_lbl = QLabel("", content)
        self.status_lbl.setStyleSheet("font-size: 10px; color: #555566; background: transparent;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setMinimumHeight(24)

        c_layout.addWidget(self.console_lbl)
        c_layout.addWidget(self.selector_box)
        c_layout.addWidget(self.single_emu_name)
        
        # Extra spacing for cleaner look
        c_layout.addSpacing(4)
        
        # Buttons Row (Manual / Folder)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_manual = QPushButton("Manual", content)
        self.btn_manual.setFixedHeight(26)
        self.btn_manual.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_manual.setStyleSheet("""
            QPushButton {
                background: #1a1c24; color: #888899;
                font-size: 9px; font-weight: bold;
                border: 1px solid #252830; border-radius: 6px;
            }
            QPushButton:hover { background: #1f2230; color: #ffffff; border-color: #444455; }
        """)
        self.btn_manual.clicked.connect(self.on_manual_clicked)

        self.btn_resource = QPushButton("Carpeta", content)
        self.btn_resource.setFixedHeight(26)
        self.btn_resource.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_resource.setStyleSheet("""
            QPushButton {
                background: #1a1c24; color: #888899;
                font-size: 9px; font-weight: bold;
                border: 1px solid #252830; border-radius: 6px;
            }
            QPushButton:hover { background: #1f2230; color: #ffffff; border-color: #444455; }
        """)
        self.btn_resource.clicked.connect(self.on_open_folder_clicked)

        btn_row.addWidget(self.btn_manual)
        btn_row.addWidget(self.btn_resource)
        c_layout.addLayout(btn_row)

        c_layout.addStretch()
        c_layout.addWidget(self.status_lbl)

        # ── BOTTOM ────────────────────────────────────────────────────────
        bottom = QFrame(self)
        bottom.setStyleSheet("background: transparent; border: none;")
        b_layout = QVBoxLayout(bottom)
        b_layout.setContentsMargins(14, 0, 14, 14)
        b_layout.setSpacing(8)

        self.progress_bar = QProgressBar(bottom)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{ background: #252830; border-radius: 2px; border: none; }}
            QProgressBar::chunk {{ background: {ACCENT}; border-radius: 2px; }}
        """)

        self.action_btn = QPushButton(bottom)
        self.action_btn.setFixedHeight(38)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_btn.clicked.connect(self.on_action_clicked)

        b_layout.addWidget(self.progress_bar)
        b_layout.addWidget(self.action_btn)

        main_layout.addWidget(banner)
        main_layout.addWidget(content)
        main_layout.addWidget(bottom)

    def _update_logo(self):
        """Actualiza el logo del banner según el emulador actual."""
        logo_path = artwork.obtener_ruta_logo_consola(self.emu["id"]).replace(".png", ".svg")
        if not os.path.exists(logo_path):
            logo_path = artwork.obtener_ruta_logo_consola(self.emu["id"])
        if not os.path.exists(logo_path):
            # Probar con ID de consola si existe un mapeo o id específico
            cid = self.emu.get("console_id", self.emu["id"])
            logo_path = artwork.obtener_ruta_logo_consola(cid).replace(".png", ".svg")
            if not os.path.exists(logo_path):
                logo_path = artwork.obtener_ruta_logo_consola(cid)

        if os.path.exists(logo_path):
            if logo_path.endswith(".svg"):
                pixmap = QIcon(logo_path).pixmap(QSize(54, 54))
            else:
                pixmap = QPixmap(logo_path).scaled(54, 54, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_lbl.setPixmap(pixmap)
        else:
            self.logo_lbl.setText("🎮")
            self.logo_lbl.setStyleSheet("font-size: 30px; background: transparent;")

    def _on_emu_changed(self, index):
        """Cambia el emulador seleccionado para esta tarjeta."""
        emu_id = self.selector_box.itemData(index)
        self.emu = next((e for e in self.emus if e["id"] == emu_id), self.emus[0])
        self._update_logo()
        self.update_ui_state()

    # ── Hover ────────────────────────────────────────────────────────────────

    def enterEvent(self, event):
        self.setStyleSheet(self._hover_style)
        eff = self.graphicsEffect()
        if isinstance(eff, QGraphicsDropShadowEffect):
            eff.setColor(QColor(ACCENT + "60"))
            eff.setBlurRadius(28)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._base_style)
        eff = self.graphicsEffect()
        if isinstance(eff, QGraphicsDropShadowEffect):
            eff.setColor(QColor(0, 0, 0, 110))
            eff.setBlurRadius(18)
        super().leaveEvent(event)

    def on_manual_clicked(self):
        """Muestra el asistente de instalación manual sin bloquear el loop de qasync de forma insegura."""
        dialog = ManualInstallDialog(self.emu, self.translator, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            zip_path = dialog.selected_file
            if zip_path and os.path.exists(zip_path):
                # Lanzamos la tarea asíncrona de instalación fuera del flujo del diálogo
                asyncio.create_task(self._do_manual_install(zip_path))

    async def _do_manual_install(self, zip_path):
        """Ejecuta la instalación manual de forma asíncrona."""
        self.action_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.action_btn.setText("INSTALANDO...")

        error_occurred = False
        async for output in self.emu_manager.installer.instalar_emulador_local(self.emu["github"], zip_path):
            if output.startswith("PROGRESS:"):
                try:
                    parts = output.replace("PROGRESS:", "").split("|")
                    val = float(parts[0]) * 100
                    msg = parts[1] if len(parts) > 1 else ""
                    self.progress_bar.setValue(int(val))
                    self.status_lbl.setText(msg)
                except:
                    pass
            elif output.startswith("ERROR:"):
                error_occurred = True
                # Mensajes amigables y cortos
                raw_err = output.replace("ERROR:", "").lower()
                if "404" in raw_err or "not found" in raw_err:
                    err_msg = "No disponible v铆a auto"
                elif "timeout" in raw_err or "connection" in raw_err:
                    err_msg = "Error de red"
                elif "manual" in raw_err:
                    err_msg = "Usa instalaci贸n Manual"
                else:
                    err_msg = "Error al instalar"
                
                self.status_lbl.setText(err_msg)
                self.status_lbl.setStyleSheet("font-size: 10px; color: #f87171; background: transparent;")
        
        if not error_occurred:
            self.status_lbl.setText("¡Instalación manual exitosa!")
            self.status_lbl.setStyleSheet("font-size: 10px; color: #4ade80; background: transparent;")
        
        self.update_ui_state(keep_status=True)
        self.action_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Ocultar mensaje después de 3 segundos
        QTimer.singleShot(3000, lambda: self.status_lbl.setText(""))
        
        # Actualizar biblioteca si es necesario
        if self.on_update_library_bg:
            self.on_update_library_bg()

    def on_open_folder_clicked(self):
        """Abre la carpeta de instalación del emulador."""
        info = self.emu_manager.installed_emus.get(self.emu["github"])
        if info:
            # Intentar obtener 'path' o deducir del primer archivo
            path = info.get("path")
            if not path and info.get("files"):
                path = os.path.dirname(info["files"][0])
            
            if path and os.path.exists(path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(path)))

    # ── State ─────────────────────────────────────────────────────────────────

    def update_ui_state(self, keep_status=False):
        is_installed = self.emu_manager.esta_instalado(self.emu["github"])
        
        path_emus = self.emu_manager.install_path
        path_roms = self.emu_manager.roms_path
        valid_paths = (bool(path_emus and os.path.exists(path_emus)) and
                      bool(path_roms and os.path.exists(path_roms)))

        if is_installed:
            self.action_btn.setText(self.translator.t("dl_btn_uninstall").upper())
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background: #2d1515; color: #f87171;
                    font-size: 11px; font-weight: bold; letter-spacing: 1px;
                    border: 1px solid #7f1d1d; border-radius: 19px;
                }
                QPushButton:hover { background: #3d1a1a; color: #fca5a5; }
                QPushButton:disabled { background: #1a1c24; color: #444455; border: 1px solid #252830; }
            """)
            self.installed_badge.setVisible(True)
            self.btn_resource.setVisible(True)
        else:
            self.action_btn.setText(self.translator.t("dl_btn_install").upper())
            self.action_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {ACCENT};
                    color: #ffffff;
                    font-size: 11px; font-weight: bold; letter-spacing: 1px;
                    border: none; border-radius: 19px;
                }}
                QPushButton:hover {{ background: {ACCENT_HOVER}; color: #ffffff; }}
                QPushButton:disabled {{ background: #1a1c24; color: #444455; border: none; }}
            """)
            self.installed_badge.hide()
            self.btn_resource.hide()

        if not valid_paths:
            self.action_btn.setEnabled(False)
            if not keep_status:
                self.status_lbl.setText(self.translator.t("dl_warn_paths_short") or "Configurar rutas")
                self.status_lbl.setStyleSheet("font-size: 10px; color: #f87171; background: transparent; border: none;")
        else:
            self.action_btn.setEnabled(True)
            if not keep_status:
                self.status_lbl.setText("")
                self.status_lbl.setStyleSheet("font-size: 10px; color: #555566; background: transparent; border: none;")

    # ── Async logic (INTACTA) ────────────────────────────────────────────────

    @asyncSlot()
    async def on_action_clicked(self):
        is_installed = self.emu_manager.esta_instalado(self.emu["github"])
        repo = self.emu["github"]

        self.action_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        if not is_installed:
            self.action_btn.setText(self.translator.t("dl_installing"))
            error_occurred = False
            async for output_line in self.emu_manager.instalar_emulador(repo):
                if output_line.startswith("PROGRESS:"):
                    try:
                        parts = output_line.replace("PROGRESS:", "").split("|")
                        val = float(parts[0]) * 100
                        msg = parts[1] if len(parts) > 1 else ""
                        self.progress_bar.setValue(int(val))
                        self.status_lbl.setText(msg)
                    except:
                        pass
                elif output_line.startswith("ERROR:") or "Error" in output_line:
                    error_occurred = True
                    raw_err = output_line.lower()
                    if "404" in raw_err or "not found" in raw_err:
                        friendly = "No disponible v铆a auto"
                    elif "timeout" in raw_err or "connection" in raw_err:
                        friendly = "Error de red"
                    else:
                        friendly = "Error en descarga"
                    self.status_lbl.setText(friendly)
                    self.status_lbl.setStyleSheet("font-size: 10px; color: #f87171; background: transparent; border: none;")
                else:
                    self.status_lbl.setText(output_line[-40:])

            if not error_occurred:
                self.status_lbl.setText(self.translator.t("dl_installed_ok"))
                self.status_lbl.setStyleSheet("font-size: 10px; color: #4ade80; background: transparent; border: none;")
        else:
            self.action_btn.setText(self.translator.t("dl_uninstalling"))
            async for output_line in self.emu_manager.desinstalar_emulador(repo):
                self.status_lbl.setText(output_line[-50:])
            self.status_lbl.setText(self.translator.t("dl_uninstalled_ok"))
            self.status_lbl.setStyleSheet("font-size: 10px; color: #a78bfa; background: transparent; border: none;")

        self.update_ui_state(keep_status=True)
        self.action_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QTimer.singleShot(3000, lambda: self.status_lbl.setText(""))

        if self.on_update_library_bg:
            self.on_update_library_bg()

        # Notificar a DownloadsView para actualizar badge
        p = self.parent()
        while p:
            if isinstance(p, DownloadsView):
                p._update_stats_badge()
                break
            p = p.parent()


# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOADS VIEW
# ─────────────────────────────────────────────────────────────────────────────

class DownloadsView(QWidget):
    FILTER_ALL = "all"
    FILTER_INSTALLED = "installed"
    FILTER_NOT_INSTALLED = "not_installed"

    def __init__(self, emu_manager, translator, on_update_library_bg, parent=None):
        super().__init__(parent)
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_library_bg = on_update_library_bg
        self._active_filter = self.FILTER_ALL
        self._all_cards = []

        self.init_ui()
        self.load_emulators()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 30, 36, 20)
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        title_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.title_lbl = QLabel("EMULADORES")
        self.title_lbl.setStyleSheet("""
            font-size: 26px; font-weight: 900; color: #ffffff;
            letter-spacing: 2px; background: transparent; border: none;
        """)
        title_row.addWidget(self.title_lbl)

        self.subtitle_lbl = QLabel("GESTIÓN Y DESCARGA AUTOMÁTICA")
        self.subtitle_lbl.setStyleSheet("""
            font-size: 11px; color: #666688; font-weight: bold;
            letter-spacing: 1px; background: transparent; border: none;
        """)
        left.addWidget(self.subtitle_lbl)

        self.stats_badge = QLabel()
        self.stats_badge.setStyleSheet(f"""
            background: rgba(77, 166, 255, 0.1);
            color: {ACCENT};
            font-size: 11px; font-weight: bold;
            border-radius: 10px; padding: 3px 12px;
            border: 1px solid rgba(77, 166, 255, 0.25);
        """)
        self.stats_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_row.addWidget(self.stats_badge)
        title_row.addStretch()

        left.addLayout(title_row)

        subtitle = QLabel(self.translator.t("dl_list_sub"))
        subtitle.setStyleSheet("font-size: 13px; color: #555566; background: transparent; border: none;")
        left.addWidget(subtitle)

        header.addLayout(left, 1)

        # ── Filter tabs ───────────────────────────────────────────────────
        self.filter_btns = {}
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(6)
        filter_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        for key, label in [
            (self.FILTER_ALL, "Todos"),
            (self.FILTER_INSTALLED, "Instalados"),
            (self.FILTER_NOT_INSTALLED, "No instalados"),
        ]:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda _, k=key: self._set_filter(k))
            self.filter_btns[key] = btn
            filter_layout.addWidget(btn)

        header.addLayout(filter_layout)
        layout.addLayout(header)
        layout.addSpacing(22)

        # ── Warning Area (Fuera del scroll para que sea fijo arriba) ──────
        self.warn_area = QWidget()
        self.warn_area.setVisible(False)
        self.warn_layout = QVBoxLayout(self.warn_area)
        self.warn_layout.setContentsMargins(0, 0, 0, 20)
        layout.addWidget(self.warn_area)

        # ── Scraping Section ─────────────────────────────────────────────
        scrap_frame = QFrame()
        scrap_frame.setStyleSheet("""
            QFrame {
                background: rgba(77,166,255,0.05);
                border: 1px solid rgba(77,166,255,0.15);
                border-radius: 12px;
            }
        """)
        scrap_layout = QHBoxLayout(scrap_frame)
        scrap_layout.setContentsMargins(20, 14, 20, 14)
        scrap_layout.setSpacing(16)

        scrap_icon = QLabel("🖼")
        scrap_icon.setStyleSheet("font-size: 22px; background: transparent; border: none;")
        scrap_layout.addWidget(scrap_icon)

        scrap_text = QVBoxLayout()
        scrap_text.setSpacing(2)
        scrap_title = QLabel("Descargar recursos de juegos")
        scrap_title.setStyleSheet("font-size: 14px; font-weight: 900; color: #ffffff; background: transparent; border: none;")
        
        scrap_sub = QLabel("Obtén carátulas, fondos e información detallada de tus juegos.")
        scrap_sub.setStyleSheet("font-size: 11px; color: #666688; background: transparent; border: none;")
        
        scrap_text.addWidget(scrap_title)
        scrap_text.addWidget(scrap_sub)
        scrap_layout.addLayout(scrap_text)

        # ── Spacer ──────────────────────────────────────────────────
        self.scrap_spacer = QWidget()
        self.scrap_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        scrap_layout.addWidget(self.scrap_spacer)

        # ── Middle: Progress Area (Label + Bar) ─────────────────────
        self.progress_container = QWidget()
        self.progress_container.setStyleSheet("background: transparent; border: none;")
        self.progress_container.setVisible(False)
        p_layout = QVBoxLayout(self.progress_container)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.setSpacing(4)

        self.scrap_status_lbl = QLabel("")
        self.scrap_status_lbl.setStyleSheet("font-size: 11px; color: #4da6ff; font-weight: bold; background: transparent; border: none;")
        
        self.scrap_bar = QProgressBar()
        self.scrap_bar.setFixedHeight(6)
        self.scrap_bar.setRange(0, 100)
        self.scrap_bar.setTextVisible(False)
        self.scrap_bar.setStyleSheet("""
            QProgressBar { background: #1a1c24; border-radius: 3px; border: none; }
            QProgressBar::chunk { background: #4da6ff; border-radius: 3px; }
        """)
        
        p_layout.addWidget(self.scrap_status_lbl)
        p_layout.addWidget(self.scrap_bar)
        scrap_layout.addWidget(self.progress_container, 1)

        self.btn_scrap = QPushButton("Descarga")
        self.btn_scrap.setToolTip("Escanea los juegos disponibles en la carpeta de roms de la consola")
        self.btn_scrap.setFixedSize(120, 40)
        self.btn_scrap.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scrap.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: #ffffff;
                font-size: 12px; font-weight: bold; letter-spacing: 0.5px;
                border: none; border-radius: 20px;
            }}
            QPushButton:hover {{ background: {ACCENT_HOVER}; }}
            QPushButton:disabled {{ background: #1a1c24; color: #444455; }}
        """)
        self.btn_scrap.clicked.connect(self._on_scrap_clicked)
        scrap_layout.addWidget(self.btn_scrap)

        layout.addWidget(scrap_frame)
        layout.addSpacing(16)

        # ── Grid ──────────────────────────────────────────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.grid_container)
        layout.addWidget(self.scroll_area)

        self._apply_filter_styles()

    def retranslate_ui(self):
        """Actualiza todos los textos de la vista al cambiar el idioma."""
        self.title_lbl.setText(self.translator.t("nav_downloads").upper())
        self.subtitle_lbl.setText(self.translator.t("dl_subtitle").upper())
        
        # Filtros
        if self.FILTER_ALL in self.filter_btns:
            self.filter_btns[self.FILTER_ALL].setText(self.translator.t("dl_filter_all") or "Todos")
        if self.FILTER_INSTALLED in self.filter_btns:
            self.filter_btns[self.FILTER_INSTALLED].setText(self.translator.t("dl_filter_installed") or "Instalados")
        if self.FILTER_NOT_INSTALLED in self.filter_btns:
            self.filter_btns[self.FILTER_NOT_INSTALLED].setText(self.translator.t("dl_filter_not_installed") or "No instalados")
        
        self.refresh_emulators() # Traduce las tarjetas
        self._update_stats_badge()

    # ── Filter ────────────────────────────────────────────────────────────────

    def _set_filter(self, key):
        self._active_filter = key
        self._apply_filter_styles()
        self._apply_filter_visibility()
        # Forzar un recalculado del layout completo
        self._current_cols = -1 
        QTimer.singleShot(10, lambda: self.resizeEvent(None))

    def _apply_filter_styles(self):
        active = f"""
            QPushButton {{
                background: {ACCENT}; color: #ffffff;
                font-size: 11px; font-weight: bold;
                border: none; border-radius: 16px; padding: 0 16px;
            }}
        """
        inactive = """
            QPushButton {
                background: #1a1c24; color: #888899;
                font-size: 11px; border: 1px solid #252830;
                border-radius: 16px; padding: 0 16px;
            }
            QPushButton:hover {
                background: #1f2230; color: #bbbbcc; border-color: #3a3d4a;
            }
        """
        for key, btn in self.filter_btns.items():
            btn.setStyleSheet(active if key == self._active_filter else inactive)

    def _apply_filter_visibility(self):
        for card in self._all_cards:
            if not isinstance(card, EmulatorCard):
                continue
            if self._active_filter == self.FILTER_ALL:
                card.setVisible(True)
            elif self._active_filter == self.FILTER_INSTALLED:
                card.setVisible(self.emu_manager.esta_instalado(card.emu["github"]))
            else:
                card.setVisible(not self.emu_manager.esta_instalado(card.emu["github"]))

    def _update_stats_badge(self):
        total = len(AVAILABLE_EMULATORS)
        installed = sum(
            1 for e in AVAILABLE_EMULATORS
            if self.emu_manager.esta_instalado(e["github"])
        )
        self.stats_badge.setText(f"  {installed} / {total} instalados  ")
        self._apply_filter_visibility()
        QTimer.singleShot(10, lambda: self.resizeEvent(None))

    # ── Load ──────────────────────────────────────────────────────────────────

    @asyncSlot()
    async def _on_scrap_clicked(self):
        """Muestra el diálogo de opciones y lanza el proceso de descarga."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Configurar Descarga")
        dlg.setMinimumWidth(380)
        dlg.setModal(True)
        dlg.setStyleSheet("""
            QDialog { background: #13151c; color: #ffffff; }
            QLabel { color: #ffffff; background: transparent; border: none; }
            QCheckBox { color: #ccccdd; font-size: 13px; background: transparent; }
            QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px;
                background: #1e2130; border: 1px solid #3a3d5a; }
            QCheckBox::indicator:checked { background: #4da6ff; border-color: #4da6ff; }
            QPushButton { border-radius: 8px; }
        """)
        dlg_layout = QVBoxLayout(dlg)
        dlg_layout.setContentsMargins(24, 20, 24, 20)
        dlg_layout.setSpacing(14)

        title_lbl = QLabel("¿Qué deseas descargar?")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 900; color: #ffffff; background:transparent;")
        dlg_layout.addWidget(title_lbl)

        cb_artwork = QCheckBox("🖼  Carátulas (cover art)")
        cb_artwork.setChecked(True)
        dlg_layout.addWidget(cb_artwork)

        cb_backgrounds = QCheckBox("🌄  Fondos de consola")
        cb_backgrounds.setChecked(True)
        dlg_layout.addWidget(cb_backgrounds)

        cb_metadata = QCheckBox("📋  Información del juego (descripción, año, desarrollador)")
        cb_metadata.setChecked(True)
        dlg_layout.addWidget(cb_metadata)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #1e2130; border: none; max-height: 1px;")
        dlg_layout.addWidget(sep)

        note = QLabel("⚠ La descarga de metadatos requiere conexión a internet. "
                       "Las carátulas se guardan junto a cada ROM.")

        note.setStyleSheet("font-size: 11px; color: #555577; background: transparent;")
        note.setWordWrap(True)
        dlg_layout.addWidget(note)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.setStyleSheet("""
            QPushButton {
                background: #4da6ff; color: #fff; font-weight: bold;
                border: none; padding: 6px 20px; border-radius: 8px; min-width: 80px;
            }
            QPushButton:hover { background: #7abfff; }
            QPushButton[text="Cancel"] { background: #1a1c24; color: #888; border: 1px solid #252830; }
        """)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        dlg_layout.addWidget(btn_box)

        # En lugar de exec() que bloquea el loop de asyncio/qasync, usamos open() o manejamos el loop
        # pero para mayor estabilidad con qasync, vamos a usar un truco: esperar a que termine el dialogo
        # de forma no bloqueante para el loop.
        
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        dlg.finished.connect(lambda r: future.set_result(r))
        dlg.show()
        
        result = await future

        if result != QDialog.DialogCode.Accepted:
            return

        # Capturar opciones
        options = {
            "artwork": cb_artwork.isChecked(),
            "backgrounds": cb_backgrounds.isChecked(),
            "metadata": cb_metadata.isChecked()
        }

        # Ejecutar la descarga real
        await self._ejecutar_descargas(options)

    async def _ejecutar_descargas(self, opts):
        """Lógica real de descarga asíncrona."""
        do_artwork = opts["artwork"]
        do_backgrounds = opts["backgrounds"]
        do_metadata = opts["metadata"]

        self.btn_scrap.setEnabled(False)
        self.scrap_spacer.setVisible(False)
        self.progress_container.setVisible(True)
        self.scrap_bar.setRange(0, 0) # Indeterminado al principio
        
        # Primero asegurar que tenemos la biblioteca escaneada
        roms_path = self.emu_manager.roms_path
        if not roms_path or not os.path.exists(roms_path):
             QMessageBox.warning(self, "Error", "Configura la ruta de ROMs en Ajustes antes de escanear.")
             self.btn_scrap.setEnabled(True)
             self.progress_container.setVisible(False)
             return

        self.scrap_status_lbl.setText("Buscando juegos...")
        juegos_lista = await scanner.escanear_roms(roms_path)
        
        if not juegos_lista:
            self.scrap_status_lbl.setText("No se encontraron juegos.")
            self.btn_scrap.setEnabled(True)
            QTimer.singleShot(3000, lambda: self.progress_container.setVisible(False))
            return
        
        # Convertir a dicts si es necesario
        juegos = [j if isinstance(j, dict) else scanner.asdict(j) for j in juegos_lista]

        from core.constants import AVAILABLE_EMULATORS
        emu_map = {e["id"]: e.get("libretro_platform") for e in AVAILABLE_EMULATORS}
        total = len(juegos)

        if do_metadata:
            self.scrap_status_lbl.setText("Obteniendo información (Metadata)...")
            self.scrap_bar.setRange(0, total)
            self.scrap_bar.setValue(0)
            
            def on_meta_progress(idx, tot, nombre):
                self.scrap_status_lbl.setText(f"Info: {nombre[:20]}...")
                self.scrap_bar.setValue(idx)

            meta_stats = await metadata.descargar_metadata_biblioteca(
                juegos, emu_map, on_progress=on_meta_progress
            )
            print(f"[DOWNLOADS] Metadatos: {meta_stats}")

        if do_artwork:
            self.scrap_status_lbl.setText("Descargando carátulas...")
            self.scrap_bar.setRange(0, total)
            self.scrap_bar.setValue(0)
            
            def on_art_progress(idx, tot, nombre):
                self.scrap_status_lbl.setText(f"Carátulas: {nombre[:20]}...")
                self.scrap_bar.setValue(idx)

            stats = await artwork.descargar_caratulas_biblioteca(
                juegos, emu_map, on_progress=on_art_progress
            )
            print(f"[DOWNLOADS] Carátulas: {stats}")

        if do_backgrounds:
            self.scrap_status_lbl.setText("Actualizando fondos de consola...")
            self.scrap_bar.setRange(0, 0)
            await artwork.descargar_fondos_consolas()

        # Finalizar
        self.scrap_status_lbl.setText("¡Descarga completada!")
        self.scrap_bar.setRange(0, 100)
        self.scrap_bar.setValue(100)
        self.btn_scrap.setEnabled(True)
        
        if self.on_update_library_bg:
            self.on_update_library_bg()

        # Ocultar progreso tras unos segundos y volver al estado normal
        def finalize_ui():
            self.progress_container.setVisible(False)
            self.scrap_spacer.setVisible(True)

        QTimer.singleShot(2000, finalize_ui)

    def refresh_emulators(self):
        """Recalcula el estado de las rutas y actualiza las tarjetas o la advertencia."""
        self.load_emulators()

    def load_emulators(self):
        # Limpiar tarjetas anteriores
        for card in self._all_cards:
            card.deleteLater()
        self._all_cards = []
        
        # Limpiar grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Limpiar warning area
        while self.warn_layout.count():
            item = self.warn_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        path_emus = self.emu_manager.install_path
        path_roms = self.emu_manager.roms_path

        valid_paths = (bool(path_emus and os.path.exists(path_emus)) and
                      bool(path_roms and os.path.exists(path_roms)))

        if not valid_paths:
            warn = QLabel(self.translator.t("dl_warn_paths"), self)
            warn.setStyleSheet("""
                background: rgba(30, 20, 22, 0.8); color: #fca5a5; font-size: 13px;
                padding: 16px; border-radius: 12px;
                border: 1px solid rgba(127, 29, 29, 0.4);
            """)
            warn.setWordWrap(True)
            self.warn_layout.addWidget(warn)
            self.warn_area.show()
            self.stats_badge.hide()
        else:
            self.warn_area.hide()
            self.stats_badge.show()

        # Agrupar emuladores por console_id
        console_groups = {}
        from core.constants import AVAILABLE_EMULATORS
        for emu in AVAILABLE_EMULATORS:
            cid = emu.get("console_id", emu["id"])
            if cid not in console_groups:
                console_groups[cid] = []
            console_groups[cid].append(emu)

        self.setUpdatesEnabled(False)
        for cid, emus in console_groups.items():
            card = EmulatorCard(emus, self.emu_manager, self.translator, self.on_update_library_bg, self.grid_container)
            self._all_cards.append(card)
            # No los mostramos ni los acomodamos hasta el final para evitar parpadeos
            card.hide()
            self.grid_layout.addWidget(card)

        self._apply_filter_visibility()
        self._update_stats_badge()
        self.setUpdatesEnabled(True)
        # Forzar reordenamiento inmediato sin esperar al timer si es posible
        QTimer.singleShot(0, lambda: self.resizeEvent(None))

    # ── Responsive grid ───────────────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self._update_stats_badge()
        QTimer.singleShot(0, lambda: self.resizeEvent(None))

    def resizeEvent(self, event):
        if event:
            super().resizeEvent(event)
        if not hasattr(self, 'grid_layout') or self.grid_layout.count() == 0:
            return

        width = self.scroll_area.viewport().width()
        card_width = 240
        spacing = self.grid_layout.spacing()
        cols = max(1, width // (card_width + spacing))

        used_width = cols * card_width + (cols - 1) * spacing
        margin = max(0, (width - used_width) // 2)
        self.grid_layout.setContentsMargins(margin, 10, margin, 20)

        if getattr(self, '_current_cols', 0) != cols:
            self._current_cols = cols
            self._rearrange_grid(cols)

    def _rearrange_grid(self, cols):
        """Reposiciona solo las tarjetas visibles en el grid según las columnas."""
        if not hasattr(self, 'grid_layout'):
            return

        # Usamos la lista maestra para asegurar que no perdemos referencias
        widgets = self._all_cards

        # Limpiar el layout actual
        for w in widgets:
            self.grid_layout.removeWidget(w)

        row, col = 0, 0
        for w in widgets:
            if not w.isHidden():
                self.grid_layout.addWidget(w, row, col)
                col += 1
                if col >= cols:
                    col = 0
                    row += 1
        
        # Opcional: añadir un stretch al final si fuera necesario, 
        # pero con AlignTop|AlignLeft en el grid suele bastar.
