import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0
import "../components"

Item {
    id: downloadsRoot
    objectName: "downloadsView"

    MainController { 
        id: controller 
        onScrapeProgressChanged: (p) => {
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
        onScrapeStatusChanged: (s) => {
            scrapeStatus = s.toUpperCase()
            for(var i=0; i < downloadsModel.count; i++) {
                if(downloadsModel.get(i).type === "MEDIA") {
                    downloadsModel.setProperty(i, "status", "Scrapeando")
                    downloadsModel.setProperty(i, "log", s)
                    break
                }
            }
        }
        onGamesUpdated: {
            // Refrescar si es necesario
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

    // Modelo de Prueba mejorado con datos técnicos
    ListModel {
        id: downloadsModel
        ListElement { name: "Mupen64Plus_Next"; type: "CORE"; platform: "N64"; progress: 0.65; size: "15.4 MB"; status: "Descargando"; speed: "1.2 MB/s"; accent: "#16a085"; eta: "00:12s"; log: "Writing core binary to disk..." }
        ListElement { name: "Dolphin Standalone"; type: "EMULATOR"; platform: "GC"; progress: 0.20; size: "142 MB"; status: "Descargando"; speed: "4.5 MB/s"; accent: "#8e44ad"; eta: "01:05m"; log: "Connecting to GitHub mirror..." }
        ListElement { name: "Beetle PSX HW"; type: "CORE"; platform: "PS1"; progress: 1.0; size: "8.2 MB"; status: "Completado"; speed: "0 KB/s"; accent: "#2980b9"; eta: "00:00s"; log: "Installation verified." }
        ListElement { name: "Media Sync (Mango)"; type: "MEDIA"; platform: "ALL"; progress: 0.45; size: "1.2 GB"; status: "Scrapeando"; speed: "850 KB/s"; accent: "#f39c12"; eta: "15:20m"; log: "Fetching 3D covers from ScreenScraper API..." }
    }
    
    // Estados
    property bool isScraping: false
    property bool isInstallingCores: false
    property bool isUpdatingSystem: false
    property real scrapeVal: 0.0
    property string scrapeStatus: "LISTO"

    Rectangle { anchors.fill: parent; color: "#050505" }

    ColumnLayout {
        anchors.fill: parent; anchors.margins: 40; spacing: 25

        // 1. CABECERA
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 4
                Text { text: "GESTOR DE DESCARGAS"; color: "white"; font.pixelSize: 28; font.bold: true; font.letterSpacing: 2 }
                Text { text: "Núcleos, emuladores y soporte de medios"; color: "#66ffffff"; font.pixelSize: 14; font.bold: true }
            }
        }        // 2. PANEL DE SERVICIOS COMPACTO (Slim Design - Fixed Height)
        RowLayout {
            Layout.fillWidth: true; Layout.preferredHeight: 110; Layout.maximumHeight: 110; spacing: 15
            
            // Tarjeta 1: Mango Media Sync
            Rectangle {
                id: mangoCard
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 16
                color: mangoMA.containsMouse ? "#1a1a20" : "#0d0d10"
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
                    Text { text: "🥭"; font.pixelSize: 28; opacity: mangoMA.containsMouse ? 1.0 : 0.7 }
                    ColumnLayout {
                        spacing: 2
                        Text { text: "MEDIA SYNC"; color: "#f39c12"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: "Motor Mango"; color: "white"; font.pixelSize: 13; font.bold: true }
                        Text { text: "Sincronizar portadas"; color: "#66ffffff"; font.pixelSize: 9 }
                    }
                }
            }

            // Tarjeta 2: Libretro Cores
            Rectangle {
                id: coresCard
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 16
                color: coresMA.containsMouse ? "#1a1a20" : "#0d0d10"
                border.color: coresMA.containsMouse ? "#16a085" : "#3316a085"
                border.width: coresMA.containsMouse ? 2 : 1
                
                scale: coresMA.pressed ? 0.98 : 1.0
                y: coresMA.containsMouse ? -3 : 0
                Behavior on color { ColorAnimation { duration: 200 } }
                Behavior on border.color { ColorAnimation { duration: 200 } }
                Behavior on y { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 100 } }

                MouseArea { id: coresMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor }

                RowLayout {
                    anchors.fill: parent; anchors.margins: 15; spacing: 15
                    Text { text: "🧩"; font.pixelSize: 28; opacity: coresMA.containsMouse ? 1.0 : 0.7 }
                    ColumnLayout {
                        spacing: 2
                        Text { text: "NÚCLEOS"; color: "#16a085"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: "Libretro Hub"; color: "white"; font.pixelSize: 13; font.bold: true }
                        Text { text: "Instalar emuladores"; color: "#66ffffff"; font.pixelSize: 9 }
                    }
                }
            }

            // Tarjeta 3: System Update
            Rectangle {
                id: systemCard
                Layout.fillWidth: true; Layout.fillHeight: true; radius: 16
                color: systemMA.containsMouse ? "#1a1a20" : "#0d0d10"
                border.color: systemMA.containsMouse ? "#8e44ad" : "#338e44ad"
                border.width: systemMA.containsMouse ? 2 : 1
                
                scale: systemMA.pressed ? 0.98 : 1.0
                y: systemMA.containsMouse ? -3 : 0
                Behavior on color { ColorAnimation { duration: 200 } }
                Behavior on border.color { ColorAnimation { duration: 200 } }
                Behavior on y { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 100 } }

                MouseArea { id: systemMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor }

                RowLayout {
                    anchors.fill: parent; anchors.margins: 15; spacing: 15
                    Text { text: "🚀"; font.pixelSize: 28; opacity: systemMA.containsMouse ? 1.0 : 0.7 }
                    ColumnLayout {
                        spacing: 2
                        Text { text: "SISTEMA"; color: "#8e44ad"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: "Update Center"; color: "white"; font.pixelSize: 13; font.bold: true }
                        Text { text: "Actualizar app"; color: "#66ffffff"; font.pixelSize: 9 }
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


