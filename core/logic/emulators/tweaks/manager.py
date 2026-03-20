import os
import json
from typing import Any
from .generic_handler import GenericTweakHandler
from .retroarch_handler import RetroArchHandler
from .dolphin_handler import DolphinHandler
from .pcsx2_handler import PCSX2Handler
from .duckstation_handler import DuckStationHandler
from .mgba_handler import MGBAHandler

class TweakManager:
    """
    Coordina los ajustes de todos los emuladores y persiste las preferencias.
    """
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.tweaks_file = os.path.join(self.data_dir, "emulator_tweaks.json")
        self.handlers = {
            "retroarch": RetroArchHandler(),
            "dolphin": DolphinHandler(),
            "pcsx2": PCSX2Handler(),
            "duckstation": DuckStationHandler(),
            "mgba": MGBAHandler(),
            "default": GenericTweakHandler()
        }
        self.user_prefs = self._load_prefs()

    def _load_prefs(self):
        if os.path.exists(self.tweaks_file):
            try:
                with open(self.tweaks_file, "r") as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save_prefs(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.tweaks_file, "w") as f:
            json.dump(self.user_prefs, f, indent=4)

    def get_handler(self, emu_id: str):
        return self.handlers.get(emu_id, self.handlers["default"])

    def get_tweaks_for_emu(self, emu_id: str):
        handler = self.get_handler(emu_id)
        available = handler.get_supported_tweaks()
        
        # Mezclar con valores guardados
        saved = self.user_prefs.get(emu_id, {})
        for t in available:
            t["value"] = saved.get(t["id"], t["default"])
        
        return available

    def save_tweak(self, emu_id: str, tweak_id: str, value: Any):
        if emu_id not in self.user_prefs:
            self.user_prefs[emu_id] = {}
        self.user_prefs[emu_id][tweak_id] = value
        self._save_prefs()

    def apply_tweaks(self, emu_id: str, args: list, game_path: str):
        handler = self.get_handler(emu_id)
        saved_settings = self.user_prefs.get(emu_id, {})
        print(f"[TWEAKS] Aplicando ajustes para '{emu_id}': {saved_settings}")
        return handler.apply_tweaks(args, game_path, saved_settings)
