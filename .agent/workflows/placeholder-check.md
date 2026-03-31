---
description: Escanea el proyecto buscando placeholders técnicos, comentarios TODO/FIXME y archivos/código que parecen no tener uso.
---

Este workflow ayuda a mantener la limpieza del proyecto identificando elementos temporales o código muerto.

### 1. Detección de Placeholders y Pendientes
Busca cadenas comunes que indican trabajo pendiente o valores temporales.

// turbo
```powershell
Write-Host "--- Buscando Placeholders y Pendientes ---" -ForegroundColor Cyan
rg -niEi "todo|fixme|placeholder|testme|temporal|temp|debugme|\.\.\." --glob "!data/*" --glob "!.agent/*" --glob "!.git/*"
```

### 2. Detección de Archivos Huérfanos (QML)
Identifica archivos .qml que no están siendo referenciados por ningún otro archivo del proyecto.
*Nota: Algunos archivos pueden ser cargados dinámicamente o ser puntos de entrada.*

```powershell
Write-Host "--- Verificando Referencias QML ---" -ForegroundColor Cyan
$qmlFiles = Get-ChildItem -Path . -Recurse -Filter *.qml | Where-Object { $_.FullName -notmatch "data" }
foreach ($file in $qmlFiles) {
    $name = $file.BaseName
    if ($name -eq "main" -or $name -eq "I18n" -or $name -eq "Theme" -or $name -eq "AppConfig") { continue }
    $count = (rg -l $name --glob "*.qml" | Measure-Object).Count
    if ($count -le 1) {
        Write-Host "Posible archivo QML huérfano: $($file.RelativePath)" -ForegroundColor Yellow
    }
}
```

### 3. Detección de Imports no utilizados (Python)
Busca imports que se declaran pero no se usan en el mismo archivo.

```powershell
Write-Host "--- Analizando Imports Python (Luz Blanca) ---" -ForegroundColor Cyan
# Este es un análisis simple basado en texto.
rg -niEi "import\s+\w+" --glob "*.py" | ForEach-Object {
    if ($_ -match "import\s+(\w+)") {
        $module = $matches[1]
        # Verificar si el módulo aparece más veces aparte del import
        $usage = (rg $module $_.split(":")[0] | Measure-Object).Count
        if ($usage -le 1) {
            Write-Host "Posible import no usado: $module en $($_.split(":")[0])" -ForegroundColor Yellow
        }
    }
}
```

### 4. Instrucciones Finales
1. Revisa la lista generada.
2. Si un placeholder es necesario para `IS_DEV_MODE`, documéntalo.
3. El código muerto debe ser eliminado o movido a una rama de archivo, NUNCA dejado comentado en el main.
