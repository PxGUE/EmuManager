import QtQuick
import ".."
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
    property var accentColor: Theme.accentColor
    readonly property color resolvedAccent: (typeof accentColor === "string" && Theme[accentColor] !== undefined) ? Theme[accentColor] : accentColor
    
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
        anchors.fill: body; radius: isFocused ? Theme.glowRadius : Theme.radiusSmall; samples: Theme.glowSamples
        color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, isFocused ? 0.6 : 0.15)
        source: body; visible: true; z: -1; transparentBorder: true
    }

    // --- CUERPO ---
    Rectangle {
        id: body
        anchors.fill: parent; radius: minimalMode ? Theme.radiusMedium : Theme.radiusExtraLarge
        color: isFocused ? Theme.panelBackground : Theme.cardBackground
        border.color: isFocused ? resolvedAccent : Theme.cardBorder
        border.width: isFocused ? Theme.borderThick : Theme.borderThin
        z: 0
        
        Rectangle {
            anchors.fill: parent; radius: parent.radius; opacity: isFocused ? 0.35 : 0.12
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: resolvedAccent }
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
        anchors.fill: parent; anchors.margins: Theme.spaceMedium; visible: minimalMode; spacing: Theme.spaceLarge; z: 5

        Rectangle {
            width: 38; height: 38; radius: Theme.radiusSmall; color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.2)
            border.color: resolvedAccent; border.width: Theme.borderThin; anchors.verticalCenter: parent.verticalCenter
            Text { text: iconEmoji; anchors.centerIn: parent; font.pixelSize: Theme.fontHeader }
        }

        Column {
            anchors.verticalCenter: parent.verticalCenter; spacing: 0
            Text { text: title.toUpperCase(); color: Theme.textMain; font.pixelSize: Theme.fontBody; font.bold: true; font.letterSpacing: 2 }
            Text { text: gameCount + " " + I18n.t.games_suffix; color: Theme.textMuted; font.pixelSize: Theme.fontMicro; font.bold: true }
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
                anchors.horizontalCenter: parent.horizontalCenter; width: 130; height: 130; radius: Theme.radiusCircle
                color: Theme.panelBackground; border.width: Theme.borderThick; border.color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.45)
                Text { text: iconEmoji; anchors.centerIn: parent; font.pixelSize: 68 }
                
                Rectangle {
                    anchors.fill: parent; radius: 65; color: resolvedAccent; opacity: isFocused ? 0.12 : 0
                    layer.enabled: isFocused && !minimalMode; layer.effect: FastBlur { radius: 25 }
                    visible: isFocused 
                }
            }

            Column {
                width: parent.width; spacing: 10
                Text {
                    width: parent.width; text: fullName.toUpperCase(); color: Theme.textMain
                    font.pixelSize: Theme.fontTitle; font.bold: true; horizontalAlignment: Text.AlignHCenter; font.letterSpacing: 4
                }
                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter; width: 60; height: 3; radius: 1.5; color: resolvedAccent
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
                            color: Theme.controlBackground; border.color: Theme.cardBorder; border.width: 1
                            Row {
                                anchors.centerIn: parent; spacing: 10
                                Rectangle { width: 8; height: 8; radius: Theme.radiusCircle; color: resolvedAccent; anchors.verticalCenter: parent.verticalCenter }
                                Text { id: emuText; text: modelData; color: Theme.textMain; font.pixelSize: Theme.fontBody; font.bold: true }
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
                anchors.left: parent.left; width: parent.width/2; spacing: Theme.spaceSmall
                Text { width: parent.width; text: I18n.t.library; color: Theme.textMuted; font.pixelSize: Theme.fontSmall; horizontalAlignment: Text.AlignHCenter; font.bold: true; font.letterSpacing: 2 }
                Text { width: parent.width; text: gameCount + " " + I18n.t.games_abbr; color: Theme.textMain; font.pixelSize: Theme.fontTitle; horizontalAlignment: Text.AlignHCenter; font.bold: true }
            }
            
            Rectangle { 
                anchors.centerIn: parent; width: 1.5; height: 45; color: resolvedAccent; opacity: 0.4
                visible: !minimalMode
            }

            Column {
                anchors.right: parent.right; width: parent.width/2; spacing: Theme.spaceSmall
                Text { width: parent.width; text: I18n.t.play_time_abbr; color: Theme.textMuted; font.pixelSize: Theme.fontSmall; horizontalAlignment: Text.AlignHCenter; font.bold: true; font.letterSpacing: 2 }
                Text { width: parent.width; text: playTime; color: Theme.textMain; font.pixelSize: Theme.fontTitle; horizontalAlignment: Text.AlignHCenter; font.bold: true }
            }
        }
    }
}
