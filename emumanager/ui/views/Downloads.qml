import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0
import "../components"

Item {
    id: downloadsRoot
    objectName: "downloadsView"

    Connections { 
        target: mainController
        function onScanProgressChanged(p) {
            for(var i=0; i < downloadsModel.count; i++) {
                if(downloadsModel.get(i).type === "SCAN") {
                    downloadsModel.setProperty(i, "progress", p)
                    if (p >= 1.0) {
                        downloadsModel.setProperty(i, "status", "Completado")
                        isScanning = false
                    }
                    break
                }
            }
        }
        function onScanStatusChanged(s) {
            for(var i=0; i < downloadsModel.count; i++) {
                if(downloadsModel.get(i).type === "SCAN") {
                    downloadsModel.setProperty(i, "status", "Escaneando")
                    downloadsModel.setProperty(i, "log", s)
                    break
                }
            }
        }
        function onScanFinished(n) {
            for(var i=0; i < downloadsModel.count; i++) {
                if(downloadsModel.get(i).type === "SCAN") {
                    downloadsModel.setProperty(i, "progress", 1.0)
                    downloadsModel.setProperty(i, "status", "Completado: " + n + " juegos")
                    isScanning = false
                    break
                }
            }
        }
        function onScrapeProgressChanged(p) {
            scrapeVal = p
            // Actualizar la tarea en el modelo de descargas
            for(var i=0; i < downloadsModel.count; i++) {
                if(downloadsModel.get(i).type === "MEDIA") {
                    downloadsModel.setProperty(i, "progress", p)
                    if (p >= 1.0) {
                        downloadsModel.setProperty(i, "status", "Completado")
                        isScraping = false
                    }
                    break
                }
            }
        }
        function onScrapeStatusChanged(s) {
            scrapeStatus = s.toUpperCase()
            for(var i=0; i < downloadsModel.count; i++) {
                if(downloadsModel.get(i).type === "MEDIA") {
                    downloadsModel.setProperty(i, "status", "Scrapeando")
                    downloadsModel.setProperty(i, "log", s)
                    break
                }
            }
        }
        function onGamesUpdated() {
            // Refrescar si es necesario
        }
        function onCoreDownloadProgressChanged(p) {
            for(var i=0; i < downloadsModel.count; i++) {
                if(downloadsModel.get(i).type === "CORE") {
                    downloadsModel.setProperty(i, "progress", p)
                    if (p >= 1.0) {
                        downloadsModel.setProperty(i, "status", "Completado")
                    }
                    break
                }
            }
        }
        function onCoreDownloadStatusChanged(s) {
            for(var i=0; i < downloadsModel.count; i++) {
                if(downloadsModel.get(i).type === "CORE") {
                    if (downloadsModel.get(i).progress < 1.0) {
                        downloadsModel.setProperty(i, "status", "Descargando")
                    }
                    downloadsModel.setProperty(i, "log", s)
                    break
                }
            }
        }
    }
    
    // Referencia para compatibilidad local
    property QtObject controller: mainController

    // Popup para seleccionar Cores disponibles
    Popup {
        id: coresPopup
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        width: 300; height: 400
        modal: true; focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Rectangle { color: "#0d0d10"; radius: 10; border.color: "#16a085"; border.width: 1 }
        
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 15; spacing: 10
            Text { text: "SELECCIONAR CORE"; color: "#16a085"; font.bold: true; font.pixelSize: 14 }
            
            ListView {
                id: coresListView
                Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                model: []
                delegate: Rectangle {
                    width: coresListView.width; height: 40; color: "transparent"
                    border.width: 1; border.color: "#33ffffff"; radius: 5
                    RowLayout {
                        anchors.fill: parent; anchors.margins: 10
                        Text { text: modelData; color: "white"; font.pixelSize: 12 }
                    }
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onEntered: parent.color = "#16a085"
                        onExited: parent.color = "transparent"
                        onClicked: {
                            coresPopup.close()
                            registerCoreTask(modelData)
                            controller.start_core_download(modelData)
                        }
                    }
                }
            }
        }
    }

    function togglePause(index) {
        var item = downloadsModel.get(index)
        if (item.status === "Pausado") {
            item.status = "Descargando"
            console.log("M.A.N.G.O: Reanudando " + item.name)
        } else {
            item.status = "Pausado"
            console.log("M.A.N.G.O: Pausando " + item.name)
        }
    }

    function cancelTask(index) {
        var item = downloadsModel.get(index)
        console.log("M.A.N.G.O: Abortando tarea " + item.name)
        if (item.type === "MEDIA") {
            controller.stop_scraping()
        }
        downloadsModel.remove(index)
    }

    function clearCompleted() {
        for (var i = downloadsModel.count - 1; i >= 0; i--) {
            if (downloadsModel.get(i).progress >= 1.0) {
                downloadsModel.remove(i)
            }
        }
    }

    function registerScanTask() {
        // Evitar duplicados
        for(var i=0; i < downloadsModel.count; i++) {
            if(downloadsModel.get(i).type === "SCAN" && downloadsModel.get(i).progress < 1.0) return;
        }
        
        downloadsModel.insert(0, {
            name: "Sincronización de Biblioteca",
            type: "SCAN",
            platform: "LOCAL",
            progress: 0.0,
            size: "--",
            status: "Iniciando radar...",
            speed: "--",
            accent: "#2ecc71",
            eta: "--",
            log: "Buscando archivos en directorios..."
        })
    }

    function registerMangoTask() {
        // Evitar duplicados
        for(var i=0; i < downloadsModel.count; i++) {
            if(downloadsModel.get(i).type === "MEDIA") return;
        }
        
        downloadsModel.insert(0, {
            name: "Media Sync (Mango)",
            type: "MEDIA",
            platform: "ALL",
            progress: 0.0,
            size: "--",
            status: "Inicializando...",
            speed: "0 KB/s",
            accent: "#f39c12",
            eta: "--",
            log: "Preparando motor M.A.N.G.O..."
        })
    }

    function registerCoreTask(coreName) {
        // Evitar duplicados
        for(var i=0; i < downloadsModel.count; i++) {
            if(downloadsModel.get(i).name === coreName) return;
        }
        
        downloadsModel.insert(0, {
            name: coreName,
            type: "CORE",
            platform: "MIX",
            progress: 0.0,
            size: "--",
            status: "Inicializando...",
            speed: "--",
            accent: "#16a085",
            eta: "--",
            log: "Conectando al Libretro Buildbot..."
        })
    }

    // Modelo de Descargas dinámico
    ListModel {
        id: downloadsModel
    }
    
    // Estados
    property bool isScraping: false
    property bool isScanning: false
    property bool isInstallingCores: false
    property bool isUpdatingSystem: false
    property real scrapeVal: 0.0
    property string scrapeStatus: "LISTO"
    property string scanStatus: "ESPERANDO"

    Rectangle { anchors.fill: parent; color: "#050505" }

    ColumnLayout {
        anchors.fill: parent; anchors.margins: 40; spacing: 25

        // 1. CABECERA
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 4
                Text { text: "CENTRO DE SINCRONIZACIÓN"; color: "white"; font.pixelSize: 28; font.bold: true; font.letterSpacing: 2 }
                Text { text: "Gestiona tu biblioteca, medios y emuladores desde un solo lugar"; color: "#66ffffff"; font.pixelSize: 14; font.bold: true }
            }
        }
        // 2. PANEL DE OPERACIONES (Control Maestro)
        RowLayout {
            Layout.fillWidth: true; Layout.preferredHeight: 120; Layout.maximumHeight: 120; spacing: 15
            
            // Tarjeta 1: Escanear Biblioteca (Radar)
            Rectangle {
                id: scanCard
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 16
                color: scanMA.containsMouse ? "#1a2a20" : "#0d0d10"
                border.color: scanMA.containsMouse ? "#2ecc71" : "#332ecc71"
                border.width: scanMA.containsMouse ? 2 : 1
                
                scale: scanMA.pressed ? 0.98 : 1.0
                y: scanMA.containsMouse ? -3 : 0
                Behavior on color { ColorAnimation { duration: 200 } }
                Behavior on border.color { ColorAnimation { duration: 200 } }
                Behavior on y { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 100 } }

                MouseArea { 
                    id: scanMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor 
                    onClicked: {
                        registerScanTask()
                        isScanning = true
                        controller.scan_directories()
                    }
                }

                RowLayout {
                    anchors.fill: parent; anchors.margins: 15; spacing: 15
                    Text { text: "📡"; font.pixelSize: 32; opacity: scanMA.containsMouse ? 1.0 : 0.7 }
                    ColumnLayout {
                        spacing: 2
                        Text { text: "BIBLIOTECA"; color: "#2ecc71"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: "Sincronizar ROMs"; color: "white"; font.pixelSize: 14; font.bold: true }
                        Text { text: "Escanear directorios locales"; color: "#66ffffff"; font.pixelSize: 9 }
                    }
                }
            }

            // Tarjeta 2: Mango Media Sync (El Scraping Modular)
            Rectangle {
                id: mangoCard
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 16
                color: mangoMA.containsMouse ? "#2a1a10" : "#0d0d10"
                border.color: mangoMA.containsMouse ? "#f39c12" : "#33f39c12"
                border.width: mangoMA.containsMouse ? 2 : 1
                
                scale: mangoMA.pressed ? 0.98 : 1.0
                y: mangoMA.containsMouse ? -3 : 0
                Behavior on color { ColorAnimation { duration: 200 } }
                Behavior on border.color { ColorAnimation { duration: 200 } }
                Behavior on y { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 100 } }

                MouseArea { 
                    id: mangoMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor 
                    onClicked: {
                        registerMangoTask()
                        isScraping = true
                        controller.start_scraping()
                    }
                }

                RowLayout {
                    anchors.fill: parent; anchors.margins: 15; spacing: 15
                    Text { text: "🥭"; font.pixelSize: 32; opacity: mangoMA.containsMouse ? 1.0 : 0.7 }
                    ColumnLayout {
                        spacing: 2
                        Text { text: "M.A.N.G.O SCRAPER"; color: "#f39c12"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: "Metadatos y Arte"; color: "white"; font.pixelSize: 14; font.bold: true }
                        Text { text: "ScreenScraper + Libretro"; color: "#66ffffff"; font.pixelSize: 9 }
                    }
                }
            }

            // Tarjeta 3: Libretro Cores (Hub)
            Rectangle {
                id: coresCard
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 16
                color: coresMA.containsMouse ? "#1a2a25" : "#0d0d10"
                border.color: coresMA.containsMouse ? "#16a085" : "#3316a085"
                border.width: coresMA.containsMouse ? 2 : 1
                
                scale: coresMA.pressed ? 0.98 : 1.0
                y: coresMA.containsMouse ? -3 : 0
                Behavior on color { ColorAnimation { duration: 200 } }
                Behavior on border.color { ColorAnimation { duration: 200 } }
                Behavior on y { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 100 } }

                MouseArea { 
                    id: coresMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor 
                    onClicked: {
                        let cores = controller.fetch_available_cores()
                        if (cores && cores.length > 0) {
                            coresListView.model = cores
                            coresPopup.open()
                        }
                    }
                }

                RowLayout {
                    anchors.fill: parent; anchors.margins: 15; spacing: 15
                    Text { text: "🧩"; font.pixelSize: 32; opacity: coresMA.containsMouse ? 1.0 : 0.7 }
                    ColumnLayout {
                        spacing: 2
                        Text { text: "NÚCLEOS"; color: "#16a085"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: "Emu-Hub"; color: "white"; font.pixelSize: 14; font.bold: true }
                        Text { text: "Motores de emulación"; color: "#66ffffff"; font.pixelSize: 9 }
                    }
                }
            }
        }

        // 3. SECCIÓN DE TAREAS (Todo el progreso vive aquí)
        // Se eliminó la barra de estado superior redundante.

        // 5. LISTA DE TAREAS (Ahora con scroll y estirado correcto)
        ListView {
            id: tasksList
            Layout.fillWidth: true; Layout.fillHeight: true
            model: downloadsModel; spacing: 12; clip: true
            
            delegate: DownloadItem {
                width: tasksList.width
                itemIndex: index
                itemName: model.name; itemType: model.type; platform: model.platform
                progressValue: model.progress; totalSize: model.size; statusText: model.status
                downloadSpeed: model.speed; accentColor: model.accent; eta: model.eta; lastLog: model.log
                
                onPauseRequested: (idx) => togglePause(idx)
                onResumeRequested: (idx) => togglePause(idx)
                onCancelRequested: (idx) => cancelTask(idx)
                onOpenFolderRequested: (idx) => console.log("Abriendo carpeta de " + downloadsModel.get(idx).name)
            }
            
            // Estado vacío
            Column {
                anchors.centerIn: parent
                visible: downloadsModel.count === 0
                spacing: 15; opacity: 0.3
                Text { text: "📥"; font.pixelSize: 48; anchors.horizontalCenter: parent.horizontalCenter }
                Text { text: "SIN DESCARGAS PENDIENTES"; color: "white"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2; anchors.horizontalCenter: parent.horizontalCenter }
            }
        }

        // 4. ACCIONES GLOBALES
        RowLayout {
            Layout.fillWidth: true; Layout.topMargin: 10
            visible: downloadsModel.count > 0
            
            Button {
                text: "LIMPIAR COMPLETADOS"; flat: true; Material.accent: "#16a085"
                font.pixelSize: 10; font.bold: true; font.letterSpacing: 1
                onClicked: clearCompleted()
            }
            Item { Layout.fillWidth: true }
            Text { 
                text: downloadsModel.count + " TAREAS EN COLA"; color: "#33ffffff"
                font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 
            }
        }
    }
}


