@echo off
echo 🚀 Starting EmuManager Windows Packaging (Portable EXE)...

REM Ir a la raíz del proyecto (subir 3 niveles desde scripts/releases)
pushd %~dp0..\..\..

REM Limpiar versiones anteriores
if exist release\Windows\Portable rmdir /s /q release\Windows\Portable
mkdir release\Windows\Portable

REM Asegurar que el motor nativo sea visible para Nuitka durante la compilación
set "PYTHONPATH=%CD%\mango\bin\windows;%PYTHONPATH%"

REM Ejecutar empaquetado con Nuitka --onefile (Portable)
python -m nuitka --onefile ^
    --output-dir=release/Windows/Portable ^
    --show-progress ^
    --enable-plugin=pyside6 ^
    --include-qt-plugins=qml,iconengines,imageformats ^
    --windows-console-mode=disable ^
    --windows-uac-level=asInvoker ^
    --windows-icon-from-ico=emumanager/ui/assets/logo.ico ^
    --company-name="PxGUE" ^
    --product-name="EmuManager" ^
    --file-version=0.5.0 ^
    --product-version=0.5.0 ^
    --file-description="Modern Retro Game Emulator Manager" ^
    --copyright="Copyright 2026 PxGUE" ^
    --output-filename=EmuManager ^
    --include-data-dir=./emumanager/ui=ui ^
    --include-data-dir=./emumanager/resources=resources ^
    --include-module=mango_engine ^
    ./emumanager/app.py


popd
echo ✅ Portable package complete. Check the 'release' directory.
