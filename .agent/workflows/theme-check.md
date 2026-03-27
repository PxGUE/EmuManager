---
description: Escanea el proyecto buscando colores hardcodeados (Hex/Literal) para mantener la Zero-Hex Policy.
---
# Verificación de Zero-Hex Policy (EmuManager)

Este flujo asegura que todos los colores de la interfaz utilicen los tokens centralizados en `Theme.qml`.

1. **Definir Patrones de Búsqueda:**
   - Buscamos códigos Hexadecimales (ej: `#FFFFFF`, `#abc`).
   - Buscamos colores literales comunes (ej: `"red"`, `"transparent"`, `"white"`).
   - Ignoramos `Theme.qml` (donde se definen los colores).

2. **Escanear QML (Hex & Literals):**
// turbo
   - Ejecutar: `rg -g "!Theme.qml" -g "*.qml" "#[0-9a-fA-F]{3,8}" f:/00_CHRISTIAN/00_PROJECTS/EmuManager/emumanager/ui`

3. **Escanear QML (Colores Nombrados):**
// turbo
   - Ejecutar: `rg -g "!Theme.qml" -g "*.qml" "\b(red|blue|green|white|black|transparent|gray|grey|yellow|purple|cyan)\b" f:/00_CHRISTIAN/00_PROJECTS/EmuManager/emumanager/ui`

4. **Escanear Python (Opcional):**
// turbo
   - Ejecutar: `rg -g "*.py" "#[0-9a-fA-F]{3,6}" f:/00_CHRISTIAN/00_PROJECTS/EmuManager/emumanager`

5. **Acción Correctiva:**
   - Todas las coincidencias encontradas deben ser reemplazadas por una referencia a `Theme.[nombre_del_token]`. 
   - Si el color no existe en el tema, agrégalo a `Theme.qml` primero.
