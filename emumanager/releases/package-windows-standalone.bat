@echo off
echo 🚀 Starting EmuManager Windows Packaging (Standalone Folder)...

REM Ir a la raíz del proyecto (asumiendo que el script está en EmuManager\emumanager\releases\)
pushd %~dp0\..\..

REM Limpiar versiones anteriores
if exist release\Windows\Standalone rmdir /s /q release\Windows\Standalone
mkdir release\Windows\Standalone

REM Ejecutar empaquetado con Nuitka --standalone (Normal)
python -m nuitka --standalone ^
    --output-dir=release/Windows/Standalone ^
    --show-progress ^
    --enable-plugin=pyside6 ^
    --include-qt-plugins=qml,iconengines,imageformats ^
    --windows-disable-console ^
    --windows-icon-from-ico=emumanager/ui/assets/logo.ico ^
    --company-name="PxGUE" ^
    --product-name="EmuManager" ^
    --file-version=0.3.5 ^
    --product-version=0.3.5 ^
    --file-description="Modern Retro Game Emulator Manager" ^
    --copyright="Copyright 2026 PxGUE" ^
    --output-filename=EmuManager ^
    --include-data-dir=./emumanager/ui=emumanager/ui ^
    --include-data-dir=./emumanager/resources=emumanager/resources ^
    --include-data-dir=./mango/bin/windows=mango/bin/windows ^
    ./emumanager/app.py


echo 🚚 Finalizing structure...
if exist release\Windows\Standalone\app.dist (
    xcopy /E /I /Y release\Windows\Standalone\app.dist\* release\Windows\Standalone\
    rmdir /S /Q release\Windows\Standalone\app.dist
)

popd
echo ✅ Standalone package complete. Check 'release/Windows/Standalone'.
