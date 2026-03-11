"""
library.py — Vista de la Biblioteca (Consolas y Juegos)
Gestiona el escaneo de consolas, descarga de carátulas y visualización en rejilla (Grid).
"""

import asyncio
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QGridLayout, QStackedWidget,
    QLineEdit, QSizePolicy, QProgressBar, QApplication, QSplitter,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QTimer, QVariantAnimation, QEasingCurve, QRectF, QPropertyAnimation
from PyQt6.QtGui import QPixmap, QColor, QPainter, QLinearGradient, QPainterPath, QFont, QPen
from PyQt6.QtWidgets import QMessageBox
from qasync import asyncSlot
import core.scanner as scanner
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork
import core.metadata as metadata
from ui.views.loading import LoadingOverlay

class ConsoleCarousel(QWidget):
    """Carrusel interactivo de consolas a pantalla completa."""
    def __init__(self, translator, on_click_callback, parent_view=None):
        super().__init__(parent_view)
        self.translator = translator
        self.on_click_callback = on_click_callback
        self.parent_view = parent_view # Referencia para sincronizar el fondo
        self.consoles_data = [] # Lista de (emu, count, playtime)
        self.current_index = 0
        self.current_bg_pixmap = None
        self.current_color = "#15171e"
        self.target_opacity = 1.0
        self.progress = 0.0
        self.slide_direction = 1
        self.is_animating = False
        self.old_bg = None
        self.cached_bg = None
        self.cached_old_bg = None
        
        self.anim = QVariantAnimation()
        self.anim.setDuration(400) # Más rápido para mayor fluidez
        self.anim.setStartValue(0)
        self.anim.setEndValue(100)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad) # Curva suave pero ágil
        self.anim.valueChanged.connect(self._on_anim_value_changed)
        self.anim.finished.connect(self._on_anim_finished)
        
        self.init_ui()
        
    def _on_anim_value_changed(self, value):
        self.progress = value / 100.0
        self._update_geometries()
        self.update()
        
    def _on_anim_finished(self):
        self.progress = 1.0
        self._update_geometries()
        self.is_animating = False
        
        # Rotación de paneles
        self.current_pane, self.next_pane = self.next_pane, self.current_pane
        self.next_pane.hide()
        
        # ACTUALIZAR FONDO GLOBAL (LibraryView)
        if hasattr(self.parent(), "parent") and hasattr(self.parent().parent(), "current_bg_pixmap"):
            lib_view = self.parent().parent() # ConsoleCarousel -> Page -> Stack -> LibraryView (o similar)
            # En realidad es self.parent() (Page) -> Layout -> Stack -> LibraryView
            # Vamos a buscarlo de forma más robusto o simplemente emitir un señal si fuera más formal
            # Pero como estamos en el mismo archivo, usaremos acceso directo al parent_view si lo guardamos
            pass
            
        # Forma simple: El carousel tiene una referencia a LibraryView? No directamente.
        # Vamos a añadirla en __init__
        if hasattr(self, "parent_view") and self.parent_view:
            self.parent_view.current_bg_pixmap = self.current_bg_pixmap
            self.parent_view.current_color = self.current_color
            self.parent_view.cached_bg = self.parent_view._get_scaled_bg(self.current_bg_pixmap)
            self.parent_view.update()

        # Limpiar caché viejo
        self.old_bg = None
        self.cached_old_bg = None
        
        self.current_pane.setGeometry(self.overlay_container.rect())
        self.update()
        
    def _update_geometries(self):
        """Posiciona los paneles en vivo durante la animación."""
        try:
            if not self or not hasattr(self, 'overlay_container') or self.overlay_container is None:
                return
            
            rect = self.overlay_container.rect()
            if rect.isEmpty(): return
            
            w = rect.width()
            
            if not self.is_animating:
                # En estado de reposo, el panel debe estar perfectamente en (0,0)
                self.current_pane.setGeometry(rect)
                self.next_pane.hide()
                return
                
            # Calcular offset preciso
            offset = self.progress * w * self.slide_direction
            
            # Mover paneles con precisión entera final solo para el dibujo
            self.current_pane.move(int(-offset), 0)
            
            new_start_x = w if self.slide_direction > 0 else -w
            self.next_pane.move(int(new_start_x - offset), 0)
            self.next_pane.show()
        except (RuntimeError, AttributeError):
            pass
        
    def init_ui(self):
        self.setProperty("class", "carouselContainer")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(60, 0, 60, 0)
        
        self.btn_left = QPushButton("‹")
        self.btn_left.setProperty("class", "carouselNavButton")
        self.btn_left.setFixedSize(60, 60)
        self.btn_left.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_left.clicked.connect(self.prev_console)
        
        self.btn_right = QPushButton("›")
        self.btn_right.setProperty("class", "carouselNavButton")
        self.btn_right.setFixedSize(60, 60)
        self.btn_right.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_right.clicked.connect(self.next_console)
        
        # Contenedor para el contenido que se desliza
        self.overlay_container = QWidget()
        self.overlay_container.setProperty("class", "transparentBg")
        
        # Crear dos paneles idénticos para transiciones fluidas
        self.panel_a = self._create_content_panel()
        self.panel_b = self._create_content_panel()
        self.panel_a.setParent(self.overlay_container)
        self.panel_b.setParent(self.overlay_container)
        self.panel_b.hide()
        
        self.current_pane = self.panel_a
        self.next_pane = self.panel_b
        
        # Contenedor para Dots
        self.dots_container = QWidget()
        self.dots_container.setProperty("class", "carouselPaginationContainer")
        self.dots_container.setFixedHeight(25)
        self.dots_layout = QHBoxLayout(self.dots_container)
        self.dots_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dots_layout.setSpacing(8)
        self.dots_layout.setContentsMargins(0, 0, 0, 0)
        
        # Layout Vertical que sostiene el Viewport y los Dots
        self.overlay_layout = QVBoxLayout()
        self.overlay_layout.addStretch(1)
        self.overlay_layout.addWidget(self.overlay_container, 2) # Viewport ocupa el centro
        self.overlay_layout.addStretch(1)
        self.overlay_layout.addWidget(self.dots_container)
        self.overlay_layout.addSpacing(20)
        
        main_layout.addWidget(self.btn_left, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(self.overlay_layout, 1) 
        main_layout.addWidget(self.btn_right, 0, Qt.AlignmentFlag.AlignCenter)

    def _create_content_panel(self):
        """Crea la estructura de labels para un panel de consola."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(80, 50, 50, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        panel.lbl_title = QLabel()
        panel.lbl_title.setProperty("class", "carouselTitle")
        panel.lbl_title.setWordWrap(True)
        panel.lbl_title.setMinimumWidth(600)
        panel.lbl_title.setMinimumHeight(60)
        panel.lbl_title.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        
        panel.lbl_emu = QLabel()
        panel.lbl_emu.setProperty("class", "carouselEmu")
        panel.lbl_emu.setFixedHeight(40)
        
        panel.lbl_info = QLabel()
        panel.lbl_info.setProperty("class", "carouselInfo")
        panel.lbl_info.setFixedHeight(30)
        
        panel.lbl_empty_icon = QLabel("🗄️")
        panel.lbl_empty_icon.setProperty("class", "carouselEmptyIcon")
        panel.lbl_empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel.lbl_empty_icon.hide()

        # --- PANEL ESTADO VACÍO (premium, centrado) ---
        panel.empty_card = QFrame()
        panel.empty_card.setStyleSheet("""
            QFrame {
                background: rgba(15, 18, 28, 0.92);
                border-radius: 24px;
                border: 1px solid rgba(77, 166, 255, 0.25);
            }
        """)
        panel.empty_card.setFixedSize(480, 260)
        empty_card_layout = QVBoxLayout(panel.empty_card)
        empty_card_layout.setContentsMargins(48, 36, 48, 36)
        empty_card_layout.setSpacing(14)
        empty_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ec_icon = QLabel("🕹️")
        ec_icon.setStyleSheet("font-size: 56px; background: transparent; border: none;")
        ec_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_card_layout.addWidget(ec_icon)

        ec_title = QLabel("Sin emuladores instalados")
        ec_title.setStyleSheet("""
            font-size: 20px; font-weight: 900;
            color: #ffffff; background: transparent; border: none;
        """)
        ec_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_card_layout.addWidget(ec_title)

        ec_sub = QLabel("Ve a la sección Descargas para instalar\nun emulador y empezar a jugar.")
        ec_sub.setStyleSheet("""
            font-size: 13px; color: #666688;
            background: transparent; border: none;
        """)
        ec_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ec_sub.setWordWrap(True)
        empty_card_layout.addWidget(ec_sub)

        panel.empty_card.hide()

        panel.btn_play = QPushButton(self.translator.t("lib_btn_view_games").upper())
        panel.btn_play.setStyleSheet("""
            QPushButton {
                background-color: #1976d2; color: white;
                border-radius: 6px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #1565c0; }
        """)
        panel.btn_play.setFixedSize(180, 45)
        panel.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        panel.btn_play.clicked.connect(self.on_play_clicked)

        # Elementos normales (consola con datos)
        layout.addWidget(panel.lbl_title)
        layout.addWidget(panel.lbl_emu)
        layout.addSpacing(5)
        layout.addWidget(panel.lbl_info)
        layout.addSpacing(20)
        layout.addWidget(panel.btn_play)
        layout.addWidget(panel.lbl_empty_icon)

        # Empty card centrada (se muestra solo cuando no hay consolas)
        layout.addStretch(1)
        layout.addWidget(panel.empty_card, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        
        return panel

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_geometries()
        
    def set_data(self, consoles_data):
        self.consoles_data = consoles_data
        self.current_index = 0
        self._update_dots()
        self.update_ui()
        
    def _update_dots(self):
        # Limpiar dots previos
        while self.dots_layout.count():
            item = self.dots_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if len(self.consoles_data) <= 1:
            self.dots_container.hide()
            return
            
        self.dots_container.show()
        for i in range(len(self.consoles_data)):
            dot = QPushButton()
            
            if i == self.current_index:
                dot.setStyleSheet("""
                    QPushButton { background-color: #4da6ff; border: none; border-radius: 5px; min-width: 25px; max-width: 25px; min-height: 10px; max-height: 10px; }
                    QPushButton:hover { background-color: #7abfff; }
                """)
            else:
                dot.setStyleSheet("""
                    QPushButton { background-color: rgba(255, 255, 255, 60); border: none; border-radius: 5px; min-width: 10px; max-width: 10px; min-height: 10px; max-height: 10px; }
                    QPushButton:hover { background-color: rgba(255, 255, 255, 120); }
                """)
                
            dot.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Conexión con el índice actual mediante lambda con captura de variable
            dot.clicked.connect(lambda checked, idx=i: self.jump_to_console(idx))
            
            self.dots_layout.addWidget(dot)

    def _start_transition(self, direction):
        if self.is_animating: return
        
        self.slide_direction = direction
        self.progress = 0
        
        # Caché del fondo viejo para el crossfade interno
        self.cached_old_bg = self.cached_bg
        self.old_bg = self.current_bg_pixmap
        
        # Preparar el panel entrante
        self.update_ui(self.next_pane)
        self.next_pane.setGeometry(self.overlay_container.rect())
        
        # Pre-cachear el fondo nuevo
        if self.current_bg_pixmap:
            self.cached_bg = self._get_scaled_bg(self.current_bg_pixmap)
        else:
            self.cached_bg = None
            
        self.is_animating = True
        self.anim.stop()
        self.anim.start()

    def jump_to_console(self, index):
        if self.current_index == index: return
        direction = 1 if index > self.current_index else -1
        self.current_index = index
        self._update_dots()
        self._start_transition(direction)

    def prev_console(self):
        if not self.consoles_data: return
        self.current_index = (self.current_index - 1) % len(self.consoles_data)
        self._update_dots()
        self._start_transition(-1)
        
    def next_console(self):
        if not self.consoles_data: return
        self.current_index = (self.current_index + 1) % len(self.consoles_data)
        self._update_dots()
        self._start_transition(1)
        
    def on_play_clicked(self):
        if not self.consoles_data: return
        emu = self.consoles_data[self.current_index][0]
        self.on_click_callback(emu)
        
    def update_ui(self, target_pane=None):
        """Si target_pane es None, actualiza el actual. Si no, actualiza el especificado."""
        pane = target_pane if target_pane else self.current_pane
        
        if not self.consoles_data:
            pane.lbl_title.setText("")
            pane.lbl_title.hide()
            pane.lbl_emu.hide()
            pane.lbl_info.hide()
            pane.btn_play.hide()
            pane.lbl_empty_icon.hide()
            if hasattr(pane, 'empty_card'):
                pane.empty_card.show()
            # Centrar el layout del panel para que el empty_card quede centrado
            pane.layout().setContentsMargins(0, 0, 0, 0)
            pane.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.btn_left.hide()
            self.btn_right.hide()
            self.current_bg_pixmap = None
            self.current_color = "#1a2540"
            self.update()
            return
            
        is_carousel = len(self.consoles_data) > 1
        self.btn_left.setVisible(is_carousel)
        self.btn_right.setVisible(is_carousel)
        
        # Restaurar alineación izquierda y márgenes normales cuando hay consolas
        pane.layout().setContentsMargins(80, 50, 50, 50)
        pane.layout().setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # Mostrar elementos necesarios
        pane.lbl_emu.show()
        pane.lbl_info.show()
        pane.btn_play.show()
        # Ocultar panel vacío y restaurar lbl_title
        if hasattr(pane, 'empty_card'):
            pane.empty_card.hide()
        pane.lbl_empty_icon.hide()
        pane.lbl_title.show()
        
        emu, count, playtime = self.consoles_data[self.current_index]
        self.current_color = emu.get("color", "#4da6ff")
        
        console_key = f"emu_{emu['id']}_console"
        pane.lbl_title.setText(self.translator.t(console_key).upper())
        pane.lbl_title.setStyleSheet(f"color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 {self.current_color}, stop:1 #ffffff);")
        pane.lbl_emu.setText(emu["name"])
        pane.lbl_emu.setStyleSheet(f"color: {self.current_color}; font-weight: bold;")
        
        h = int(playtime // 3600)
        m = int((playtime % 3600) // 60)
        time_str = f"⏱ {self.translator.t('lib_played_hours', h, m)}" if h > 0 or m > 0 else ""
        count_str = self.translator.t("lib_games_count", count).upper()
        pane.lbl_info.setText(f"{count_str}   |   {time_str}")
        
        bg_path = artwork.obtener_ruta_fondo_consola(emu["id"])
        self.current_bg_pixmap = QPixmap(bg_path) if os.path.exists(bg_path) else None
        
        # Pre-cachear fondo si no estamos en animación (estado estático)
        if not self.is_animating:
            if self.current_bg_pixmap:
                self.cached_bg = self._get_scaled_bg(self.current_bg_pixmap)
            else:
                self.cached_bg = None
        
        self.update()

    def _get_scaled_bg(self, pixmap):
        """Escala el pixmap una sola vez para caché."""
        if not pixmap or pixmap.isNull(): return None
        return pixmap.scaled(self.size(), 
                            Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                            Qt.TransformationMode.SmoothTransformation)
        
    def paintEvent(self, event):
        # El fondo principal ahora lo dibuja LibraryView para persistencia
        # Solo dibujamos el fondo aquí durante la animación para el crossfade
        if not self.is_animating:
            return
            
        from PyQt6.QtGui import QPainter
        from PyQt6.QtCore import QRectF
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect_f = QRectF(self.rect())
        
        # Crossfade interno durante transición
        if self.cached_old_bg:
            painter.setOpacity(1.0 - self.progress)
            self._draw_cached_bg(painter, rect_f, self.cached_old_bg, self.current_color)
        
        if self.cached_bg:
            painter.setOpacity(self.progress)
            self._draw_cached_bg(painter, rect_f, self.cached_bg, self.current_color)
            
        # IMPORTANTE: Re-dibujar el degradado encima durante la animación 
        # porque los fondos del carrusel se dibujan sobre el fondo estático de LibraryView
        painter.setOpacity(1.0)
        if hasattr(self, 'parent_view') and self.parent_view:
            self.parent_view._draw_overlay_gradient(painter, self.rect())

    def _draw_cached_bg(self, painter, rect, pixmap, color):
        if pixmap:
            x = rect.x() + (rect.width() - pixmap.width()) / 2.0
            y = rect.y() + (rect.height() - pixmap.height()) / 2.0
            painter.drawPixmap(int(x), int(y), pixmap)
        else:
            from PyQt6.QtGui import QColor, QLinearGradient
            base_color = QColor(color)
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, base_color.darker(300))
            gradient.setColorAt(1, QColor(15, 17, 22))
            painter.fillRect(rect, gradient)

    def _draw_bg_at(self, painter, rect, pixmap, color):
        from PyQt6.QtGui import QColor, QLinearGradient
        from PyQt6.QtCore import Qt, QRectF
        
        # rect puede ser QRect o QRectF
        r_f = QRectF(rect)
        
        if pixmap and not pixmap.isNull():
            # Escalado suave del fondo
            scaled_bg = pixmap.scaled(rect.toRect().size() if hasattr(rect, "toRect") else rect.size(), 
                                     Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation)
            x_offset = r_f.x() + (r_f.width() - scaled_bg.width()) / 2.0
            y_offset = r_f.y() + (r_f.height() - scaled_bg.height()) / 2.0
            painter.drawPixmap(QRectF(x_offset, y_offset, scaled_bg.width(), scaled_bg.height()), scaled_bg, QRectF(scaled_bg.rect()))
        else:
            base_color = QColor(color)
            x, y, w, h = r_f.x(), r_f.y(), r_f.width(), r_f.height()
            gradient = QLinearGradient(x, y, x + w, y + h)
            gradient.setColorAt(0, base_color.darker(300))
            gradient.setColorAt(1, QColor(15, 17, 22))
            painter.fillRect(r_f, gradient)



class GameCard(QFrame):
    """Tarjeta visual de Juego con efectos premium: glow, favorito y hover border."""

    CARD_W = 170   # Proporcion boxart 3:4 — no estirado
    CARD_H = 240
    CARD_W_HOVER = 183  # ~7% scale on hover
    CARD_H_HOVER = 259

    def __init__(self, game, translator, on_launch_callback,
                 on_hover_callback=None, accent_color="#4da6ff", parent=None):
        super().__init__(parent)
        self.game = game
        self.translator = translator
        self.on_launch_callback = on_launch_callback
        self.on_hover_callback = on_hover_callback
        self.accent_color = accent_color
        self._selected = False  # Cuando True, el hero panel queda "pinado"
        self.init_ui()

    def init_ui(self):
        self.setObjectName("gameCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(self.CARD_W, self.CARD_H)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(18)
        self._shadow.setOffset(0, 5)
        self._shadow.setColor(QColor(0, 0, 0, 170))
        self.setGraphicsEffect(self._shadow)

        self.setStyleSheet("""
            QFrame#gameCard {
                background-color: #141620;
                border-radius: 14px;
                border: 1.5px solid #22253a;
            }
        """)

        layers = QGridLayout(self)
        layers.setContentsMargins(0, 0, 0, 0)
        layers.setSpacing(0)

        # Layer 1: artwork — fixed size container with rounded corners
        # KeepAspectRatio preserves image ratio, painted manually
        self.img_lbl = QLabel()
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setFixedSize(self.CARD_W, self.CARD_H)
        self.img_lbl.setStyleSheet("""
            background: #0e1018;
            border-radius: 14px;
        """)
        ruta_rom = self.game.get("ruta", "")
        caratula_path = artwork.obtener_ruta_caratula(ruta_rom) if ruta_rom else None
        self.set_artwork(caratula_path)
        layers.addWidget(self.img_lbl, 0, 0)

        # Layer 2: overlay
        overlay = QFrame()
        overlay.setFixedSize(self.CARD_W, self.CARD_H)
        overlay.setStyleSheet("background: transparent; border: none;")
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        ov_layout = QVBoxLayout(overlay)
        ov_layout.setContentsMargins(0, 0, 0, 0)
        ov_layout.setSpacing(0)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(8, 8, 8, 0)
        self.fav_lbl = QLabel("\u2605")
        self.fav_lbl.setFixedSize(26, 26)
        self.fav_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_fav_label()
        top_row.addWidget(self.fav_lbl)
        top_row.addStretch()
        self.playtime_badge = QLabel()
        self.playtime_badge.setStyleSheet("""
            background: rgba(0,0,0,0.82); color: #4da6ff;
            font-size: 9px; font-weight: bold;
            border-radius: 7px; padding: 2px 8px;
            border: 1px solid rgba(77,166,255,0.35);
        """)
        self.playtime_badge.hide()
        top_row.addWidget(self.playtime_badge)
        ov_layout.addLayout(top_row)
        ov_layout.addStretch()

        title_strip = QFrame()
        title_strip.setFixedHeight(100)
        title_strip.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        title_strip.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 rgba(0,0,0,0),
                    stop:0.4 rgba(0,0,0,0.82),
                    stop:1 rgba(0,0,0,0.97));
                border-bottom-left-radius: 14px;
                border-bottom-right-radius: 14px;
                border: none;
            }
        """)
        strip_layout = QVBoxLayout(title_strip)
        strip_layout.setContentsMargins(12, 8, 12, 14)
        strip_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.name_lbl = QLabel(self.game["nombre"])
        self.name_lbl.setStyleSheet("""
            font-size: 11px; font-weight: 900; color: #ffffff;
            background: transparent; border: none;
        """)
        self.name_lbl.setWordWrap(True)
        strip_layout.addWidget(self.name_lbl)
        ov_layout.addWidget(title_strip)
        layers.addWidget(overlay, 0, 0)

        # Layer 3: hover border
        self._hover_frame = QFrame(self)
        self._hover_frame.setFixedSize(self.CARD_W, self.CARD_H)
        self._hover_frame.setStyleSheet("""
            QFrame { background: transparent; border-radius: 14px;
                     border: 2px solid transparent; }
        """)
        self._hover_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layers.addWidget(self._hover_frame, 0, 0)

    def _update_fav_label(self):
        ruta = self.game.get("ruta", "")
        is_fav = scanner.es_favorito(ruta)
        if is_fav:
            self.fav_lbl.setStyleSheet("""
                color: #FFD700; font-size: 16px; font-weight: bold;
                background: rgba(0,0,0,0.7); border-radius: 13px;
                border: 1px solid rgba(255,215,0,0.4);
            """)
        else:
            self.fav_lbl.setStyleSheet("""
                color: rgba(255,255,255,0.2); font-size: 15px;
                background: rgba(0,0,0,0.45); border-radius: 13px;
                border: 1px solid rgba(255,255,255,0.07);
            """)

    def set_artwork(self, img_path):
        """Carga y muestra la caratula del juego con proporcion correcta y esquinas redondeadas."""
        success = False
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                # KeepAspectRatio: nunca estira, centra la imagen en el contenedor
                pixmap = pixmap.scaled(self.CARD_W, self.CARD_H,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                # Aplicar mascara de esquinas redondeadas al pixmap mismo
                rounded = QPixmap(pixmap.size())
                rounded.fill(Qt.GlobalColor.transparent)
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), 14, 14)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
                self.img_lbl.setPixmap(rounded)
                self.img_lbl.setText("")
                success = True
        if not success:
            initial = self.game.get("nombre", "?")[0].upper()
            self.img_lbl.setPixmap(QPixmap())
            self.img_lbl.setText(initial)
            self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.img_lbl.setStyleSheet(f"""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #1a2235, stop:1 #080a12);
                border-radius: 14px; font-size: 58px; font-weight: 900;
                color: {self.accent_color}33;
            """)

    def set_playtime(self, hours, minutes):
        if hours > 0 or minutes > 0:
            text = f"\u23f1 {hours}h {minutes}m" if hours > 0 else f"\u23f1 {minutes}m"
            self.playtime_badge.setText(text)
            self.playtime_badge.show()

    def refresh_fav(self):
        self._update_fav_label()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.fav_lbl.geometry().contains(event.pos()):
                ruta = self.game.get("ruta", "")
                scanner.toggle_favorito(ruta)
                self._update_fav_label()
                if self.on_hover_callback:
                    self.on_hover_callback(self.game)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Clic: ancla el hero panel a este juego (no lanza directamente)."""
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.fav_lbl.geometry().contains(event.pos()):
                # Notificar seleccion al padre (library view)
                if self.on_hover_callback:
                    self.on_hover_callback(self.game, pinned=True)

    def enterEvent(self, event):
        """Hover: resaltar borde, shadow glow, y escalar la tarjeta."""
        self._shadow.setColor(QColor(self.accent_color))
        self._shadow.setBlurRadius(36)
        self._shadow.setOffset(0, 8)
        self._hover_frame.setStyleSheet(f"""
            QFrame {{ background: transparent; border-radius: 14px;
                     border: 2.5px solid {self.accent_color}; }}
        """)
        # Scale up
        self.setFixedSize(self.CARD_W_HOVER, self.CARD_H_HOVER)
        if self.on_hover_callback:
            self.on_hover_callback(self.game)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Leave: restaurar tamano y glow. El hero panel NO se limpia (queda el ultimo)."""
        self._shadow.setColor(QColor(0, 0, 0, 170))
        self._shadow.setBlurRadius(18)
        self._shadow.setOffset(0, 5)
        self._hover_frame.setStyleSheet("""
            QFrame { background: transparent; border-radius: 14px;
                     border: 2px solid transparent; }
        """)
        # Scale back to normal
        self.setFixedSize(self.CARD_W, self.CARD_H)
        # No llamar on_hover_callback(None) — el hero panel persiste
        super().leaveEvent(event)


class GameHeroPanel(QFrame):
    """Panel lateral derecho que muestra los detalles del juego seleccionado/hovered."""

    def __init__(self, translator, on_launch_callback, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.on_launch_callback = on_launch_callback
        self.current_game = None
        self.init_ui()

    def init_ui(self):
        self.setObjectName("gameHeroPanel")
        self.setMinimumWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("""
            QFrame#gameHeroPanel {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #0e1018, stop:1 #11131d);
                border-left: 1px solid #1e2130;
                border-radius: 0px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Artwork section (top half) ────────────────────────────────────
        self.art_container = QFrame()
        self.art_container.setFixedHeight(300)
        self.art_container.setStyleSheet("background: transparent; border: none;")
        art_layout = QVBoxLayout(self.art_container)
        art_layout.setContentsMargins(0, 0, 0, 0)

        self.art_lbl = QLabel()
        self.art_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.art_lbl.setStyleSheet("background: transparent; border: none;")
        self.art_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        art_layout.addWidget(self.art_lbl)
        main_layout.addWidget(self.art_container)

        # ── Info section (bottom half) ─────────────────────────────────────
        info_frame = QFrame()
        info_frame.setStyleSheet("background: transparent; border: none;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(24, 20, 24, 24)
        info_layout.setSpacing(8)

        self.title_lbl = QLabel()
        self.title_lbl.setStyleSheet("""
            font-size: 20px; font-weight: 900; color: #ffffff;
            background: transparent; border: none;
            letter-spacing: 0.5px;
        """)
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setMaximumHeight(70)
        info_layout.addWidget(self.title_lbl)

        # Meta row: developer | year | genre
        self.meta_lbl = QLabel()
        self.meta_lbl.setStyleSheet("""
            font-size: 11px; color: #5566aa;
            background: transparent; border: none;
        """)
        self.meta_lbl.setWordWrap(True)
        info_layout.addWidget(self.meta_lbl)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #1e2130; border: none; margin: 4px 0;")
        info_layout.addWidget(sep)

        # Description
        self.desc_lbl = QLabel()
        self.desc_lbl.setStyleSheet("""
            font-size: 12px; color: #7788aa; line-height: 1.5;
            background: transparent; border: none;
        """)
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setMaximumHeight(90)
        self.desc_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_layout.addWidget(self.desc_lbl)

        info_layout.addStretch()

        # Playtime
        self.playtime_lbl = QLabel()
        self.playtime_lbl.setStyleSheet("""
            font-size: 11px; color: #4da6ff;
            background: transparent; border: none;
        """)
        info_layout.addWidget(self.playtime_lbl)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_play = QPushButton("\u25b6  JUGAR")
        self.btn_play.setFixedHeight(44)
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play.setStyleSheet("""
            QPushButton {
                background: #4da6ff; color: #ffffff;
                font-size: 13px; font-weight: 900;
                border-radius: 10px; border: none;
                letter-spacing: 1px; padding: 0 20px;
            }
            QPushButton:hover { background: #6ab8ff; }
            QPushButton:pressed { background: #2d8ae0; }
        """)
        self.btn_play.clicked.connect(self._on_play)
        btn_row.addWidget(self.btn_play, 2)

        self.btn_fav = QPushButton("\u2605")
        self.btn_fav.setFixedSize(44, 44)
        self.btn_fav.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fav.setStyleSheet("""
            QPushButton {
                background: #1a1e2a; color: rgba(255,255,255,0.3);
                font-size: 18px; border-radius: 10px;
                border: 1px solid #252838;
            }
            QPushButton:hover { background: #1e2436; color: #FFD700; border-color: #FFD700; }
        """)
        self.btn_fav.clicked.connect(self._on_fav_toggle)
        btn_row.addWidget(self.btn_fav)

        info_layout.addLayout(btn_row)
        main_layout.addWidget(info_frame, 1)

        # ── Empty state ────────────────────────────────────────────────────
        self.empty_state = QFrame()
        self.empty_state.setStyleSheet("background: transparent; border: none;")
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setContentsMargins(32, 0, 32, 0)
        empty_icon = QLabel("\U0001f3ae")
        empty_icon.setStyleSheet("font-size: 52px; background: transparent; border: none;")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)
        empty_hint = QLabel("Pasa el cursor sobre un juego\npara ver sus detalles")
        empty_hint.setStyleSheet("""
            font-size: 13px; color: #2d3250;
            background: transparent; border: none;
            font-weight: 600; letter-spacing: 0.3px;
        """)
        empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_hint)
        main_layout.addWidget(self.empty_state)

        self._show_empty()

    def _show_empty(self):
        self.art_container.hide()
        self.empty_state.show()
        # Hide info widgets inside info_frame
        for child in self.findChildren(QLabel):
            if child != self.empty_state and child.parent() != self.empty_state:
                pass  # managed by layout

    def set_game(self, game):
        """Actualiza el hero panel con la info de un juego."""
        self.current_game = game

        if game is None:
            self.art_container.hide()
            self.empty_state.show()
            return

        self.empty_state.hide()
        self.art_container.show()

        # Artwork
        ruta_rom = game.get("ruta", "")
        caratula_path = artwork.obtener_ruta_caratula(ruta_rom) if ruta_rom else None
        if caratula_path and os.path.exists(caratula_path):
            pix = QPixmap(caratula_path).scaled(
                self.art_lbl.width() or 240, 300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.art_lbl.setPixmap(pix)
        else:
            self.art_lbl.setPixmap(QPixmap())
            self.art_lbl.setText(game.get("nombre", "?")[0].upper())
            self.art_lbl.setStyleSheet("""
                font-size: 96px; font-weight: 900;
                color: rgba(77,166,255,0.12);
                background: transparent; border: none;
            """)

        # Title
        self.title_lbl.setText(game.get("nombre", ""))

        # Metadata from local cache
        meta = metadata.obtener_metadata_local(ruta_rom)
        year = meta.get("year", "")
        developer = meta.get("developer", "")
        genre = meta.get("genre", "")
        desc = meta.get("description", "")
        rating = meta.get("rating", "")

        meta_parts = []
        if developer: meta_parts.append(developer)
        if year: meta_parts.append(year)
        if genre: meta_parts.append(genre)
        self.meta_lbl.setText("  \u2022  ".join(meta_parts) if meta_parts else game.get("consola", ""))

        if desc:
            # Truncate at 220 chars
            short_desc = desc[:220] + "..." if len(desc) > 220 else desc
            self.desc_lbl.setText(short_desc)
        else:
            self.desc_lbl.setText("")

        # Favorite button state
        is_fav = scanner.es_favorito(ruta_rom)
        self._set_fav_style(is_fav)

    def _set_fav_style(self, is_fav: bool):
        if is_fav:
            self.btn_fav.setStyleSheet("""
                QPushButton {
                    background: rgba(255,215,0,0.15); color: #FFD700;
                    font-size: 18px; border-radius: 10px;
                    border: 1.5px solid #FFD700;
                }
                QPushButton:hover { background: rgba(255,215,0,0.25); }
            """)
        else:
            self.btn_fav.setStyleSheet("""
                QPushButton {
                    background: #1a1e2a; color: rgba(255,255,255,0.3);
                    font-size: 18px; border-radius: 10px;
                    border: 1px solid #252838;
                }
                QPushButton:hover { background: #1e2436; color: #FFD700; border-color: #FFD700; }
            """)

    def set_playtime(self, hours, minutes):
        if hours > 0 or minutes > 0:
            text = f"\u23f1 {hours}h {minutes}m jugados" if hours > 0 else f"\u23f1 {minutes}m jugados"
            self.playtime_lbl.setText(text)
        else:
            self.playtime_lbl.setText("Sin jugar aun")

    def _on_play(self):
        if self.current_game:
            self.on_launch_callback(self.current_game)

    def _on_fav_toggle(self):
        if not self.current_game:
            return
        ruta = self.current_game.get("ruta", "")
        is_fav = scanner.toggle_favorito(ruta)
        self._set_fav_style(is_fav)


class LibraryView(QWidget):
    """Controlador principal de la pestaña 'Biblioteca'."""
    def __init__(self, emu_manager, emu_platform_map, translator, parent_app=None):
        super().__init__()
        self.emu_manager = emu_manager
        self.emu_platform_map = emu_platform_map # Mapeo de IDs a Libretro Platforms
        self.translator = translator
        self.parent_app = parent_app
        
        # Gestión de fondos persistentes
        self.current_bg_pixmap = None
        self.cached_bg = None
        self.current_color = "#15171e"
        
        # Estado de carga
        self._needs_refresh = True  # Solo recargar cuando sea necesario
        self._pinned_game = None    # Juego anclado en hero panel (clic)

        self.init_ui()
        
        # Overlay Global de la Pestaña Library
        self.overlay = LoadingOverlay(self)
        
    def init_ui(self):
        """Construye las dos páginas de la Biblioteca (Lista de Consolas y Detalle de ROMs)."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # El QStackedWidget nos permite intercambiar entre Consolas <-> Juegos
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent; border: none;") # Solo este stack es transparente
        
        # --- PÁGINA 1: LISTA DE CONSOLAS ---
        self.page_consoles = QWidget()
        self.page_consoles.setProperty("class", "transparentBg")
        pc_layout = QVBoxLayout(self.page_consoles)
        pc_layout.setContentsMargins(0, 0, 0, 0)
        
        self.carousel = ConsoleCarousel(self.translator, self.abrir_detalle_consola, self)
        pc_layout.addWidget(self.carousel)
        
        self.stack.addWidget(self.page_consoles)
        
        # --- PÁGINA 2: LISTA DE JUEGOS ---
        self.page_games = QWidget()
        self.page_games.setProperty("class", "transparentBg")
        page_games_layout = QVBoxLayout(self.page_games)
        page_games_layout.setContentsMargins(30, 30, 30, 20)
        
        # EXPLICACIÓN HEADER: El Header es fijo para evitar saltos visuales al mover el ratón
        # ── Header Compacto e Informativo ───────────────────────────────────
        header_container = QWidget()
        header_container.setFixedHeight(110)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        title_block = QVBoxLayout()
        title_block.setSpacing(6)
        title_block.setContentsMargins(0, 0, 0, 0)

        # Fila de Título + Badge de Contador
        title_row = QHBoxLayout()
        title_row.setSpacing(14)
        title_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.games_title_lbl = QLabel("")
        self.games_title_lbl.setStyleSheet("""
            font-size: 32px; font-weight: 900; color: #ffffff;
            letter-spacing: 1px; background: transparent; border: none;
        """)
        title_row.addWidget(self.games_title_lbl)

        self.games_subtitle_lbl = QLabel("")
        self.games_subtitle_lbl.setStyleSheet("""
            background: rgba(77,166,255,0.12); color: #4da6ff;
            font-size: 11px; font-weight: bold;
            border-radius: 10px; padding: 4px 14px;
            border: 1px solid rgba(77,166,255,0.25);
        """)
        self.games_subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_row.addWidget(self.games_subtitle_lbl)
        title_row.addStretch()
        title_block.addLayout(title_row)

        self.games_desc_lbl = QLabel("")
        self.games_desc_lbl.setStyleSheet("""
            font-size: 13px; color: #666677;
            background: transparent; border: none;
        """)
        self.games_desc_lbl.setWordWrap(True)
        self.games_desc_lbl.setMaximumHeight(36)
        title_block.addWidget(self.games_desc_lbl)
        title_block.addStretch()

        header_layout.addLayout(title_block, 1)
        page_games_layout.addWidget(header_container)


        # ── Barra de Búsqueda + Filtro Favoritos ─────────────────────────────────────
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 14)
        search_layout.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translator.t('lib_search'))
        self.search_input.setFixedHeight(40)
        self.search_input.setMinimumWidth(260)
        self.search_input.setMaximumWidth(380)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 0 18px;
                background-color: #0d0f16;
                color: #f0f0f0;
                border: 1px solid #252838;
                border-radius: 20px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #4da6ff;
                background-color: #12151e;
            }
        """)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.filter_games)
        search_layout.addWidget(self.search_input)

        # Favorites filter pill
        self.btn_fav_filter = QPushButton("★  Favoritos")
        self.btn_fav_filter.setCheckable(True)
        self.btn_fav_filter.setFixedHeight(40)
        self.btn_fav_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fav_filter.setStyleSheet("""
            QPushButton {
                padding: 0 18px;
                background: transparent; color: #666688;
                border: 1px solid #2a2d3a; border-radius: 20px;
                font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background: #1a1c28; color: #FFD700; border-color: #FFD700; }
            QPushButton:checked {
                background: rgba(255,215,0,0.12); color: #FFD700;
                border: 1.5px solid #FFD700;
            }
        """)
        self.btn_fav_filter.toggled.connect(self._on_fav_filter_toggled)
        search_layout.addWidget(self.btn_fav_filter)
        search_layout.addStretch()
        page_games_layout.addLayout(search_layout)

        # --- MIDDLE: Grid (left ~65%) + Hero Panel (right ~35%) ---
        self.games_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.games_splitter.setStyleSheet(
            "QSplitter::handle { background: #1a1c28; width: 1px; }"
        )
        self.games_splitter.setHandleWidth(1)

        # Left: scrollable grid of cards
        left_widget = QWidget()
        left_widget.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        self.games_scroll = QScrollArea()
        self.games_scroll.setWidgetResizable(True)
        self.games_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.games_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.games_scroll.setProperty("class", "transparentScrollArea")
        self.games_scroll.setStyleSheet("background: transparent; border: none;")
        self.games_grid_container = QWidget()
        self.games_grid_container.setProperty("class", "transparentBg")
        self.games_grid = QGridLayout(self.games_grid_container)
        self.games_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.games_grid.setSpacing(16)
        self.games_scroll.setWidget(self.games_grid_container)
        left_layout.addWidget(self.games_scroll)

        # Right: hero panel (Hidden by default)
        self.hero_panel = GameHeroPanel(self.translator, self.lanzar_con_info)
        self.hero_panel.setMinimumWidth(270)
        self.hero_panel.setMaximumWidth(420)
        self.hero_panel.hide()

        self.games_splitter.addWidget(left_widget)
        self.games_splitter.addWidget(self.hero_panel)
        self.games_splitter.setStretchFactor(0, 1)
        self.games_splitter.setStretchFactor(1, 0)

        page_games_layout.addWidget(self.games_splitter, 1)


        # ── Barra Inferior con Botones Pill ────────────────────────────────
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        bottom_layout.setContentsMargins(0, 10, 0, 0)

        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        status_layout.setSpacing(4)

        self.games_status_lbl = QLabel("")
        self.games_status_lbl.setStyleSheet(
            "font-size: 11px; color: #555566; background: transparent; border: none;"
        )
        self.games_status_lbl.setFixedWidth(280)

        self.games_progress = QProgressBar()
        self.games_progress.setVisible(False)
        self.games_progress.setFixedHeight(4)
        self.games_progress.setFixedWidth(280)
        self.games_progress.setTextVisible(False)
        self.games_progress.setStyleSheet("""
            QProgressBar { background: #1a1c24; border-radius: 2px; border: none; }
            QProgressBar::chunk { background: #4da6ff; border-radius: 2px; }
        """)

        status_layout.addWidget(self.games_status_lbl)
        status_layout.addWidget(self.games_progress)

        bottom_layout.addLayout(status_layout)
        bottom_layout.addStretch()

        btn_refresh = QPushButton(self.translator.t("lib_refresh").upper())
        btn_refresh.clicked.connect(self.refresh_games)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setFixedHeight(40)
        btn_refresh.setStyleSheet("""
            QPushButton {
                padding: 0 25px;
                background: transparent; color: #4da6ff;
                border: 1px solid #4da6ff; border-radius: 20px;
                font-size: 11px; font-weight: bold; letter-spacing: 1px;
            }
            QPushButton:hover { background: #4da6ff; color: #ffffff; }
        """)

        btn_back = QPushButton(self.translator.t("lib_btn_back").upper())
        btn_back.clicked.connect(self.back_to_consoles)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setFixedHeight(40)
        btn_back.setStyleSheet("""
            QPushButton {
                padding: 0 25px;
                background: transparent; color: #777788;
                border: 1px solid #2a2d3a; border-radius: 20px;
                font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background: #1f2130; color: #ccccdd; border-color: #4a4d5a; }
        """)

        bottom_layout.addWidget(btn_refresh)
        bottom_layout.addSpacing(10)
        bottom_layout.addWidget(btn_back)

        page_games_layout.addLayout(bottom_layout)
        
        self.stack.addWidget(self.page_games)
        layout.addWidget(self.stack)
        
        # Cargar datos iniciales
        self.mostrar_consolas()

    def paintEvent(self, event):
        """Dibuja el fondo de la consola para toda la biblioteca (edge-to-edge)."""
        from PyQt6.QtGui import QPainter
        from PyQt6.QtCore import QRectF, Qt
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect_f = QRectF(self.rect())
        
        # 1. Dibujar Fondo (Usando el mismo sistema de caché que el carrusel)
        # Si el carrusel está animando, él dibuja su propio crossfade encima
        if self.cached_bg:
            self._draw_cached_bg(painter, rect_f, self.cached_bg, self.current_color)
        else:
            # Fallback degradado
            from PyQt6.QtGui import QColor, QLinearGradient
            base_color = QColor(self.current_color)
            gradient = QLinearGradient(rect_f.topLeft(), rect_f.bottomRight())
            gradient.setColorAt(0, base_color.darker(300))
            gradient.setColorAt(1, QColor(15, 17, 22))
            painter.fillRect(rect_f, gradient)
            
        # 2. Capa de degradado cinematográfico (B-Spline)
        self._draw_overlay_gradient(painter, self.rect())

    def _draw_cached_bg(self, painter, rect, pixmap, color):
        if pixmap:
            x = rect.x() + (rect.width() - pixmap.width()) / 2.0
            y = rect.y() + (rect.height() - pixmap.height()) / 2.0
            painter.drawPixmap(int(x), int(y), pixmap)

    def _get_scaled_bg(self, pixmap):
        if not pixmap or pixmap.isNull(): return None
        return pixmap.scaled(self.size(), 
                            Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                            Qt.TransformationMode.SmoothTransformation)
                            
    def _draw_overlay_gradient(self, painter, rect):
        from PyQt6.QtGui import QColor, QLinearGradient
        # Usamos un negro con un ligero matiz frío para el estilo moderno
        c = QColor(10, 11, 14)
        x, y, w, h = float(rect.x()), float(rect.y()), float(rect.width()), float(rect.height())
        grad = QLinearGradient(x, y, x + w, y)
        
        # Zona negra sólida (Color Ramp a 0.3)
        grad.setColorAt(0.0, c)
        grad.setColorAt(0.3, c)
        
        # Simulación de suavizado B-Spline (puntos de transición orgánica desde 0.3 a 1.0)
        grad.setColorAt(0.42, QColor(10, 11, 14, 240))
        grad.setColorAt(0.55, QColor(10, 11, 14, 190))
        grad.setColorAt(0.70, QColor(10, 11, 14, 110))
        grad.setColorAt(0.85, QColor(10, 11, 14, 40))
        grad.setColorAt(1.0, QColor(10, 11, 14, 0))
        
        painter.fillRect(rect, grad)
        
    def mostrar_consolas(self):
        """Carga y rellena el carrusel de consolas instaladas."""
        biblioteca = scanner.cargar_biblioteca_cache()
        counts = {}
        playtimes = {} # Tiempo total por emu_id
        
        for j in biblioteca:
            id_emu = j.get("id_emu")
            counts[id_emu] = counts.get(id_emu, 0) + 1
            
            # Sumar tiempo de juego
            ruta = j.get("ruta")
            if ruta:
                seconds, _, _ = self.emu_manager.get_playtime(ruta)
                playtimes[id_emu] = playtimes.get(id_emu, 0) + seconds
            
        sorted_emus = sorted(AVAILABLE_EMULATORS, key=lambda x: x["console"].lower())
        
        consoles_data = []
        for emu in sorted_emus:
            if self.emu_manager.esta_instalado(emu["github"]):
                consoles_data.append((emu, counts.get(emu["id"], 0), playtimes.get(emu["id"], 0)))
                
        self.carousel.set_data(consoles_data)
        
        # Inicializar fondo de LibraryView con la consola actual del carrusel
        if consoles_data:
            current_emu = consoles_data[self.carousel.current_index][0]
            bg_path = artwork.obtener_ruta_fondo_consola(current_emu["id"])
            self.current_bg_pixmap = QPixmap(bg_path) if os.path.exists(bg_path) else None
            self.current_color = current_emu.get("color", "#4da6ff")
            self.cached_bg = self._get_scaled_bg(self.current_bg_pixmap)

        self.stack.setCurrentIndex(0)
 
    def showEvent(self, event):
        """Refresca los datos solo cuando sea estrictamente necesario."""
        super().showEvent(event)
        if self.isVisible() and self._needs_refresh:
            self._needs_refresh = False
            def defered_load():
                try:
                    if not hasattr(self, 'stack') or self.stack is None:
                        return
                    if self.stack.currentIndex() == 0:
                        self.mostrar_consolas()
                    elif hasattr(self, "current_emu_data"):
                        self.abrir_detalle_consola(self.current_emu_data)
                    self._reflow_games()
                    if hasattr(self, "overlay"):
                        self.overlay.resize(self.size())
                except (RuntimeError, AttributeError):
                    pass
            QTimer.singleShot(10, defered_load)
 
    def resizeEvent(self, event):
        """Re-layout dinámico al redimensionar la ventana."""
        super().resizeEvent(event)
        
        # Re-esclalar fondo persistente para que siempre ocupe toda la pantalla
        if self.current_bg_pixmap:
            self.cached_bg = self._get_scaled_bg(self.current_bg_pixmap)
            
        self._reflow_games()
        if hasattr(self, 'overlay'):
            self.overlay.resize(self.size())

    def _reflow_games(self):
        """Idem para el grid de juegos (ROMs)."""
        if self.stack.currentIndex() == 1 and hasattr(self, 'games_grid') and self.games_grid.count() > 0:
            width = self.games_scroll.viewport().width()
            card_width = 175
            spacing = self.games_grid.spacing()
            cols = max(1, width // (card_width + spacing))
            
            used_width = cols * card_width + (cols - 1) * spacing
            margin = max(0, (width - used_width) // 2)
            self.games_grid.setContentsMargins(margin, 10, margin, 10)
            
            if getattr(self, '_current_game_cols', 0) != cols:
                self._current_game_cols = cols
                widgets = []
                for i in range(self.games_grid.count()):
                    item = self.games_grid.itemAt(i)
                    if item and item.widget(): widgets.append(item.widget())
                
                for w in widgets: self.games_grid.removeWidget(w)
                
                row, col = 0, 0
                for w in widgets:
                    self.games_grid.addWidget(w, row, col)
                    col += 1
                    if col >= cols: col, row = 0, row + 1
        
    def back_to_consoles(self):
        """Regresa a la página de consolas."""
        self.stack.setCurrentIndex(0)
        self.current_emu = None
        # Al volver atrás, el fondo debe ser el de la consola actual del carrusel
        self.carousel.update_ui()

    def retranslate_ui(self):
        """Actualiza todos los textos de la vista biblioteca al cambiar el idioma."""
        self.search_input.setPlaceholderText(self.translator.t('lib_search'))
        # Actualizar carrusel
        self.carousel.update_ui()
        # Reforzar carga si estamos en la vista de consolas o juegos
        if self.stack.currentIndex() == 0:
            self.mostrar_consolas()
        elif self.current_emu:
            self.abrir_detalle_consola(self.current_emu)
        self._current_console_cols = -1

    def abrir_detalle_consola(self, emu):
        """Muestra los ROMs filtrados para una consola específica."""
        self.current_emu_data = emu
        
        console_key = f"emu_{emu['id']}_console"
        self.games_title_lbl.setText(self.translator.t(console_key).upper())
        self.games_subtitle_lbl.setText(emu["name"])
        
        # Calcular tiempo total de esta consola para el header
        biblioteca = scanner.cargar_biblioteca_cache()
        console_games = [j for j in biblioteca if j.get("id_emu") == emu["id"]]
        total_seconds = 0
        for g in console_games:
            s, _, _ = self.emu_manager.get_playtime(g.get("ruta"))
            total_seconds += s
            
            
        h = int(total_seconds // 3600)
        m = int((total_seconds % 3600) // 60)
        time_str = f" | {self.translator.t('lib_total_time', self.translator.t('lib_played_hours', h, m))}" if h > 0 or m > 0 else ""
        
        desc_key = f"emu_{emu['id']}_desc"
        self.games_desc_lbl.setText(f"{self.translator.t(desc_key)}{time_str}")
        
        biblioteca = scanner.cargar_biblioteca_cache()
        self.current_games_all = [j for j in biblioteca if j.get("id_emu") == emu["id"]]
        self.current_games_all.sort(key=lambda x: x.get("nombre", "").lower())
        
        # Limpiar juegos anteriores inmediatamente para evitar "efecto fantasma"
        while self.games_grid.count():
            item = self.games_grid.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()

        # Reset pinned game and hero panel on console change
        self._pinned_game = None
        if hasattr(self, 'hero_panel'):
            self.hero_panel.set_game(None)

        self.search_input.setText("")
        self.stack.setCurrentIndex(1)
        self._current_game_cols = -1
        
        # Actualizar fondo global para que coincida con esta consola
        bg_path = artwork.obtener_ruta_fondo_consola(emu["id"])
        self.current_bg_pixmap = QPixmap(bg_path) if os.path.exists(bg_path) else None
        self.current_color = emu.get("color", "#4da6ff")
        self.cached_bg = self._get_scaled_bg(self.current_bg_pixmap)
        self.update()

        # Loading Effect
        self.overlay.show_loading(self.translator.t("lib_status_processing"))
        
        # Procesar en el siguiente event loop para NO BLOQUEAR el cambio de pantalla del Stack
        # y que el overlay pueda dibujarse.
        QApplication.processEvents() # Forzar dibujado de UI antes de la carga
        QTimer.singleShot(100, lambda: self._actualizar_rejilla_juegos(self.current_games_all))
        
    def _actualizar_rejilla_juegos(self, juegos):
        """Dibuja las tarjetas de los juegos en el area de contenido."""
        while self.games_grid.count():
            item = self.games_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Reset hero panel
        if hasattr(self, 'hero_panel'):
            self.hero_panel.set_game(None)

        if not juegos:
            no_games_lbl = QLabel(self.translator.t("lib_no_games"))
            no_games_lbl.setProperty("class", "libraryNoGamesText")
            self.games_grid.addWidget(no_games_lbl, 0, 0)
            if self.overlay.isVisible():
                QTimer.singleShot(250, self.overlay.hide_loading)
            return

        # Get accent color from current console
        accent = "#4da6ff"
        if hasattr(self, "current_emu_data"):
            accent = self.current_emu_data.get("color", "#4da6ff")

        for game in juegos:
            card = GameCard(game, self.translator, self.lanzar_con_info,
                            self._on_game_hover, accent_color=accent)
            try:
                _, h, m = self.emu_manager.get_playtime(game.get("ruta", ""))
                card.set_playtime(h, m)
            except Exception:
                pass
            self.games_grid.addWidget(card, 0, 0)

        self._current_game_cols = -1
        QTimer.singleShot(0, self._reflow_games)

        if self.overlay.isVisible():
            QTimer.singleShot(250, self.overlay.hide_loading)

    def _on_game_hover(self, game, pinned=False):
        """Actualiza el Hero Panel.
        pinned=True: se fija el juego seleccionado (clic), no se limpia al salir.
        pinned=False: hover simple, actualiza sin fijar.
        """
        if pinned:
            self._pinned_game = game
        self.current_hovered_game = game or self._pinned_game

        display_game = self.current_hovered_game

        # Update hero panel (siempre muestra algo si hay pinned)
        if hasattr(self, 'hero_panel'):
            if display_game:
                self.hero_panel.show()
                self.hero_panel.set_game(display_game)
                try:
                    _, h, m = self.emu_manager.get_playtime(display_game.get("ruta", ""))
                    self.hero_panel.set_playtime(h, m)
                except Exception:
                    self.hero_panel.set_playtime(0, 0)
            elif not self._pinned_game:
                # No hay hover ni pinned -> ocultar
                self.hero_panel.hide()

        # Update header label
        if display_game:
            self.games_title_lbl.setText(display_game["nombre"])
        else:
            if hasattr(self, "current_emu_data"):
                emu = self.current_emu_data
                console_key = f"emu_{emu['id']}_console"
                self.games_title_lbl.setText(self.translator.t(console_key))
                
                
    def filter_games(self, text=None):
        """Buscador instantaneo por nombre con soporte de filtro favoritos."""
        query = (text or self.search_input.text()).lower().strip()
        only_favs = hasattr(self, 'btn_fav_filter') and self.btn_fav_filter.isChecked()
        all_games = getattr(self, "current_games_all", [])
        filtered = [j for j in all_games
                    if query in j["nombre"].lower()
                    and (not only_favs or scanner.es_favorito(j.get("ruta", "")))]
        self._actualizar_rejilla_juegos(filtered)

    def _on_fav_filter_toggled(self, checked):
        """Activa/desactiva el filtro de favoritos."""
        self.filter_games()
        
    def lanzar_con_info(self, game):
        """Ejecuta el lanzamiento del ROM verificando antes si hay uno abierto."""
        if self.emu_manager.is_emulator_running():
            actual = self.emu_manager.launcher.current_game
            nombre_actual = actual.get("nombre", "Un juego") if actual else "Un juego"
            consola_actual = actual.get("consola", "el emulador") if actual else "el emulador"
            
            # Crear un cuadro de diálogo con MessageBox
            # Usa el tema oscuro global gracias al qss que aplicamos
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.translator.t("lib_change_game_title"))
            msg_box.setText(self.translator.t("lib_change_game_msg", nombre_actual, consola_actual, game['nombre']))
            msg_box.setIcon(QMessageBox.Icon.Warning)
            
            btn_yes = msg_box.addButton(self.translator.t("lib_yes_change"), QMessageBox.ButtonRole.YesRole)
            btn_no = msg_box.addButton(self.translator.t("lib_keep_current"), QMessageBox.ButtonRole.NoRole)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == btn_yes:
                self.emu_manager.terminar_proceso_actual()
                asyncio.get_event_loop().create_task(self._ejecutar_lanzamiento(game))
        else:
            asyncio.get_event_loop().create_task(self._ejecutar_lanzamiento(game))
        
    async def _ejecutar_lanzamiento(self, game):
        repo = next((emu["github"] for emu in AVAILABLE_EMULATORS if emu["id"] == game["id_emu"]), None)
        success, msg = await self.emu_manager.lanzar_juego(repo, game["ruta"], juego_obj=game)
        print(f"Lanzamiento: {msg}")
        
    @asyncSlot()
    async def refresh_games(self):
        """Escaneo completo de la carpeta de ROMs (solo búsqueda de archivos)."""
        if not self.emu_manager.roms_path: return
            
        id_filtro = self.current_emu_data["id"] if hasattr(self, "current_emu_data") else None
        
        self.games_status_lbl.setText(self.translator.t("lib_status_scanning"))
        self.games_progress.setVisible(True)
        self.games_progress.setRange(0, 0) # Efecto indeterminante (buscando)
        
        self.overlay.show_loading(self.translator.t("lib_status_scanning"))
        
        # Realizar el escaneo físico de archivos
        await scanner.escanear_roms(self.emu_manager.roms_path, emu_id=id_filtro)
        
        self.games_status_lbl.setText(self.translator.t("lib_status_complete"))
        self.games_progress.setVisible(False)
        self.overlay.hide_loading()
        QTimer.singleShot(2000, lambda: self.games_status_lbl.setText(""))
        
        # Refrescar la vista actual (consolas o juegos)
        self._needs_refresh = True  # Forzar recarga tras escanear
        if self.stack.currentIndex() == 0:
            self.mostrar_consolas()
        else:
            self.abrir_detalle_consola(self.current_emu_data)
