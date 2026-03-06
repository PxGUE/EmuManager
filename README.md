# EmuManager 🎮

![Versión](https://img.shields.io/badge/version-0.1.0--alpha-blue.svg)
![Licencia](https://img.shields.io/badge/license-GNU%20GPLv3-green.svg)

EmuManager es un gestor integral de juegos retro con una interfaz moderna y sumamente intuitiva, construida con Flet (Flutter para Python). Te permite descargar, organizar y ejecutar tus emuladores y ROMs clásicas desde un solo lugar, de una forma visualmente atractiva y fácil de usar.

## ✨ Características Principales

- **Interfaz Moderna**: Diseño minimalista, responsivo y adaptativo.
- **Gestión Centralizada**: Configura y administra tus emuladores favoritos (mGBA, Dolphin, PCSX2, DuckStation, SNES9x, Genesis Plus GX, entre otros).
- **Descarga Directa**: Descarga e instala emuladores directamente desde la aplicación.
- **Escáner Inteligente**: Encuentra automáticamente tus ROMs y las organiza por consola.
- **Scraper de Arte Automático**: Descarga automáticamente las carátulas (boxarts) y logos correspondientes a tus juegos.
- **Búsqueda en Tiempo Real**: Encuentra rápidamente cualquier juego en tu colección mediante una potente barra de búsqueda.
- **Ejecución de Juegos**: Lanza tus juegos directamente en el emulador correspondiente con un solo clic.

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

*Nota: Dependiendo de tu sistema y de los emuladores seleccionados, asegúrate de tener instaladas las dependencias gráficas u otros paquetes del sistema operativo necesarios.*

## ⚙️ Instrucciones de Uso (Guía Paso a Paso)

Para que EmuManager funcione correctamente, sigue estos pasos:

### 1. Configuración Inicial (Primer Inicio)
Al abrir la aplicación por primera vez, lo más importante es configurar las rutas de trabajo:
- Ve a la pestaña de **Configuración** (`⚙️`).
- **Ruta de Emuladores**: Selecciona una carpeta vacía donde quieras que el programa descargue y guarde los archivos de los emuladores (.exe, AppImages, cores, etc.).
- **Ruta de ROMs/Juegos**: Selecciona la carpeta principal donde guardarás tus juegos. 

### 2. Organización de tus Juegos (Muy Importante)
Una vez que selecciones la **Ruta de ROMs**, EmuManager creará automáticamente (o esperará encontrar) subcarpetas específicas para cada sistema. **Debes colocar tus juegos dentro de la carpeta correspondiente para que el escáner los encuentre**:
- `GBA/` -> Juegos de Game Boy Advance (.gba)
- `SNES/` -> Juegos de Super Nintendo (.sfc, .smc)
- `GENESIS/` -> Juegos de Sega Genesis (.md, .bin)
- `PS1/` -> Juegos de PlayStation 1 (.bin/cue, .chd)
- `PS2/` -> Juegos de PlayStation 2 (.iso, .chd)
- `GAMECUBE/` -> Juegos de GameCube (.iso, .rvz)
- `WII/` -> Juegos de Wii (.wbfs, .rvz)

### 3. Instalación de Emuladores
Navega a la pestaña de **Descargas** (`⬇️`). Verás una lista de emuladores populares:
- Haz clic en **Instalar** en el emulador que desees. El programa lo descargará, extraerá y configurará automáticamente en la ruta que elegiste en el paso 1.
- *Nota: Si ya tienes el emulador instalado mediante el programa, el botón cambiará a "Desinstalar".*

### 4. Escaneo de la Biblioteca
Una vez que tengas tus ROMs en sus carpetas correspondientes:
- Ve a la pestaña de **Biblioteca** (`📚`).
- Selecciona la consola que quieres jugar.
- Haz clic en el botón **ESCANEAR**. El programa buscará los archivos, los añadirá a tu colección y descargará automáticamente la carátula y el arte del juego desde servidores oficiales.

### 5. ¡A Jugar!
- Simplemente haz clic en la tarjeta de cualquier juego para ver su información.
- Haz clic en el botón de **Play** (el ícono azul que aparece al pasar el ratón sobre un juego) para lanzar el emulador directamente con ese juego cargado.

### 6. Cambio de Idioma
EmuManager es multilingüe. Puedes cambiar entre **Español** e **Inglés** en cualquier momento desde la pestaña de **Configuración**. El cambio se aplica instantáneamente a toda la interfaz.

---

## ⚙️ How to Use (Step-by-Step Guide)

### 1. Initial Setup
When you open the app for the first time, you need to configure the working paths:
- Go to the **Settings** tab (`⚙️`).
- **Emulators Path**: Select an empty folder where you want the program to download and store emulator files.
- **ROMs/Games Path**: Select the main folder where you will store your game collection.

### 2. Organizing Your Games (Crucial)
After selecting the **ROMs Path**, EmuManager will automatically create (or look for) specific subfolders for each system. **You must place your games inside the correct subfolder for the scanner to find them**:
- `GBA/`, `SNES/`, `GENESIS/`, `PS1/`, `PS2/`, `GAMECUBE/`, `WII/`, etc.

### 3. Installing Emulators
Go to the **Downloads** tab (`⬇️`):
- Click **Install** on any emulator. The program will handle the download and setup automatically.

### 4. Library Scanning
Once your ROMs are in place:
- Go to the **Library** tab (`📚`).
- Pick a console and click **SCAN**. The program will find your games and automatically download box art and metadata.

### 5. Play!
- Click on any game card to see details, or click the **Play** button that appears when hovering to start the game directly.

## 👨‍💻 Autor
- **Christian A. Ordoñez** - *Desarrollador Principal*
- Correo: cris.ordonezal@gmail.com

## 📄 Licencia

Este proyecto está bajo la Licencia GNU GPLv3 - mira el archivo [LICENSE](LICENSE) o [detalles de la licencia](https://www.gnu.org/licenses/gpl-3.0.html) para más detalles.

---