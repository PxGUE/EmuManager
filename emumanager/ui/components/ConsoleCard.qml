import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects

Item {
    id: consoleCardRoot
    
    // --- DATOS ---
    property string title: "Console"
    property string fullName: "Full Console Name"
    property string emulatorName: "Emulator"
    property string gameCount: "0"
    property string playTime: "0h"
    property string iconEmoji: "🎮"
    property color accentColor: "#8e44ad"
    
    // --- ESTADOS ---
    property bool isSelected: false
    property bool isFocused: isSelected || mainMA.containsMouse
    property bool minimalMode: true 
    property bool hasCore: true 

    // --- DIMENSIONES ---
    width: minimalMode ? 260 : 420 
    height: minimalMode ? 65 : 540
    
    Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
    Behavior on height { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }

    signal clicked()

    // --- CAPA DE EFECTOS ---
    DropShadow {
        id: externalGlow
        anchors.fill: body; radius: isFocused ? 24 : 10; samples: 14
        color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, isFocused ? 0.6 : 0.15)
        source: body; visible: true; z: -1; transparentBorder: true
    }

    // --- CUERPO ---
    Rectangle {
        id: body
        anchors.fill: parent; radius: minimalMode ? 18 : 34
        color: isFocused ? "#1a1a26" : "#0d0d12"
        border.color: isFocused ? accentColor : "#252535"
        border.width: isFocused ? 2 : 1
        z: 0
        
        Rectangle {
            anchors.fill: parent; radius: parent.radius; opacity: isFocused ? 0.35 : 0.12
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: accentColor }
                GradientStop { position: 0.5; color: "transparent" }
            }
        }
    }

    // Área de ratón global (fondo)
    MouseArea { 
        id: mainMA; anchors.fill: parent; hoverEnabled: true; z: 1
        cursorShape: Qt.PointingHandCursor
        onClicked: consoleCardRoot.clicked() 
    }

    // --- CONTENIDO: MODALIDAD MÍNIMA ---
    Row {
        anchors.fill: parent; anchors.margins: 12; visible: minimalMode; spacing: 18; z: 5

        Rectangle {
            width: 38; height: 38; radius: 10; color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.2)
            border.color: accentColor; border.width: 1; anchors.verticalCenter: parent.verticalCenter
            Text { text: iconEmoji; anchors.centerIn: parent; font.pixelSize: 20 }
        }

        Column {
            anchors.verticalCenter: parent.verticalCenter; spacing: 0
            Text { text: title.toUpperCase(); color: "white"; font.pixelSize: 13; font.bold: true; font.letterSpacing: 2 }
            Text { text: gameCount + " " + I18n.t.games_suffix; color: "#66ffffff"; font.pixelSize: 9; font.bold: true }
        }
    }

    // --- CONTENIDO: MODALIDAD COMPLETA ---
    Item {
        anchors.fill: parent; visible: !minimalMode; z: 5

        // 1. BLOQUE SUPERIOR
        Column {
            anchors.top: parent.top; anchors.topMargin: 40
            anchors.left: parent.left; anchors.right: parent.right
            spacing: 25

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter; width: 130; height: 130; radius: 65
                color: "#16161c"; border.width: 2.2; border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.45)
                Text { text: iconEmoji; anchors.centerIn: parent; font.pixelSize: 68 }
                
                Rectangle {
                    anchors.fill: parent; radius: 65; color: accentColor; opacity: isFocused ? 0.12 : 0
                    layer.enabled: isFocused && !minimalMode; layer.effect: FastBlur { radius: 25 }
                    visible: isFocused 
                }
            }

            Column {
                width: parent.width; spacing: 10
                Text {
                    width: parent.width; text: fullName.toUpperCase(); color: "white"
                    font.pixelSize: 26; font.bold: true; horizontalAlignment: Text.AlignHCenter; font.letterSpacing: 4
                }
                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter; width: 60; height: 3; radius: 1.5; color: accentColor
                }
            }

            Item {
                width: parent.width; height: 35
                Row {
                    anchors.horizontalCenter: parent.horizontalCenter; spacing: 12
                    Repeater {
                        model: hasCore ? emulatorName.split(" | ") : []
                        delegate: Rectangle {
                            height: 32; radius: 16; implicitWidth: emuText.width + 42
                            color: "#18ffffff"; border.color: "#30ffffff"; border.width: 1
                            Row {
                                anchors.centerIn: parent; spacing: 10
                                Rectangle { width: 8; height: 8; radius: 4; color: accentColor; anchors.verticalCenter: parent.verticalCenter }
                                Text { id: emuText; text: modelData; color: "white"; font.pixelSize: 11; font.bold: true }
                            }
                        }
                    }
                }
            }
        }

        // 2. BLOQUE DE ESTADÍSTICAS (Re-anclado al fondo para mayor equilibrio)
        Item {
            anchors.bottom: parent.bottom; anchors.bottomMargin: 60
            width: parent.width; height: 60

            Column {
                anchors.left: parent.left; width: parent.width/2; spacing: 8
                Text { width: parent.width; text: I18n.t.library; color: "#66ffffff"; font.pixelSize: 10; horizontalAlignment: Text.AlignHCenter; font.bold: true; font.letterSpacing: 2 }
                Text { width: parent.width; text: gameCount + " " + I18n.t.games_abbr; color: "white"; font.pixelSize: 24; horizontalAlignment: Text.AlignHCenter; font.bold: true }
            }
            
            Rectangle { 
                anchors.centerIn: parent; width: 1.5; height: 45; color: accentColor; opacity: 0.4
                visible: !minimalMode
            }

            Column {
                anchors.right: parent.right; width: parent.width/2; spacing: 8
                Text { width: parent.width; text: I18n.t.play_time_abbr; color: "#66ffffff"; font.pixelSize: 10; horizontalAlignment: Text.AlignHCenter; font.bold: true; font.letterSpacing: 2 }
                Text { width: parent.width; text: playTime; color: "white"; font.pixelSize: 24; horizontalAlignment: Text.AlignHCenter; font.bold: true }
            }
        }
    }
}
