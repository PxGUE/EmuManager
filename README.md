# 🕹️ EmuManager v0.2.5-alpha

<div align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Frontend-QML%20(Qt%20Quick)-41CD52.svg" alt="Frontend: QML">
  <img src="https://img.shields.io/badge/Backend-PySide6%20(Python)-3776AB.svg" alt="Backend: PySide6">
  <img src="https://img.shields.io/badge/Engine-Rust%20(MANGO)-DEA584.svg" alt="Engine: Rust">
  <img src="https://img.shields.io/badge/Database-SQLite3-003B57.svg" alt="Database: SQLite3">
</div>

---

## 🌟 La Experiencia Definitiva de Orquestación de Juegos

**EmuManager** no es solo un frontend; es un ecosistema local de alto rendimiento diseñado para coleccionistas y entusiastas del gaming. Construido bajo la filosofía **"Local-First & Private"**, EmuManager te otorga el control total de tu biblioteca digital con una interfaz premium inspirada en las consolas de nueva generación.

### 🥭 M.A.N.G.O: El Corazón de Acero (Rust)
El motor principal, **M.A.N.G.O.** (*Multithreaded Asynchronous Native Game Orchestrator*), está escrito íntegramente en **Rust (Edición 2024)**.
*   **Velocidad Extrema:** Escaneo de miles de archivos en milisegundos.
*   **Integridad de Datos:** Hashing nativo (MD5/CRC32) para identificación precisa de ROMs.
*   **Cero Lag:** Toda la carga pesada ocurre fuera del hilo de la interfaz de usuario.

### 🍱 Interfaz Premium (QML/PySide6)
Dile adiós a las interfaces toscas. EmuManager utiliza **Qt Quick (QML)** para ofrecer:
*   **Carrusel 3D Dinámico:** Navegación fluida entre consolas con efectos de *glassmorphism* y neón.
*   **Tarjetas de Control Inteligentes:** Gestión granular de emuladores, estadísticas de juego y tiempo total jugado.
*   **Modo Biblioteca Pro:** Galería de juegos con portadas en 2D/3D y búsqueda instantánea difusa (*fuzzy search*).

### 🛠️ Gestión de Emuladores de un Solo Click
Instala y configura tus motores de juego sin salir de la app.
*   **Orquestador Libretro:** Descarga automática de "núcleos" organizados por carpetas de consola.
*   **Configuración Local:** Tus partidas y estados de guardado se quedan contigo, en tu PC.
*   **Tooltips e Info Intuitiva:** Nomenclatura amigable para humanos; porque no necesitas ser un experto para jugar.

---

## 🏗️ Arquitectura del Proyecto (MVC Estricto)

| Capa | Carpeta / Módulo | Propósito |
| :--- | :--- | :--- |
| **Vista (UI)** | `emumanager/ui/` | Componentes QML, temas y animaciones de hardware acelerado. |
| **Controlador** | `emumanager/controllers/` | Puentes PySide6 (Python) que orquestan la lógica y la UI. |
| **Backend** | `emumanager/backend/` | Acceso a SQLite, lógica de Libretro y el binario nativo de MANGO. |
| **Core (Rust)** | `mango_engine/` | Código fuente nativo para potencia de cálculo bruta vía PyO3. |

---

## 🚦 Guía Rápida de Inicio

### 1. Requisitos
*   Python 3.12+
*   Toolchain de Rust (para compilar el motor)
*   `pip install -r requirements.txt`

### 2. Compilación del Motor (M.A.N.G.O)
Si deseas compilar el núcleo nativo tú mismo:
```bash
cd mango_engine
maturin build --release
```

### 3. Lanzamiento
```bash
python emumanager/app.py
```

---

## 📜 Filosofía: Privacidad y Respeto
*   **NUNCA** moveremos ni renombraremos tus ROMs. Respetamos tu estructura de archivos.
*   **CERO Telemetría:** Tus credenciales de APIs (ScreenScraper, RetroAchievements) se guardan solo en tu SQLite local.
*   **Gratis y Open Source:** Hecho por y para la comunidad.

---
<div align="center">
  🚀 <i>Lleva tu colección al siguiente nivel con EmuManager.</i>
</div>
