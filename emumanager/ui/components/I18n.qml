import QtQuick

pragma Singleton

Item {
    id: i18n
    property string language: "es" 

    Component.onCompleted: {
        if (mainController) {
            language = mainController.get_language()
        }
    }

    Connections {
        target: mainController
        function onLanguage_changed(lang) {
            language = lang
        }
    }

    readonly property var t: texts[language] ? texts[language] : texts["es"]

    // Función para traducir patrones complejos (ej: "core_downloading|SNES")
    function tp(s) {
        if (!s) return ""
        let parts = s.split("|")
        let key = parts[0]
        let res = t[key] || key
        if (parts.length > 1 && typeof res === "string") {
            return res.replace("%1", parts[1])
        }
        return res
    }

    readonly property var texts: ({
        "es": {
            // Main Navigation
            "dashboard": "DASHBOARD",
            "library": "BIBLIOTECA",
            "downloads": "DESCARGAS",
            "settings": "CONFIGURACIÓN",
            "explore": "EXPLORAR",
            "play": "JUGAR",
            "back": "VOLVER",
            
            // Settings Tabs
            "tab_general": "General",
            "tab_library": "Biblioteca",
            "tab_services": "Servicios",
            "tab_advanced": "Avanzado",
            "tab_about": "Acerca de",

            // Settings Panels
            "system_preferences": "PREFERENCIAS DE SISTEMA",
            "global_language": "Idioma Global",
            "global_language_desc": "Elige el idioma de la interfaz",
            "auto_theme": "Tema Automático",
            "auto_theme_desc": "Sincronizar luz/oscuridad automáticamente",
            
            "paths_scanning": "RUTAS Y ESCANEO",
            "roms_path": "CARPETA DE ROMS",
            "emus_path": "CARPETA DE EMULADORES",
            "change_btn": "CAMBIAR",
            "collection_info": "INFO DE COLECCIÓN",
            "games_registered": "Tienes %1 juegos registrados.",
            "section_downloads_ref": "Para actualizar la biblioteca, ve a la sección de DESCARGAS.",

            "external_resources": "RECURSOS EXTERNOS",
            "api_screenscraper": "API de ScreenScraper",
            "api_desc": "Introduce tus credenciales para descargar portadas automáticamente.",
            "api_saved": "Configuración guardada. M.A.N.G.O la usará al sincronizar.",

            "mango_engine": "M.A.N.G.O (NATIVO)",
            "opt_multicore": "Optimización Multinúcleo",
            "opt_multicore_desc": "Usa todos los hilos del CPU para el hashing",
            "opt_integrity": "Verificación de Integridad",
            "opt_integrity_desc": "Comprobar archivos corruptos al escanear",
            "opt_low_latency": "Modo Ultra-Baja Latencia",
            "opt_low_latency_desc": "Scraping asíncrono optimizado por Rust",
            "purge_cache": "PURGAR CACHÉ DEL MOTOR",

            "about_desc": "EmuManager es software <b>Libre y Gratuito</b>, impulsado por el motor nativo <b>M.A.N.G.O</b>. Diseñado con un enfoque <b>Local-First</b>, garantizamos que tu privacidad es absoluta: tus datos y biblioteca permanecen exclusivamente en tu equipo, sin telemetría ni dependencias de la nube.",
            "os_spec": "SISTEMA OPERATIVO",
            "engine_spec": "MOTOR NATIVO",
            "ram_spec": "MEMORIA RAM",
            "cpu_spec": "PROCESAMIENTO",
            "python_spec": "ENTORNO PYTHON",
            "contribute_github": "CONTRIBUIR EN GITHUB",
            "official_site": "SITIO OFICIAL",
            "copyright": "© 2026 PAIDEX | EMUMANAGER TEAM | LICENCIA MIT",

            // Library & Dashboard
            "empty_library": "BIBLIOTECA VACÍA",
            "empty_library_desc": "No se han detectado juegos todavía.\nVe a Configuración para añadir rutas de escaneo.",
            "configure_paths_btn": "CONFIGURAR RUTAS",
            "search_placeholder": "Búsqueda instantánea...",
            "stats_total_games": "JUEGOS TOTALES",
            "stats_play_time": "TIEMPO JUGADO",
            "stats_most_played": "PLATAFORMA LÍDER",
            "stats_last_game": "RECIENTE",
            "stats_favorites": "FAVORITOS",

            // Downloads
            "sync_center": "CENTRO DE SINCRONIZACIÓN",
            "sync_center_desc": "Gestiona tu biblioteca, medios y emuladores desde un solo lugar",
            "check_updates_btn": "BUSCAR ACTUALIZACIONES ↻",
            "sync_roms": "Sincronizar ROMs",
            "sync_media": "Metadatos y Arte",
            "emu_gallery": "GALERÍA DE EMULADORES",
            "scan_idle": "Escanear directorios locales",
            "scan_done": "Biblioteca al día ✓",
            "scrape_idle": "ScreenScraper + Libretro",
            "scrape_done": "Media sincronizada ✓",

            // New Additions
            "settings_title": "CONFIGURACIÓN",
            "username_placeholder": "Usuario",
            "password_placeholder": "Contraseña",
            "engine_online": "Motor Activo",
            "cpu_threads": "%1 hilos",
            "status_active": "Activo",
            "status_inactive": "Inactivo",

            // Card Extras
            "games_suffix": "JUEGOS",
            "games_abbr": "JX",
            "play_time_abbr": "TIEMPO",
            "launch_adventure": "LANZAR AVENTURA",
            "status_processing": "PROCESANDO...",
            "status_installed": "INSTALADO",
            "status_available": "DISPONIBLE",
            "btn_install": "INSTALAR",
            "btn_update": "ACTUALIZAR",
            "btn_uninstall": "DESINSTALAR",

            // Startup & Workers
            "startup_ready": "Misiones inicializadas. Bienvenida.",
            "core_downloading": "Descargando %1 usando M.A.N.G.O...",
            "core_installed": "¡Core instalado!",
            "install_success": "✓ Instalación completada.",
            "install_failed": "Fallo en la orquestación.",
            
            // System Info Tech Keys
            "tech_active": "ACTIVO",
            "tech_inactive": "INACTIVO",
            "tech_threads": "HILOS",
            "tech_cores": "NÚCLEOS",
            "tech_engine_ready": "MOTOR SINCRONIZADO",
            "tech_system_specs": "ESPECIFICACIONES DEL SISTEMA",
            "pill_free_open": "LIBRE Y GRATUITO",
            "pill_local_privacy": "PRIVACIDAD LOCAL",
            "engine_tool_tip": "Motor de Orquestación Nativo: %1",

            // Scan & Scrape Workers
            "scan_starting": "Escaneando archivos con M.A.N.G.O...",
            "scan_no_roms": "No se encontraron ROMs soportadas.",
            "scan_registering": "Registrando: %1",
            "scan_finished": "Escaneo finalizado. %1 juegos nuevos registrados.",
            "scrape_starting": "Iniciando M.A.N.G.O Batch Scraper...",
            "scrape_finished": "Scrapeado completado con éxito.",

            // Game Details
            "loading": "CARGANDO...",
            "no_description": "Sin descripción disponible.",
            "no_description_template": "Sin descripción adicional disponible para este título de %1.",

            // Dashboard Extras
            "command_center": "CENTRO DE COMANDO",
            "operational": "OPERATIVO",
            "next_challenge": "SIGUIENTE RETO",
            "platform_prefix": "PLATAFORMA: ",
            "resume_mission": "▶ REANUDAR MISIÓN",
            "idle": "REPOSO",
            "mango_monitor": "MOTOR M.A.N.G.O (VITAL-LOG)",
            "processing_caps": "PROCESANDO",
            "running_caps": "EJECUTANDO",
            "status_prefix": "ESTADO: ",
            "ready_caps": "LISTO",
            "waiting_caps": "ESPERANDO",

            // RetroArch Panel
            "ra_settings": "AJUSTES: RETROARCH",
            "ra_management": "Gestión avanzada de núcleos",
            "ra_not_detected": "⚠️ RETROARCH NO DETECTADO",
            "ra_install_warning": "Debes instalar RetroArch desde el panel principal antes de descargar núcleos.",
            "core_ready": "Núcleo listo para usar",
            "core_available": "Disponible para descarga",
            "btn_delete": "BORRAR",

            // Emulator States
            "emu_status_installed": "✓ Instalado",
            "emu_status_available": "Disponible para instalar",

            // Emulator Repository
            "emu_retroarch_fullname": "Repositorio Universal Libretro",
            "emu_retroarch_desc": "El frontend definitivo para emulación. Permite gestionar cientos de cores desde una sola interfaz con soporte para shaders y guardado en la nube.",
            "emu_dolphin_fullname": "Emulador Independiente GameCube / Wii",
            "emu_dolphin_desc": "Potente emulador con soporte para alta resolución (4K), juego online y compatibilidad casi perfecta con el catálogo de Nintendo Wii y GameCube.",
            "emu_ppsspp_fullname": "Emulador de PlayStation Portable",
            "emu_ppsspp_desc": "Corre tus juegos de PSP en HD con texturas mejoradas. Soporta guardado rápido, multijugador asíncrono y mapeado de controles avanzado.",
            "emu_pcsx2_fullname": "Emulador de PlayStation 2",
            "emu_pcsx2_desc": "El estándar de oro para emulación de PS2. Soporta miles de juegos, mejoras gráficas mediante Vulkan y soporte para DualShock nativo.",
            "emu_rpcs3_fullname": "Emulador de PlayStation 3",
            "emu_rpcs3_desc": "Emulador experimental de código abierto que permite jugar títulos de PS3 en PC. Requiere hardware potente y el firmware original de Sony.",
            "emu_duckstation_fullname": "Emulador de PlayStation 1",
            "emu_duckstation_desc": "Increíble emulador de PSX enfocado en la jugabilidad, velocidad y mantenibilidad a largo plazo. Incluye corrección de perspectiva de texturas."
        },
        "en": {
            // Main Navigation
            "dashboard": "DASHBOARD",
            "library": "LIBRARY",
            "downloads": "DOWNLOADS",
            "settings": "SETTINGS",
            "explore": "EXPLORE",
            "play": "PLAY",
            "back": "BACK",

            // Settings Tabs
            "tab_general": "General",
            "tab_library": "Library",
            "tab_services": "Services",
            "tab_advanced": "Advanced",
            "tab_about": "About",

            // Settings Panels
            "system_preferences": "SYSTEM PREFERENCES",
            "global_language": "Global Language",
            "global_language_desc": "Select the interface language",
            "auto_theme": "Automatic Theme",
            "auto_theme_desc": "Sync light/dark mode automatically",
            
            "paths_scanning": "PATHS & SCANNING",
            "roms_path": "ROMS FOLDER",
            "emus_path": "EMULATORS FOLDER",
            "change_btn": "CHANGE",
            "collection_info": "COLLECTION INFO",
            "games_registered": "You have %1 games registered.",
            "section_downloads_ref": "To update your library, go to the DOWNLOADS section.",

            "external_resources": "EXTERNAL RESOURCES",
            "api_screenscraper": "ScreenScraper API",
            "api_desc": "Enter your credentials to download covers automatically.",
            "api_saved": "Settings saved. M.A.N.G.O will use them when syncing.",

            "mango_engine": "M.A.N.G.O ENGINE (NATIVE)",
            "opt_multicore": "Multi-core Optimization",
            "opt_multicore_desc": "Uses all CPU threads for hashing",
            "opt_integrity": "Integrity Check",
            "opt_integrity_desc": "Check for corrupt files during scanning",
            "opt_low_latency": "Ultra-Low Latency Mode",
            "opt_low_latency_desc": "Asynchronous scraping optimized by Rust",
            "purge_cache": "PURGE ENGINE CACHE",

            "about_desc": "EmuManager is <b>Free and Open Source</b> software, powered by the <b>M.A.N.G.O</b> native engine. Built with a <b>Local-First</b> approach, we guarantee absolute privacy: your data and library stay exclusively on your device, with no telemetry or cloud dependencies.",
            "os_spec": "OPERATING SYSTEM",
            "engine_spec": "NATIVE ENGINE",
            "ram_spec": "RAM MEMORY",
            "cpu_spec": "PROCESSING",
            "python_spec": "PYTHON RUNTIME",
            "contribute_github": "CONTRIBUTE ON GITHUB",
            "official_site": "OFFICIAL SITE",
            "copyright": "© 2026 PAIDEX | EMUMANAGER TEAM | MIT LICENSE",

            // Library & Dashboard
            "empty_library": "EMPTY LIBRARY",
            "empty_library_desc": "No games detected yet.\nGo to Settings to add scan paths.",
            "configure_paths_btn": "CONFIGURE PATHS",
            "search_placeholder": "Instant search...",
            "stats_total_games": "TOTAL GAMES",
            "stats_play_time": "PLAY TIME",
            "stats_most_played": "TOP PLATFORM",
            "stats_last_game": "RECENT",
            "stats_favorites": "FAVORITES",

            // Downloads
            "sync_center": "SYNC CENTER",
            "sync_center_desc": "Manage your library, media, and emulators from one place",
            "check_updates_btn": "CHECK FOR UPDATES ↻",
            "sync_roms": "Sync ROMs",
            "sync_media": "Metadata & Art",
            "emu_gallery": "EMULATOR GALLERY",
            "scan_idle": "Scan local directories",
            "scan_done": "Library up to date ✓",
            "scrape_idle": "ScreenScraper + Libretro",
            "scrape_done": "Media synced ✓",

            // New Additions
            "settings_title": "SETTINGS",
            "username_placeholder": "Username",
            "password_placeholder": "Password",
            "engine_online": "Engine Online",
            "cpu_threads": "%1 threads",
            "status_active": "Active",
            "status_inactive": "Inactive",

            // Card Extras
            "games_suffix": "GAMES",
            "games_abbr": "GM",
            "play_time_abbr": "TIME",
            "launch_adventure": "LAUNCH ADVENTURE",
            "status_processing": "PROCESSING...",
            "status_installed": "INSTALLED",
            "status_available": "AVAILABLE",
            "btn_install": "INSTALL",
            "btn_update": "UPDATE",
            "btn_uninstall": "UNINSTALL",

            // Startup & Workers
            "initializing": "INITIALIZING...",
            "startup_native": "Engaging M.A.N.G.O native engine (Rust)...",
            "startup_db": "Verifying library integrity...",
            "startup_assets": "Optimizing media and covers cache...",
            "startup_ready": "Missions initialized. Welcome.",
            "core_downloading": "Downloading %1 using M.A.N.G.O...",
            "core_installed": "Core installed!",
            "install_success": "✓ Installation completed.",
            "install_failed": "Orchestration failed.",

            // System Info Tech Keys
            "tech_active": "ACTIVE",
            "tech_inactive": "INACTIVE",
            "tech_threads": "THREADS",
            "tech_cores": "CORES",
            "tech_engine_ready": "ENGINE SYNCED",
            "tech_system_specs": "SYSTEM SPECIFICATIONS",
            "pill_free_open": "FREE & OPEN SOURCE",
            "pill_local_privacy": "LOCAL PRIVACY",
            "engine_tool_tip": "Native Orchestration Engine: %1",

            // Scan & Scrape Workers
            "scan_starting": "Scanning files with M.A.N.G.O...",
            "scan_no_roms": "No supported ROMs found.",
            "scan_registering": "Registering: %1",
            "scan_finished": "Scan finished. %1 new games registered.",
            "scrape_starting": "Starting M.A.N.G.O Batch Scraper...",
            "scrape_finished": "Scraping completed successfully.",

            // Game Details
            "loading": "LOADING...",
            "no_description": "No description available.",
            "no_description_template": "No additional description available for this %1 title.",

            // Dashboard Extras
            "command_center": "COMMAND CENTER",
            "operational": "OPERATIONAL",
            "next_challenge": "NEXT CHALLENGE",
            "platform_prefix": "PLATFORM: ",
            "resume_mission": "▶ RESUME MISSION",
            "idle": "IDLE",
            "mango_monitor": "M.A.N.G.O ENGINE (VITAL-LOG)",
            "processing_caps": "PROCESSING",
            "running_caps": "RUNNING",
            "status_prefix": "STATUS: ",
            "ready_caps": "READY",
            "waiting_caps": "WAITING",

            // RetroArch Panel
            "ra_settings": "RETROARCH SETTINGS",
            "ra_management": "Advanced core management",
            "ra_not_detected": "⚠️ RETROARCH NOT DETECTED",
            "ra_install_warning": "You must install RetroArch from the main panel before downloading cores.",
            "core_ready": "Core ready to use",
            "core_available": "Available for download",
            "btn_delete": "DELETE",

            // Emulator States
            "emu_status_installed": "✓ Installed",
            "emu_status_available": "Available to install",

            // Emulator Repository
            "emu_retroarch_fullname": "Universal Libretro Repository",
            "emu_retroarch_desc": "The ultimate frontend for emulation. Manage hundreds of cores from a single interface with shader support and cloud saving.",
            "emu_dolphin_fullname": "Standalone GameCube / Wii Emulator",
            "emu_dolphin_desc": "Powerful emulator with high-resolution support (4K), online play, and near-perfect compatibility with the Wii and GameCube catalog.",
            "emu_ppsspp_fullname": "PlayStation Portable Emulator",
            "emu_ppsspp_desc": "Run your PSP games in HD with enhanced textures. Supports quick saves, asynchronous multiplayer, and advanced control mapping.",
            "emu_pcsx2_fullname": "PlayStation 2 Emulator",
            "emu_pcsx2_desc": "The gold standard for PS2 emulation. Supports thousands of games, graphical enhancements via Vulkan, and native DualShock support.",
            "emu_rpcs3_fullname": "PlayStation 3 Emulator",
            "emu_rpcs3_desc": "Experimental open-source emulator that allows playing PS3 titles on PC. Requires powerful hardware and original Sony firmware.",
            "emu_duckstation_fullname": "PlayStation 1 Emulator",
            "emu_duckstation_desc": "Incredible PSX emulator focused on playability, speed, and long-term maintainability. Includes texture perspective correction."
        }
    })
}
