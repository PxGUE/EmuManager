@echo off
echo 🧪 Running EmuManager Test Suite (Windows)...
:: Aseguramos que emumanager esté en el path para las importaciones
set PYTHONPATH=%CD%\emumanager
python -m pytest
if %ERRORLEVEL% EQU 0 (
    echo.
    echo All tests passed!
) else (
    echo.
    echo Some tests failed. Check the logs above.
)
pause
