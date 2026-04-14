import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "../components"
import "../components/cards"
import "../components/system"
import "../components/effects"

Item {
    id: discoveryRoot
    anchors.fill: parent
    
    property var discoveryData: ({ "on_this_day": [], "hidden_gems": [], "random_batch": [] })
    property bool isLoading: true

    function refresh() {
        isLoading = true
        discoveryData = mainController.statsController.get_discovery_data()
        isLoading = false
    }

    Component.onCompleted: refresh()

    // --- 1. THE KINETIC VAULT BACKGROUND ---
    NebulaBackground {
        accentColor: Theme.accentElectric
        interactiveForce: 0.1
    }

    // --- 2. MAIN HUB ---
    Flickable {
        id: vaultScroll
        anchors.fill: parent
        anchors.topMargin: 0
        clip: true
        
        contentWidth: width; contentHeight: vaultContent.height
        flickableDirection: Flickable.VerticalFlick
        boundsBehavior: Flickable.StopAtBounds
        
        ScrollBar.vertical: ScrollBar { 
            width: 4; policy: ScrollBar.AsNeeded; active: true
            contentItem: Rectangle { color: Theme.accentElectric; radius: 2; opacity: 0.3 }
        }

        ColumnLayout {
            id: vaultContent
            width: discoveryRoot.width - 90
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 50
            
            Item { Layout.preferredHeight: 60 } // Top Padding

            // --- A. MISSION TITLE & ENGINE STATUS ---
            RowLayout {
                Layout.fillWidth: true
                ColumnLayout {
                    spacing: 0
                    Text { 
                        text: I18n.t.vault_title.toUpperCase(); 
                        color: Theme.textMain; font.pixelSize: 48; font.weight: Font.Black; font.letterSpacing: -2 
                    }
                    Text { 
                        text: "EXPLORA LOS SECRETOS DE TU COLECCIÓN"; 
                        color: Theme.accentElectric; font.pixelSize: 12; font.bold: true; font.letterSpacing: 4; opacity: 0.8
                    }
                }
                Item { Layout.fillWidth: true }
                GlassPanel {
                    width: 140; height: 50; radius: 12
                    content: ColumnLayout {
                        anchors.centerIn: parent; spacing: -2
                        Text { text: "ESTADO"; color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1; Layout.alignment: Qt.AlignCenter }
                        Text { text: "SINCRO OK"; color: Theme.statusSuccess; font.pixelSize: 12; font.bold: true; Layout.alignment: Qt.AlignCenter }
                    }
                }
            }

            // --- B. HERO SECTION: ON THIS DAY (THE SPOTLIGHT) ---
            Item {
                Layout.fillWidth: true; Layout.preferredHeight: 320
                visible: true
                
                property bool hasData: discoveryData.on_this_day && discoveryData.on_this_day.length > 0
                property var heroGame: hasData ? discoveryData.on_this_day[0] : null

                GlassPanel {
                    anchors.fill: parent; radius: 24; glassOpacity: 0.3
                    borderColor: Theme.accentElectric; borderWidth: 2
                    
                    RowLayout {
                        anchors.fill: parent; anchors.margins: 30; spacing: 40
                        
                        // Game Cover with Reflection
                        Item {
                            Layout.preferredWidth: 180; Layout.fillHeight: true
                            Rectangle {
                                anchors.fill: parent; radius: 15; color: Theme.backgroundVoid; clip: true
                                Image {
                                    anchors.fill: parent; fillMode: Image.PreserveAspectCrop
                                    source: parent.parent.parent.parent.heroGame ? "file:///" + parent.parent.parent.parent.heroGame.cover_2d_path : ""
                                    asynchronous: true; opacity: status === Image.Ready ? 1.0 : 0.2
                                }
                                visible: parent.parent.parent.parent.hasData
                            }
                            // Placeholder
                            Text { 
                                anchors.centerIn: parent; text: "📅"; font.pixelSize: 64; opacity: 0.2
                                visible: !parent.parent.parent.parent.hasData
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 15
                            Rectangle {
                                width: 120; height: 24; radius:12; color: Theme.accentElectric
                                Text { anchors.centerIn: parent; text: "EFEMÉRIDES"; color: Theme.white; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
                            }
                            
                            Text { 
                                text: parent.parent.parent.hasData ? parent.parent.parent.heroGame.title : "NADA QUE REPORTAR HOY"
                                color: Theme.textMain; font.pixelSize: 32; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true 
                            }
                            
                            Text { 
                                text: parent.parent.parent.hasData ? 
                                    "Un día como hoy en " + parent.parent.parent.heroGame.release_date.split("-")[0] + ", este clásico llegaba a las tiendas. ¿Listo para revivir la historia?" :
                                    "No hay registros históricos en tu colección para la fecha de hoy. ¡Escanea más juegos para completar el calendario!"
                                color: Theme.textMuted; font.pixelSize: 16; wrapMode: Text.WordWrap; Layout.fillWidth: true; opacity: 0.8
                            }
                            
                            Item { Layout.fillHeight: true }
                            
                            Button {
                                text: parent.parent.parent.hasData ? "REVIVIR HISTORIA" : "IR A LA BIBLIOTECA"
                                Layout.preferredWidth: 200; Layout.preferredHeight: 44
                                Material.background: parent.parent.parent.hasData ? Theme.accentElectric : Theme.controlBackground
                                onClicked: parent.parent.parent.hasData ? mainController.launch_game_by_id(parent.parent.parent.heroGame.id) : activeViewId = "libraryView"
                            }
                        }
                    }
                }
            }

            // --- C. HORIZONTAL STRIP: HIDDEN GEMS ---
            ColumnLayout {
                Layout.fillWidth: true; spacing: 20
                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "RELIQUIAS OLVIDADAS"; color: Theme.textMain; font.pixelSize: 18; font.bold: true; font.letterSpacing: 2 }
                    Rectangle { Layout.fillWidth: true; height: 1; color: Theme.cardBorder; opacity: 0.1; Layout.leftMargin: 20 }
                }

                Text {
                    visible: !(discoveryData.hidden_gems && discoveryData.hidden_gems.length > 0)
                    text: "M.A.N.G.O no ha encontrado joyas ocultas. Scrapea tu colección para analizar juegos nunca antes jugados."; 
                    color: Theme.textDim; font.pixelSize: 14; opacity: 0.6
                }

                RowLayout {
                    Layout.fillWidth: true; spacing: 20
                    visible: discoveryData.hidden_gems && discoveryData.hidden_gems.length > 0
                    Repeater {
                        model: discoveryData.hidden_gems
                        delegate: GlassPanel {
                            width: 320; height: 120; radius: 20; glassOpacity: 0.4
                            content: RowLayout {
                                anchors.fill: parent; anchors.margins: 15; spacing: 15
                                Rectangle {
                                    width: 70; height: 90; radius: 8; color: Theme.backgroundVoid; clip: true
                                    Image { anchors.fill: parent; source: modelData.cover_2d_path ? "file:///" + modelData.cover_2d_path : ""; fillMode: Image.PreserveAspectCrop }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 2
                                    Text { text: modelData.title; color: Theme.textMain; font.pixelSize: 14; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }
                                    Text { text: modelData.platform.toUpperCase(); color: Theme.colorForPlatform(modelData.platform); font.pixelSize: 9; font.bold: true }
                                    Item { Layout.fillHeight: true }
                                    Text { text: "0 HORAS JUGADAS"; color: Theme.accentElectric; font.pixelSize: 9; font.bold: true; opacity: 0.8 }
                                }
                            }
                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: window.openGameDetails(modelData.id) }
                        }
                    }
                }
            }

            // --- D. THE INFINITE VAULT WALL ---
            ColumnLayout {
                Layout.fillWidth: true; spacing: 20; Layout.bottomMargin: 100
                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "MOSAICO INFINITO"; color: Theme.textMain; font.pixelSize: 18; font.bold: true; font.letterSpacing: 2 }
                    Rectangle { Layout.fillWidth: true; height: 1; color: Theme.cardBorder; opacity: 0.1; Layout.leftMargin: 20 }
                }

                Flow {
                    Layout.fillWidth: true; spacing: 12
                    Repeater {
                        model: discoveryData.random_batch
                        delegate: Rectangle {
                            id: wallItem
                            width: 110; height: 160; radius: 10; color: Theme.backgroundVoid
                            border.color: wallMA.containsMouse ? Theme.accentElectric : Theme.transparent; border.width: 2
                            clip: true
                            scale: wallMA.containsMouse ? 1.05 : 1.0
                            z: wallMA.containsMouse ? 10 : 1
                            
                            Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }
                            Behavior on border.color { ColorAnimation { duration: 150 } }
                            
                            Image { 
                                anchors.fill: parent; source: modelData.cover ? "file:///" + modelData.cover : ""; 
                                fillMode: Image.PreserveAspectCrop; asynchronous: true; 
                                opacity: wallMA.containsMouse ? 1.0 : 0.5 
                                Behavior on opacity { NumberAnimation { duration: 250 } }
                            }

                            MouseArea { 
                                id: wallMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor 
                                onClicked: window.openGameDetails(modelData.id)
                            }
                        }
                    }
                }
            }
        }
    }
}
