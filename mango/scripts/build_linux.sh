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
# Usamos --skip-auditwheel para evitar errores de reparación dinámicos en local
python3 -m maturin build --release --out "$OUT_DIR" --skip-auditwheel

# Copiar el binario nativo al directorio esperado con el nombre correcto para Python
TARGET_SO="target/release/libmango_engine.so"

if [ -f "$TARGET_SO" ]; then
    echo "--- Copiando binario nativo: $TARGET_SO -> $OUT_DIR/mango_engine.so ---"
    cp "$TARGET_SO" "$OUT_DIR/mango_engine.so"
else
    echo -e "\033[0;31m!!! ERROR: No se encontró el binario compilado en $TARGET_SO !!!\033[0m"
    exit 1
fi

# Limpieza: Borrar los archivos .whl sobrantes
rm -f "$OUT_DIR"/*.whl

echo -e "\033[0;32m--- Compilación finalizada en $OUT_DIR ---\033[0m"
