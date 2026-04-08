#!/bin/bash
echo "🧪 Running EmuManager Test Suite (Linux)..."
# Aseguramos que emumanager esté en el path para las importaciones
export PYTHONPATH=$PWD/emumanager
python3 -m pytest
if [ $? -eq 0 ]; then
    echo -e "\n All tests passed!"
else
    echo -e "\n Some tests failed. Check the logs above."
fi
