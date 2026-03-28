---
description: Empaqueta EmuManager usando Nuitka para distribución multiplataforma.
---
# Empaquetado con Nuitka

Genera versiones distribuibles de la aplicación (AppImage en Linux, EXE instalable/portable en Windows).

1. **Preparación y Limpieza:**
// turbo
   - **Limpiar Entorno:** `if exist release rmdir /s /q release` (Asegura un empaquetado libre de residuos previos).

2. **Asegurar Compilación Nativa:**
   Ejecutar el workflow `compile-mango` para tener los últimos binarios de Rust actualizados en `./mango/bin`.

2. **Empaquetado para Windows (Portable/Instalable):**
// turbo
   - **Versión Standalone (Folder):** `python -m nuitka --standalone --output-dir=release --show-progress --enable-plugin=pyside6 --include-qt-plugins=qml --include-data-dir=./emumanager/ui=emumanager/ui --include-data-dir=./mango/bin=mango/bin ./emumanager/app.py`
   - **Versión Portable (EXE):** `python -m nuitka --onefile --output-dir=release --show-progress --enable-plugin=pyside6 --include-qt-plugins=qml --include-data-dir=./emumanager/ui=emumanager/ui --include-data-dir=./mango/bin=mango/bin ./emumanager/app.py`

3. **Empaquetado para Linux (AppImage):**
// turbo
   - **AppImage:** `python -m nuitka --standalone --output-dir=release --appimage --enable-plugin=pyside6 --include-qt-plugins=qml --include-data-dir=./emumanager/ui=emumanager/ui --include-data-dir=./mango/bin=mango/bin ./emumanager/app.py`

4. **Resultado:**
   Los archivos generados estarán en la carpeta `app.dist` (Standalone) o como un binario único (Onefile) en el directorio raíz.
