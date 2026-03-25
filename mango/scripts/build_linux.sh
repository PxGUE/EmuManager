#!/bin/bash
# build_linux.sh
# Build the mango_engine with maturin EXCLUSIVELY for Linux

# Move to the engine root (one level up from this script)
cd "$(dirname "$0")/.." || exit

OS_NAME="linux"
OUT_DIR="bin/$OS_NAME"

echo -e "\033[0;36m--- Compilando M.A.N.G.O. Engine para $OS_NAME (Linux) ---\033[0m"

# Crear directorio de salida si no existe
mkdir -p "$OUT_DIR"

# Compilar con maturin (vía Python)
python3 -m maturin build --release --out "$OUT_DIR"

# Limpieza: Borrar los archivos .whl sobrantes (Solo necesitamos el .so)
rm -f "$OUT_DIR"/*.whl

echo -e "\033[0;32m--- Compilación finalizada en $OUT_DIR ---\033[0m"
