"""
downloads.py — Vista de Descarga e Instalación de Emuladores
Diseño premium: nombre de consola como elemento principal, color único, filtros.
"""

import asyncio
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QProgressBar, QGridLayout,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor
from qasync import asyncSlot
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork

ACCENT = "#4da6ff"
ACCENT_HOVER = "#7abfff"
CARD_DARK = "#13151c"
CARD_BG = "#16181f"
CARD_BG_HOVER = "#1b1e2a"


# ─────────────────────────────────────────────────────────────────────────────
# EMULATOR CARD
# ─────────────────────────────────────────────────────────────────────────────

class EmulatorCard(QFrame):
    """Tarjeta de emulador. Prioridad: nombre de consola. Color único de acento."""

    def __init__(self, emu, emu_manager, translator, on_update_library_bg, parent=None):
        super().__init__(parent)
        self.emu = emu
        self.emu_manager = emu_manager
        self.translator = translator
        self.on_update_library_bg = on_update_library_bg

        self.init_ui()
        self.update_ui_state()

    # ── Layout ────────────────────────────────────────────────────────────────

    def init_ui(self):
        self.setFixedSize(240, 310)
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

        # ── BANNER: logo pequeño centrado ──────────────────────────────────
        banner = QFrame()
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
        self.installed_badge = QLabel("✓ INSTALADO")
        self.installed_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.installed_badge.setStyleSheet(f"""
            background: rgba(34, 197, 94, 0.18);
            color: #4ade80;
            font-size: 9px; font-weight: bold; letter-spacing: 1px;
            border-radius: 8px; padding: 2px 8px;
            border: 1px solid rgba(74, 222, 128, 0.3);
        """)
        self.installed_badge.setFixedHeight(18)
        self.installed_badge.hide()

        # Logo small
        logo_lbl = QLabel()
        logo_path = artwork.obtener_ruta_logo_consola(self.emu["id"]).replace(".png", ".svg")
        if not os.path.exists(logo_path):
            logo_path = artwork.obtener_ruta_logo_consola(self.emu["id"])
        if not os.path.exists(logo_path):
            logo_path = artwork.obtener_ruta_logo_emulador(self.emu["id"]).replace(".png", ".svg")
        if not os.path.exists(logo_path):
            logo_path = artwork.obtener_ruta_logo_emulador(self.emu["id"])

        if os.path.exists(logo_path):
            if logo_path.endswith(".svg"):
                pixmap = QIcon(logo_path).pixmap(QSize(54, 54))
            else:
                pixmap = QPixmap(logo_path).scaled(
                    54, 54, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            logo_lbl.setPixmap(pixmap)
        else:
            logo_lbl.setText("🎮")
            logo_lbl.setStyleSheet("font-size: 30px;")

        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet("background: transparent; border: none;")

        banner_layout.addWidget(self.installed_badge, 0, Qt.AlignmentFlag.AlignCenter)
        banner_layout.addWidget(logo_lbl)

        # ── CONTENT: console name FIRST ────────────────────────────────────
        content = QFrame()
        content.setStyleSheet("background: transparent; border: none;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(16, 14, 16, 8)
        c_layout.setSpacing(4)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # 1. Console name — primary, biggest
        console_lbl = QLabel(self.emu.get("console", "Emulador"))
        console_lbl.setStyleSheet("""
            font-size: 17px; font-weight: 900; color: #f8f8ff;
            background: transparent; border: none;
            letter-spacing: 0.5px;
        """)
        console_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        console_lbl.setWordWrap(True)

        # 2. Emulator name — secondary, muted
        name_lbl = QLabel(self.emu["name"])
        name_lbl.setStyleSheet(f"""
            font-size: 11px; color: {ACCENT};
            background: transparent; border: none; font-weight: 600;
        """)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setWordWrap(True)

        # 3. Status text — tiny
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("""
            font-size: 10px; color: #555566;
            background: transparent; border: none;
        """)
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setMinimumHeight(28)

        c_layout.addWidget(console_lbl)
        c_layout.addWidget(name_lbl)
        c_layout.addStretch()
        c_layout.addWidget(self.status_lbl)

        # ── BOTTOM: progress + button ──────────────────────────────────────
        bottom = QFrame()
        bottom.setStyleSheet("background: transparent; border: none;")
        b_layout = QVBoxLayout(bottom)
        b_layout.setContentsMargins(14, 0, 14, 14)
        b_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: #252830; border-radius: 2px; border: none;
            }}
            QProgressBar::chunk {{
                background: {ACCENT}; border-radius: 2px;
            }}
        """)

        self.action_btn = QPushButton()
        self.action_btn.setFixedHeight(38)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_btn.clicked.connect(self.on_action_clicked)

        b_layout.addWidget(self.progress_bar)
        b_layout.addWidget(self.action_btn)

        main_layout.addWidget(banner)
        main_layout.addWidget(content)
        main_layout.addWidget(bottom)

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

    # ── State ─────────────────────────────────────────────────────────────────

    def update_ui_state(self, keep_status=False):
        is_installed = self.emu_manager.esta_instalado(self.emu["github"])

        if is_installed:
            self.action_btn.setText(self.translator.t("dl_btn_uninstall").upper())
            self.action_btn.setStyleSheet("""
                QPushButton {
                    background: #2d1515; color: #f87171;
                    font-size: 11px; font-weight: bold; letter-spacing: 1px;
                    border: 1px solid #7f1d1d; border-radius: 19px;
                }
                QPushButton:hover { background: #3d1a1a; color: #fca5a5; }
                QPushButton:disabled { background: #1a1c24; color: #444455; }
            """)
            self.installed_badge.show()
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
                        msg = parts[1] if len(parts) > 1 else self.translator.t("lib_status_processing")
                        self.progress_bar.setValue(int(val))
                        self.status_lbl.setText(msg)
                        self.status_lbl.setStyleSheet("font-size: 10px; color: #aaaacc; background: transparent; border: none;")
                    except:
                        self.status_lbl.setText(output_line)
                elif output_line.startswith("ERROR:") or "Error" in output_line:
                    error_occurred = True
                    self.status_lbl.setText(output_line.replace("ERROR:", "").strip())
                    self.status_lbl.setStyleSheet("font-size: 10px; color: #f87171; background: transparent; border: none;")
                else:
                    self.status_lbl.setText(output_line[-60:])

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

    def __init__(self, emu_manager, translator, on_update_library_bg):
        super().__init__()
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

        title = QLabel("EMULADORES")
        title.setStyleSheet("""
            font-size: 26px; font-weight: 900; color: #ffffff;
            letter-spacing: 2px; background: transparent; border: none;
        """)
        title_row.addWidget(title)

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

    # ── Filter ────────────────────────────────────────────────────────────────

    def _set_filter(self, key):
        self._active_filter = key
        self._apply_filter_styles()
        self._apply_filter_visibility()
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

    def load_emulators(self):
        path_emus = self.emu_manager.install_path
        path_roms = self.emu_manager.roms_path

        if not (bool(path_emus and os.path.exists(path_emus)) and
                bool(path_roms and os.path.exists(path_roms))):
            warn = QLabel(self.translator.t("dl_warn_paths"))
            warn.setStyleSheet("""
                background: #1e1416; color: #fca5a5; font-size: 13px;
                padding: 16px; border-radius: 10px;
                border: 1px solid #7f1d1d;
            """)
            warn.setWordWrap(True)
            self.grid_layout.addWidget(warn, 0, 0, 1, 3)
            self.stats_badge.hide()
            return

        for emu in AVAILABLE_EMULATORS:
            card = EmulatorCard(emu, self.emu_manager, self.translator, self.on_update_library_bg)
            self._all_cards.append(card)
            self.grid_layout.addWidget(card)

        self._update_stats_badge()
        QTimer.singleShot(50, lambda: self.resizeEvent(None))

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
        widgets = []
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                widgets.append(item.widget())

        for w in widgets:
            self.grid_layout.removeWidget(w)

        row, col = 0, 0
        for w in widgets:
            if isinstance(w, QLabel):
                self.grid_layout.addWidget(w, row, 0, 1, cols)
                row += 1
                col = 0
            else:
                self.grid_layout.addWidget(w, row, col)
                if w.isVisible():
                    col += 1
                    if col >= cols:
                        col = 0
                        row += 1
