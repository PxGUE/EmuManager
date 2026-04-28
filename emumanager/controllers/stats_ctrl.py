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
            "snes": {"title": "SNES", "fullName": "plat_snes_full", "icon": "🕹️", "color": "platSnes"},
            "nes": {"title": "NES", "fullName": "plat_nes_full", "icon": "📺", "color": "platNes"},
            "gb": {"title": "GB", "fullName": "plat_gb_full", "icon": "📟", "color": "platGb"},
            "gbc": {"title": "GBC", "fullName": "plat_gbc_full", "icon": "🌈", "color": "platGbc"},
            "gba": {"title": "GBA", "fullName": "plat_gba_full", "icon": "📱", "color": "platGba"},
            "n64": {"title": "N64", "fullName": "plat_n64_full", "icon": "🏰", "color": "platN64"},
            "ps1": {"title": "PS1", "fullName": "plat_ps1_full", "icon": "💿", "color": "platPs1"},
            "ps2": {"title": "PS2", "fullName": "plat_ps2_full", "icon": "🚀", "color": "platPs2"},
            "psp": {"title": "PSP", "fullName": "plat_psp_full", "icon": "🔋", "color": "platPsp"},
            "ds": {"title": "DS", "fullName": "plat_ds_full", "icon": "📖", "color": "platDs"},
            "gc": {"title": "GAMECUBE", "fullName": "plat_gc_full", "icon": "🧊", "color": "platGc"},
            "wii": {"title": "WII", "fullName": "plat_wii_full", "icon": "🎾", "color": "platWii"},
            "megadrive": {"title": "MEGADRIVE", "fullName": "plat_megadrive_full", "icon": "🌀", "color": "platMegaDrive"},
            "mastersystem": {"title": "MASTER SYSTEM", "fullName": "plat_mastersystem_full", "icon": "🕹️", "color": "platMegaDrive"},
            "gamegear": {"title": "GAME GEAR", "fullName": "plat_gamegear_full", "icon": "📺", "color": "platMegaDrive"},
            "dreamcast": {"title": "DREAMCAST", "fullName": "plat_dreamcast_full", "icon": "🍥", "color": "platDreamcast"},
            "unknown": {"title": "others", "fullName": "plat_miscellaneous_full", "icon": "❓", "color": "platUnknown"}
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
            return self.db.get_discovery_data(today_md)
        except Exception as e:
            EmuLog.error(f"Error generando datos de descubrimiento: {e}")
            return {"on_this_day": [], "hidden_gems": [], "random_batch": []}

    def clear_cache(self):
        self._cached_summary = None
        self.db.clear_count_cache()
