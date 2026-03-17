# EmuManager

![Versión](https://img.shields.io/badge/version-0.1.12--alpha-blue.svg)
![Licencia](https://img.shields.io/badge/license-GNU%20GPLv3-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)

EmuManager es un gestor integral de videojuegos retro diseñado para ofrecer una experiencia premium en entornos de escritorio. Construido con **PySide6 (Qt)** y **QML**, combina una interfaz moderna y declarativa con la potencia de **Asyncio** para una gestión fluida y eficiente de emuladores y ROMs.

## 🚀 Características Principales

- **Interfaz "Glassmorphic" Premium**: Un diseño visualmente impactante con efectos de cristal, animaciones fluidas y una navegación intuitiva.
- **Scraper Hub Avanzado**: Sistema de búsqueda inteligente que integra múltiples fuentes (**RAWG, TheGamesDB, SteamGridDB**) para obtener metadatos y arte oficial de alta calidad mediante algoritmos de *fuzzy matching*.
- **Gestión Automatizada de Emuladores**: Descarga, instalación y configuración automática de una amplia variedad de emuladores (RetroArch, Dolphin, PCSX2, DuckStation, Ryubing, Eden, Vita3K, y más).
- **Biblioteca Dinámica**: Escaneo inteligente de ROMs organizado por consolas, con seguimiento de tiempo de juego y estadísticas en tiempo real.
- **Motor Multi-idioma**: Soporte completo para Español e Inglés con cambio dinámico de interfaz sin necesidad de reiniciar.
- **Seguridad y Persistencia**: Integración con **Keyring** y **SecretStorage** para el manejo seguro de claves de API y configuraciones críticas.
- **Soporte de Archivos Modernos**: Compatibilidad nativa con formatos comprimidos como `.7z` y `.zstd` para optimizar el almacenamiento.

## 🛠️ Requisitos e Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/PxGUE/EmuManager.git
   cd EmuManager
   ```

2. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

*Nota: Se recomienda el uso de un entorno virtual (venv).*

## 📦 Dependencias Core

| Paquete | Versión | Propósito |
|---|---|---|
| **PySide6** | ≥ 6.8.0 | Framework de interfaz gráfica (Qt/QML). |
| **qasync** | ≥ 0.28.0 | Puente entre el event loop de Qt y Asyncio. |
| **aiohttp** | ≥ 3.11.0 | Comunicaciones de red y descargas asíncronas. |
| **beautifulsoup4** | ≥ 4.13.0 | Procesamiento de metadatos y scraping web. |
| **psutil** | ≥ 7.0.0 | Monitoreo y control de procesos de emuladores. |
| **py7zr** | ≥ 1.0.0 | Manejo de archivos comprimidos 7z. |
| **keyring** | ≥ 25.7.0 | Almacenamiento seguro de credenciales. |

## 📖 Guía de Uso Rápido

1. **Configuración Inicial**: Al iniciar, dirígete a la pestaña de **Configuración** para definir tus rutas de emuladores y ROMs. EmuManager creará la estructura de carpetas necesaria.
2. **Instalación de Emuladores**: En la sección de **Descargas**, elige tus consolas favoritas y pulsa "Instalar". El sistema descargará y preparará los ejecutables automáticamente.
3. **Poblar la Biblioteca**: Coloca tus juegos en las carpetas correspondientes y pulsa **REFRESCAR** en la biblioteca. El Scraper Hub se encargará de buscar el arte y la información de cada título.
4. **¡A Jugar!**: Haz clic en cualquier juego para lanzarlo instantáneamente. El programa registrará automáticamente tu tiempo de sesión.

---

## 👨‍💻 Autor
- **Christian A. Ordoñez** - *Desarrollador Principal*
- **GitHub**: [@PxGUE](https://github.com/PxGUE)
- **Email**: [cris.ordonezal@gmail.com](mailto:cris.ordonezal@gmail.com)

## ⚖️ Licencia
Este proyecto está bajo la [Licencia GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).