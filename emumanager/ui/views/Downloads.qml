import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0
import "../components"
import "../console_settings"

Item {
    id: downloadsRoot
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
        // Forzamos la creación de roles críticos para evitar avisos de 'undefined'
        Component.onCompleted: {
            if (count === 0) {
                append({
                    "id": "", "name": "", "fullName": "", "description": "", 
                    "icon": "", "accent": "", "downloadUrl": "", "executable": "", 
                    "isInstalled": false, "hasUpdate": false, "progress": 0.0, "statusText": ""
                })
                clear()
            }
        }
    }
    
    // Estados Centralizados
    readonly property bool isScraping: mainController ? mainController.isScraping : false
    readonly property bool isScanning: mainController ? mainController.isScanning : false
    // Propiedades de Progreso (Actualizadas por señales para máxima reactividad)
    // Propiedades de Progreso (Vinculación Directa al Motor Nativo)
    property real scrapeVal: mainController ? mainController.scrapeProgress : 0.0
    property real scanVal: mainController ? mainController.scanProgress : 0.0
    
    // Logs locales para UX inmediata
    property string scrapeLog: ""
    property string scanLog: ""
    
    // UX: Estado centralizado para bloqueo de concurrencia
    readonly property bool isAnyOperationRunning: mainController ? mainController.isEngineBusy : false

    Rectangle { anchors.fill: parent; color: Theme.viewBackground }

    ColumnLayout {
        anchors.fill: parent; anchors.margins: Theme.spaceExtraLarge; spacing: Theme.spaceLarge

        // 1. CABECERA
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 4
                Text { text: I18n.t.sync_center; color: Theme.textMain; font.pixelSize: Theme.fontTitle; font.bold: true; font.letterSpacing: 2 }
                Text { text: I18n.t.sync_center_desc; color: Theme.textMuted; font.pixelSize: Theme.fontBody; font.bold: true }
            }
            Item { Layout.fillWidth: true }
            Button {
                id: syncBtn
                text: I18n.t.check_updates_btn
                flat: true; font.bold: true; font.pixelSize: 11
                Material.accent: Theme.accentColor
                background: Rectangle {
                    color: syncBtn.hovered ? Theme.accentColor + "11" : Theme.transparent
                    border.color: Theme.accentColor; border.width: Theme.borderThin; radius: Theme.radiusMedium
                }
                enabled: !isAnyOperationRunning
                opacity: enabled ? 1.0 : 0.3
                Behavior on opacity { NumberAnimation { duration: 300 } }
                onClicked: mainController.check_for_updates()
            }
        }
        // 2. PANEL DE OPERACIONES (Control Maestro)
        RowLayout {
            Layout.fillWidth: true; Layout.preferredHeight: 120; Layout.maximumHeight: 120; spacing: Theme.spaceMedium
            
            // Tarjeta 1: Escanear Biblioteca (Radar)
            Rectangle {
                id: scanCard
                Layout.fillWidth: true; Layout.fillHeight: true; radius: Theme.radiusMedium
                color: (scanMA.containsMouse && scanMA.enabled) ? Theme.statusSuccess + "11" : Theme.cardBackground
                border.color: (scanMA.containsMouse && scanMA.enabled) ? Theme.statusSuccess : Theme.cardBorder
                border.width: (scanMA.containsMouse && scanMA.enabled) ? Theme.borderThick : Theme.borderThin
                
                scale: scanMA.pressed ? 0.98 : 1.0
                y: (scanMA.containsMouse && scanMA.enabled) ? -3 : 0
                Behavior on color { ColorAnimation { duration: 200 } }
                Behavior on border.color { ColorAnimation { duration: 200 } }
                Behavior on y { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 100 } }

                MouseArea { 
                    id: scanMA; anchors.fill: parent; hoverEnabled: !isAnyOperationRunning; cursorShape: isAnyOperationRunning ? Qt.ArrowCursor : Qt.PointingHandCursor 
                    enabled: !isAnyOperationRunning
                    onClicked: {
                        mainController.start_full_scan()
                    }
                }

                RowLayout {
                    anchors.fill: parent; anchors.margins: Theme.spaceMedium; spacing: Theme.spaceMedium
                    
                    // Icono con indicador de actividad
                    Item {
                        Layout.preferredWidth: 40; Layout.fillHeight: true
                        Text { 
                            anchors.centerIn: parent; text: "📡"; font.pixelSize: Theme.fontTitle
                            opacity: scanMA.containsMouse || isScanning ? 1.0 : 0.4
                        }
                        // Pulso de Actividad
                        Rectangle {
                            visible: isScanning; width: 8; height: 8; radius: 4; color: Theme.statusSuccess
                            anchors.right: parent.right; anchors.top: parent.top; anchors.topMargin: 10
                            SequentialAnimation on opacity {
                                loops: Animation.Infinite; NumberAnimation { from: 1; to: 0; duration: 800 }
                                NumberAnimation { from: 0; to: 1; duration: 800 }
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true; spacing: 4
                        Text { text: I18n.t.library; color: Theme.statusSuccess; font.pixelSize: Theme.fontSmall; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: I18n.t.sync_roms; color: Theme.textMain; font.pixelSize: Theme.fontBody; font.bold: true }
                        
                        // Barra de Progreso Maestra
                        ProgressBar {
                            visible: isScanning; value: scanVal; Layout.fillWidth: true; Layout.preferredHeight: 6
                            background: Rectangle { color: Theme.transparent; radius: 3; border.color: Theme.cardBorder }
                            contentItem: Rectangle { 
                                width: parent.visualPosition * parent.width
                                height: parent.height; radius: 3; color: Theme.statusSuccess 
                            }
                        }

                        Text { 
                            text: isScanning ? scanLog : (scanVal >= 1.0 ? I18n.t.scan_done : I18n.t.scan_idle)
                            color: isScanning ? Theme.statusSuccess : Theme.textMuted
                            font.pixelSize: Theme.fontMicro; font.bold: isScanning; elide: Text.ElideRight; Layout.fillWidth: true 
                        }
                    }
                }
            }

            // Tarjeta 2: Mango Media Sync (El Scraping Modular)
            Rectangle {
                id: mangoCard
                Layout.fillWidth: true; Layout.fillHeight: true; radius: Theme.radiusMedium
                color: (mangoMA.containsMouse && mangoMA.enabled) ? Theme.statusWarning + "11" : Theme.cardBackground
                border.color: (mangoMA.containsMouse && mangoMA.enabled) ? Theme.statusWarning : Theme.cardBorder
                border.width: (mangoMA.containsMouse && mangoMA.enabled) ? Theme.borderThick : Theme.borderThin
                
                scale: mangoMA.pressed ? 0.98 : 1.0
                y: (mangoMA.containsMouse && mangoMA.enabled) ? -3 : 0
                Behavior on color { ColorAnimation { duration: 200 } }
                Behavior on border.color { ColorAnimation { duration: 200 } }
                Behavior on y { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                Behavior on scale { NumberAnimation { duration: 100 } }

                MouseArea { 
                    id: mangoMA; anchors.fill: parent; hoverEnabled: !isAnyOperationRunning; cursorShape: isAnyOperationRunning ? Qt.ArrowCursor : Qt.PointingHandCursor 
                    enabled: !isAnyOperationRunning
                    onClicked: {
                        mainController.start_scraping()
                    }
                }

                RowLayout {
                    anchors.fill: parent; anchors.margins: Theme.spaceMedium; spacing: Theme.spaceMedium
                    
                    // Icono con indicador de actividad
                    Item {
                        Layout.preferredWidth: 40; Layout.fillHeight: true
                        Text { 
                            anchors.centerIn: parent; text: "🥭"; font.pixelSize: Theme.fontTitle
                            opacity: mangoMA.containsMouse || isScraping ? 1.0 : 0.4
                        }
                        // Pulso de Actividad
                        Rectangle {
                            visible: isScraping; width: 8; height: 8; radius: 4; color: Theme.statusWarning
                            anchors.right: parent.right; anchors.top: parent.top; anchors.topMargin: 10
                            SequentialAnimation on opacity {
                                loops: Animation.Infinite; NumberAnimation { from: 1; to: 0; duration: 800 }
                                NumberAnimation { from: 0; to: 1; duration: 800 }
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true; spacing: 4
                        Text { text: I18n.t.mango_monitor; color: Theme.statusWarning; font.pixelSize: Theme.fontSmall; font.bold: true; font.letterSpacing: 1.5 }
                        Text { text: I18n.t.sync_media; color: Theme.textMain; font.pixelSize: Theme.fontBody; font.bold: true }

                        // Barra de Progreso Maestra
                        ProgressBar {
                            visible: isScraping; value: scrapeVal; Layout.fillWidth: true; Layout.preferredHeight: 6
                            background: Rectangle { color: Theme.transparent; radius: 3; border.color: Theme.cardBorder }
                            contentItem: Rectangle { 
                                width: parent.visualPosition * parent.width
                                height: parent.height; radius: 3; color: Theme.statusWarning 
                            }
                        }

                        Text { 
                            text: isScraping ? scrapeLog : (scrapeVal >= 1.0 ? I18n.t.scrape_done : I18n.t.scrape_idle)
                            color: isScraping ? Theme.statusWarning : Theme.textMuted
                            font.pixelSize: Theme.fontMicro; font.bold: isScraping; elide: Text.ElideRight; Layout.fillWidth: true 
                        }
                    }
                }
            }
        }

        // 3. GALERÍA DE REPOSITORIOS (NUEVO PROTAGONISTA)
        ColumnLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: Theme.spaceMedium
            
            RowLayout {
                Layout.fillWidth: true
                Text { text: I18n.t.emu_gallery; color: Theme.accentColor; font.pixelSize: Theme.fontBody; font.bold: true; font.letterSpacing: 2 }
                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider; Layout.leftMargin: Theme.spaceMedium }
            }

            ListView {
                id: emuList
                Layout.fillWidth: true; Layout.fillHeight: true
                model: emulatorsModel; clip: true; spacing: Theme.spaceLarge
                
                delegate: DownloadConsoleItem {
                    width: emuList.width - 20; height: 180
                    emuId: model.id
                    name: model.name; consoleName: model.fullName
                    description: model.description; icon: model.icon
                    accent: model.accent; downloadUrl: model.downloadUrl
                    executable: model.executable; isInstalled: model.isInstalled
                    hasUpdate: model.hasUpdate !== undefined ? model.hasUpdate : false
                    
                    // UX: Bloqueo por concurrencia global
                    enabled: !isAnyOperationRunning || progress > 0
                    opacity: enabled ? 1.0 : 0.5
                    Behavior on opacity { NumberAnimation { duration: 300 } }
                    
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
    RetroArchSettings { 
        id: retroArchPopup; 
        controller: mainController; 
        isGlobalBusy: downloadsRoot.isAnyOperationRunning 
    }

    // Conectar señales globales para refrescar la lista de instalados
    Connections {
        target: mainController
        
        function onScanStatusChanged(s) { scanLog = I18n.tp(s) }
        function onScanFinished(n) { 
            scanLog = I18n.t.scan_finished.arg(n); 
            window.pushNotification("Operación Completada", "MANGO", "Se han registrado " + n + " nuevos juegos en tu biblioteca.", Theme.statusSuccess)
        }
        
        function onScrapeStatusChanged(s) { scrapeLog = I18n.tp(s) }
        function onScrapeFinished(n) { 
            scrapeLog = I18n.t.scrape_done; 
            window.pushNotification("Actualización de Media", "MANGO", "Se ha completado el proceso de obtención de metadatos.", Theme.statusWarning)
        }

        // Señales de Core (Actualización de ambos modelos)
        function onCoreDownloadStatusChanged(emu_id, s) {
            if (emu_id === "all") {
                for(var i=0; i < emulatorsModel.count; i++) {
                    if (emulatorsModel.get(i).isInstalled) {
                        emulatorsModel.setProperty(i, "hasUpdate", true)
                    }
                }
            } else {
                for(var i=0; i < emulatorsModel.count; i++) {
                    if(emulatorsModel.get(i).id === emu_id) {
                        emulatorsModel.setProperty(i, "statusText", s)
                        break
                    }
                }
            }
        }

        function onCoreDownloadProgressChanged(emu_id, p) {
            for(var i=0; i < emulatorsModel.count; i++) {
                if(emulatorsModel.get(i).id === emu_id) {
                    emulatorsModel.setProperty(i, "progress", p)
                    break
                }
            }
            retroArchPopup.updateProgress(emu_id, p)
        }

        function onCoreDownloadFinished(emu_id, path) {
            updateRepositories() 
            retroArchPopup.markFinished(emu_id)
        }

        function onGamesUpdated() { updateRepositories() }
    }
}


