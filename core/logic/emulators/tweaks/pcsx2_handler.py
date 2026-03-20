from .base_handler import BaseTweakHandler
from typing import List, Dict, Any

class PCSX2Handler(BaseTweakHandler):
    """
    Handler especializado para PCSX2 (PS2).
    """

    def get_supported_tweaks(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "fullscreen",
                "label": "Pantalla Completa",
                "type": "bool",
                "default": True,
                "flag": "--fullscreen"
            },
            {
                "id": "nogui",
                "label": "Sin Interfaz de Usuario",
                "type": "bool",
                "default": True,
                "flag": "--nogui"
            },
            {
                "id": "batch",
                "label": "Modo Batch (Cerrar al salir)",
                "type": "bool",
                "default": True,
                "flag": "--batch"
            },
            {
                "id": "no_patch",
                "label": "Desactivar Parches/Widescreen",
                "type": "bool",
                "default": False,
                "flag": "--no-patch"
            },
            {
                "id": "resolution",
                "label": "ResoluciÃ³n de Ventana",
                "type": "list",
                "options": ["640x480", "1280x720", "1920x1080", "2560x1440"],
                "default": "1280x720",
                "depends_on": {"fullscreen": False}
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
            
            elif t["id"] == "resolution" and not is_fullscreen:
                try:
                    w, h = val.split("x")
                    args.extend([f"--width={w}", f"--height={h}"])
                except: pass

        return args
