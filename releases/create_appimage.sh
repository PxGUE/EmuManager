#!/bin/bash
# releases/create_appimage.sh
# Script para empaquetar EmuManager como AppImage en Linux.

# 1. Asegurar que estamos en la raíz del proyecto
cd "$(dirname "$0")/.."

# 2. Compilar primero con Nuitka para obtener el binario optimizado
echo "--- Compilando con Nuitka ---"
python3 releases/compile_nuitka.py

# 3. Descargar herramientas necesarias (linuxdeploy)
if [ ! -f "releases/linuxdeploy-x86_64.AppImage" ]; then
    echo "--- Descargando linuxdeploy ---"
    wget -O releases/linuxdeploy-x86_64.AppImage https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x releases/linuxdeploy-x86_64.AppImage
fi

# 4. Crear el AppImage
echo "--- Generando AppImage ---"
export VERSION=$(grep "APP_VERSION =" core/config.py | cut -d '"' -f 2)

./releases/linuxdeploy-x86_64.AppImage --appdir AppDir \
    -e releases/main.bin \
    -i media/icon.svg \
    -d releases/emumanager.desktop \
    --output appimage

# 5. Limpieza
echo "--- Limpiando archivos temporales ---"
rm -rf AppDir
mv EmuManager-*.AppImage releases/

echo "--- ¡Proceso finalizado! AppImage disponible en releases/ ---"
