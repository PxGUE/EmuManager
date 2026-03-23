---
trigger: always_on
---

# Reglas de Proyecto: EmuManager

## Filosofía Core
- **FOSS & Privacidad:** La app es gratuita, de código abierto y "Local-First". 
- **Integridad de Datos:** NUNCA modifiques, muevas ni renombres las ROMs. Lee las rutas absolutas del usuario y guárdalas en SQLite.
- **Gestión de APIs:** El usuario provee sus propias credenciales (ej. ScreenScraper, RetroAchievements).

## Stack Tecnológico
- **Frontend (UI):** Exclusivamente `QML` (Qt Quick) para la vista, orquestado por `PySide6` (Controlador/Modelo).
- **Backend (Lógica):** Python (3.12+). Uso estricto de `pathlib` para compatibilidad nativa Linux/Windows.
- **Core (Rendimiento):** Rust (Edición 2024, vía `PyO3`) para escaneo de archivos y hashing MD5/CRC32.
- **Base de Datos:** SQLite3 local.

## Arquitectura y Navegación
1. **Patrón MVC Estricto:** Los archivos `.qml` solo manejan UI y animaciones. La lógica, los hilos y el acceso a base de datos ocurren en Python (`QAbstractListModel` para listas masivas de juegos).
2. **Layout Principal:** Barra de navegación lateral (Sidebar) con 4 secciones:
   - **Dashboard:** Widgets de descubrimiento local, efemérides, estadísticas de juego y estado del motor Rust.
   - **Biblioteca:** Cuadrícula de juegos (Lazy loading) con panel lateral de detalles.
   - **Descargas:** Gestor no intrusivo en segundo plano.
   - **Configuración:** Gestión de rutas, APIs y temas.
3. **Modularidad y Componentes:** Se debe priorizar la creación de componentes reusables en `ui/components/` (EmuButton, ConsoleCard, RomItem, etc.) para mantener un código limpio y evitar la duplicidad de lógica visual.
4. **Gestión de Emuladores:** Descarga de cores de Libretro para consolas clásicas; orquestación del OS (Flatpak/winget) para emuladores standalone modernos.
5. **Soporte Multi-idioma (i18n):** Todo texto visible en la interfaz debe estar desacoplado del código QML a través de un sistema de traducción dinámico (Español/Inglés inicialmente).

## Estilo de Diseño
- Tema Oscuro (Dark Mode), bordes redondeados, tipografía moderna y transiciones fluidas.