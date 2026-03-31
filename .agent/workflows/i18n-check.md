---
description: Escanea el proyecto buscando cadenas de texto visibles que no usen el sistema I18n.
---
# Verificación de Strict I18n

Este flujo asegura que todo el texto de la interfaz esté centralizado en `I18n.qml`.

1. **Definir Patrones de Búsqueda:**
   Buscamos comillas dobles o simples que contengan texto pero que no estén envueltas en `I18n.t`, `I18n.tp`, o sean puramente técnicas (como rutas o IDs).

2. **Ejecutar Escaneo en QML:**
// turbo
   - Ejecutar: `rg -g "*.qml" "\"[^\"].*\"" f:/00_CHRISTIAN/00_PROJECTS/EmuManager/emumanager/ui | grep -v "EmuLog" | grep -v "print("` (Filtrando falsos positivos manualmente después).

3. **Ejecutar Escaneo en Python:**
// turbo
   - Ejecutar: `rg -g "*.py" "\"[^\"].*\"" f:/00_CHRISTIAN/00_PROJECTS/EmuManager/emumanager/controllers | grep -v "EmuLog" | grep -v "print("`

4. **Reporte:**
   Listar las líneas sospechosas para que el desarrollador las mueva a `I18n.qml`.
