<div align="center">
  <img src="doc/assets/logo_wide.svg" alt="EmuManager Logo" width="400">
  
  # 🌌 EmuManager: The Nebula Ecosystem
  **La Orquestación Definitiva para el Retrogaming Moderno**

  [![Status](https://img.shields.io/badge/Status-Ecosystem_v0.5.0-00f2ff?style=for-the-badge)](https://github.com/PxGUE/EmuManager)
  [![Engine](https://img.shields.io/badge/Engine-M.A.N.G.O-orange?style=for-the-badge)](https://github.com/PxGUE/EmuManager/tree/main/mango)
  [![Local](https://img.shields.io/badge/Local--First-Guaranteed-green?style=for-the-badge)](https://github.com/PxGUE/EmuManager)
</div>

---

## 🚀 Bienvenido a la Nueva Era de la Emulación
**EmuManager** no es un gestor de ROMs convencional. Es un ecosistema completo diseñado para ser **espectacular al usar y sencillo de configurar**. Olvida las hojas de cálculo aburridas y los menús arcaicos. Entra en una experiencia cinematográfica impulsada por procesamiento nativo de alto rendimiento.

### 🥭 M.A.N.G.O Engine (Core Nativo)
El **Multithreaded Asynchronous Native Game Orchestrator** es el músculo de la aplicación. Escrito en **Rust**, garantiza un rendimiento inigualable:
- **Lightning Scan**: Escaneo de miles de archivos en segundos mediante procesamiento paralelo.
- **Deep Scraping**: Sistema de obtención de metadatos multicanal (Wikipedia, ScreenScraper, GameTDB) integrado directamente en binario.
- **Non-Blocking Architecture**: Arquitectura asíncrona total; tu interfaz nunca se detiene, sin importar la carga de trabajo de fondo.
- **Privacy First**: Sin telemetría, sin cuentas obligatorias, sin rastreo. Tus datos son tuyos.

---

## 🎨 Filosofía "Nebula Kinetic"
Cada píxel cuenta. EmuManager sigue una línea estética estricta y premium:
- **Visual Excellence**: Efectos de **Glassmorphism**, desenfoques dinámicos (Acrylic) y paletas de colores armónicas.
- **Zero-Hex Policy**: Todos los colores nacen de un sistema centralizado de temas, permitiendo una coherencia visual absoluta.
- **Micro-interacciones**: Animaciones fluidas en cada botón, card y transición para una experiencia táctil y profesional.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Rol |
| :--- | :--- | :--- |
| **Frontend** | `QML` / `Qt Quick` | Interfaz de alta fidelidad, animaciones y fluidez premium. |
| **Orquestador** | `Python 3.11` | Lógica de negocio, gestión de señales y flujo de trabajo. |
| **Motor** | `Rust` / `PyO3` | Hashing, escaneo paralelo, scraping nativo y orquestación base. |
| **Persistencia** | `SQLite3` | Base de datos robusta, escalable y 100% local. |

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
