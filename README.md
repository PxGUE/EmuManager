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
   git clone https://github.com/TU_USUARIO/EmuManager.git
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

## ⚙️ Uso

1. **Configuración de Rutas**: Al iniciar, entra en la pestaña de `Configuración` (⚙️). Selecciona el directorio donde quieres que se instalen los emuladores y la carpeta raíz donde están almacenados tus ROMs.
2. **Descarga de Emuladores**: Navega a la sección `Descargas` para ver la lista de emuladores recomendados. Haz clic en "Instalar", y se encargarán automáticamente.
3. **Escaneo de Biblioteca**: Entra a tu `Biblioteca` y utiliza el botón "Escanear" en la consola elegida; esto buscará todos los juegos y descargará su arte oficial disponible.

## 👨‍💻 Autor
- **Christian A. Ordoñez** - *Desarrollador Principal*
- Correo: cris.ordonezal@gmail.com

## 📄 Licencia

Este proyecto está bajo la Licencia GNU GPLv3 - mira el archivo [LICENSE](LICENSE) o [detalles de la licencia](https://www.gnu.org/licenses/gpl-3.0.html) para más detalles.

---