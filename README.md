<div align="center">
  <img src="doc/assets/logo_wide.svg" alt="EmuManager Logo" width="400">
  
  # 🌌 EmuManager: The Nebula Ecosystem
  **La Orquestación Definitiva para el Retrogaming Moderno**

  [![Status](https://img.shields.io/badge/Status-Ecosystem_v0.5.0-00f2ff?style=for-the-badge)](https://github.com/PxGUE/EmuManager)
  [![Engine](https://img.shields.io/badge/Engine-M.A.N.G.O-orange?style=for-the-badge)](https://github.com/PxGUE/EmuManager/tree/main/mango)
  [![AI](https://img.shields.io/badge/AI-M.A.I_Active-blueviolet?style=for-the-badge)](https://github.com/PxGUE/EmuManager)
</div>

---

## 🚀 Bienvenido a la Nueva Era de la Emulación
**EmuManager** no es un gestor de ROMs convencional. Es un ecosistema completo diseñado para ser **espectacular al usar y sencillo de configurar**. Olvida las hojas de cálculo aburridas y los menús arcaicos. Entra en una experiencia cinematográfica impulsada por procesamiento nativo e inteligencia artificial.

### 🥭 M.A.N.G.O Engine (Core Nativo)
El **Multithreaded Asynchronous Native Game Orchestrator** es el músculo de la aplicación. Escrito en **Rust**, garantiza un rendimiento inigualable:
- **Lightning Scan**: Escaneo de miles de archivos en segundos.
- **Native Scraping**: Ahora con búsqueda integrada en Wikipedia directamente en binario para una velocidad de red superior.
- **Non-Blocking**: Arquitectura asíncrona total; tu interfaz nunca se congelará, sin importar el trabajo que haya de fondo.

### 🧠 M.A.I (Mango Artificial Intelligence)
Tu asistente personal de metadatos. Basado en modelos de lenguaje ligeros (SmolLM2-135M), M.A.I vive en tu PC y se encarga del trabajo sucio:
- **Refinamiento Semántico**: Lee información técnica y la transforma en descripciones bellas y coherentes.
- **Identificación de Joyas**: Encuentra datos sobre desarrolladores, géneros y fechas omitidas por los scrapers tradicionales.
- **100% Local**: Tu privacidad es absoluta. M.A.I no envía ni un solo bit de información a la nube.

---

## 🎨 Filosofía "Nebula Kinetic"
Cada píxel cuenta. EmuManager sigue una línea estética estricta:
- **Visual Excellence**: Efectos de **Glassmorphism**, desenfoques dinámicos (Acrylic) y paletas de colores armónicas.
- **Zero-Hex Policy**: Todos los colores nacen de un sistema centralizado en el tema, permitiendo cambios de atmósfera globales instantáneos.
- **Micro-interacciones**: Animaciones fluidas en cada botón, card y transición para que la app se sienta viva.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Rol |
| :--- | :--- | :--- |
| **Frontend** | `QML` / `Qt Quick` | Interfaz de alta fidelidad, animaciones y fluidez. |
| **Orquestador** | `Python 3.11` | Lógica de negocio, gestión de señales y bridge de IA. |
| **Motor** | `Rust` / `PyO3` | Hashing, escaneo masivo, scraping nativo y multi-threading. |
| **Inteligencia** | `Llama-cpp` | Procesamiento de lenguaje natural local (M.A.I). |
| **Persistencia** | `SQLite3` | Base de datos robusta, escalable y totalmente local. |

---

## 🚥 Guía de Despegue

### Requisitos Mínimos
- **Python 3.11** o superior.
- **Compilador de Rust** (para el motor M.A.N.G.O).

### Instalación Express
1. **Obtener el código:**
   ```bash
   git clone https://github.com/PxGUE/EmuManager.git
   cd EmuManager
   ```
2. **Preparar el entorno:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Compilar el corazón (M.A.N.G.O):**
   ```powershell
   # En Windows
   python scripts/build_engine.py
   ```
4. **Iniciar EmuManager:**
   ```bash
   python emumanager/app.py
   ```

---

## 🔧 Flujos de Poder (Slash Commands)
El desarrollo se apoya en comandos de automatización internos:
- `/compile-mango`: Reconstruye el motor Rust.
- `/hard-reset`: Limpieza profunda del entorno y datos locales.
- `/theme-check`: Validador de consistencia visual (No Hardcoded Colors).
- `/i18n-check`: Asegura que el ecosistema hable tu idioma.

---

<div align="center">
  <br>
  Creado con pasión por la preservación y el diseño.
  <br>
  <b>EmuManager Project &copy; 2026</b>
</div>
