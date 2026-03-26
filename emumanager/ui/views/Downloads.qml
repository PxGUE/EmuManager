import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0
import "../components"
import "../console_settings"

Item {
    id: downloadsRoot
    objectName: "downloadsView"
    
    // ... (anterior arriba omitido pero se asume igual)

    // Funciones de navegación y actualización
    function updateRepositories() {
        var repos = mainController.get_emulator_repositories()
        emulatorsModel.clear()
        for(var i=0; i < repos.length; i++) {
            emulatorsModel.append(repos[i])
        }
    }

    Component.onCompleted: {
        updateRepositories()
    }

    // Modelo de Repositorios (Emuladores)
    ListModel {
        id: emulatorsModel
    }
    
    // Estados
    property bool isScraping: false
    property bool isScanning: false
    property real scrapeVal: 0.0
    property real scanVal: 0.0
    property string scrapeLog: ""
    property string scanLog: ""
    property string scrapeStatus: I18n.t.ready_caps
    property string scanStatus: I18n.t.waiting_caps
    property bool isInstallingCores: false
    property bool isUpdatingSystem: false

    Rectangle { anchors.fill: parent; color: "#050505" }

    ColumnLayout {
        anchors.fill: parent; anchors.margins: 40; spacing: 25

        // 1. CABECERA
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 4
                Text { text: I18n.t.sync_center; color: "white"; font.pixelSize: 28; font.bold: true; font.letterSpacing: 2 }
                Text { text: I18n.t.sync_center_desc; color: "#66ffffff"; font.pixelSize: 14; font.bold: true }
            }
            Item { Layout.fillWidth: true }
            Button {
                id: syncBtn
                text: I18n.t.check_updates_btn
                flat: true; font.bold: true; font.pixelSize: 11
                Material.accent: "#16a085"
                background: Rectangle {
                    color: syncBtn.hovered ? "#16a08511" : "transparent"
                    border.color: "#16a085"; border.width: 1; radius: 20
                }
                onClicked: mainController.check_for_updates()
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
                    id: scanMA; anchors.fill: parent; hoverEnabled: !isScanning; cursorShape: isScanning ? Qt.ArrowCursor : Qt.PointingHandCursor 
                    enabled: !isScanning
                    onClicked: {
                        isScanning = true
                        mainController.scan_directories()
                    }
                }

                RowLayout {
                    anchors.fill: parent; anchors.margins: 15; spacing: 15
                    Text { text: "📡"; font.pixelSize: 32; opacity: scanMA.containsMouse || isScanning ? 1.0 : 0.7 }
                    ColumnLayout {
                        spacing: 2
                        Text { text: I18n.t.library; color: "#2ecc71"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: I18n.t.sync_roms; color: "white"; font.pixelSize: 14; font.bold: true }
                        Text { 
                            text: isScanning ? scanLog : (scanVal >= 1.0 ? I18n.t.scan_done : I18n.t.scan_idle)
                            color: isScanning ? "#2ecc71" : "#66ffffff"; font.pixelSize: 9; elide: Text.ElideRight; Layout.fillWidth: true 
                        }
                    }
                }
                
                // Barra de Progreso integrada (scan)
                Rectangle {
                    anchors.bottom: parent.bottom; anchors.left: parent.left; anchors.right: parent.right
                    height: 4; radius: 2; color: "transparent"; visible: isScanning
                    Rectangle {
                        width: parent.width * scanVal; height: parent.height; color: "#2ecc71"
                        Behavior on width { NumberAnimation { duration: 300 } }
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
                    id: mangoMA; anchors.fill: parent; hoverEnabled: !isScraping; cursorShape: isScraping ? Qt.ArrowCursor : Qt.PointingHandCursor 
                    enabled: !isScraping
                    onClicked: {
                        isScraping = true
                        mainController.start_scraping()
                    }
                }

                RowLayout {
                    anchors.fill: parent; anchors.margins: 15; spacing: 15
                    Text { text: "🥭"; font.pixelSize: 32; opacity: mangoMA.containsMouse || isScraping ? 1.0 : 0.7 }
                    ColumnLayout {
                        spacing: 2
                        Text { text: I18n.t.mango_monitor; color: "#f39c12"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: I18n.t.sync_media; color: "white"; font.pixelSize: 14; font.bold: true }
                        Text { 
                            text: isScraping ? scrapeLog : (scrapeVal >= 1.0 ? I18n.t.scrape_done : I18n.t.scrape_idle)
                            color: isScraping ? "#f39c12" : "#66ffffff"; font.pixelSize: 9; elide: Text.ElideRight; Layout.fillWidth: true 
                        }
                    }
                }

                // Barra de Progreso integrada (scrape)
                Rectangle {
                    anchors.bottom: parent.bottom; anchors.left: parent.left; anchors.right: parent.right
                    height: 4; radius: 2; color: "transparent"; visible: isScraping
                    Rectangle {
                        width: parent.width * scrapeVal; height: parent.height; color: "#f39c12"
                        Behavior on width { NumberAnimation { duration: 300 } }
                    }
                }
            }
        }

        // 3. GALERÍA DE REPOSITORIOS (NUEVO PROTAGONISTA)
        ColumnLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 15
            
            RowLayout {
                Layout.fillWidth: true
                Text { text: I18n.t.emu_gallery; color: "#16a085"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2 }
                Rectangle { Layout.fillWidth: true; height: 1; color: "#1a1a1f"; Layout.leftMargin: 15 }
            }

            ListView {
                id: emuList
                Layout.fillWidth: true; Layout.fillHeight: true
                model: emulatorsModel; clip: true; spacing: 20
                
                delegate: DownloadConsoleItem {
                    width: emuList.width - 20; height: 180
                    emuId: model.id
                    name: model.name; consoleName: model.fullName
                    description: model.description; icon: model.icon
                    accent: model.accent; downloadUrl: model.downloadUrl
                    executable: model.executable; isInstalled: model.isInstalled
                    hasUpdate: model.hasUpdate !== undefined ? model.hasUpdate : false
                    
                    // Vinculación directa a señales
                    progress: model.progress !== undefined ? model.progress : 0.0
                    statusText: model.statusText !== undefined ? model.statusText : ""

                    onConfigClicked: {
                        if (emuId === "retroarch") {
                            retroArchPopup.open()
                        } else {
                            mainController.open_emulator_folder(executable)
                        }
                    }
                }
            }
        }

    }

    // --- COMPONENTES MODULARES DE AJUSTES ---
    RetroArchSettings { id: retroArchPopup; controller: mainController }

    // Conectar señales globales para refrescar la lista de instalados
    Connections {
        target: mainController
        
        function onScanProgressChanged(p) { scanVal = p }
        function onScanStatusChanged(s) { scanLog = I18n.tp(s); isScanning = true }
        function onScanFinished(n) { scanVal = 1.0; scanLog = I18n.t.scan_finished.arg(n); isScanning = false }
        
        function onScrapeProgressChanged(p) { scrapeVal = p }
        function onScrapeStatusChanged(s) { scrapeLog = I18n.tp(s); isScraping = true }
        function onScrapeFinished(n) { scrapeVal = 1.0; scrapeLog = I18n.t.scrape_done; isScraping = false }

        // Señales de Core (Actualización de ambos modelos)
        function onCoreDownloadStatusChanged(emu_id, s) {
            if (emu_id === "all") {
                // Simular actualizaciones si es necesario
                for(var i=0; i < emulatorsModel.count; i++) {
                    if (emulatorsModel.get(i).isInstalled) {
                        emulatorsModel.setProperty(i, "hasUpdate", true)
                    }
                }
            } else {
                // Actualización masiva de estado para un ID específico
                for(var i=0; i < emulatorsModel.count; i++) {
                    if(emulatorsModel.get(i).id === emu_id) {
                        emulatorsModel.setProperty(i, "statusText", I18n.tp(s))
                        break
                    }
                }
            }
        }

        function onCoreDownloadProgressChanged(emu_id, p) {
            // 1. Actualizar Galería de Emuladores
            for(var i=0; i < emulatorsModel.count; i++) {
                if(emulatorsModel.get(i).id === emu_id) {
                    emulatorsModel.setProperty(i, "progress", p)
                    break
                }
            }
            // 2. Actualizar Popup de Cores (Si está en el módulo)
            retroArchPopup.updateProgress(emu_id, p)
        }

        function onCoreDownloadFinished(emu_id, path) {
            updateRepositories() 
            retroArchPopup.markFinished(emu_id)
        }

        function onGamesUpdated() {
            updateRepositories()
        }
    }
}


