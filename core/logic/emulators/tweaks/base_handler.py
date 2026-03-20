from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseTweakHandler(ABC):
    """
    Clase base para todos los gestores de ajustes (tweaks) de emuladores.
    Cada emulador que necesite lÃ³gica especial heredarÃ¡ de aquÃ­.
    """
    
    @abstractmethod
    def get_supported_tweaks(self) -> List[Dict[str, Any]]:
        """
        Retorna una lista de ajustes soportados con sus metadatos para la UI.
        Formato: [
            {
                "id": "fullscreen",
                "label": "Pantalla Completa",
                "type": "bool",
                "default": True
            },
            ...
        ]
        """
        pass

    @abstractmethod
    def apply_tweaks(self, args: List[str], game_path: str, user_settings: Dict[str, Any]) -> List[str]:
        """
        Modifica la lista de argumentos (args) que se pasarÃ¡n al subprocess.Popen
        basÃ¡ndose en los ajustes del usuario.
        """
        return args

    def apply_config_patch(self, emu_path: str, user_settings: Dict[str, Any]):
        """
        (Opcional) Parchea archivos .ini o .cfg fÃ­sicos en el disco si el emulador
        no soporta ciertos ajustes por CLI.
        """
        pass
