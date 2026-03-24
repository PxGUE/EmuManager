import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Rectangle {
    id: consoleCard
    
    property string title: "Console"
    property string fullName: "Full Console Name"
    property string emulatorName: "Emulator"
    property string gameCount: "0"
    property string playTime: "0h"
    property string iconEmoji: "🎮"
    property color accentColor: "#16a085"
    property bool isSelected: false
    property bool isFocused: isSelected || mainMA.containsMouse
    property bool minimalMode: true 
    property bool hasCore: true 

    width: minimalMode ? 240 : 380
    height: minimalMode ? 60 : 440
    radius: minimalMode ? 16 : 28
    
    Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutQuint } }
    Behavior on height { NumberAnimation { duration: 400; easing.type: Easing.OutQuint } }
    Behavior on radius { NumberAnimation { duration: 400; easing.type: Easing.OutQuint } }

    color: "#0d0d12"
    border.color: isFocused ? accentColor : "#1a1a24"
    border.width: isFocused ? 2 : 1
    clip: false
    antialiasing: true

    signal clicked()

    // --- RESPLANDOR NEÓN EXTERIOR ---
    Rectangle {
        anchors.fill: parent
        anchors.margins: -4
        radius: parent.radius + 4
        color: "transparent"
        border.color: accentColor
        border.width: 1
        opacity: isFocused ? 0.4 : 0
        visible: isFocused
        antialiasing: true
        Behavior on opacity { NumberAnimation { duration: 300 } }
    }

    // --- MOUSE AREA PARA HOVER GLOBAL ---
    MouseArea {
        id: mainMA; anchors.fill: parent; hoverEnabled: true; z: -1
    }

    // --- FONDO PREMIUM ---
    Rectangle {
        anchors.fill: parent
        radius: parent.radius
        color: "#0a0a0f"
        antialiasing: true
        
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            antialiasing: true
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.1) }
                GradientStop { position: 0.5; color: "transparent" }
                GradientStop { position: 1.0; color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.05) }
            }
        }
        
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            opacity: isSelected ? 0.2 : 0.05
            antialiasing: true
            gradient: Gradient {
                GradientStop { position: 0.0; color: accentColor }
                GradientStop { position: 1.0; color: "transparent" }
            }
        }
    }

    // --- DISEÑO COMPACTO (MINIMAL MODE) ---
    RowLayout {
        anchors.fill: parent
        anchors.margins: 12
        visible: minimalMode
        spacing: 15

        Rectangle {
            width: 36; height: 36; radius: 18
            color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.2)
            border.color: accentColor; border.width: 1; antialiasing: true
            Text { text: iconEmoji; anchors.centerIn: parent; font.pixelSize: 18 }
        }

        Text {
            text: title.toUpperCase()
            color: "white"; font.pixelSize: 14; font.bold: true; font.letterSpacing: 2
            Layout.fillWidth: true
        }
    }

    // --- DISEÑO COMPLETO (FULL MODE) ---
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 32
        spacing: 18
        visible: !minimalMode

        // ICONO (Centrado)
        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            Rectangle {
                width: 110; height: width; radius: width/2
                color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.15)
                border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.3)
                border.width: 2; antialiasing: true
                Text { text: iconEmoji; anchors.centerIn: parent; font.pixelSize: 56 }
            }
            Item { Layout.fillWidth: true }
        }

        // TEXTO (Centrado)
        ColumnLayout {
            Layout.fillWidth: true; spacing: 4
            Text {
                text: fullName.toUpperCase()
                color: "white"; font.pixelSize: 24; font.bold: true
                font.letterSpacing: 4; elide: Text.ElideRight; Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }
        }

        // EMULADORES
        ColumnLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 12
            
            RowLayout {
                Layout.fillWidth: true; spacing: 10
                Text {
                    text: "EMULADORES INSTALADOS"
                    color: accentColor; font.pixelSize: 8; font.bold: true; font.letterSpacing: 2; opacity: 0.8
                }
                Rectangle { 
                    Layout.fillWidth: true; height: 1; opacity: 0.2
                    gradient: Gradient { 
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: accentColor }
                        GradientStop { position: 1.0; color: "transparent" } 
                    } 
                }
            }
            
            Column {
                spacing: 6; Layout.fillWidth: true; Layout.topMargin: 5
                Repeater {
                    model: hasCore ? emulatorName.split(", ") : []
                    delegate: Item {
                        id: emuItem
                        width: parent.width; height: 38
                        property bool rowHovered: emuMA.containsMouse || cnfMA.containsMouse || delMA.containsMouse
                        Rectangle {
                            anchors.fill: parent; radius: 10; opacity: rowHovered ? 0.12 : 0; antialiasing: true
                            gradient: Gradient { 
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0.0; color: accentColor }
                                GradientStop { position: 1.0; color: "transparent" } 
                            }
                            Behavior on opacity { NumberAnimation { duration: 250 } }
                        }
                        MouseArea { id: emuMA; anchors.fill: parent; hoverEnabled: true; z: -1 }
                        RowLayout {
                            anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 12
                            Text { text: "✦"; color: accentColor; font.pixelSize: 11; opacity: rowHovered ? 1.0 : 0.4 }
                            Text { text: modelData; color: "white"; font.pixelSize: 13; font.bold: true; Layout.fillWidth: true }
                            Row {
                                spacing: 10; opacity: rowHovered ? 1.0 : 0; visible: rowHovered
                                Rectangle {
                                    width: 30; height: 30; radius: 8; color: cnfMA.containsMouse ? Qt.rgba(1,1,1,0.15) : "transparent"
                                    Text { text: "⚙️"; anchors.centerIn: parent; font.pixelSize: 16; opacity: cnfMA.containsMouse ? 1.0 : 0.7 }
                                    MouseArea { id: cnfMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor }
                                    Rectangle {
                                        visible: cnfMA.containsMouse; z: 100
                                        anchors.bottom: parent.top; anchors.bottomMargin: 10; anchors.horizontalCenter: parent.horizontalCenter
                                        width: 90; height: 22; radius: 6; color: "#111"; border.color: accentColor; border.width: 1
                                        Text { text: "CONFIGURAR"; color: "white"; anchors.centerIn: parent; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1 }
                                    }
                                }
                                Rectangle {
                                    width: 30; height: 30; radius: 8; color: delMA.containsMouse ? Qt.rgba(1,0,0,0.15) : "transparent"
                                    Text { text: "❌"; anchors.centerIn: parent; font.pixelSize: 14; opacity: delMA.containsMouse ? 1.0 : 0.7 }
                                    MouseArea { id: delMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor }
                                    Rectangle {
                                        visible: delMA.containsMouse; z: 100
                                        anchors.bottom: parent.top; anchors.bottomMargin: 10; anchors.horizontalCenter: parent.horizontalCenter
                                        width: 90; height: 22; radius: 6; color: "#111"; border.color: "#ff416c"; border.width: 1
                                        Text { text: "ELIMINAR"; color: "white"; anchors.centerIn: parent; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1 }
                                    }
                                }
                            }
                        }
                    }
                }
                Text {
                    text: "Sin emuladores instalados."
                    visible: !hasCore; color: "#44ffffff"; font.pixelSize: 11; font.italic: true
                    horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true
                }
            }
        }

        Item { Layout.fillHeight: true }

        // STATS
        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; opacity: 0.1; color: "white" }

        RowLayout {
            Layout.fillWidth: true; spacing: 20
            Column {
                spacing: 4
                Text { text: "BIBLIOTECA"; color: "#555"; font.pixelSize: 8; font.bold: true; font.letterSpacing: 2 }
                Text { text: gameCount + " JUEGOS"; color: "white"; font.pixelSize: 14; font.bold: true }
            }
            Column {
                spacing: 4
                Text { text: "TIEMPO TOTAL"; color: "#555"; font.pixelSize: 8; font.bold: true; font.letterSpacing: 2 }
                Text { text: playTime; color: "white"; font.pixelSize: 14; font.bold: true }
            }
            Item { Layout.fillWidth: true }
            Rectangle {
                Layout.preferredWidth: 130; Layout.preferredHeight: 38; radius: 12
                color: expMA.containsMouse ? accentColor : "transparent"
                border.color: accentColor; border.width: 2; antialiasing: true
                Text {
                    text: "EXPLORAR"
                    anchors.centerIn: parent
                    color: expMA.containsMouse ? "black" : "white"
                    font.pixelSize: 11; font.bold: true; font.letterSpacing: 2
                }
                MouseArea {
                    id: expMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onClicked: consoleCard.clicked()
                }
            }
        }
    }
}
