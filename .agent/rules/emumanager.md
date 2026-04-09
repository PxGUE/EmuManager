---
trigger: always_on
---

# Reglas de Proyecto: EmuManager

- **Filosofía Core:**
    - **FOSS & Privacidad:** App gratuita, código abierto y "Local-First". 
    - **Simplicidad & Elegancia:** "Fácil de configurar, espectacular al usar". La interfaz debe ser intuitiva pero con un acabado premium que la distinga de frontends tradicionales.
    - **Excelencia Visual (Premium UX):** El diseño DEBE wow-ear al usuario. Usar estéticas modernas (Glassmorphism, gradientes vibrantes, desenfoques dinámicos).
    - **Robustez Híbrida:** M.A.N.G.O (Rust) para potencia bruta y Python (PySide6) para fluidez. El UI nunca debe bloquearse (0 stutters).
    - **Gestión de Datos:** Respeto total a la librería del usuario. Las optimizaciones destructivas (ej. compresión) solo se realizan bajo petición explícita.

- **Stack Tecnológico:**
    - **Frontend (UI):** `QML` (Qt Quick). Se prefiere el uso de componentes personalizados que aprovechen `GraphicalEffects` y `PropertyAnimation`.
    - **Backend (Lógica):** Python (3.11+). Se permite `asyncio` para tareas de red (Scraping) si mejora la legibilidad frente a `QThreads`.
    - **Flexible I18n:** Todo texto final debe ir en `I18n.qml`. Se permite texto hardcodeado marcado con `// TODO: i18n` durante el desarrollo de nuevas features.
    - **Core (Performance):** Rust (Motor M.A.N.G.O) para el trabajo sucio (escaneo, hashing, parsing de headers).

- **Estilo de Diseño (Aesthetics Engine):**
    - **Dynamic Design System:** `Theme.qml` es el núcleo, pero es "vivo". Se permite la manipulación dinámica de colores (opacidad, brillo, mezclas) directamente en el componente para lograr efectos visuales ricos.
    - **Rich UI Policy:** Prohibido el uso de colores planos y básicos sin intención. Se priorizan sombras suaves, capas de profundidad y transiciones fluidas.
    - **Micro-interacciones:** Cada elemento interactivo debe reaccionar al usuario (hover, click, focus) con animaciones sutiles.

- **Ciclo de Desarrollo & Updates:**
    - **IS_DEV_MODE:** Activo durante el desarrollo para evitar desgaste de APIs y facilitar el testing local.
    - **Coherencia de Versión:** Sincronizar siempre `AppConfig.py`, `Cargo.toml` e `I18n.qml` antes de cerrar una versión.