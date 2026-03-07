"""
library.py — Vista de la Biblioteca (Consolas y Juegos)
Gestiona el escaneo de consolas, descarga de carátulas y visualización en rejilla (Grid).
"""

import asyncio
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QGridLayout, QStackedWidget,
    QLineEdit, QSizePolicy, QProgressBar
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from qasync import asyncSlot
import core.scanner as scanner
from core.constants import AVAILABLE_EMULATORS
import core.artwork as artwork

class ConsoleCard(QFrame):
    """Tarjeta visual de Consola (mGBA, Dolphin, etc.)"""
    def __init__(self, emu, count, playtime, translator, on_click_callback, parent=None):
        super().__init__(parent)
        self.emu = emu
        self.count = count # Número de juegos encontrados
        self.playtime = playtime # Tiempo total en segundos
        self.translator = translator
        self.on_click_callback = on_click_callback
        
        self.init_ui()
        
    def init_ui(self):
        """Dibuja el diseño de la tarjeta de consola."""
        brand_color = self.emu.get("color", "#4da6ff")
        self.setObjectName("consoleCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame#consoleCard {{
                background-color: #1a1c24;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #2a2d3a;
            }}
            QFrame#consoleCard:hover {{
                background-color: #242835;
                border: 2px solid {brand_color};
            }}
        """)
        # Configurar límites de tamaño para que se vea cuadrada/rectangular compacta
        self.setMinimumWidth(320)
        self.setMaximumWidth(450)
        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        
        # --- LOGO DE LA CONSOLA ---
        # Priorizar logo de consolas para biblioteca
        logo_path = os.path.join(artwork.CONSOLES_DIR, f"{self.emu['id']}.png")
        if not os.path.exists(logo_path):
             logo_path = artwork.obtener_ruta_logo_emulador(self.emu["id"])
        
        icon_lbl = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(85, 85, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_lbl.setPixmap(pixmap)
        else:
            icon_lbl.setText("🎮")
            icon_lbl.setStyleSheet("font-size: 50px; color: #444;")
            
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedWidth(85)
        # Quitar el fondo del icono para que flote sobre la tarjeta
        icon_lbl.setStyleSheet("background-color: transparent;")
        
        # --- TEXTOS (Título y Cantidad) ---
        titles_layout = QVBoxLayout()
        titles_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        titles_layout.setSpacing(4)
        
        # Nombre de la consola transladado
        console_key = f"emu_{self.emu['id']}_console"
        console_lbl = QLabel(self.translator.t(console_key))
        console_lbl.setStyleSheet("font-weight: bold; font-size: 22px; color: white;")
        
        # Nombre del emulador asignado (con el color de la marca)
        emu_lbl = QLabel(self.emu["name"])
        emu_lbl.setStyleSheet(f"color: {brand_color}; font-size: 14px; font-weight: bold; text-transform: uppercase;")
        
        # Conteo de juegos y Tiempo jugado
        info_layout = QHBoxLayout()
        info_layout.setSpacing(15)
        
        count_lbl = QLabel(self.translator.t("lib_games_count", self.count).upper())
        count_lbl.setStyleSheet("color: #888888; font-size: 11px; font-weight: bold;")
        
        # Formatear tiempo total
        h = int(self.playtime // 3600)
        m = int((self.playtime % 3600) // 60)
        time_str = f"⏱ {self.translator.t('lib_played_hours', h, m)}" if h > 0 or m > 0 else ""
        
        time_lbl = QLabel(time_str)
        time_lbl.setStyleSheet(f"color: {brand_color}; font-size: 11px; font-weight: bold;")
        
        info_layout.addWidget(count_lbl)
        info_layout.addWidget(time_lbl)
        info_layout.addStretch()
        
        titles_layout.addWidget(console_lbl)
        titles_layout.addWidget(emu_lbl)
        titles_layout.addLayout(info_layout)
        
        main_layout.addWidget(icon_lbl)
        main_layout.addLayout(titles_layout)
        
    def mousePressEvent(self, event):
        """Inicia el efecto de click visual."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setProperty("pressed", True)
            self.style().unpolish(self)
            self.style().polish(self)
            
    def mouseReleaseEvent(self, event):
        """Lanza la acción de abrir el emulador al soltar el click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setProperty("pressed", False)
            self.style().unpolish(self)
            self.style().polish(self)
            self.on_click_callback(self.emu)

class GameCard(QFrame):
    """Tarjeta visual de Juego (ROM) con su carátula."""
    def __init__(self, game, translator, on_launch_callback, on_hover_callback=None, parent=None):
        super().__init__(parent)
        self.game = game # Datos del ROM (ruta, nombre, id_emu)
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
        
        # Buscar el archivo de imagen en la carpeta media local del ROM
        ruta_rom = self.game.get("ruta", "")
        caratula_path = artwork.obtener_ruta_caratula(ruta_rom) if ruta_rom else None
        self.set_artwork(caratula_path)
        
        layout.addWidget(self.img_lbl)
        
        # --- TÍTULO DEL JUEGO ---
        name_lbl = QLabel(self.game["nombre"])
        name_lbl.setStyleSheet("color: white; font-size: 11px; padding: 5px;")
        name_lbl.setWordWrap(True)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_lbl)
        
    def set_artwork(self, img_path):
        """
        Carga la imagen de disco hacia la etiqueta visual.
        Previene errores de memoria si la imagen está corrupta.
        """
        success = False
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            # Verificar que PyQt pudo interpretar los bytes (Metadatos CRC)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(140, 160, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.img_lbl.setPixmap(pixmap)
                self.img_lbl.setText("")
                self.img_lbl.setStyleSheet("")
                success = True
        
        # Si no hay imagen o está dañada: Ponemos el emoji de mando como Placeholder
        if not success:
            self.img_lbl.setText("🎮")
            self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.img_lbl.setStyleSheet("font-size: 40px; background-color: #2a2c34;")
            self.img_lbl.setFixedHeight(160)

    def mousePressEvent(self, event):
        """Efecto visual de hundido al pulsar."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setProperty("pressed", True)
            self.style().unpolish(self)
            self.style().polish(self)
            
    def mouseReleaseEvent(self, event):
        """Lanza el juego a través del emulador seleccionado."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setProperty("pressed", False)
            self.style().unpolish(self)
            self.style().polish(self)
            self.on_launch_callback(self.game)

    def enterEvent(self, event):
        """Notifica para actualizar el Header dinámico con info del juego."""
        if self.on_hover_callback:
            self.on_hover_callback(self.game)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Restablece al Header original con info del emulador."""
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
        
        self.init_ui()
        
    def init_ui(self):
        """Construye las dos páginas de la Biblioteca (Lista de Consolas y Detalle de ROMs)."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # El QStackedWidget nos permite intercambiar entre Consolas <-> Juegos
        self.stack = QStackedWidget()
        
        # --- PÁGINA 1: LISTA DE CONSOLAS ---
        self.page_consoles = QWidget()
        self.page_consoles.setStyleSheet("background-color: transparent;")
        pc_layout = QVBoxLayout(self.page_consoles)
        pc_layout.setContentsMargins(30, 30, 30, 30)
        
        # Título decorativo
        lbl_c_title = QLabel(self.translator.t("nav_library").upper())
        lbl_c_title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        pc_layout.addWidget(lbl_c_title)
        pc_layout.addSpacing(20)
        
        # Grid scrolleable de Consolas
        self.consoles_scroll = QScrollArea()
        self.consoles_scroll.setWidgetResizable(True)
        self.consoles_scroll.setFrameShape(QFrame.Shape.NoFrame)
        # Deshabilitar scroll horizontal para diseño Grid móvil/aséptico
        self.consoles_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.consoles_grid_container = QWidget()
        self.consoles_grid = QGridLayout(self.consoles_grid_container)
        self.consoles_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.consoles_grid.setSpacing(25)
        
        self.consoles_scroll.setWidget(self.consoles_grid_container)
        pc_layout.addWidget(self.consoles_scroll)
        
        self.stack.addWidget(self.page_consoles)
        
        # --- PÁGINA 2: LISTA DE JUEGOS ---
        self.page_games = QWidget()
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
        self.games_title_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        self.games_title_lbl.setFixedHeight(35)
        
        self.games_subtitle_lbl = QLabel("")
        self.games_subtitle_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #4da6ff;")
        self.games_subtitle_lbl.setFixedHeight(20)
        
        self.games_desc_lbl = QLabel("")
        self.games_desc_lbl.setStyleSheet("color: #a0a0a0; font-size: 14px;")
        self.games_desc_lbl.setWordWrap(True)
        self.games_desc_lbl.setFixedHeight(60)
        
        header_layout.addWidget(self.games_title_lbl)
        header_layout.addWidget(self.games_subtitle_lbl)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.games_desc_lbl)
        header_layout.addStretch() # Mantener textos arriba
        
        page_games_layout.addWidget(header_container)
        
        # SECCIÓN SEARCH (Buscador dinámico)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 10, 0, 15)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translator.t("lib_search").upper())
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px; background-color: #1a1c24; color: white;
                border: 1px solid #333; border-radius: 8px; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #4da6ff; }
        """)
        self.search_input.textChanged.connect(self.filter_games)
        search_layout.addWidget(self.search_input)
        page_games_layout.addLayout(search_layout)
        
        # --- MIDDLE: Grid de ROMs ---
        middle_layout = QVBoxLayout()
        self.games_scroll = QScrollArea()
        self.games_scroll.setWidgetResizable(True)
        self.games_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.games_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.games_grid_container = QWidget()
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
        self.games_status_lbl.setStyleSheet("color: #a0a0a0; font-size: 13px; font-weight: bold;")
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
        
        # Botón Refrescar (Escaneo y Carátulas)
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
        
        # Caragar datos iniciales
        self.mostrar_consolas()
        
    def mostrar_consolas(self):
        """Carga y rellena el grid de consolas instaladas."""
        while self.consoles_grid.count():
            item = self.consoles_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
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
        
        for emu in sorted_emus:
            if self.emu_manager.esta_instalado(emu["github"]):
                card = ConsoleCard(
                    emu, 
                    counts.get(emu["id"], 0), 
                    playtimes.get(emu["id"], 0),
                    self.translator, 
                    self.abrir_detalle_consola
                )
                self.consoles_grid.addWidget(card, 0, 0) # Relleno inicial para el Reflow
                
        self.stack.setCurrentIndex(0)
        self._current_console_cols = -1
        # El QTimer permite que el layout de Qt se asiente antes de calcular columnas
        QTimer.singleShot(0, self._reflow_consoles)
 
    def showEvent(self, event):
        """Refresca los datos e iconos cada vez la vista se vuelve visible."""
        super().showEvent(event)
        if self.stack.currentIndex() == 0:
            self.mostrar_consolas()
        elif hasattr(self, "current_emu_data"):
             self.abrir_detalle_consola(self.current_emu_data)
             
        QTimer.singleShot(0, self._reflow_consoles)
        QTimer.singleShot(0, self._reflow_games)
 
    def resizeEvent(self, event):
        """Re-layout dinámico al redimensionar la ventana."""
        super().resizeEvent(event)
        self._reflow_consoles()
        self._reflow_games()
        
    def _reflow_consoles(self):
        """Recalcula las columnas de las consolas y las centra."""
        if self.stack.currentIndex() == 0 and hasattr(self, 'consoles_grid') and self.consoles_grid.count() > 0:
            width = self.consoles_scroll.viewport().width()
            card_width = 350 # Ancho base de cálculo
            spacing = self.consoles_grid.spacing()
            cols = max(1, width // (card_width + spacing))
            
            # Cálculo de margen izquierdo de centrado
            used_width = (cols * card_width) + ((cols - 1) * spacing)
            margin = max(0, (width - used_width) // 2)
            self.consoles_grid.setContentsMargins(margin, 0, 0, 0)
            
            # Solo mover widgets si el número de columnas cambió
            if getattr(self, '_current_console_cols', 0) != cols:
                self._current_console_cols = cols
                widgets = []
                for i in range(self.consoles_grid.count()):
                    item = self.consoles_grid.itemAt(i)
                    if item and item.widget(): widgets.append(item.widget())
                
                for w in widgets: self.consoles_grid.removeWidget(w)
                
                row, col = 0, 0
                for w in widgets:
                    self.consoles_grid.addWidget(w, row, col)
                    col += 1
                    if col >= cols: col, row = 0, row + 1

    def _reflow_games(self):
        """Idem para el grid de juegos (ROMs)."""
        if self.stack.currentIndex() == 1 and hasattr(self, 'games_grid') and self.games_grid.count() > 0:
            width = self.games_scroll.viewport().width()
            card_width = 150
            spacing = self.games_grid.spacing()
            cols = max(1, width // (card_width + spacing))
            
            used_width = cols * card_width + (cols - 1) * spacing
            margin = max(0, (width - used_width) // 2)
            self.games_grid.setContentsMargins(margin, 0, 0, 0)
            
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
        self.consoles_scroll.verticalScrollBar().setValue(0)
        self._current_console_cols = -1
        QTimer.singleShot(50, self._reflow_consoles)

    def abrir_detalle_consola(self, emu):
        """Muestra los ROMs filtrados para una consola específica."""
        self.current_emu_data = emu
        self.games_title_lbl.setText(emu["console"])
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
        
        self.search_input.setText("")
        self.stack.setCurrentIndex(1)
        self._current_game_cols = -1
        self._actualizar_rejilla_juegos(self.current_games_all)
        
    def _actualizar_rejilla_juegos(self, juegos):
        """Dibuja las tarjetas de los juegos en el área de contenido."""
        while self.games_grid.count():
            item = self.games_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        if not juegos:
            no_games_lbl = QLabel(self.translator.t("lib_no_games"))
            no_games_lbl.setStyleSheet("color: #888888; font-size: 16px;")
            self.games_grid.addWidget(no_games_lbl, 0, 0)
            return

        for game in juegos:
            card = GameCard(game, self.translator, self.lanzar_con_info, self._on_game_hover)
            self.games_grid.addWidget(card, 0, 0)
            
        self._current_game_cols = -1
        QTimer.singleShot(0, self._reflow_games)

    def _on_game_hover(self, game):
        """Actualiza el Header con info del juego cuando el ratón pasa por encima."""
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
                
    def filter_games(self, text):
        """Buscador instantáneo por nombre."""
        query = text.lower().strip()
        filtered = [j for j in getattr(self, "current_games_all", []) if query in j["nombre"].lower()]
        self._actualizar_rejilla_juegos(filtered)
        
    def lanzar_con_info(self, game):
        """Ejecuta el lanzamiento del ROM en un hilo asíncrono."""
        asyncio.get_event_loop().create_task(self._ejecutar_lanzamiento(game))
        
    async def _ejecutar_lanzamiento(self, game):
        repo = next((emu["github"] for emu in AVAILABLE_EMULATORS if emu["id"] == game["id_emu"]), None)
        success, msg = await self.emu_manager.lanzar_juego(repo, game["ruta"], juego_obj=game)
        print(f"Lanzamiento: {msg}")
        
    @asyncSlot()
    async def refresh_games(self):
        """Escaneo completo de la carpeta de ROMs y descarga de carátulas nuevas."""
        if not self.emu_manager.roms_path: return
            
        id_filtro = self.current_emu_data["id"] if hasattr(self, "current_emu_data") else None
        
        self.games_status_lbl.setText(self.translator.t("lib_status_scanning"))
        self.games_progress.setVisible(True)
        self.games_progress.setRange(0, 0) # Efecto indeterminante (buscando)
        
        juegos = await scanner.escanear_roms(self.emu_manager.roms_path, emu_id=id_filtro)
        
        if not juegos:
            self.games_status_lbl.setText("")
            self.games_progress.setVisible(False)
            self.abrir_detalle_consola(self.current_emu_data)
            return
            
        j_dict = [j if isinstance(j, dict) else j.__dict__ for j in juegos]
        j_proc = [j for j in j_dict if j.get("id_emu") == id_filtro] if id_filtro else j_dict
        
        self.games_status_lbl.setText(self.translator.t("lib_status_artwork"))
        self.games_progress.setRange(0, len(j_proc))
        
        def on_progress(actual, total, nombre):
            self.games_progress.setValue(actual)
            self.games_status_lbl.setText(self.translator.t("lib_status_downloading", nombre) if nombre else self.translator.t("lib_status_processing"))
            
        await artwork.descargar_caratulas_biblioteca(
            j_proc, self.emu_platform_map, self.emu_manager.roms_path, on_progress
        )
        
        self.games_status_lbl.setText(self.translator.t("lib_status_complete"))
        self.games_progress.setVisible(False)
        QTimer.singleShot(3000, lambda: self.games_status_lbl.setText(""))
        self.abrir_detalle_consola(self.current_emu_data)
