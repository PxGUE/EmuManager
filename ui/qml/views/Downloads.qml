import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: downloadsRoot
    
    property string activeGroup: "all"
    property string searchText: ""

    property bool scrapersExpanded: false

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
                    text: (bridge && bridge.currentLanguage) ? bridge.translate("nav_downloads") : "Downloads"
                    font.pixelSize: 32
                    font.bold: true
                    color: "white"
                }
                Label {
                    text: (bridge && bridge.currentLanguage) ? bridge.translate("dl_list_sub") : ""
                    font.pixelSize: 14
                    color: "#888899"
                }
            }
            Item { Layout.fillWidth: true }
        }
        
        // SECTION TITLE: EMULATORS
        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 10
            spacing: 12
            Rectangle { 
                width: 4; height: 24; radius: 2; color: "#4da6ff" 
            }
            Label {
                text: (bridge && bridge.currentLanguage ? bridge.translate("dl_main_title") : "EMULATORS")
                font.pixelSize: 18
                font.bold: true
                color: "white"
                font.letterSpacing: 1
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
                        // Convertimos la lista de emuladores a string para que ListModel la acepte
                        row.emulatorsJson = JSON.stringify(row.emulators)
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
                    emulatorsJson: model.emulatorsJson // Pasamos el string JSON
                    isInstalled: model.isInstalled
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
                color: "#1a1626"
                border.color: "#2a2838"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20
                    spacing: 12

                    Label {
                        text: scrapersExpanded ? "▼" : "▶"
                        font.pixelSize: 12
                        color: "#7c6ff7"
                    }

                    Label {
                        text: (bridge && bridge.currentLanguage ? bridge.translate("dl_scrap_title").toUpperCase() : "METADATA & ARTWORK")
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
                Layout.preferredHeight: scrapersExpanded ? 80 : 0
                clip: true
                color: "#13111d"
                border.color: "#2a2838"
                border.width: 1
                bottomLeftRadius: 15
                bottomRightRadius: 15
                
                Behavior on Layout.preferredHeight {
                    NumberAnimation { duration: 300; easing.type: Easing.OutCubic }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 20
                    visible: scrapContent.height > 10

                    ColumnLayout {
                        spacing: 2
                        Layout.fillWidth: true
                        Label {
                            text: (bridge && bridge.currentLanguage) ? bridge.translate("dl_scrap_sub") : "Obtén carátulas y fondos para tus juegos."
                            font.pixelSize: 11
                            color: "#888899"
                            wrapMode: Text.WordWrap
                        }
                    }

                    Button {
                        id: scrapeBtn
                        Layout.preferredWidth: 140
                        Layout.preferredHeight: 36
                        enabled: bridge && bridge.dashboardStats && bridge.dashboardStats.installed > 0
                        onClicked: bridge.scanGames()
                        
                        background: Rectangle {
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0.0; color: "#4da6ff" }
                                GradientStop { position: 1.0; color: "#7c6ff7" }
                            }
                            radius: 10
                            opacity: !scrapeBtn.enabled ? 0.3 : (scrapeBtn.hovered ? 1.0 : 0.9)
                        }
                        
                        contentItem: Label {
                            text: (bridge && bridge.currentLanguage) ? bridge.translate("set_btn_download") : "DESCARGAR"
                            color: scrapeBtn.enabled ? "white" : "#888899"
                            font.bold: true
                            font.pixelSize: 11
                            font.letterSpacing: 1
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }
        }
    }
}
