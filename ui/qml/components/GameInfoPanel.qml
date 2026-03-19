import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects
import QtQuick.Shapes

/**
 * GameInfoPanel.qml — (V14 - REFINED)
 * Rediseño minimalista: botones secundarios sutiles y PLAY centrado.
 */

Item {
    id: root
    
    property var gameData: null
    property color accentColor: "#00f3ff"
    property bool isOpen: false
    
    // Estado local para forzar actualización visual
    property bool localFavorite: gameData ? gameData.isFavorite : false
    onGameDataChanged: { if(gameData) localFavorite = gameData.isFavorite }

    signal launchClicked(string path, string emuId, string gameName)
    signal editClicked()
    signal favoriteClicked()
    signal closed()

    function open() { isOpen = true }
    function close() { isOpen = false; closed() }

    anchors.fill: parent
    z: 3000
    visible: opacity > 0
    opacity: isOpen ? 1.0 : 0.0
    Behavior on opacity { NumberAnimation { duration: 300 } }

    // 1. DIMMER
    Rectangle {
        anchors.fill: parent; color: "#dd000000"
        Canvas {
            anchors.fill: parent; opacity: 0.15
            onPaint: {
                var ctx = getContext("2d"); ctx.strokeStyle = "#4da6ff"; ctx.lineWidth = 0.5;
                for (var x = 0; x <= width; x += 40) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke(); }
                for (var y = 0; y <= height; y += 40) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke(); }
            }
        }
        MouseArea { anchors.fill: parent; onClicked: root.close() }
    }

    // 2. PANEL CONTENEDOR (CON EFECTO SLIDE-IN DESDE LA DERECHA)
    Item {
        id: panelContainer
        width: 500; height: parent.height * 0.92
        anchors.verticalCenter: parent.verticalCenter
        
        // Animamos la posición X para que entre deslizándose
        x: root.isOpen ? parent.width - width - 40 : parent.width + 100
        
        Behavior on x {
            NumberAnimation { 
                duration: 450
                easing.type: Easing.OutCubic // Estilo suave y tecnológico
            }
        }

        // GEOMETRÍA RECTANGULAR SOBRIA (Sin neón en el marco)
        Rectangle {
            anchors.fill: parent
            color: "#121520"
            border.color: "#33ffffff"
            border.width: 1
            radius: 0
            
            layer.enabled: true
            layer.effect: MultiEffect { shadowEnabled: true; shadowBlur: 1.0; shadowColor: "#aa000000"; shadowVerticalOffset: 20 }
        }

        ColumnLayout {
            anchors.fill: parent; spacing: 0; clip: true

            // A. BANNER
            Item {
                Layout.fillWidth: true; Layout.preferredHeight: 260; clip: true
                Image {
                    id: bannerImg
                    anchors.fill: parent; anchors.margins: 1
                    source: root.gameData ? (root.gameData.background || root.gameData.cover || "") : ""
                    fillMode: Image.PreserveAspectCrop
                }
                Rectangle {
                    anchors.fill: parent
                    gradient: Gradient {
                        GradientStop { position: 0.6; color: "transparent" }
                        GradientStop { position: 1.0; color: "#1a1c26" }
                    }
                }
                // Botón Cerrar Sutil
                Button {
                    anchors.top: parent.top; anchors.right: parent.right; anchors.margins: 15
                    width: 32; height: 32; onClicked: root.close()
                    background: Rectangle { radius: 0; color: "#44000000"; border.color: "#33ffffff"; border.width: 1 }
                    contentItem: Label { text: "✕"; color: "white"; font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }
            }

            // B. INFO AREA
            ColumnLayout {
                Layout.fillWidth: true; Layout.fillHeight: true
                Layout.margins: 40; Layout.topMargin: 0; spacing: 15

                // Fila Superior: Título + Botones Sutiles
                RowLayout {
                    Layout.fillWidth: true; spacing: 15
                    Label {
                        Layout.fillWidth: true
                        text: root.gameData ? root.gameData.name : ""
                        color: "white"; font.pixelSize: 32; font.weight: Font.Black
                        font.italic: true; wrapMode: Text.WordWrap; maximumLineCount: 2
                    }
                    
                    // Botones secundarios minimalistas
                    Row {
                        spacing: 8
                        Button {
                            id: subFavBtn; width: 36; height: 36
                            onClicked: { root.favoriteClicked(); root.localFavorite = !root.localFavorite }
                            background: Rectangle { radius: 0; color: subFavBtn.hovered ? "#33ffffff" : "transparent"; border.color: root.localFavorite ? root.accentColor : "#33ffffff"; border.width: 1 }
                            contentItem: Label { text: root.localFavorite ? "❤️" : "🤍"; font.pixelSize: 18; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        }
                        Button {
                            id: subEditBtn; width: 36; height: 36
                            onClicked: root.editClicked()
                            background: Rectangle { radius: 0; color: subEditBtn.hovered ? "#33ffffff" : "transparent"; border.color: "#33ffffff"; border.width: 1 }
                            contentItem: Label { text: "✏️"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; opacity: 0.7 }
                        }
                    }
                }

                // Metadata
                RowLayout {
                    Layout.fillWidth: true; spacing: 20
                    Column { spacing: 2; Label { text: "DESARROLLADOR"; color: "#66ffffff"; font.pixelSize: 10; font.bold: true }
                                        Label { text: root.gameData ? (root.gameData.developer || "Unknown") : ""; color: root.accentColor; font.pixelSize: 12 } }
                    Rectangle { width: 1; height: 20; color: "#1affffff" }
                    Column { spacing: 2; Label { text: "JUGADO"; color: "#66ffffff"; font.pixelSize: 10; font.bold: true }
                                        Label { text: root.gameData ? root.gameData.playtime : "0m"; color: "white"; font.pixelSize: 12 } }
                }

                // Descripción con mucho aire
                ScrollView {
                    Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded; width: 2 }
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                    Label {
                        width: panelContainer.width - 80
                        text: root.gameData ? (root.gameData.description || "No hay información adicional disponible.") : ""
                        color: "#99ffffff"; font.pixelSize: 15; wrapMode: Text.WordWrap; lineHeight: 1.7; horizontalAlignment: Text.AlignJustify
                    }
                }

                // C. ACCIÓN PRINCIPAL: PLAY (DISEÑO SLEEK CENTRADO)
                Button {
                    id: megaPlayBtn
                    Layout.fillWidth: true; Layout.preferredHeight: 60; Layout.bottomMargin: 10
                    onClicked: { if (root.gameData) { root.launchClicked(root.gameData.path, root.gameData.id_emu, root.gameData.name); root.close() } }
                    
                    background: Rectangle {
                        radius: 0; color: "transparent"; border.color: megaPlayBtn.hovered ? root.accentColor : "#44ffffff"
                        border.width: megaPlayBtn.hovered ? 2 : 1.5
                        
                        layer.enabled: megaPlayBtn.hovered
                        layer.effect: MultiEffect { shadowEnabled: true; shadowBlur: 0.4; shadowColor: root.accentColor }
                        
                        // Relleno sutil al pasar el ratón
                        Rectangle { anchors.fill: parent; radius: 0; color: root.accentColor; opacity: megaPlayBtn.hovered ? 0.1 : 0.0 }
                    }
                    
                    contentItem: Item {
                        // AQUÍ FORZAMOS EL CENTRADO TOTAL
                        Label {
                            anchors.centerIn: parent
                            text: "L A U N C H   G A M E"
                            color: megaPlayBtn.hovered ? "white" : "#ccffffff"
                            font.pixelSize: 16; font.weight: Font.Bold; font.letterSpacing: 2
                        }
                    }
                }
            }
        }
    }
}
