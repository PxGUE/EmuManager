AVAILABLE_EMULATORS = [
    {
        "id": "retroarch",
        "name": "RetroArch",
        "console": "Multi-system",
        "description": "El frontend más potente para emulación. Permite ejecutar múltiples núcleos (consolas) desde una sola interfaz.",
        "folder": "Multi",
        "github": "libretro/RetroArch",
        "fallback_url": "https://buildbot.libretro.com/stable/1.17.0/linux/x86_64/RetroArch.7z",
        "extensions": [".bin", ".cue", ".rom", ".zip"],
        "libretro_platform": None
    },
    {
        "id": "dolphin",
        "name": "Dolphin Emulator",
        "console": "GameCube / Wii",
        "description": "Emulador de GameCube y Wii de alto rendimiento. Soporta gráficos en HD y juego en red.",
        "folder": "GameCube-Wii",
        "github": "pkgforge-dev/Dolphin-emu-AppImage",
        "fallback_url": None,
        "extensions": [".iso", ".wbfs", ".gcm", ".rvz"],
        "libretro_platform": "Nintendo - GameCube"
    },
    {
        "id": "pcsx2",
        "name": "PCSX2",
        "console": "PlayStation 2",
        "description": "El emulador estándar de PlayStation 2. Compatible con la inmensa mayoría del catálogo de PS2.",
        "folder": "PS2",
        "github": "PCSX2/pcsx2",
        "fallback_url": None,
        "extensions": [".iso", ".bin", ".chd", ".gz"],
        "libretro_platform": "Sony - PlayStation 2"
    },
    {
        "id": "rpcs3",
        "name": "RPCS3",
        "console": "PlayStation 3",
        "description": "Emulador y debugger experimental de PlayStation 3 en lenguaje C++ para Windows, Linux y BSD.",
        "folder": "PS3",
        "github": "RPCS3/rpcs3-binaries-linux",
        "fallback_url": None,
        "extensions": [".ps3", ".pkg", ".iso"],
        "libretro_platform": None
    },
    {
        "id": "ppsspp",
        "name": "PPSSPP",
        "console": "PlayStation Portable",
        "description": "Emulador de PSP rápido y portátil. Permite jugar en HD y soporta texturas personalizadas.",
        "folder": "PSP",
        "github": "hrydgard/ppsspp",
        "fallback_url": None,
        "extensions": [".iso", ".cso", ".pbp"],
        "libretro_platform": "Sony - PlayStation Portable"
    },
    {
        "id": "duckstation",
        "name": "DuckStation",
        "console": "PlayStation 1",
        "description": "Enfocado en la jugabilidad, velocidad y mantenibilidad a largo plazo de la primera PlayStation.",
        "folder": "PS1",
        "github": "stenzek/duckstation",
        "fallback_url": None,
        "extensions": [".bin", ".cue", ".chd", ".pbp", ".m3u"],
        "libretro_platform": "Sony - PlayStation"
    },
    {
        "id": "xemu",
        "name": "xemu",
        "console": "Original Xbox",
        "description": "Emulador de baja latencia y alta precisión de la Xbox original.",
        "folder": "Xbox",
        "github": "xemu-project/xemu",
        "fallback_url": None,
        "extensions": [".iso", ".xbe"],
        "libretro_platform": "Microsoft - Xbox"
    },
    {
        "id": "mgba",
        "name": "mGBA",
        "console": "Game Boy Advance",
        "description": "Emulador de GBA rápido y preciso. También soporta Game Boy y Game Boy Color.",
        "folder": "GBA",
        "github": "mgba-emu/mgba",
        "fallback_url": None,
        "extensions": [".gba", ".gbp", ".zip"],
        "libretro_platform": "Nintendo - Game Boy Advance"
    },
    {
        "id": "rmg",
        "name": "RMG (Rosalie's Mupen GUI)",
        "console": "Nintendo 64",
        "description": "Interfaz moderna para Mupen64Plus centrada en la facilidad de uso y alta compatibilidad.",
        "folder": "N64",
        "github": "Rosalie241/RMG",
        "fallback_url": None,
        "extensions": [".z64", ".n64", ".v64"],
        "libretro_platform": "Nintendo - Nintendo 64"
    },
    {
        "id": "mesen",
        "name": "Mesen",
        "console": "NES / SNES",
        "description": "Multi-emulador altamente preciso para NES, Game Boy, SNES, Master System y más.",
        "folder": "NES-SNES",
        "github": "SourMesen/Mesen2",
        "fallback_url": None,
        "extensions": [".nes", ".sfc", ".smc", ".zip"],
        "libretro_platform": "Nintendo - Nintendo Entertainment System"
    },
    {
        "id": "snes9x",
        "name": "Snes9x",
        "console": "SNES",
        "description": "Emulador de Super Nintendo clásico, ligero y altamente compatible.",
        "folder": "SNES",
        "github": "snes9xgit/snes9x",
        "fallback_url": None,
        "extensions": [".sfc", ".smc", ".zip"],
        "libretro_platform": "Nintendo - Super Nintendo Entertainment System"
    },
    {
        "id": "lime3ds",
        "name": "Lime3DS",
        "console": "Nintendo 3DS",
        "description": "Sucesor espiritual de Citra, optimizado para emular la Nintendo 3DS en hardware moderno.",
        "folder": "3DS",
        "github": "Lime3DS/Lime3DS",
        "fallback_url": None,
        "extensions": [".3ds", ".cia", ".app"],
        "libretro_platform": "Nintendo - Nintendo 3DS"
    },
    {
        "id": "switch",
        "name": "Switch (Sudachi)",
        "console": "Nintendo Switch",
        "description": "Emulador de Nintendo Switch basado en Sudachi, optimizado para Linux con soporte AppImage.",
        "folder": "Switch",
        "github": "TechDevangelist/Sudachi-AppImage",
        "fallback_url": "https://github.com/TechDevangelist/Sudachi-AppImage/releases/download/Snapshot-1.0.15/Sudachi-x86_64_v3.AppImage",
        "extensions": [".nsp", ".xci"],
        "libretro_platform": None
    }
]
