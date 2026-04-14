from PySide6.QtCore import QObject, Slot, Signal
from core.config import AppConfig
from core.logger import EmuLog
import platform as py_platform
import os


class StatsController(QObject):
    """
    Controlador especializado en métricas, estadísticas y sumarios técnicos.
    """
    gamesUpdated = Signal()
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._cached_summary = None

    @Slot(result="QVariantMap")
    def get_dashboard_stats(self):
        """Retorna estadísticas avanzadas del Dashboard vía M.A.N.G.O (Rust)."""
        try:
            import mango_engine
            db_path = str(AppConfig.get_database_path())
            stats = mango_engine.fetch_dashboard_stats(db_path)
            if not stats: return {}
            
            # Mapear nombres directamente de SQL (Optimización Batch para evitar N+1)
            # Recopilar todos los IDs necesarios
            ids_to_fetch = set()
            last_game = stats.get("last_game")
            if last_game and last_game.get("id"):
                ids_to_fetch.add(last_game["id"])

            recent_games = stats.get("recent_games", [])
            for g in recent_games:
                if g.get("id"):
                    ids_to_fetch.add(g["id"])

            if ids_to_fetch:
                # Consulta única para todos los títulos vía DatabaseManager
                name_map = self.db.get_game_titles_map(list(ids_to_fetch))

                # Asignar títulos de vuelta al objeto stats
                if last_game and last_game.get("id") in name_map:
                    last_game["title"] = name_map[last_game["id"]]

                for g in recent_games:
                    gid = g.get("id")
                    if gid in name_map:
                        g["title"] = name_map[gid]
            
            EmuLog.debug(f"M.A.N.G.O (Stats): Dashboard recuperado. Total juegos: {stats.get('total_games', 0)}")
            return stats
        except Exception as e:
            EmuLog.error(f"Error cargando stats del dashboard nativo: {e}")
            return {}

    @Slot(result="QVariantList")
    @Slot(bool, result="QVariantList")
    def get_consoles_summary(self, use_cache=True):
        """Resumen dinámico de juegos por plataforma."""
        if use_cache and self._cached_summary:
            return self._cached_summary

        base_platforms = {
            "snes": {"title": "SNES", "fullName": "Super Nintendo", "icon": "🕹️", "color": "platSnes"},
            "nes": {"title": "NES", "fullName": "Nintendo Entertainment System", "icon": "📺", "color": "platNes"},
            "gb": {"title": "GB", "fullName": "Game Boy", "icon": "📟", "color": "platGb"},
            "gbc": {"title": "GBC", "fullName": "Game Boy Color", "icon": "🌈", "color": "platGbc"},
            "gba": {"title": "GBA", "fullName": "Game Boy Advance", "icon": "📱", "color": "platGba"},
            "n64": {"title": "N64", "fullName": "Nintendo 64", "icon": "🏰", "color": "platN64"},
            "ps1": {"title": "PS1", "fullName": "PlayStation 1", "icon": "💿", "color": "platPs1"},
            "ps2": {"title": "PS2", "fullName": "PlayStation 2", "icon": "🚀", "color": "platPs2"},
            "psp": {"title": "PSP", "fullName": "PlayStation Portable", "icon": "🔋", "color": "platPsp"},
            "ds": {"title": "DS", "fullName": "Nintendo DS", "icon": "📖", "color": "platDs"},
            "gc": {"title": "GAMECUBE", "fullName": "Nintendo GameCube", "icon": "🧊", "color": "platGc"},
            "wii": {"title": "WII", "fullName": "Nintendo Wii", "icon": "🎾", "color": "platWii"},
            "megadrive": {"title": "MEGADRIVE", "fullName": "Sega Mega Drive", "icon": "🌀", "color": "platMegaDrive"},
            "mastersystem": {"title": "MASTER SYSTEM", "fullName": "Sega Master System", "icon": "🕹️", "color": "platMegaDrive"},
            "gamegear": {"title": "GAME GEAR", "fullName": "Sega Game Gear", "icon": "📺", "color": "platMegaDrive"},
            "dreamcast": {"title": "DREAMCAST", "fullName": "Sega Dreamcast", "icon": "🍥", "color": "platDreamcast"},
            "unknown": {"title": "OTROS", "fullName": "Misceláneo", "icon": "❓", "color": "platUnknown"}
        }
        
        summary = []
        try:
            import mango_engine
            native_results = mango_engine.fetch_consoles_summary(
                str(AppConfig.get_database_path()),
                str(AppConfig.get_emulators_path())
            )
            for item in native_results:
                platform_id = item["platform"]
                ui_info = base_platforms.get(platform_id, base_platforms["unknown"])
                summary.append({
                    "title": ui_info["title"],
                    "fullName": ui_info["fullName"],
                    "platform": platform_id,
                    "iconEmoji": ui_info["icon"],
                    "accentColor": ui_info["color"],
                    "gameCount": item["gameCount"],
                    "playTime": item["playTime"],
                    "hasCore": item["hasCore"],
                    "emulatorName": item["emulatorName"]
                })
            self._cached_summary = summary
            
            # Log profesional y legible para el sistema de logs
            if summary:
                platforms_str = ", ".join([f"[{s['title']}: {s['gameCount']}]" for s in summary])
                EmuLog.info(f"M.A.N.G.O (UI): Sincronizados {len(summary)} sistemas en la biblioteca ({platforms_str})")
            
            return summary
        except Exception as e:
            EmuLog.error(f"Error nativo en resumen de consola: {e}")
            return []

    @Slot(result="QVariantMap")
    def get_system_info(self):
        """Información técnica del ecosistema."""
        mango_version = "N/A"
        is_engine_ready = False
        try:
            import mango_engine
            mango_version = AppConfig.MANGO_VERSION
            is_engine_ready = True
        except ImportError: pass
        
        return {
            "app_name": AppConfig.APP_NAME,
            "app_version": AppConfig.APP_VERSION,
            "os": f"{py_platform.system()} {py_platform.release()} ({py_platform.machine()})",
            "cpu_threads": os.cpu_count() or 0,
            "mango_version": mango_version,
            "is_engine_ready": is_engine_ready
        }

    @Slot(result=int)
    def get_games_count(self):
        return self.db.count_all_roms()

    @Slot(result="QVariantMap")
    def get_discovery_data(self):
        """Genera el contenido para el 'Discovery Hub'."""
        try:
            import datetime
            now = datetime.datetime.now()
            today_md = now.strftime("-%m-%d") # Buscamos coincidencia de mes-día
            
            discovery = {
                "on_this_day": [],
                "hidden_gems": [],
                "random_batch": []
            }
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. On This Day (Mismo mes y día)
                cursor.execute("""
                    SELECT g.id, g.platform, m.title, m.release_date, m.cover_2d_path
                    FROM games g
                    JOIN game_metadata m ON g.id = m.game_id
                    WHERE m.release_date LIKE ?
                    LIMIT 10
                """, (f"%{today_md}",))
                discovery["on_this_day"] = [dict(row) for row in cursor.fetchall()]
                
                # 2. Hidden Gems (0 Playtime, pero tienen metadata y buena descripción)
                cursor.execute("""
                    SELECT g.id, g.platform, m.title, m.cover_2d_path
                    FROM games g
                    JOIN game_metadata m ON g.id = m.game_id
                    LEFT JOIN play_stats s ON g.id = s.game_id
                    WHERE (s.play_time_seconds IS NULL OR s.play_time_seconds = 0)
                      AND m.description IS NOT NULL AND length(m.description) > 100
                    ORDER BY RANDOM()
                    LIMIT 10
                """)
                discovery["hidden_gems"] = [dict(row) for row in cursor.fetchall()]
                
                # 3. Random Visual Batch (Para el muro 3D)
                cursor.execute("""
                    SELECT g.id, m.cover_2d_path as cover
                    FROM games g
                    JOIN game_metadata m ON g.id = m.game_id
                    WHERE m.cover_2d_path IS NOT NULL AND m.cover_2d_path != ''
                    ORDER BY RANDOM()
                    LIMIT 40
                """)
                discovery["random_batch"] = [dict(row) for row in cursor.fetchall()]
                
            return discovery
        except Exception as e:
            EmuLog.error(f"Error generando datos de descubrimiento: {e}")
            return {"on_this_day": [], "hidden_gems": [], "random_batch": []}

    def clear_cache(self):
        self._cached_summary = None
        self.db.clear_count_cache()
