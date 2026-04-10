#!/bin/bash
# EmuManager Linux Package Script (Optimized)

# Go to project root (assuming script is in EmuManager/emumanager/releases/)
cd "$(dirname "$0")/../.."
PROJECT_ROOT=$(pwd)

echo "🚀 Starting EmuManager Linux Packaging Process..."

# 1. DOWNLOAD BASE TOOL (Always ensures we have the latest appimagetool)
if [ ! -f "appimagetool" ]; then
    echo "⬇️ Downloading appimagetool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
    chmod +x appimagetool
fi

# 2. CLEAN OLD BUILDS
echo "🧹 Cleaning previous builds..."
rm -rf build/ release/
mkdir -p build release

# 3. COMPILE TO STANDALONE
# Note: 'svg' is now part of 'iconengines' and 'imageformats' families in modern PySide6
echo "💎 Compiling Python source to Standalone C++ (this may take a few minutes)..."
python3 -m nuitka --standalone \
    --output-dir=build \
    --show-progress \
    --enable-plugin=pyside6 \
    --include-qt-plugins=qml,iconengines,imageformats \
    --output-filename=EmuManager \
    --include-data-dir=./emumanager/ui=ui \
    --include-data-dir=./emumanager/resources=resources \
    ./emumanager/app.py


if [ $? -ne 0 ]; then
    echo "❌ Nuitka compilation failed. Aborting."
    exit 1
fi

# 4. PREPARE APPDIR STRUCTURE
echo "📁 Structuring AppDir..."
mkdir -p build/AppDir/usr/bin
mkdir -p build/AppDir/usr/lib

# Copy Nuitka distribution files to the AppDir
DIST_DIR="build/app.dist"
if [ ! -d "$DIST_DIR" ]; then
    DIST_DIR=$(ls -d build/*.dist 2>/dev/null | head -n 1)
fi

if [ -z "$DIST_DIR" ] || [ ! -d "$DIST_DIR" ]; then
    echo "❌ Could not find Nuitka distribution directory. Aborting."
    exit 1
fi

cp -a "$DIST_DIR"/* build/AppDir/usr/bin/

# 5. FIX PATHS FOR ASSETS (Aligning with app.py logic)
# EmuManager expects mango/ relative to the executable (usr/bin/)
echo "⚙️  Bundling M.A.N.G.O engine..."
mkdir -p build/AppDir/usr/bin/mango
cp -a mango/bin/linux/* build/AppDir/usr/bin/mango/

# 6. CREATE DESKTOP METADATA
cat > build/AppDir/emumanager.desktop <<EOF
[Desktop Entry]
Name=EmuManager
Exec=EmuManager
Icon=emumanager
Type=Application
Categories=Game;Emulator;
Comment=Modern Retro Game Emulator Manager
Terminal=false
EOF

# 7. SETUP ICONS (Using SVG official logo)
cp emumanager/ui/assets/logo.svg build/AppDir/emumanager.svg
cp emumanager/ui/assets/logo.svg build/AppDir/.DirIcon

# 8. CREATE MASTER APPRUN (Entry point)
cat > build/AppDir/AppRun <<EOF
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"

# Configurar rutas de librerías internas
export LD_LIBRARY_PATH="\$HERE/usr/bin:\$HERE/usr/lib:\$LD_LIBRARY_PATH"
export PATH="\$HERE/usr/bin:\$PATH"

# Evitar conflictos con librerías del sistema antiguas
export QT_QPA_PLATFORM_PLUGIN_PATH="\$HERE/usr/bin/PySide6/qt-plugins/platforms"
export QML2_IMPORT_PATH="\$HERE/usr/bin/PySide6/qml"

# Ejecutar el binario de EmuManager
exec "\$HERE/usr/bin/EmuManager" "\$@"
EOF
chmod +x build/AppDir/AppRun


# 9. BUILD FINAL APPIMAGE
echo "📦 Finalizing AppImage..."
mkdir -p release/Linux
ARCH=x86_64 ./appimagetool build/AppDir release/Linux/EmuManager.AppImage

# 10. FINAL PERMISSIONS & CLEANUP
chmod +x release/Linux/EmuManager.AppImage

echo "✅ Success! Your professional AppImage is ready at: release/Linux/EmuManager.AppImage"
