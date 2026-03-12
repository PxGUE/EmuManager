# EmuManager 🎮

![Versión](https://img.shields.io/badge/version-0.1.5--alpha-blue.svg)
![Licencia](https://img.shields.io/badge/license-GNU%20GPLv3-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)

- **Fondos de Consola Dinámicos**: Nuevo sistema que descarga fondos de alta resolución específicos para cada sistema.
- **Background Sharing**: Múltiples emuladores de una misma consola comparten el mismo arte de fondo, ahorrando espacio y manteniendo la coherencia visual.

EmuManager es un gestor integral de juegos retro con una interfaz moderna y sumamente intuitiva, construida con **PyQt6** y **Asyncio**. Te permite descargar, organizar y ejecutar tus emuladores y ROMs clásicas desde un solo lugar, de una forma visualmente atractiva y fácil de usar en entornos de escritorio.

## ✨ Características Principales

- **Interfaz Nativa Premium**: Construida con PyQt6 para una experiencia fluida y robusta en escritorio.
- **Gestión Centralizada**: Configura y administra tus emuladores favoritos (mGBA, Dolphin, PCSX2, DuckStation, SNES9x, PPSSPP, entre otros).
- **Descarga Directa**: Descarga e instala emuladores directamente desde la aplicación.
- **Escáner Inteligente**: Encuentra automáticamente tus ROMs y las organiza por consola.
- **Artwork Scraper**: Sistema de búsqueda por similitud (Fuzzy Match) contra el índice de Libretro para encontrar carátulas automáticamente.
- **Carrusel de Consolas**: Navegación animada entre consolas con imagen de fondo, degradado de color y estadísticas de juego.
- **Búsqueda en Tiempo Real**: Barra de búsqueda con limpieza rápida (botón ✕) para filtrar juegos al instante.
- **Seguimiento de Tiempo**: Registra automáticamente cuánto tiempo has dedicado a cada juego.
- **Multi-idioma**: Soporte para Español e Inglés.

## 🚀 Requisitos y Configuración

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/PxGUE/EmuManager.git
   cd EmuManager
   ```

2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

*Nota: Requiere Python 3.9 o superior.*

## 📦 Dependencias

| Paquete | Versión mínima | Uso |
|---|---|---|
| PyQt6 | 6.7.0 | Interfaz gráfica |
| qasync | 0.28.0 | Integración asyncio + Qt |
| aiohttp | 3.11.0 | Descargas HTTP asíncronas |
| beautifulsoup4 | 4.13.0 | Scraping de artwork |
| psutil | 6.1.0 | Gestión de procesos de emuladores |

## ⚙️ Instrucciones de Uso (Guía Paso a Paso)

Para que EmuManager funcione correctamente, sigue estos pasos:

### 1. Configuración Inicial (Primer Inicio)
Al abrir la aplicación por primera vez, ve a la pestaña de **Configuración** (`⚙️`) y define las rutas:
- **Ruta de Emuladores**: Carpeta donde se descargarán los ejecutables.
- **Ruta de ROMs/Juegos**: Carpeta principal de tu colección de juegos.

### 2. Organización de tus Juegos
Coloca tus ROMs en las carpetas que el programa creará automáticamente (GBA, SNES, PS1, etc.) para que el escáner pueda identificarlas correctamente.

### 3. Instalación de Emuladores
En la pestaña de **Descargas** (`⬇️`), selecciona el emulador deseado y pulsa **Instalar**. El sistema se encarga del resto.

### 4. Escaneo de la Biblioteca
En la pestaña de **Biblioteca** (`📚`), entra en la consola deseada y pulsa **REFRESCAR**. El programa buscará los juegos y descargará su arte oficial automáticamente.

### 5. ¡A Jugar!
Haz clic en cualquier tarjeta de juego para lanzarlo instantáneamente con su emulador.

---

## 👨‍💻 Autor
- **Christian A. Ordoñez** - *Desarrollador Principal*
- Correo: cris.ordonezal@gmail.com

## 📄 Licencia
Este proyecto está bajo la [Licencia GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).