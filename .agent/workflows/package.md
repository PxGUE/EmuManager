---
description: Empaqueta EmuManager usando Nuitka para distribución multiplataforma.
---
# Empaquetado con Nuitka

Genera versiones distribuibles de la aplicación (AppImage en Linux, EXE instalable/portable en Windows).

1. **Asegurar Compilación Nativa:**
   Ejecutar el workflow `compile-mango` para tener los últimos binarios de Rust.

2. **Empaquetado para Windows:**
// turbo
   - **Versión Instalable (Folder):** `nuitka --standalone --show-progress --enable-plugin=pyside6 --include-data-dir=f:/00_CHRISTIAN/00_PROJECTS/EmuManager/emumanager/ui=ui --include-data-dir=f:/00_CHRISTIAN/00_PROJECTS/EmuManager/data=data --include-data-dir=f:/00_CHRISTIAN/00_PROJECTS/EmuManager/mango/bin=mango/bin f:/00_CHRISTIAN/00_PROJECTS/EmuManager/emumanager/app.py`
   - **Versión Portable (EXE):** `nuitka --onefile --show-progress --enable-plugin=pyside6 ... f:/00_CHRISTIAN/00_PROJECTS/EmuManager/emumanager/app.py`

3. **Empaquetado para Linux (AppImage):**
// turbo
   - Ejecutar `nuitka --standalone --appimage --enable-plugin=pyside6 ... f:/00_CHRISTIAN/00_PROJECTS/EmuManager/emumanager/app.py`

4. **Verificación de Paquetes:**
   Listar los archivos generados en la carpeta `build/` o `dist/`.
