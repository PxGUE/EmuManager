#!/bin/bash
# releases/create_appimage.sh
# Script para empaquetar EmuManager como AppImage en Linux.

# 1. Asegurar que estamos en la raíz del proyecto
cd "$(dirname "$0")/.."
set -e

# Limpieza previa
echo "--- Limpiando archivos temporales ---"
rm -rf AppDir releases/build_output
rm -f releases/emumanager.AppImage
rm -f releases/emumanager.desktop

# 2. Compilar con Nuitka (Standalone)
echo "--- Compilando con Nuitka ---"
python3 releases/compile_nuitka.py

# 3. Descargar herramientas necesarias (linuxdeploy)
if [ ! -f "releases/linuxdeploy-x86_64.AppImage" ]; then
    echo "--- Descargando linuxdeploy ---"
    wget -O releases/linuxdeploy-x86_64.AppImage https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x releases/linuxdeploy-x86_64.AppImage
fi

# 4. Preparar archivos para linuxdeploy
echo "--- Preparando archivos y AppDir ---"
export VERSION=$(grep "APP_VERSION =" core/config.py | cut -d '"' -f 2 | tr -d ' ')
export ARCH=x86_64

# Generar el archivo .desktop
cat > releases/emumanager.desktop <<EOF
[Desktop Entry]
Type=Application
Name=EmuManager
Comment=Manager for retro emulators and libraries
Exec=emumanager
Icon=icon
Terminal=false
Categories=Game;Emulator;
EOF

# Crear estructura AppDir y copiar el contenido de Nuitka
mkdir -p AppDir/usr/bin
cp -r releases/build_output/main.dist/* AppDir/usr/bin/

# 5. Generar AppImage usando linuxdeploy
echo "--- Generando AppImage ---"
./releases/linuxdeploy-x86_64.AppImage --appimage-extract-and-run --appdir AppDir \
    -e AppDir/usr/bin/emumanager \
    -i media/icon.svg \
    -d releases/emumanager.desktop \
    --output appimage

# 6. Limpieza final y renombrado
echo "--- Limpiando y finalizando ---"
rm -rf AppDir releases/build_output releases/emumanager.desktop

if ls EmuManager-*.AppImage 1> /dev/null 2>&1; then
    mv EmuManager-*.AppImage releases/emumanager.AppImage
    chmod +x releases/emumanager.AppImage
    echo "--- ¡Proceso finalizado! AppImage disponible en releases/emumanager.AppImage ---"
else
    echo "--- ERROR: No se pudo generar el AppImage ---"
    exit 1
fi
