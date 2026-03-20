from .base_handler import BaseTweakHandler
from typing import List, Dict, Any

class GenericTweakHandler(BaseTweakHandler):
    """
    Handler genÃ©rico para la mayorÃ­a de emuladores que siguen convenciones
    estÃ¡ndar de CLI (--fullscreen, --nogui, etc.)
    """

    def get_supported_tweaks(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "fullscreen",
                "label": "lib_tweak_fullscreen",
                "type": "bool",
                "default": True,
                "flag": "--fullscreen"
            },
            {
                "id": "headless",
                "label": "lib_tweak_headless",
                "type": "bool",
                "default": True,
                "flag": "--nogui"
            }
        ]

    def apply_tweaks(self, args: List[str], game_path: str, user_settings: Dict[str, Any]) -> List[str]:
        tweaks = self.get_supported_tweaks()
        is_fullscreen = user_settings.get("fullscreen", True)
        
        for t in tweaks:
            val = user_settings.get(t["id"], t["default"])
            
            if t["type"] == "bool" and val:
                if t.get("flag") and t["flag"] not in args:
                    args.append(t["flag"])

        return args
