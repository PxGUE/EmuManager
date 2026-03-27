---
trigger: always_on
---

# Reglas de Proyecto: EmuManager

- **Filosofía Core:**
    - **FOSS & Privacidad:** La app es gratuita, de código abierto y "Local-First". 
    - **Simplicidad:** "Fácil de configurar, fácil de usar". El objetivo es que la app sea una alternativa sencilla y fluida a otros frontends complejos.
    - **Robustez:** M.A.N.G.O y EmuManager deben ser sólidos para garantizar una experiencia sin fricciones ("Black Box Architecture": lógica pesada en `QThreads`).
    - **Integridad de Datos:** NUNCA modifiques, muevas ni renombres las ROMs. Lee las rutas absolutas del usuario y guárdalas en SQLite.
    - **Gestión de APIs:** El usuario provee sus propias credenciales (ej. ScreenScraper, RetroAchievements).

- **Stack Tecnológico:**
    - **Frontend (UI):** Exclusivamente `QML` (Qt Quick) para la vista, orquestado por `PySide6` (Controlador/Modelo). 
    - **Backend (Lógica):** Python (3.11+ para mayor compatibilidad). Uso estricto de `pathlib`.
    - **Strict I18n:** Prohibido el uso de texto visible hardcodeado en QML o Python. Todo texto debe pasar por `I18n.qml`.
    - **Core (Rendimiento):** Rust (vía `PyO3`) para escaneo y hashing (Motor M.A.N.G.O).
    - **Base de Datos:** SQLite3 local con optimización por hilos e índices para grandes colecciones.

- **Estilo de Diseño:**
    - **Zero-Hex Policy:** Prohibido el uso de colores hardcodeados (hex/literal) en QML. `Theme.qml` es la ÚNICA fuente de verdad para el diseño y color. Cualquier nuevo componente o rediseño debe usar o extender `Theme.qml`.