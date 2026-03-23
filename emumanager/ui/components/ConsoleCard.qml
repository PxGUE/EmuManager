import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Rectangle {
    id: consoleCard
    
    // Propiedades de la Tarjeta
    property string title: "" // Título para la vista de biblioteca
    property string consoleName: title // Alias para compatibilidad
    property string emulatorName: ""
    property string gameCount: "0"
    property string playTime: "0h"
    property string iconEmoji: "🎮"
    property color accentColor: "#16a085"
    property bool isSelected: false
    property bool isFocused: isSelected || mouseArea.containsMouse
    property bool minimalMode: true // Por defecto para el carrusel superior

    width: minimalMode ? 140 : 380
    height: minimalMode ? 80 : 480
    radius: minimalMode ? 12 : 32
    color: isSelected ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.1) : "#1a1a1f"
    border.color: isFocused ? accentColor : "#25252b"
    border.width: isFocused ? 2 : 1
    clip: true
    
    signal clicked()

    Behavior on color { ColorAnimation { duration: 200 } }
    Behavior on border.color { ColorAnimation { duration: 200 } }

    // --- DISEÑO MINIMALISTA (CARRUSEL SUPERIOR / BIBLIOTECA) ---
    Item {
        anchors.fill: parent
        visible: minimalMode

        Column {
            anchors.centerIn: parent
            spacing: 2
            
            Text {
                text: iconEmoji
                font.pixelSize: 26
                anchors.horizontalCenter: parent.horizontalCenter
                opacity: isFocused ? 1.0 : 0.6
            }
            
            Text {
                text: title
                color: isSelected ? "white" : "#88ffffff"
                font.pixelSize: 12
                font.bold: isSelected
                font.letterSpacing: 1
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

    // --- DISEÑO NORMAL (DASHBOARD - Omitido abreviado para estabilidad) ---
    // (Podemos restaurarlo luego si se necesita en el dashboard)

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: consoleCard.clicked()
    }
}
