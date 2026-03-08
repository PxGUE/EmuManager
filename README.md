# EmuManager 🎮

![Versión](https://img.shields.io/badge/version-0.1.3--alpha-blue.svg)
![Licencia](https://img.shields.io/badge/license-GNU%20GPLv3-green.svg)

EmuManager es un gestor integral de juegos retro con una interfaz moderna y sumamente intuitiva, construida con **PyQt6** y **Asyncio**. Te permite descargar, organizar y ejecutar tus emuladores y ROMs clásicas desde un solo lugar, de una forma visualmente atractiva y fácil de usar en entornos de escritorio.

## ✨ Características Principales

- **Interfaz Nativa Premium**: Construida con PyQt6 para una experiencia fluida y robusta en escritorio.
- **Gestión Centralizada**: Configura y administra tus emuladores favoritos (mGBA, Dolphin, PCSX2, DuckStation, SNES9x, Genesis Plus GX, entre otros).
- **Descarga Directa**: Descarga e instala emuladores directamente desde la aplicación.
- **Escáner Inteligente**: Encuentra automáticamente tus ROMs y las organiza por consola.
- **Artwork 2.0 (Scraper Inteligente)**: Sistema de búsqueda por similitud (Fuzzy Match) contra el índice de Libretro para encontrar carátulas con 100% de precisión sin errores 404.
- **Búsqueda en Tiempo Real**: Encuentra rápidamente cualquier juego mediante una barra de búsqueda ultra-rápida.
- **Seguimiento de Tiempo**: Registra automáticamente cuánto tiempo has dedicado a cada juego.

## 🚀 Requisitos y Configuración

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/PxGUE/EmuManager.git
   cd EmuManager
   ```

2. Instalar los requerimientos (dependencias de Python):
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

*Nota: Requiere Python 3.9 o superior.*

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
Pasa el ratón por encima de cualquier juego para ver los detalles y haz clic para lanzarlo instantáneamente.

---

## 👨‍💻 Autor
- **Christian A. Ordoñez** - *Desarrollador Principal*
- Correo: cris.ordonezal@gmail.com

## 📄 Licencia
Este proyecto está bajo la Licencia GNU GPLv3 - mira el archivo [LICENSE](LICENSE) para más detalles.