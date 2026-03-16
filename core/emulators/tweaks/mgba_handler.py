from .base_handler import BaseTweakHandler
from typing import List, Dict, Any

class MGBAHandler(BaseTweakHandler):
    """
    Handler especializado para mGBA.
    Soporta pantalla completa y modo sin interfaz (solo versión Qt).
    """

    def get_supported_tweaks(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "fullscreen",
                "label": "lib_tweak_fullscreen",
                "type": "bool",
                "default": True,
                "flag": "-f"
            },
            {
                "id": "headless",
                "label": "lib_tweak_headless",
                "type": "bool",
                "default": True,
                "flag": "-n"
            },
            {
                "id": "scaling",
                "label": "Escala de Ventana",
                "type": "list",
                "options": ["1x", "2x", "3x", "4x"],
                "default": "2x",
                "depends_on": {"fullscreen": False}
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
        # 1. Pantalla Completa
        if user_settings.get("fullscreen", True):
            if "-f" not in args: args.append("-f")
        else:
            # 2. Escala (mGBA usa -1, -2, -3, -4 directamente)
            scale = str(user_settings.get("scaling", "2x")).replace("x", "")
            flag = f"-{scale}"
            if flag not in args:
                args.append(flag)
        
        # 3. Mute
        if user_settings.get("mute", False):
            if "-m" not in args: args.append("-m")

        # 4. Ocultar Interfaz (Solo en Qt)
        is_sdl = any("sdl" in a.lower() for a in args)
        if not is_sdl and user_settings.get("headless", True):
            if "-n" not in args: args.append("-n")
                
        return args
