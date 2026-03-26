---
description: Compila el motor nativo de Rust (M.A.N.G.O Engine) según el sistema operativo actual.
---
# Compilar M.A.N.G.O (Rust Engine)

Este workflow automatiza la revisión y ejecución del script de compilación nativo.

1. **Identificar el Sistema Operativo:**
   Revisar si estamos en un entorno **Windows** o **Linux**.

2. **Verificar el Script de Construcción:**
   Si es Windows, revisar `f:/00_CHRISTIAN/00_PROJECTS/EmuManager/mango/scripts/build_windows.ps1`.
   Si es Linux, revisar `f:/00_CHRISTIAN/00_PROJECTS/EmuManager/mango/scripts/build_linux.sh`.

3. **Ejecutar la Compilación:**
// turbo
   - En Windows (PowerShell): `powershell -ExecutionPolicy Bypass -File "f:/00_CHRISTIAN/00_PROJECTS/EmuManager/mango/scripts/build_windows.ps1"`
   - En Linux (Bash): `bash "f:/00_CHRISTIAN/00_PROJECTS/EmuManager/mango/scripts/build_linux.sh"`

4. **Confirmar Despliegue:**
   Verificar que el binario fue copiado correctamente a `mango/bin/windows/mango_engine.pyd` o la ruta de Linux correspondiente.
