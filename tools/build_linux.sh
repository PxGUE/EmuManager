#!/bin/bash
# EmuManager v0.1.3 alpha — Script de generación de ejecutable (Linux)

# Cambiar al directorio raíz del proyecto (un nivel arriba de /tools)
cd "$(dirname "$0")/.." || exit 1

echo "--- Iniciando generación de ejecutable para Linux desde $(pwd) ---"

# 1. Asegurar que las carpetas de release existen
mkdir -p releases/linux releases/windows

# 2. Correr PyInstaller con la configuración adecuada
# --onefile: Empaqueta todo en un solo binario
# --windowed: Para aplicaciones con GUI
# --add-data: Incluimos recursos visuales e i18n
pyinstaller --onefile --windowed \
    --name="EmuManager" \
    --add-data "media:media" \
    --add-data "ui/styles:ui/styles" \
    --noconfirm \
    main.py

# 3. Mover el resultado a la carpeta releases/linux
if [ -f "dist/EmuManager" ]; then
    echo "--- Éxito: Binario generado en releases/linux/EmuManager ---"
    mv dist/EmuManager releases/linux/
    # Limpiar archivos temporales
    rm -rf build/ dist/ EmuManager.spec
else
    echo "--- Error: No se pudo generar el binario ---"
    exit 1
fi
