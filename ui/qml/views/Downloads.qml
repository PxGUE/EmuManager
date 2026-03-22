import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects
import "../components"

Item {
    id: downloadsRoot
    
    property string activeGroup: "all"
    property string searchText: ""

    property bool scrapersExpanded: false
    property bool downloadArtwork: true
    property bool downloadMetadata: true
    
    property real scanProgress: 0.0
    property string scanStatusText: ""
    property bool isCheckingUpdates: false
    property var updateResults: ({})

    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 40
        spacing: 20

        // HEADER
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 4
                Label {
                    text: tr("nav_downloads")
                    font.pixelSize: 32
                    font.bold: true
                    color: "white"
                }
                Label {
                    text: tr("dl_list_sub")
                    font.pixelSize: 14
                    color: "#888899"
                }
            }
            Item { Layout.fillWidth: true }

            Button {
                id: btnCheckUpdates
                Layout.preferredHeight: 44
                padding: 15
                enabled: !isCheckingUpdates
                onClicked: {
                    isCheckingUpdates = true
                    bridge.maint.checkUpdates()
                }
                
                background: Rectangle {
                    color: btnCheckUpdates.pressed ? Qt.rgba(0.12, 0.05, 0.22, 1.0) : (btnCheckUpdates.hovered ? Qt.rgba(0.08, 0.05, 0.18, 0.9) : "transparent")
                    radius: 14
                    border.color: isCheckingUpdates ? window.neonGold : (btnCheckUpdates.hovered ? window.neonViolet : Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.3))
                    border.width: 1
                    scale: btnCheckUpdates.pressed ? 0.98 : 1.0
                    Behavior on scale { NumberAnimation { duration: 100 } }
                    Behavior on border.color { ColorAnimation { duration: 200 } }
                }

                contentItem: RowLayout {
                    spacing: 10
                    Label { 
                        text: ""
                        font.pixelSize: 16
                        RotationAnimation on rotation {
                            from: 0; to: 360; duration: 1000; loops: Animation.Infinite; running: isCheckingUpdates
                        }
                    }
                    Label { 
                        text: isCheckingUpdates ? tr("maint_checking_updates").toUpperCase() : tr("maint_check_btn").toUpperCase()
                        color: isCheckingUpdates ? window.neonGold : "#f0e8ff"
                        font.pixelSize: 12; font.bold: true; font.letterSpacing: 0.5
                    }
                }
            }
        }
        
        // STATUS BAR FOR UPDATES (REDISEÑADA)
        ColumnLayout {
            Layout.fillWidth: true
            Layout.topMargin: -10
            Layout.bottomMargin: 10
            visible: isCheckingUpdates
            spacing: 6
            
            Label {
                text: tr("maint_checking_updates").toUpperCase()
                font.pixelSize: 10
                font.bold: true
                color: window.neonGold
                font.letterSpacing: 1.2
                Layout.alignment: Qt.AlignHCenter
            }

            Rectangle {
                id: progressContainer
                Layout.fillWidth: true; height: 3; radius: 2
                color: Qt.rgba(1,1,1,0.06); clip: true
                Rectangle {
                    id: indicator
                    width: parent.width * 0.3; height: parent.height; radius: 2
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: window.neonViolet }
                        GradientStop { position: 1.0; color: window.neonMagenta }
                    }
                    NumberAnimation on x {
                        from: -indicator.width; to: progressContainer.width
                        duration: 1200; loops: Animation.Infinite; running: isCheckingUpdates
                    }
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 10
            spacing: 12
            Rectangle { 
                width: 3; height: 22; radius: 2; color: window.neonViolet
                layer.enabled: true
                layer.effect: MultiEffect { shadowEnabled: true; shadowColor: window.neonViolet; shadowBlur: 0.8; shadowOpacity: 0.7 }
            }
            Label {
                text: tr("dl_main_title")
                font.pixelSize: 18; font.bold: true; color: "#f0e8ff"; font.letterSpacing: 0.5
            }
        }

        // Local Model to prevent scroll reset
        ListModel {
            id: localEmuModel
            function refresh() {
                if (!bridge) return
                var data = bridge.allEmulators
                if (count === 0) {
                    for (var i = 0; i < data.length; i++) {
                        var row = data[i]
                        row.emulatorsJson = JSON.stringify(row.emulators)
                        delete row.emulators // ¡SOLUCIÓN!
                        append(row)
                    }
                } else {
                    for (var j = 0; j < data.length; j++) {
                        setProperty(j, "isInstalled", data[j].isInstalled)
                        setProperty(j, "emulatorsJson", JSON.stringify(data[j].emulators))
                    }
                }
            }
        }

        Component.onCompleted: localEmuModel.refresh()

        Connections {
            target: bridge
            function onStatsUpdated() { localEmuModel.refresh() }
            function onScanProgress(prog, status) {
                downloadsRoot.scanProgress = prog
                downloadsRoot.scanStatusText = status
            }
            function onDownloadFinished(emu_id, success, msg) {
                if (success) {
                    var temp = downloadsRoot.updateResults
                    if (temp[emu_id]) {
                        delete temp[emu_id]
                        downloadsRoot.updateResults = Object.assign({}, temp)
                    }
                }
            }
        }

        Connections {
            target: bridge ? bridge.maint : null
            function onUpdatesDiscoveryFinished(results) {
                isCheckingUpdates = false
                var count = Object.keys(results).filter(k => results[k].update_available).length
                console.log("[UI] Descubrimiento de actualizaciones finalizado. Encontradas:", count)
                downloadsRoot.updateResults = results
            }
        }

        // GRID
        GridView {
            id: downloadGrid
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            cellWidth: width / Math.max(1, Math.floor(width / 340))
            cellHeight: 520
            
            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
            }

            model: localEmuModel
            
            delegate: Item {
                property bool isMatch: (activeGroup === "all" || model.id === activeGroup) && 
                                      (searchText === "" || model.name.toLowerCase().includes(searchText.toLowerCase()))
                
                width: isMatch ? downloadGrid.cellWidth : 0
                height: isMatch ? downloadGrid.cellHeight : 0
                visible: isMatch

                EmulatorCard {
                    anchors.centerIn: parent
                    anchors.margins: 10
                    width: parent.width - 20
                    height: parent.height - 20
                    
                    name: model.name
                    accentColor: model.accentColor
                    emulatorsJson: model.emulatorsJson 
                    isInstalled: model.isInstalled
                    updateResults: downloadsRoot.updateResults
                }
            }
        }

        // BARRA DE SCRAPEO DESPLEGABLE
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 0
            
            // Header / Toggle
            Rectangle {
                Layout.fillWidth: true
                height: 50
                radius: scrapersExpanded ? 0 : 15
                topLeftRadius: 15
                topRightRadius: 15
                bottomLeftRadius: scrapersExpanded ? 0 : 15
                bottomRightRadius: scrapersExpanded ? 0 : 15
                color: Qt.rgba(0.07, 0.04, 0.15, 0.9)
                border.color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.22)
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20
                    spacing: 12

                    Label {
                        text: scrapersExpanded ? "▼" : "▶"
                        font.pixelSize: 12
                        color: window.neonViolet
                    }

                    Label {
                        text: tr("dl_scrap_title").toUpperCase()
                        font.pixelSize: 14
                        font.bold: true
                        color: "white"
                        font.letterSpacing: 1
                    }

                    Item { Layout.fillWidth: true }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: scrapersExpanded = !scrapersExpanded
                }
            }

            // Contenido Desplegable
            Rectangle {
                id: scrapContent
                Layout.fillWidth: true
                Layout.preferredHeight: scrapersExpanded ? scrapLayout.implicitHeight + 50 : 0
                clip: true
                color: Qt.rgba(0.05, 0.02, 0.1, 0.97)
                border.color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.18)
                border.width: 1
                bottomLeftRadius: 15
                bottomRightRadius: 15
                
                Behavior on Layout.preferredHeight {
                    NumberAnimation { duration: 400; easing.type: Easing.OutCubic }
                }

                ColumnLayout {
                    id: scrapLayout
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 25
                    spacing: 25
                    visible: scrapContent.height > 20

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            Label {
                                text: tr("dl_scrap_dlg_q").toUpperCase()
                                font.pixelSize: 12; font.bold: true; color: window.neonViolet; font.letterSpacing: 1.5
                            }
                            Label {
                                text: tr("dl_scrap_sub")
                                font.pixelSize: 13; color: "#888899"
                            }
                        }

                        Button {
                            id: scrapeBtn
                            Layout.preferredWidth: 180
                            Layout.preferredHeight: 44
                            enabled: bridge && bridge.lib.dashboardStats && bridge.lib.dashboardStats.installed > 0
                            onClicked: bridge.lib.scanGames(downloadArtwork, downloadMetadata, "")
                            
                            background: Rectangle {
                                gradient: Gradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop { position: 0.0; color: window.neonViolet }
                                    GradientStop { position: 1.0; color: window.neonMagenta }
                                }
                                radius: 14
                                opacity: !scrapeBtn.enabled ? 0.3 : (scrapeBtn.hovered ? 1.0 : 0.9)
                                Rectangle {
                                    anchors.fill: parent; radius: 14
                                    color: "transparent"; border.color: "white"; border.width: 1
                                    opacity: scrapeBtn.hovered ? 0.2 : 0
                                    Behavior on opacity { NumberAnimation { duration: 200 } }
                                }
                            }
                            
                            contentItem: RowLayout {
                                spacing: 10
                                Label { text: "⚡"; font.pixelSize: 16 }
                                Label {
                                    text: tr("set_btn_download")
                                    color: "white"; font.bold: true; font.pixelSize: 12; font.letterSpacing: 1
                                }
                            }
                        }
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.15); opacity: 0.7 }

                    // LISTA DE OPCIONES CREATIVA
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        // Reusable delegate-like items for the list
                        // Artwork Item
                        Rectangle {
                            Layout.fillWidth: true; height: 52; radius: 16
                            color: downloadArtwork ? Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.12) : Qt.rgba(1,1,1,0.03)
                            border.color: downloadArtwork ? window.neonViolet : Qt.rgba(1,1,1,0.08); border.width: 1
                            Behavior on color { ColorAnimation { duration: 200 } }
                            
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 15; spacing: 15
                                Label { text: "🖼️"; font.pixelSize: 18 }
                                Label { 
                                    text: tr("dl_scrap_opt_artwork")
                                    color: "white"; font.pixelSize: 13; font.weight: Font.Medium; Layout.fillWidth: true 
                                }
                                Switch {
                                    checked: downloadArtwork
                                    onToggled: downloadArtwork = checked
                                }
                            }
                        }


                        // Metadata Item
                        Rectangle {
                            Layout.fillWidth: true; height: 52; radius: 16
                            color: downloadMetadata ? Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.12) : Qt.rgba(1,1,1,0.03)
                            border.color: downloadMetadata ? window.neonViolet : Qt.rgba(1,1,1,0.08); border.width: 1
                            Behavior on color { ColorAnimation { duration: 200 } }
                            
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 15; spacing: 15
                                Label { text: "📋"; font.pixelSize: 18 }
                                Label { 
                                    text: tr("dl_scrap_opt_metadata")
                                    color: "white"; font.pixelSize: 13; font.weight: Font.Medium; Layout.fillWidth: true 
                                }
                                Switch {
                                    checked: downloadMetadata
                                    onToggled: downloadMetadata = checked
                                }
                            }
                        }
                    }

                    // SCAN PROGRESS (NUEVO)
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        visible: scanProgress > 0 || scanStatusText !== ""
                        
                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                text: scanStatusText
                                color: "#888899"
                                font.pixelSize: 12
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                            Label {
                                text: Math.round(scanProgress * 100) + "%"
                                color: window.themeAccent
                                font.pixelSize: 12
                                font.bold: true
                            }
                        }

                        ProgressBar {
                            id: scanBar
                            Layout.fillWidth: true
                            Layout.preferredHeight: 8
                            value: scanProgress
                            
                            background: Rectangle {
                                implicitWidth: 200
                                implicitHeight: 8
                                color: "#1a1e2e"
                                radius: 4
                            }

                            contentItem: Item {
                                implicitWidth: 200
                                implicitHeight: 8

                                Rectangle {
                                    width: scanBar.visualPosition * parent.width
                                    height: parent.height; radius: 4
                                    gradient: Gradient {
                                        orientation: Gradient.Horizontal
                                        GradientStop { position: 0.0; color: window.neonViolet }
                                        GradientStop { position: 1.0; color: window.neonMagenta }
                                    }
                                    layer.enabled: true
                                    layer.effect: MultiEffect {
                                        shadowEnabled: true; shadowColor: window.neonViolet
                                        shadowBlur: 0.8; shadowOpacity: 0.7
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
