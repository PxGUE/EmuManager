---
description: Borra la base de datos y la caché de medios para permitir un re-escaneo limpio desde cero.
---
# Hard Reset de Base de Datos y Medios

Este flujo de trabajo elimina todos los datos locales para iniciar una sesión de prueba limpia.

1. **Localizar Directorio de Datos:**
   Identificar la carpeta `data/` en la raíz del proyecto.

2. **Borrar Base de Datos:**
// turbo
   - En Windows: `if (Test-Path "f:/00_CHRISTIAN/00_PROJECTS/EmuManager/data/emumanager.db") { Remove-Item "f:/00_CHRISTIAN/00_PROJECTS/EmuManager/data/emumanager.db" -Force }`
   - En Linux: `rm -f "f:/00_CHRISTIAN/00_PROJECTS/EmuManager/data/emumanager.db"`

3. **Limpiar Caché de Medios:**
// turbo
   - En Windows: `if (Test-Path "f:/00_CHRISTIAN/00_PROJECTS/EmuManager/data/media") { Remove-Item "f:/00_CHRISTIAN/00_PROJECTS/EmuManager/data/media/*" -Recurse -Force }`
   - En Linux: `rm -rf "f:/00_CHRISTIAN/00_PROJECTS/EmuManager/data/media/*"`

4. **Confirmación:**
   Indicar al usuario que los datos han sido borrados y el sistema está listo para un nuevo escaneo.
