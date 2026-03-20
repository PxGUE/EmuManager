"""
library.py — Bridge especializado para la gestión de la biblioteca de juegos.

Este sub-bridge maneja:
1. Estadísticas del dashboard (juegos instalados, tiempo total).
2. Actividad reciente de juego.
3. Listado de consolas con ROMs.
4. Información detallada de los juegos y sus metadatos.
5. Sincronización (escaneo) de ROMs y descarga de arte/info.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from collections import defaultdict

from PySide6.QtCore import QObject, Slot, Property, Signal, QUrl
import core.logic.scanner as scanner
from core.logic.constants import AVAILABLE_EMULATORS
from core.logic.artwork import obtener_ruta_caratula, obtener_ruta_fondo_consola, obtener_ruta_background
from core.logic.metadata import obtener_metadata_local, guardar_metadata_local

class LibraryBridge(QObject):
    """
    Gestiona la lógica de la biblioteca y la exposición de datos de juegos a QML.
    """
    
    # --- Señales de Notificación ---
    dashboardStatsChanged = Signal()
    recentActivityChanged = Signal()
    scannedConsolesChanged = Signal()

    def __init__(self, main_bridge):
        """
        Args:
            main_bridge (AppBridge): Referencia al bridge principal para emitir señales globales.
        """
        super().__init__()
        self.main = main_bridge
        self.emu_manager = main_bridge.emu_manager
        self.translator = main_bridge.translator

        # Vincular el refresco global con el refresco de este bridge
        self.main.statsUpdated.connect(self.dashboardStatsChanged)
        self.main.statsUpdated.connect(self.recentActivityChanged)
        self.main.statsUpdated.connect(self.scannedConsolesChanged)

    @Property(dict, notify=dashboardStatsChanged)
    def dashboardStats(self):
        """
        Calcula las estadísticas generales para la pantalla de inicio.
        
        Returns:
            dict: {installed, totalRoms, totalConsoles, totalHours, totalTimeDisplay}
        """
        biblioteca = scanner.cargar_biblioteca_cache()
        installed = sum(1 for emu in AVAILABLE_EMULATORS if self.emu_manager.esta_instalado(emu["github"]))
        total_seconds = sum(self.emu_manager.get_playtime(j.get("ruta", ""))[0] for j in biblioteca)
        total_hours = int(total_seconds // 3600)
        total_mins = int((total_seconds % 3600) // 60)
        
        if total_hours > 0:
            time_display = self.translator.t("dash_hours_suffix", total_hours, total_mins)
        elif total_mins > 0:
            time_display = self.translator.t("dash_mins_suffix", total_mins)
        else:
            time_display = "0h"

        return {
            "installed": installed,
            "totalRoms": len(biblioteca),
            "totalConsoles": len(set(j.get("id_emu") for j in biblioteca)),
            "totalHours": total_hours,
            "totalTimeDisplay": time_display
        }

    @Property(list, notify=recentActivityChanged)
    def recentActivity(self):
        """
        Retorna la lista de los últimos 10 juegos jugados con su tiempo y carátula.
        """
        biblioteca = scanner.cargar_biblioteca_cache()
        juegos_con_tiempo = []
        for j in biblioteca:
            s, h, m = self.emu_manager.get_playtime(j.get("ruta", ""))
            if s > 0:
                emu = next((e for e in AVAILABLE_EMULATORS if e["id"] == j.get("id_emu")), {})
                color = emu.get("color", "#4da6ff")
                if h > 0:
                    time_str = self.translator.t("dash_hours_suffix", h, m)
                elif m > 0:
                    time_str = self.translator.t("dash_mins_suffix", m)
                else:
                    time_str = self.translator.t("dash_less_min")
                
                juegos_con_tiempo.append({
                    "name": j["nombre"],
                    "console": j.get("consola", ""),
                    "playtime": time_str,
                    "color": color,
                    "seconds": s,
                    "path": j.get("ruta", ""),
                    "id_emu": j.get("id_emu", ""),
                    "cover": QUrl.fromLocalFile(obtener_ruta_caratula(j.get("ruta", ""), j.get("id_emu", ""))).toString() if os.path.exists(obtener_ruta_caratula(j.get("ruta", ""), j.get("id_emu", ""))) else "",
                    "cover_3d": QUrl.fromLocalFile(obtener_ruta_caratula(j.get("ruta", ""), j.get("id_emu", ""), "3d")).toString() if os.path.exists(obtener_ruta_caratula(j.get("ruta", ""), j.get("id_emu", ""), "3d")) else "",
                    "background": QUrl.fromLocalFile(obtener_ruta_background(j.get("ruta", ""), j.get("id_emu", ""))).toString() if os.path.exists(obtener_ruta_background(j.get("ruta", ""), j.get("id_emu", ""))) else ""
                })
        
        juegos_con_tiempo.sort(key=lambda x: x["seconds"], reverse=True)
        return juegos_con_tiempo[:10]

    @Property(list, notify=scannedConsolesChanged)
    def scannedConsoles(self):
        """
        Retorna la lista de consolas que tienen al menos un juego en la biblioteca.
        Utilizado para mostrar la cuadrícula de plataformas.
        """
        lib = scanner.cargar_biblioteca_cache()
        result = []
        game_counts = defaultdict(int)
        game_playtimes = defaultdict(float)
        
        for juego in lib:
            pid = juego.get("id_emu")
            if pid:
                game_counts[pid] += 1
                game_playtimes[pid] += float(juego.get("playtime_seconds", 0))

        for emu in AVAILABLE_EMULATORS:
            count = game_counts.get(emu["id"], 0)
            is_installed = self.emu_manager.esta_instalado(emu.get("github", "")) 
            
            if is_installed:
                total_s = game_playtimes.get(emu["id"], 0)
                bg_raw = obtener_ruta_fondo_consola(emu)
                bg_url = QUrl.fromLocalFile(bg_raw).toString() if os.path.exists(bg_raw) else ""
                
                result.append({
                    "id": emu["id"],
                    "name": emu["console"],
                    "emu_name": emu["name"],
                    "count": count,
                    "playtime": f"{int(total_s // 3600)}h {int((total_s % 3600) // 60)}m",
                    "color": emu.get("color", "#4da6ff"),
                    "background": bg_url
                })
        
        result.sort(key=lambda x: x["count"], reverse=True)
        return result

    @Slot(str, result=list)
    def getGamesForConsole(self, console_id):
        """
        Retorna la lista detallada de juegos para una consola específica.
        
        Args:
            console_id (str): ID del emulador/consola (ej: 'mgba').
        """
        biblioteca = scanner.cargar_biblioteca_cache()
        games = []
        for j in biblioteca:
            if j.get("id_emu") == console_id:
                ruta = j.get("ruta", "")
                s, h, m = self.emu_manager.get_playtime(ruta)
                cover_raw = obtener_ruta_caratula(ruta, console_id, "2d")
                cover_url = QUrl.fromLocalFile(cover_raw).toString() if os.path.exists(cover_raw) else ""
                cover_3d_raw = obtener_ruta_caratula(ruta, console_id, "3d")
                cover_3d_url = QUrl.fromLocalFile(cover_3d_raw).toString() if os.path.exists(cover_3d_raw) else ""
                bg_raw = obtener_ruta_background(ruta, console_id)
                bg_url = QUrl.fromLocalFile(bg_raw).toString() if os.path.exists(bg_raw) else ""
                meta = obtener_metadata_local(ruta)
                
                games.append({
                    "name": j["nombre"],
                    "title": meta.get("title") or j["nombre"],
                    "path": ruta,
                    "console": j.get("consola", ""),
                    "playtime": f"{h}h {m}m" if h > 0 else f"{m}m",
                    "cover": cover_url,
                    "cover_3d": cover_3d_url,
                    "background": bg_url,
                    "id_emu": console_id,
                    "isFavorite": scanner.es_favorito(ruta),
                    "description": meta.get("description", ""),
                    "developer": meta.get("developer") or meta.get("publisher", "Desconocido"),
                    "year": meta.get("year", "N/A"),
                    "rating": float(meta.get("rating", 0)),
                    "genre": meta.get("genre", "General")
                })
        
        games.sort(key=lambda x: x["name"].lower())
        print(f"[BRIDGE] getGamesForConsole({console_id}) -> {len(games)} juegos encontrados.")
        return games

    @Slot(str, dict)
    def saveMetadata(self, game_path, metadata):
        """Guarda manualmente metadatos editados por el usuario."""
        guardar_metadata_local(game_path, metadata)
        self.main.statsUpdated.emit()

    @Slot(str, str)
    def launchGame(self, game_path, emu_id):
        """Inicia un juego usando el emulador especificado."""
        biblioteca = scanner.cargar_biblioteca_cache()
        game = next((j for j in biblioteca if j["ruta"] == game_path), None)
        if game:
            emu_info = next((e for e in AVAILABLE_EMULATORS if e["id"] == emu_id), None)
            if emu_info:
                async def do_launch():
                    success, msg = await self.emu_manager.lanzar_juego(emu_info["github"], game_path, game)
                    if success:
                        self.main.statsUpdated.emit()
                asyncio.create_task(do_launch())

    @Slot(str, result=bool)
    def toggleFavorite(self, game_path):
        """Alterna el estado favorito de un juego."""
        is_fav = scanner.toggle_favorito(game_path)
        self.main.statsUpdated.emit()
        return is_fav

    @Slot(str, result=bool)
    def isFavorite(self, game_path):
        """Consulta si un juego es favorito."""
        return scanner.es_favorito(game_path)

    @Slot(str, result=int)
    def checkLaunchState(self, game_path):
        """
        Verifica si el juego ya está en ejecución.
        Devuelve: 0 (No), 1 (Otro juego), 2 (Este mismo juego).
        """
        if not self.emu_manager.is_emulator_running():
            return 0
        current = self.emu_manager.launcher.current_game
        if current and current.get("ruta") == game_path:
            return 2
        return 1

    @Slot(str, str)
    def forceLaunchGame(self, game_path, emu_id):
        """Cierra cualquier juego activo e inicia el nuevo inmediatamente."""
        self.emu_manager.terminar_proceso_actual()
        self.launchGame(game_path, emu_id)

    @Slot(bool, bool, str)
    def scanGames(self, dl_artwork=True, dl_metadata=True, emu_id=None):
        """
        Inicia el proceso asíncrono de escaneo y actualización de la biblioteca.
        """
        from core.logic.scanner import escanear_roms, asdict
        async def do_scan():
            try:
                msg = f"[BRIDGE] Iniciando escaneo (Arte={dl_artwork}, Meta={dl_metadata}"
                if emu_id:
                    msg += f", Emulador={emu_id}"
                msg += ")"
                print(f"[BRIDGE] {msg}")
                
                self.main.scanProgress.emit(0.0, self.translator.t("dl_scrap_scanning"))
                juegos_obj = await escanear_roms(self.emu_manager.roms_path, emu_id=emu_id)
                library_dicts = [asdict(j) for j in juegos_obj]
                self.main.statsUpdated.emit()
                
                if dl_artwork:
                    self.main.scanProgress.emit(0.1, self.translator.t("lib_status_artwork"))
                    from core.logic.artwork import descargar_caratulas_biblioteca
                    def on_art_progress(curr, total, name):
                        prog = 0.1 + (curr / total) * 0.4
                        self.main.scanProgress.emit(prog, self.translator.t("dl_status_art", name))
                    emu_map = {e["id"]: e for e in AVAILABLE_EMULATORS}
                    stats_art = await descargar_caratulas_biblioteca(library_dicts, emu_map, on_progress=on_art_progress)
                    print(f"[BRIDGE] Artwork completado: {stats_art}")
                    self.main.statsUpdated.emit()

                if dl_metadata:
                    self.main.scanProgress.emit(0.5, self.translator.t("lib_status_processing"))
                    from core.logic.metadata import descargar_metadata_biblioteca
                    def on_meta_progress(curr, total, name):
                        prog = 0.5 + (curr / total) * 0.5
                        self.main.scanProgress.emit(prog, self.translator.t("dl_status_meta", name))
                    emu_map = {e["id"]: e for e in AVAILABLE_EMULATORS}
                    stats_meta = await descargar_metadata_biblioteca(library_dicts, emu_map, on_progress=on_meta_progress)
                    print(f"[BRIDGE] Metadatos completados: {stats_meta}")
                    self.main.statsUpdated.emit()
                
                print("[BRIDGE] Proceso de sincronización finalizado.")
                self.main.scanProgress.emit(1.0, self.translator.t("lib_status_complete"))
                self.main.statsUpdated.emit()
                await asyncio.sleep(3)
                self.main.scanProgress.emit(0.0, "")
            except Exception as e:
                print(f"[BRIDGE] Error en escaneo: {e}")
                self.main.scanProgress.emit(0.0, f"Error: {str(e)}")
            
        asyncio.create_task(do_scan())
