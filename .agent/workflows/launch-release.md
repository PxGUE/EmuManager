---
description: Automatiza el proceso de release de EmuManager (Inmovilización de IS_DEV_MODE y empaquetado multi-formato).
---

Este workflow prepara la aplicación para una versión estable, eliminando los bypasses de desarrollo y ejecutando los scripts de empaquetado correspondientes al sistema operativo actual.

### Pasos del Workflow:

1. **Desactivar el Modo Desarrollo**
   // turbo
   ```powershell
   python emumanager/releases/toggle_dev_mode.py off
   ```

2. **Ejecutar Empaquetado (OS Specific)**

   **Si estás en Windows:**
   // turbo
   ```powershell
   ./emumanager/releases/package-windows-portable.bat
   ```
   // turbo
   ```powershell
   ./emumanager/releases/package-windows-standalone.bat
   ```

   **Si estás en Linux:**
   // turbo
   ```bash
   bash ./emumanager/releases/package-linux.sh
   ```

3. **Restaurar el Modo Desarrollo**
   // turbo
   ```powershell
   python emumanager/releases/toggle_dev_mode.py on
   ```

> [!TIP]
> Los binarios finales se encontrarán en la carpeta `/release` en la raíz del proyecto. Asegúrate de haber compilado el motor M.A.N.G.O antes de lanzar este workflow si has hecho cambios en Rust.
