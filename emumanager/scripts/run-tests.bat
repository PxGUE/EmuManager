@echo off
setlocal
echo 🧪 Running EmuManager Test Suite (Windows)...

:: Nos movemos a la raiz del proyecto relativa a la ubicacion del script
pushd "%~dp0..\.."

:: Configuramos PYTHONPATH para incluir la raiz
set PYTHONPATH=%CD%

:: Ejecutamos pytest con verbose para ver cada test individual
python -m pytest -v

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ All tests passed!
) else (
    echo.
    echo ❌ Some tests failed. Check the logs above.
)

popd
pause
