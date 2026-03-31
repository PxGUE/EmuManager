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
            
            # Mapear nombres directamente de SQL
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                if stats.get("last_game") and stats["last_game"].get("id"):
                    cursor.execute("SELECT display_name FROM games WHERE id = ?", (stats["last_game"]["id"],))
                    row = cursor.fetchone()
                    if row and row[0]: stats["last_game"]["title"] = row[0]
                
                if stats.get("recent_games"):
                    for g in stats["recent_games"]:
                        if g.get("id"):
                            cursor.execute("SELECT display_name FROM games WHERE id = ?", (g["id"],))
                            row = cursor.fetchone()
                            if row and row[0]: g["title"] = row[0]
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
            "gba": {"title": "GBA", "fullName": "Game Boy Advance", "icon": "📱", "color": "platGba"},
            "n64": {"title": "N64", "fullName": "Nintendo 64", "icon": "🏰", "color": "platN64"},
            "ps1": {"title": "PS1", "fullName": "PlayStation 1", "icon": "💿", "color": "platPs1"},
            "ps2": {"title": "PS2", "fullName": "PlayStation 2", "icon": "🚀", "color": "platPs2"},
            "psp": {"title": "PSP", "fullName": "PlayStation Portable", "icon": "🔋", "color": "platPsp"},
            "ds": {"title": "DS", "fullName": "Nintendo DS", "icon": "📖", "color": "platDs"},
            "gc": {"title": "GAMECUBE", "fullName": "Nintendo GameCube", "icon": "🧊", "color": "platGc"},
            "wii": {"title": "WII", "fullName": "Nintendo Wii", "icon": "🎾", "color": "platWii"},
            "megadrive": {"title": "MEGADRIVE", "fullName": "Sega Mega Drive", "icon": "🌀", "color": "platMegaDrive"},
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

    def clear_cache(self):
        self._cached_summary = None
