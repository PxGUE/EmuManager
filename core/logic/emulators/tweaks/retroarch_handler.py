from .base_handler import BaseTweakHandler
from typing import List, Dict, Any

class RetroArchHandler(BaseTweakHandler):
    """
    Handler especializado para RetroArch.
    Usa flags cortas (-f) y soporta configuraciones pesadas.
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
                "id": "aspect_ratio",
                "label": "RelaciÃ³n de Aspecto",
                "type": "list",
                "options": ["Core Provided", "4:3", "16:9", "Full"],
                "default": "Core Provided"
            },
            {
                "id": "mute",
                "label": "lib_tweak_mute",
                "type": "bool",
                "default": False,
                "flag": "--mute"
            },
            {
                "id": "fps",
                "label": "lib_tweak_fps",
                "type": "bool",
                "default": False,
                "flag": "--fps"
            }
        ]

    def apply_tweaks(self, args: List[str], game_path: str, user_settings: Dict[str, Any]) -> List[str]:
        tweaks = self.get_supported_tweaks()
        for t in tweaks:
            val = user_settings.get(t["id"], t["default"])
            
            if t["id"] == "aspect_ratio":
                # LÃ³gica especial para aspect ratio
                mapping = {"Core Provided": "0", "4:3": "1", "16:9": "2", "Full": "3"}
                args.extend(["--aspect-ratio-index", mapping.get(val, "0")])
            
            elif t["type"] == "bool" and val:
                if t.get("flag") and t["flag"] not in args:
                    args.append(t["flag"])

        return args
