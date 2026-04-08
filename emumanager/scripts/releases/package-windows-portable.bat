@echo off
echo 🚀 Starting EmuManager Windows Packaging (Portable EXE)...

REM Ir a la raíz del proyecto (subir 3 niveles desde scripts/releases)
pushd %~dp0..\..\..

REM Limpiar versiones anteriores
if exist release\Windows\Portable rmdir /s /q release\Windows\Portable
mkdir release\Windows\Portable

REM Ejecutar empaquetado con Nuitka --onefile (Portable)
python -m nuitka --onefile ^
    --output-dir=release/Windows/Portable ^
    --show-progress ^
    --enable-plugin=pyside6 ^
    --include-qt-plugins=qml,iconengines,imageformats ^
    --windows-console-mode=force ^
    --windows-icon-from-ico=emumanager/ui/assets/logo.ico ^
    --company-name="PxGUE" ^
    --product-name="EmuManager" ^
    --file-version=0.3.5 ^
    --product-version=0.3.5 ^
    --file-description="Modern Retro Game Emulator Manager" ^
    --copyright="Copyright 2026 PxGUE" ^
    --output-filename=EmuManager ^
    --include-data-dir=./emumanager/ui=ui ^
    --include-data-dir=./emumanager/resources=resources ^
    --include-data-dir=./mango/bin/windows=mango ^
    ./emumanager/app.py


popd
echo ✅ Portable package complete. Check the 'release' directory.
