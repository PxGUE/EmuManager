---
description: Realiza un reset completo eliminando carpetas de construcción (build), ejecutables (release) y datos locales (data).
---
# Hard Reset de Proyecto (Limpieza Total)

Este flujo de trabajo elimina todos los archivos generados y carpetas de datos para realizar un reinicio completo del sistema de desarrollo y empaquetado.

1. **Ejecutar Limpieza de Directorios:**
// turbo
   - En Linux/macOS: `rm -rf build/ release/ data/`
   - En Windows (PowerShell): `Remove-Item -Path build, release, data -Recurse -Force -ErrorAction SilentlyContinue`

2. **Confirmación:**
   Indicar al usuario que las carpetas `build/`, `release/` y `data/` han sido eliminadas por completo y el proyecto está en estado "fábrica".

