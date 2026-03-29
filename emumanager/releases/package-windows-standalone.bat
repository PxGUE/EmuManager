@echo off
echo 🚀 Starting EmuManager Windows Packaging (Standalone Folder)...

REM Ir a la raíz del proyecto (asumiendo que el script está en EmuManager\emumanager\releases\)
pushd %~dp0\..\..

REM Limpiar versiones anteriores
if exist release rmdir /s /q release

REM Ejecutar empaquetado con Nuitka --standalone (Normal)
python -m nuitka --standalone ^
    --output-dir=release ^
    --show-progress ^
    --enable-plugin=pyside6 ^
    --include-qt-plugins=qml,iconengines,imageformats ^
    --windows-disable-console ^
    --output-filename=EmuManager ^
    --include-data-dir=./emumanager/ui=ui ^
    --include-data-dir=./emumanager/resources=resources ^
    --include-data-dir=./mango/bin=mango/bin ^
    ./emumanager/app.py


popd
echo ✅ Standalone package complete. Check the 'release' (app.dist) directory.
