# build_windows.ps1
# Build the mango_engine with maturin EXCLUSIVELY for Windows

$ErrorActionPreference = "Stop"

# Resolve the project root (ensure we are in mango_engine context)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$engineDir = Split-Path -Parent $scriptDir
Push-Location $engineDir

$os_name = "windows"
$out_dir = "bin/$os_name"

if (-not (Test-Path $out_dir)) {
    New-Item -ItemType Directory -Force -Path $out_dir
}

Write-Host "--- Compilando M.A.N.G.O. Engine para $os_name (Windows) ---" -ForegroundColor Cyan

# Compilar con maturin (vía Python para mayor compatibilidad)
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY = 1
$env:CARGO_TARGET_DIR = "C:\mango_build"

Write-Host "--- Usando target dir externo: $env:CARGO_TARGET_DIR ---"
python -m maturin build --release

if ($LASTEXITCODE -ne 0) {
    Write-Error "¡Error Crítico! maturin falló con código de salida $LASTEXITCODE"
    exit $LASTEXITCODE
}

# Buscar el binario en la carpeta target y moverlo al destino final (.dll -> .pyd)
# Nota: Cargo coloca los resultados en $target_dir/release/ si se define CARGO_TARGET_DIR
$target_bin = "$env:CARGO_TARGET_DIR/release/mango_engine.dll"
if (Test-Path $target_bin) {
    Copy-Item $target_bin "$out_dir/mango_engine.pyd" -Force
    Write-Host "--- Binario nativo desplegado en $out_dir/mango_engine.pyd ---" -ForegroundColor Green
} else {
    Write-Error "¡Error Crítico! No se encontró el binario compilado en $target_bin"
}

# Limpieza: Borrar los archivos .whl sobrantes si fueron generados en la raíz por defecto
if (Test-Path "target/wheels") {
    Remove-Item -Path "target/wheels" -Recurse -Force
}

Pop-Location

Write-Host "--- Compilación finalizada exitosamente ---" -ForegroundColor Green
