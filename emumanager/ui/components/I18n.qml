import QtQuick

pragma Singleton

QtObject {
    id: i18n
    property string language: "es" 

    // Robustez: Siempre devolvemos al menos el español si el idioma actual falla o no está listo
    readonly property var t: texts[language] ? texts[language] : texts["es"]

    readonly property var texts: {
        "es": {
            "dashboard": "DASHBOARD",
            "library": "BIBLIOTECA",
            "downloads": "DESCARGAS",
            "settings": "CONFIGURACIÓN",
            "explore": "EXPLORAR",
            "play": "JUGAR",
            "back": "VOLVER",
            "games_count": "JUEGOS",
            "time_count": "TIEMPO",
            "download_manager": "GESTOR DE DESCARGAS",
            "auto_download": "DESCARGAS AUTOMÁTICAS",
            "settings_sub": "Gestiona tus bibliotecas, APIs y experiencia visual",
            "section_paths": "RUTAS Y BIBLIOTECAS",
            "section_apis": "SERVICIOS Y APIs",
            "section_interface": "INTERFAZ Y TEMAS",
            "section_system": "SISTEMA"
        },
        "en": {
            "dashboard": "DASHBOARD",
            "library": "LIBRARY",
            "downloads": "DOWNLOADS",
            "settings": "SETTINGS",
            "explore": "EXPLORE",
            "play": "PLAY",
            "back": "BACK",
            "games_count": "GAMES",
            "time_count": "TIME",
            "download_manager": "DOWNLOAD MANAGER",
            "auto_download": "AUTO DOWNLOADS",
            "settings_sub": "Manage your libraries, APIs and visual experience",
            "section_paths": "PATHS & LIBRARIES",
            "section_apis": "SERVICES & APIs",
            "section_interface": "INTERFACE & THEMES",
            "section_system": "SYSTEM"
        }
    }
}
