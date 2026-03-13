"""
dashboard.py — Vista de Inicio (Dashboard)
Un centro de mando premium con estadísticas, actividad reciente y estado del sistema.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QVariantAnimation, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QPixmap, QLinearGradient, QColor, QPainter, QFont, QPainterPath
import core.scanner as scanner
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork
from core.config import APP_VERSION


class AnimatedCounterLabel(QLabel):
    """Label que anima su valor numérico de 0 hasta el valor final."""
    def __init__(self, target_value, suffix="", parent=None):
        super().__init__("0" + suffix, parent)
        self.target_value = target_value
        self.suffix = suffix
        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(0)
        self._anim.setEndValue(target_value)
        self._anim.setDuration(1200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(lambda v: self.setText(f"{int(v):,}{self.suffix}".replace(",", ".")))

    def start_animation(self):
        self._anim.start()


class StatCard(QFrame):
    """Tarjeta de estadística con icono, valor animado y etiqueta."""
    def __init__(self, icon, value, label, accent_color="#4da6ff", parent=None):
        super().__init__(parent)
        self.accent_color = accent_color
        self.setFixedSize(200, 120)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        # Solo el QFrame base responde al hover, no los hijos
        self.setStyleSheet(f"""
            QFrame#statCard_{id(self)} {{
                background-color: #1a1c24;
                border-radius: 14px;
                border: 1px solid #2a2d3a;
            }}
            QFrame#statCard_{id(self)}:hover {{
                background-color: #1f2230;
                border: 1px solid {accent_color};
            }}
        """)
        self.setObjectName(f"statCard_{id(self)}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        # Top row: icon + label
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 20px; color: {accent_color};")
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        # Animated counter
        self.counter = AnimatedCounterLabel(value, parent=self)
        self.counter.setStyleSheet(f"""
            font-size: 28px; font-weight: 900;
            color: {accent_color};
            background: transparent; border: none;
        """)
        layout.addWidget(self.counter)

        # Label
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px; color: #888888; background: transparent; border: none;")
        layout.addWidget(lbl)

    def start_animation(self):
        self.counter.start_animation()


class RecentGameRow(QFrame):
    """Fila de juego reciente con icono de consola y tiempo jugado."""
    def __init__(self, game_name, console_name, playtime_str, color="#4da6ff", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-bottom: 1px solid #1f2230;
            }
            QFrame:hover { background-color: #1a1c24; border-radius: 8px; }
        """)
        self.setFixedHeight(52)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)

        # Color dot as console indicator
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {color}; font-size: 10px; background: transparent; border: none;")
        dot.setFixedWidth(16)
        layout.addWidget(dot)

        # Game name + console
        info = QVBoxLayout()
        info.setSpacing(1)
        name_lbl = QLabel(game_name)
        name_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #e0e0e0; background: transparent; border: none;")
        name_lbl.setMaximumWidth(280)
        name_lbl.setWordWrap(False)
        # Truncate if too long
        console_lbl = QLabel(console_name)
        console_lbl.setStyleSheet("font-size: 11px; color: #666666; background: transparent; border: none;")
        info.addWidget(name_lbl)
        info.addWidget(console_lbl)
        layout.addLayout(info)
        layout.addStretch()

        # Playtime
        time_lbl = QLabel(playtime_str)
        time_lbl.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: bold; background: transparent; border: none;")
        layout.addWidget(time_lbl)


class SectionTitle(QLabel):
    """Título de sección con línea acento."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #4da6ff;
            letter-spacing: 2px;
            background: transparent;
            border: none;
            padding-bottom: 4px;
        """)


class DashboardView(QWidget):
    def __init__(self, emu_manager, translator, parent=None):
        super().__init__(parent)
        self.emu_manager = emu_manager
        self.translator = translator
        self._stat_cards = []
        self.init_ui()

    def init_ui(self):
        # Main scroll area so content doesn't get cut off on small screens
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(32)

        # ─── HERO HEADER ────────────────────────────────────────────────
        hero = self._build_hero()
        main_layout.addWidget(hero)

        # ─── STATS ROW ──────────────────────────────────────────────────
        stats_section = QWidget()
        stats_section.setStyleSheet("background: transparent;")
        stats_layout = QVBoxLayout(stats_section)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)
        stats_layout.addWidget(SectionTitle(self.translator.t("dash_stats_title")))
        stats_layout.addLayout(self._build_stats_row())
        main_layout.addWidget(stats_section)

        # ─── CONTENT: Recent games + Quick Status ───────────────────────
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)

        # Left: Recent activity
        recent_section = QWidget()
        recent_section.setStyleSheet("background: transparent;")
        recent_layout = QVBoxLayout(recent_section)
        recent_layout.setContentsMargins(0, 0, 0, 0)
        recent_layout.setSpacing(12)
        recent_layout.addWidget(SectionTitle(self.translator.t("dash_recent_title")))
        recent_panel = self._build_recent_games()
        recent_layout.addWidget(recent_panel)
        recent_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        content_layout.addWidget(recent_section, 3, Qt.AlignmentFlag.AlignTop)

        # Right: System status
        status_section = QWidget()
        status_section.setStyleSheet("background: transparent;")
        status_layout = QVBoxLayout(status_section)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(12)
        status_layout.addWidget(SectionTitle(self.translator.t("dash_status_title_panel")))
        status_layout.addWidget(self._build_status_panel())
        status_layout.addStretch()
        status_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        content_layout.addWidget(status_section, 2, Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(content_layout)
        main_layout.addStretch()

        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        # Trigger animations after a short delay
        QTimer.singleShot(200, self._start_animations)

    def _build_hero(self):
        """Panel hero con saludo y resumen visual."""
        hero = QFrame()
        hero.setFixedHeight(160)
        hero.setStyleSheet("""
            QFrame {
                background-color: #1a1c24;
                border-radius: 18px;
                border: 1px solid #2a2d3a;
            }
        """)

        layout = QHBoxLayout(hero)
        layout.setContentsMargins(36, 0, 36, 0)

        left = QVBoxLayout()
        left.setSpacing(6)
        left.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        greeting = QLabel(self.translator.t("dash_greeting"))
        greeting.setStyleSheet("""
            font-size: 11px; font-weight: bold; color: #4da6ff;
            letter-spacing: 2px; background: transparent; border: none;
        """)
        left.addWidget(greeting)

        app_name = QLabel("EmuManager")
        app_name.setStyleSheet("""
            font-size: 40px; font-weight: 900; color: #ffffff;
            background: transparent; border: none;
        """)
        left.addWidget(app_name)

        tagline = QLabel(self.translator.t("dash_tagline", APP_VERSION))
        tagline.setStyleSheet("""
            font-size: 13px; color: #666666;
            background: transparent; border: none;
        """)
        left.addWidget(tagline)
        layout.addLayout(left)

        layout.addStretch()

        # App logo
        deco = QLabel()
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "media", "icon.svg")
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            pixmap = QIcon(icon_path).pixmap(90, 90)
            deco.setPixmap(pixmap)
        else:
            deco.setText("🎮")
            deco.setStyleSheet("font-size: 80px; background: transparent; border: none;")
        deco.setAlignment(Qt.AlignmentFlag.AlignCenter)
        deco.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(deco)

        return hero

    def _build_stats_row(self):
        """Fila de tarjetas de estadísticas."""
        biblioteca = scanner.cargar_biblioteca_cache()
        installed = sum(
            1 for emu in AVAILABLE_EMULATORS
            if self.emu_manager.esta_instalado(emu["github"])
        )
        total_roms = len(biblioteca)
        total_consoles = len(set(j.get("id_emu") for j in biblioteca))

        # Total playtime in hours
        total_seconds = sum(
            self.emu_manager.get_playtime(j.get("ruta", ""))[0]
            for j in biblioteca
        )
        total_hours = int(total_seconds // 3600)

        cards_data = [
            ("🎯", installed,      self.translator.t("dash_stat_installed"),  "#4da6ff"),
            ("📀", total_roms,     self.translator.t("dash_stat_roms"),       "#7c6ff7"),
            ("🖥️", total_consoles, self.translator.t("dash_stat_consoles"),   "#4dc6a6"),
            ("⏱️", total_hours,    self.translator.t("dash_stat_hours"),      "#f0a040"),
        ]

        row = QHBoxLayout()
        row.setSpacing(16)
        for icon, val, lbl, color in cards_data:
            card = StatCard(icon, val, lbl, color)
            self._stat_cards.append(card)
            row.addWidget(card)
        row.addStretch()
        return row

    def _build_recent_games(self):
        """Panel con los últimos juegos con tiempo de juego registrado."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1a1c24;
                border-radius: 14px;
                border: 1px solid #2a2d3a;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        biblioteca = scanner.cargar_biblioteca_cache()

        # Filtrar juegos con tiempo de juego y ordenar por más tiempo
        juegos_con_tiempo = []
        for j in biblioteca:
            s, h, m = self.emu_manager.get_playtime(j.get("ruta", ""))
            if s > 0:
                juegos_con_tiempo.append((j, s, h, m))

        juegos_con_tiempo.sort(key=lambda x: x[1], reverse=True)

        # Buscar color de consola
        color_map = {emu["id"]: emu.get("color", "#4da6ff") for emu in AVAILABLE_EMULATORS}

        if juegos_con_tiempo:
            for j, s, h, m in juegos_con_tiempo[:7]:  # Max 7
                if h > 0:
                    time_str = f"{h}h {m}m"
                elif m > 0:
                    time_str = f"{m}m"
                else:
                    time_str = "< 1m"

                color = color_map.get(j.get("id_emu"), "#4da6ff")
                row = RecentGameRow(j["nombre"], j.get("consola", ""), time_str, color)
                layout.addWidget(row)
        else:
            empty_lbl = QLabel(self.translator.t("dash_empty_recent"))
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("""
                color: #555566; font-size: 13px;
                padding: 40px; background: transparent; border: none;
            """)
            layout.addWidget(empty_lbl)

        return panel

    def _build_status_panel(self):
        """Panel de estado del sistema."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1a1c24;
                border-radius: 14px;
                border: 1px solid #2a2d3a;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        def status_row(icon, label, path, ok_color="#4dc6a6"):
            row = QHBoxLayout()
            if not path:
                state = "❌"
                color = "#e05050"
                note = self.translator.t("dash_missing")
            elif not os.path.exists(path):
                state = "⚠️"
                color = "#f0a040"
                note = self.translator.t("dash_path_missing")
            else:
                state = "✅"
                color = ok_color
                # Show last folder name
                note = os.path.basename(path.rstrip("/")) or path

            state_lbl = QLabel(state)
            state_lbl.setStyleSheet("font-size: 16px; background: transparent; border: none;")
            state_lbl.setFixedWidth(26)
            row.addWidget(state_lbl)

            right = QVBoxLayout()
            right.setSpacing(2)
            name = QLabel(label)
            name.setStyleSheet("font-size: 12px; font-weight: bold; color: #c0c0c0; background: transparent; border: none;")
            val = QLabel(note)
            val.setStyleSheet(f"font-size: 11px; color: {color}; background: transparent; border: none;")
            val.setMaximumWidth(220)
            right.addWidget(name)
            right.addWidget(val)
            row.addLayout(right)
            row.addStretch()
            return row

        layout.addLayout(status_row("📁", self.translator.t("dash_status_path_emus"), self.emu_manager.install_path))
        layout.addLayout(status_row("🎮", self.translator.t("dash_status_path_roms"), self.emu_manager.roms_path))

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2a2d3a; border: none; max-height: 1px;")
        layout.addWidget(sep)

        # Installed emus list
        installed_emus = [
            emu for emu in AVAILABLE_EMULATORS
            if self.emu_manager.esta_instalado(emu["github"])
        ]

        emus_title = QLabel(self.translator.t("dash_stat_installed"))
        emus_title.setStyleSheet("font-size: 11px; color: #666666; font-weight: bold; background: transparent; border: none;")
        layout.addWidget(emus_title)

        if installed_emus:
            for emu in installed_emus[:6]:
                color = emu.get("color", "#4da6ff")
                row_w = QHBoxLayout()
                dot = QLabel("●")
                dot.setStyleSheet(f"color: {color}; font-size: 9px; background: transparent; border: none;")
                dot.setFixedWidth(16)
                row_w.addWidget(dot)
                name = QLabel(emu["name"])
                name.setStyleSheet("font-size: 12px; color: #c0c0c0; background: transparent; border: none;")
                row_w.addWidget(name)
                row_w.addStretch()
                console_translated = self.translator.t(f"emu_{emu['id']}_console", emu.get("console", "SYSTEM"))
                console_lbl = QLabel(console_translated)
                console_lbl.setStyleSheet("font-size: 10px; color: #555555; background: transparent; border: none;")
                row_w.addWidget(console_lbl)
                layout.addLayout(row_w)
        else:
            none_lbl = QLabel(self.translator.t("dash_status_no_emus"))
            none_lbl.setStyleSheet("font-size: 11px; color: #555555; background: transparent; border: none;")
            layout.addWidget(none_lbl)

        layout.addStretch()

        # Store reference to update later
        self._status_panel = panel
        return panel

    def _start_animations(self):
        """Dispara las animaciones de las tarjetas de estadísticas en cadena."""
        for i, card in enumerate(self._stat_cards):
            QTimer.singleShot(i * 120, card.start_animation)

    def showEvent(self, event):
        """Refresca los datos del dashboard cada vez que la pestaña se vuelve visible."""
        super().showEvent(event)
        if self.isVisible():
            QTimer.singleShot(50, self.update_dashboard_status)

    def retranslate_ui(self):
        """Alias para actualizar el contenido traduciendo etiquetas."""
        self.update_dashboard_status()

    def update_dashboard_status(self):
        """Reconstruye el contenido dinámico del dashboard con datos frescos."""
        try:
            self._stat_cards.clear()
            # Eliminar el scroll anterior y recrear todo el contenido
            layout = self.layout()
            if layout:
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

            # Recrear el scroll y el contenedor
            scroll = QScrollArea(self)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setStyleSheet("background: transparent;")

            container = QWidget()
            container.setStyleSheet("background: transparent;")
            main_layout = QVBoxLayout(container)
            main_layout.setContentsMargins(40, 40, 40, 40)
            main_layout.setSpacing(32)

            main_layout.addWidget(self._build_hero())

            stats_section = QWidget()
            stats_section.setStyleSheet("background: transparent;")
            stats_layout = QVBoxLayout(stats_section)
            stats_layout.setContentsMargins(0, 0, 0, 0)
            stats_layout.setSpacing(12)
            stats_layout.addWidget(SectionTitle(self.translator.t("dash_stats_title")))
            stats_layout.addLayout(self._build_stats_row())
            main_layout.addWidget(stats_section)

            content_layout = QHBoxLayout()
            content_layout.setSpacing(24)

            recent_section = QWidget()
            recent_section.setStyleSheet("background: transparent;")
            recent_layout = QVBoxLayout(recent_section)
            recent_layout.setContentsMargins(0, 0, 0, 0)
            recent_layout.setSpacing(12)
            recent_layout.addWidget(SectionTitle(self.translator.t("dash_recent_title")))
            recent_layout.addWidget(self._build_recent_games())
            recent_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            content_layout.addWidget(recent_section, 3, Qt.AlignmentFlag.AlignTop)

            status_section = QWidget()
            status_section.setStyleSheet("background: transparent;")
            status_layout = QVBoxLayout(status_section)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.setSpacing(12)
            status_layout.addWidget(SectionTitle(self.translator.t("dash_status_title_panel")))
            status_layout.addWidget(self._build_status_panel())
            status_layout.addStretch()
            status_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            content_layout.addWidget(status_section, 2, Qt.AlignmentFlag.AlignTop)

            main_layout.addLayout(content_layout)
            main_layout.addStretch()
            scroll.setWidget(container)
            layout.addWidget(scroll)

            QTimer.singleShot(200, self._start_animations)
        except (RuntimeError, AttributeError):
            pass
