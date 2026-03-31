# <div align="center">🕹️ EmuManager</div>

<div align="center">
  <br>
  <b>La Orquestación Definitiva para tu Colección de Videojuegos Clásicos.</b><br>
  <i>Potenciado por el motor nativo <b>M.A.N.G.O (Multithreaded Asynchronous Native Game Orchestrator)</b></i>
  <br><br>
  <img src="https://img.shields.io/badge/Status-Activo-00f2ff?style=for-the-badge&logoColor=white" alt="Status Badge">
  <img src="https://img.shields.io/badge/Licence-MIT-F2A71B?style=for-the-badge" alt="Licence Badge">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge">
  <img src="https://img.shields.io/badge/Rust-Core-000000?style=for-the-badge&logo=rust&logoColor=white" alt="Rust Badge">
</div>

---

## 🌌 Filosofía: "Nebula Kinetic"
EmuManager no es solo un backend. Es una experiencia visual diseñada bajo la estética **Nebula Kinetic**:
- **Fluidez Extrema:** Animaciones basadas en curvas QML para una navegación orgánica.
- **Zero-Hex Policy:** Un sistema de color centralizado e inteligente gestionado exclusivamente en `Theme.qml`.
- **Strict I18n:** Traducción local instantánea (ES/EN) para todos los elementos, desde la UI hasta los logs técnicos.

## 🚀 Características Premium

### 🥭 M.A.N.G.O Engine (Core Nativo)
El corazón de EmuManager está escrito en **Rust (vía PyO3)**. Capaz de realizar escaneos masivos e hashing de miles de ROMs en segundos utilizando todos los hilos de tu CPU. 
- **Black Box Architecture:** Hilos dedicados para que la interfaz nunca se bloquee.
- **Integridad Total:** EmuManager **NUNCA** modifica, mueve ni renombra tus archivos.

### 🧩 Orquestación Automática
- **Instalación con un Click:** Descarga, extrae y configura emuladores (RetroArch, Dolphin, PCSX2, etc.) sin salir de la app.
- **Cores Libretro:** Gestión avanzada de núcleos desde un panel unificado.
- **Scraping Inteligente:** Integración con **ScreenScraper API** y metadatos de Libretro para carátulas en HD.

### 🛡️ Privacidad Local-First
Tus datos son tuyos. 
- Sin telemetría. Sin nube obligatoria.
- Almacenamiento SQLite local optimizado.
- Todos tus recursos (carátulas, logs, bases de datos) se quedan en tu equipo.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Función |
| :--- | :--- | :--- |
| **Interfaz (UI)** | **QML (Qt Quick)** | Presentación de alta fidelidad y animaciones. |
| **Controlador** | **PySide6 (Python)** | Orquestación de lógica y señales. |
| **Motor (Backend)** | **M.A.N.G.O (Rust)** | Escaneo, Hashing y Rendimiento Nativo. |
| **Persistencia** | **SQLite3** | Base de Datos local-first con ACID. |

---

## 🚦 Primeros Pasos

### Requisitos Previos
- **Python 3.11+**
- **Rust Compiler** (Opcional, solo si deseas recompilar el motor M.A.N.G.O).

### Instalación Rápida
1.  **Clonar el Repositorio:**
    ```bash
    git clone https://github.com/PxGUE/EmuManager.git
    cd EmuManager
    ```
2.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Compilar el Motor Nativo (Windows):**
    ```powershell
    ./.agent/workflows/compile-mango.ps1
    ```
4.  **Lanzar la Aventura:**
    ```bash
    python emumanager/app.py
    ```

---

## ⚙️ Flujos de Trabajo (Power User)
El proyecto incluye un conjunto de automatizaciones para mantener la calidad:
- `/compile-mango`: Compila el motor Rust según tu sistema operativo.
* `/hard-reset`: Reset total del entorno (limpieza de caché y datos).
* `/theme-check`: Validar que no hay colores hardcodeados (Zero-Hex).
* `/i18n-check`: Validar que todos los textos están en el sistema de traducción.

---

<div align="center">
  <br>
  Hecho con ❤️ para la comunidad de preservación de videojuegos.
  <br>
  <b>EmuManager Project - 2026</b>
</div>
