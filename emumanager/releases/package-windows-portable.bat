@echo off
echo 🚀 Starting EmuManager Windows Packaging (Portable EXE)...

REM Ir a la raíz del proyecto (asumiendo que el script está en EmuManager\emumanager\releases\)
pushd %~dp0\..\..

REM Limpiar versiones anteriores
if exist release\Windows\Portable rmdir /s /q release\Windows\Portable
mkdir release\Windows\Portable

REM Ejecutar empaquetado con Nuitka --onefile (Portable)
python -m nuitka --onefile ^
    --output-dir=release/Windows/Portable ^
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


popd
echo ✅ Portable package complete. Check the 'release' directory.
