# 🕹️ EmuManager

**EmuManager** es una aplicación diseñada para gestionar y jugar colecciones de videojuegos clásicos desde una interfaz moderna y fluida. Se centra en el alto rendimiento, la portabilidad y el respeto absoluto por tus archivos originales.

---

## 🚀 Características Principales

*   **Alto Rendimiento:** Motor nativo **M.A.N.G.O.** (Multithreaded Asynchronous Native Game Orchestrator) para procesar miles de juegos en segundos sin bloquear la interfaz.
*   **Interfaz Moderna:** Construida con **QML (Qt Quick)** para ofrecer efectos visuales fluidos y una navegación intuitiva.
*   **Instalación Inteligente:** Orquestación automática de emuladores (RetroArch, Dolphin, etc.) y descarga de núcleos de Libretro.
*   **Privacidad Local:** Todos los datos, carátulas y configuraciones se guardan localmente en tu equipo. No hay telemetría ni uso de la nube.
*   **Respeto por el Dato:** EmuManager lee tus rutas de juegos pero **NUNCA** mueve, renombra ni modifica tus ROMs originales.

---

## 🛠️ Stack Tecnológico

EmuManager combina la flexibilidad de Python con la potencia de M.A.N.G.O:
*   **Frontend:** QML (Qt Quick) para la interfaz de usuario.
*   **Lógica:** Python 3.12+ (vía PySide6).
*   **Motor (Core):** **M.A.N.G.O.** para escaneo masivo, hashing y orquestación de red.
*   **Base de Datos:** SQLite3 local.

---

## 🚦 Instalación y Uso

### Requisitos Previos
*   Tener instalado **Python 3.12** o superior.
*   Cuenta de ScreenScraper (Opcional, para descargar portadas).

### Pasos para iniciar
1.  **Clona el repositorio** o descarga los archivos.
2.  **Instala las dependencias** de Python:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Ejecuta la aplicación:**
    ```bash
    python emumanager/app.py
    ```

---

## 📜 Filosofía de Desarrollo

*   **Local-First:** La aplicación debe funcionar sin conexión a Internet (salvo para descargas de metadatos o emuladores).
*   **Portabilidad:** Puedes copiar la carpeta de EmuManager a otro disco y todo seguirá funcionando gracias a las rutas relativas.
*   **Código Abierto:** Gratuito y diseñado para la comunidad de entusiastas de la emulación.

---

<div align="center">
  🚀 <i>Organiza tu colección al siguiente nivel con EmuManager.</i>
</div>
