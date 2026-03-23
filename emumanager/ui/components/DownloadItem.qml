import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Rectangle {
    id: downloadItem
    
    property string itemName: ""
    property string itemType: "" // CORE, EMULATOR, ASSET
    property string platform: ""
    property real progressValue: 0.0
    property string totalSize: ""
    property string statusText: ""
    property string downloadSpeed: ""
    property color accentColor: "#4f319b"

    height: 90
    radius: 16
    color: "#16161a"
    border.color: progressValue > 0 && progressValue < 1 ? Qt.alpha(accentColor, 0.3) : "#25252b"
    border.width: 1
    clip: true

    // Efecto de Brillo Sutil al completar
    Rectangle {
        anchors.fill: parent
        visible: progressValue >= 1.0
        opacity: 0.05
        color: accentColor
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 25; anchors.rightMargin: 25
        spacing: 20

        // 1. Icono de Estado Adaptativo
        Rectangle {
            width: 45; height: 45; radius: 12
            color: "#1a1a20"
            border.color: "#333"; border.width: 1
            
            Text {
                anchors.centerIn: parent
                text: itemType === "CORE" ? "🧩" : (itemType === "EMULATOR" ? "🖥️" : "📦")
                font.pixelSize: 22
                opacity: progressValue >= 1.0 ? 1.0 : 0.6
            }
        }

        // 2. Info Principal
        ColumnLayout {
            Layout.fillWidth: true; spacing: 2
            
            RowLayout {
                spacing: 12
                Text {
                    text: itemName
                    color: "white"; font.pixelSize: 16; font.bold: true
                }
                Rectangle {
                    width: 45; height: 16; radius: 4; color: "#222"
                    Text { anchors.centerIn: parent; text: platform; color: accentColor; font.pixelSize: 9; font.bold: true }
                }
            }
            
            Text {
                text: statusText === "Downloading" ? (downloadSpeed + " • " + Math.floor(progressValue * 100) + "% de " + totalSize) : statusText
                color: "#66ffffff"; font.pixelSize: 11; font.bold: true
            }
        }

        // 3. Botones de Acción Rápidos
        RowLayout {
            spacing: 10
            visible: progressValue < 1.0
            
            ToolButton {
                icon.name: statusText === "Paused" ? "play" : "pause"
                Material.foreground: "white"
                opacity: 0.5
            }
            ToolButton {
                icon.name: "close"
                Material.foreground: "#e74c3c"
                opacity: 0.5
            }
        }

        // Check de Completado
        Text {
            visible: progressValue >= 1.0
            text: "✓"
            color: "#16a085"; font.pixelSize: 24; font.bold: true
        }
    }

    // 4. Barra de Progreso Minimalista (1px en la base)
    Rectangle {
        anchors.bottom: parent.bottom; anchors.left: parent.left
        height: 3; width: parent.width * progressValue
        color: accentColor
        opacity: progressValue >= 1.0 ? 0 : 0.8
        
        Behavior on width { NumberAnimation { duration: 500; easing.type: Easing.OutCubic } }
        
        // Brillo de la punta de carga
        Rectangle {
            anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
            width: 10; height: 6; radius: 3; color: "white"
            visible: progressValue > 0 && progressValue < 1.0
            opacity: 0.8
        }
    }
}
