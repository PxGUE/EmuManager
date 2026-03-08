"""
library.py — Vista de la Biblioteca (Consolas y Juegos)
Gestiona el escaneo de consolas, descarga de carátulas y visualización en rejilla (Grid).
"""

import asyncio
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QGridLayout, QStackedWidget,
    QLineEdit, QSizePolicy, QProgressBar, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer, QVariantAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QMessageBox
from qasync import asyncSlot
import core.scanner as scanner
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork
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
    """Tarjeta visual de Juego (ROM) con su carátula."""
    def __init__(self, game, translator, on_launch_callback, on_hover_callback=None, parent=None):
        super().__init__(parent)
        self.game = game
        self.translator = translator
        self.on_launch_callback = on_launch_callback
        self.on_hover_callback = on_hover_callback
        self.init_ui()
        
    def init_ui(self):
        """Diseño de la carátula rectangular de juego."""
        self.setObjectName("gameCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame#gameCard {
                background-color: #1a1c24;
                border-radius: 8px;
            }
            QFrame#gameCard:hover {
                border: 2px solid #4da6ff;
                background-color: #202430;
            }
        """)
        self.setFixedSize(150, 210)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # --- CARÁTULA (Imagen de Boxart) ---
        self.img_lbl = QLabel()
        self.img_lbl.setScaledContents(True)
        self.img_lbl.setFixedSize(140, 160)
        
        ruta_rom = self.game.get("ruta", "")
        caratula_path = artwork.obtener_ruta_caratula(ruta_rom) if ruta_rom else None
        self.set_artwork(caratula_path)
        
        layout.addWidget(self.img_lbl)
        
        # --- TÍTULO DEL JUEGO ---
        name_lbl = QLabel(self.game["nombre"])
        name_lbl.setProperty("class", "gameCardTitle")
        name_lbl.setWordWrap(True)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_lbl)
        
    def set_artwork(self, img_path):
        success = False
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(140, 160, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.img_lbl.setPixmap(pixmap)
                self.img_lbl.setText("")
                self.img_lbl.setStyleSheet("")
                success = True
        
        if not success:
            self.img_lbl.setText("🎮")
            self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.img_lbl.setProperty("class", "gameCardPlaceholder")
            self.img_lbl.setFixedHeight(160)

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_launch_callback(self.game)

    def enterEvent(self, event):
        if self.on_hover_callback:
            self.on_hover_callback(self.game)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.on_hover_callback:
            self.on_hover_callback(None)
        super().leaveEvent(event)


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
        header_container = QWidget()
        header_container.setFixedHeight(180) # Altura fija de seguridad
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Textos informativos de cabecera
        self.games_title_lbl = QLabel("")
        self.games_title_lbl.setProperty("class", "pageTitle")
        self.games_title_lbl.setFixedHeight(35)
        
        self.games_subtitle_lbl = QLabel("")
        self.games_subtitle_lbl.setProperty("class", "libraryGamesSubtitle")
        self.games_subtitle_lbl.setFixedHeight(20)
        
        self.games_desc_lbl = QLabel("")
        self.games_desc_lbl.setProperty("class", "libraryGamesDesc")
        self.games_desc_lbl.setWordWrap(True)
        self.games_desc_lbl.setFixedHeight(60)
        
        header_layout.addWidget(self.games_title_lbl)
        header_layout.addWidget(self.games_subtitle_lbl)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.games_desc_lbl)
        header_layout.addSpacing(15)
        
        header_layout.addStretch() # Mantener textos arriba
        
        page_games_layout.addWidget(header_container)
        
        # SECCIÓN SEARCH (Buscador dinámico)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 10, 0, 15)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(f"🔍 {self.translator.t('lib_search').upper()}")
        self.search_input.setFixedWidth(400)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 18px;
                background-color: #0c0d12;
                color: white;
                border: 2px solid #4da6ff;
                border-radius: 22px;
                font-size: 14px;
                selection-background-color: #4da6ff;
            }
            QLineEdit:hover {
                border: 2px solid #7abfff;
                background-color: #15171e;
            }
            QLineEdit:focus {
                border: 2px solid #7abfff;
                background-color: #15171e;
            }
        """)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.filter_games)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch() # Mantener a la izquierda
        page_games_layout.addLayout(search_layout)
        
        # --- MIDDLE: Grid de ROMs ---
        middle_layout = QVBoxLayout()
        self.games_scroll = QScrollArea()
        self.games_scroll.setWidgetResizable(True)
        self.games_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.games_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.games_scroll.setProperty("class", "transparentScrollArea")
        
        self.games_grid_container = QWidget()
        self.games_grid_container.setProperty("class", "transparentBg")
        self.games_grid = QGridLayout(self.games_grid_container)
        self.games_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.games_grid.setSpacing(20)
        
        self.games_scroll.setWidget(self.games_grid_container)
        middle_layout.addWidget(self.games_scroll)
        page_games_layout.addLayout(middle_layout)
        
        # --- BOTTOM: Barra de progreso y Botones ---
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Área de Estado vertical [Texto informativo / Barra]
        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        status_layout.setSpacing(2)
        
        self.games_status_lbl = QLabel("")
        self.games_status_lbl.setProperty("class", "libraryGamesStatus")
        self.games_status_lbl.setFixedWidth(250)
        
        self.games_progress = QProgressBar()
        self.games_progress.setVisible(False)
        self.games_progress.setFixedHeight(8)
        self.games_progress.setFixedWidth(250)
        self.games_progress.setTextVisible(False)
        
        status_layout.addWidget(self.games_status_lbl)
        status_layout.addWidget(self.games_progress)
        
        bottom_layout.addLayout(status_layout)
        bottom_layout.addStretch() # Dejar los botones a la derecha
        
        btn_refresh = QPushButton(self.translator.t("lib_refresh").upper())
        btn_refresh.clicked.connect(self.refresh_games)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                padding: 10px 20px; background-color: #1a1c24; color: #4da6ff; border: 1px solid #4da6ff;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #4da6ff; color: white; }
        """)
        
        # Botón Atrás
        btn_back = QPushButton(self.translator.t("lib_btn_back").upper())
        btn_back.clicked.connect(self.back_to_consoles)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                padding: 10px 20px; background-color: transparent; color: #a0a0a0; border: 1px solid #555555;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #333333; color: white; }
        """)
        
        bottom_layout.addWidget(btn_refresh)
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
            card_width = 150
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
        # self.consoles_scroll ya no existe al usar el Carousel
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
        """Dibuja las tarjetas de los juegos en el área de contenido."""
        while self.games_grid.count():
            item = self.games_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        if not juegos:
            no_games_lbl = QLabel(self.translator.t("lib_no_games"))
            no_games_lbl.setProperty("class", "libraryNoGamesText")
            self.games_grid.addWidget(no_games_lbl, 0, 0)
            if self.overlay.isVisible():
                QTimer.singleShot(250, self.overlay.hide_loading)
            return

        for game in juegos:
            card = GameCard(game, self.translator, self.lanzar_con_info, self._on_game_hover)
            self.games_grid.addWidget(card, 0, 0)
            
        self._current_game_cols = -1
        QTimer.singleShot(0, self._reflow_games)
        
        if self.overlay.isVisible():
             QTimer.singleShot(250, self.overlay.hide_loading)

    def _on_game_hover(self, game):
        """Actualiza el Header con info del juego cuando el ratón pasa por encima."""
        self.current_hovered_game = game
        if game:
            self.games_title_lbl.setText(game["nombre"])
            self.games_subtitle_lbl.setText(self.translator.t("lib_game_details"))
            _, h, m = self.emu_manager.get_playtime(game["ruta"])
            playtime_str = self.translator.t('lib_played_hours', h, m) if h > 0 or m > 0 else self.translator.t("lib_never_played")
            self.games_desc_lbl.setText(self.translator.t("lib_playtime", playtime_str))
        else:
            if hasattr(self, "current_emu_data"):
                emu = self.current_emu_data
                console_key = f"emu_{emu['id']}_console"
                self.games_title_lbl.setText(self.translator.t(console_key))
                self.games_subtitle_lbl.setText(emu["name"])
                desc_key = f"emu_{emu['id']}_desc"
                self.games_desc_lbl.setText(self.translator.t(desc_key))
                
    def lanzar_hovered_game(self):
        """Lanza el juego que está actualmente bajo el mouse."""
        if hasattr(self, "current_hovered_game") and self.current_hovered_game:
            self.lanzar_con_info(self.current_hovered_game)
                
    def filter_games(self, text):
        """Buscador instantáneo por nombre."""
        query = text.lower().strip()
        filtered = [j for j in getattr(self, "current_games_all", []) if query in j["nombre"].lower()]
        self._actualizar_rejilla_juegos(filtered)
        
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
