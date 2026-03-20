from .base_handler import BaseTweakHandler
from typing import List, Dict, Any

class DolphinHandler(BaseTweakHandler):
    """
    Handler especializado para Dolphin Emulator.
    """

    def get_supported_tweaks(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "fullscreen",
                "label": "Pantalla Completa",
                "type": "bool",
                "default": True,
                "flag": "-f"
            },
            {
                "id": "batch",
                "label": "Modo Batch (Auto-Cerrar)",
                "type": "bool",
                "default": True,
                "flag": "-b"
            },
            {
                "id": "no_gui",
                "label": "Sin Interfaz (GUI)",
                "type": "bool",
                "default": True,
                "flag": "-n"
            },
            {
                "id": "mute",
                "label": "lib_tweak_mute",
                "type": "bool",
                "default": False,
                "flag": "-m"
            }
        ]

    def apply_tweaks(self, args: List[str], game_path: str, user_settings: Dict[str, Any]) -> List[str]:
        tweaks = self.get_supported_tweaks()
        for t in tweaks:
            val = user_settings.get(t["id"], t["default"])
            if val and "flag" in t:
                if t["flag"] not in args:
                    args.append(t["flag"])
        return args
