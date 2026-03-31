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
    property var accentColor: undefined
    readonly property color resolvedAccent: Theme.resolveColor(accentColor, title)
    
    // --- ESTADOS ---
    property bool isSelected: false
    property bool isFocused: isSelected || mainMA.containsMouse
    property bool minimalMode: true 
    property bool hasCore: true 

    // --- DIMENSIONES REDISEÑADAS ---
    width: minimalMode ? 260 : 640 
    height: minimalMode ? 65 : 380
    
    Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
    Behavior on height { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }

    signal clicked()

    // --- CAPA DE EFECTOS (Sutil y Optimizado) ---
    DropShadow {
        id: externalGlow
        anchors.fill: body; radius: isFocused ? 25 : 10; samples: 12
        color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, isFocused ? 0.35 : 0.1)
        source: body; visible: true; z: -1; transparentBorder: true
    }

    // --- CUERPO (Usando GlassPanel optimizado) ---
    GlassPanel {
        id: body
        anchors.fill: parent
        radius: minimalMode ? Theme.radiusMedium : Theme.radiusLarge
        backgroundColor: isFocused ? Theme.panelBackground : Theme.cardBackground
        borderColor: isFocused ? resolvedAccent : Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.3)
        borderWidth: isFocused ? Theme.borderThick : Theme.borderThin
        glassOpacity: isFocused ? 0.85 : 0.75
        showHighlight: isFocused
        
        // Área de ratón interna
        MouseArea { 
            id: mainMA; anchors.fill: parent; hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: consoleCardRoot.clicked() 
        }

        // --- CONTENIDO: MODALIDAD MÍNIMA ---
        Row {
            anchors.fill: parent; anchors.margins: Theme.spaceMedium; visible: minimalMode; spacing: Theme.spaceLarge

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

        // --- CONTENIDO: MODALIDAD COMPLETA (HUD LAYOUT) ---
        RowLayout {
            anchors.fill: parent; anchors.margins: 35; spacing: 40; visible: !minimalMode

            // Lado Izquierdo: Hero & Title
            Item {
                Layout.fillHeight: true; Layout.preferredWidth: 200
                
                // Icono Ghost (Fondo)
                Text {
                    text: iconEmoji; font.pixelSize: 180; opacity: 0.04
                    anchors.centerIn: parent; anchors.verticalCenterOffset: -10
                }

                ColumnLayout {
                    anchors.fill: parent; spacing: 15
                    
                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter; width: 110; height: 110; radius: 55
                        color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.1); border.width: 2; border.color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.3)
                        Text { text: iconEmoji; anchors.centerIn: parent; font.pixelSize: 62 }
                    }

                    ColumnLayout {
                        spacing: 5; Layout.fillWidth: true
                        Text {
                            Layout.fillWidth: true; text: fullName.toUpperCase(); color: Theme.textMain
                            font.pixelSize: 20; font.bold: true; horizontalAlignment: Text.AlignHCenter; font.letterSpacing: 2
                            wrapMode: Text.WordWrap; maximumLineCount: 2
                        }
                        Rectangle {
                            Layout.alignment: Qt.AlignHCenter; width: 40; height: 3; radius: 1.5; color: resolvedAccent
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                }
            }

            // Separador Vertical (Sutil)
            Rectangle { Layout.fillHeight: true; width: 1; color: resolvedAccent; opacity: 0.15 }

            // Lado Derecho: Specs & Data
            ColumnLayout {
                Layout.fillWidth: true; Layout.fillHeight: true; spacing: 25

                // 1. Emulador/Core Info
                ColumnLayout {
                    spacing: 12
                    Text { text: I18n.t.config_active_caps; color: Theme.textMuted; font.pixelSize: 9; font.bold: true; font.letterSpacing: 2 }
                    Row {
                        spacing: 10
                        Repeater {
                            model: hasCore ? emulatorName.split(" | ") : []
                            delegate: Rectangle {
                                height: 34; radius: 17; implicitWidth: emuText.width + 40
                                color: Theme.controlBackground; border.color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.4)
                                Row {
                                    anchors.centerIn: parent; spacing: 10
                                    Rectangle { width: 8; height: 8; radius: 4; color: resolvedAccent }
                                    Text { id: emuText; text: modelData; color: Theme.textMain; font.pixelSize: 12; font.bold: true }
                                }
                            }
                        }
                    }
                }

                // 2. Stats Grid
                GridLayout {
                    columns: 2; rowSpacing: 25; columnSpacing: 40
                    
                    ColumnLayout {
                        spacing: 5
                        Text { text: I18n.t.library.toUpperCase(); color: Theme.textMuted; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                        Text { text: gameCount + " " + I18n.t.games_abbr; color: Theme.textMain; font.pixelSize: 28; font.bold: true }
                    }

                    ColumnLayout {
                        spacing: 5
                        Text { text: I18n.t.play_time_abbr.toUpperCase(); color: Theme.textMuted; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                        Text { text: playTime; color: Theme.textMain; font.pixelSize: 28; font.bold: true }
                    }
                }

                Item { Layout.fillHeight: true }
                
                // Botón Acción Rápida (Estilo HUD)
                Rectangle {
                    Layout.fillWidth: true; height: 48; radius: Theme.radiusSmall
                    color: isFocused ? Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.2) : Theme.transparent
                    border.color: resolvedAccent; border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: I18n.t.enter_library_caps
                        color: Theme.textMain
                        font.bold: true; font.letterSpacing: 1; font.pixelSize: 11
                    }
                    
                    Behavior on color { ColorAnimation { duration: 250 } }
                }
            }
        }
    }
}
