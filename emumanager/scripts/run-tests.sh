#!/bin/bash
echo "🧪 Running EmuManager Test Suite (Linux/Unix)..."

# Nos movemos a la raiz del proyecto relativa a la ubicacion del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/../.."

# Configuramos PYTHONPATH para incluir la raiz
export PYTHONPATH=$(pwd)

# Ejecutamos pytest con verbose para ver cada test individual
python3 -m pytest -v

if [ $? -eq 0 ]; then
    echo -e "\n ✅ All tests passed!"
else
    echo -e "\n ❌ Some tests failed. Check the logs above."
fi
