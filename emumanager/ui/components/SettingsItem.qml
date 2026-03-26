import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import "../components"

Item {
    id: settingsItem
    
    property string title: ""
    property string description: ""
    property string iconEmoji: ""
    property color accentColor: "#4f319b"
    property bool showArrow: false
    property alias controlArea: controlContainer.data

    height: 75
    width: parent.width

    // Fondo Sutil de Hover
    Rectangle {
        id: hoverRect
        anchors.fill: parent
        radius: 12
        color: "white"
        opacity: 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered: hoverRect.opacity = 0.04
        onExited: hoverRect.opacity = 0
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 25; anchors.rightMargin: 25
        spacing: 25

        // 1. ICONO
        Rectangle {
            width: 45; height: 45; radius: 10
            color: "#1a1a20"
            border.color: "#333"; border.width: 1
            Text {
                anchors.centerIn: parent
                text: iconEmoji
                font.pixelSize: 22
            }
        }

        // 2. TEXTO
        ColumnLayout {
            Layout.fillWidth: true; spacing: 0
            Text {
                text: title
                color: "white"; font.pixelSize: 16; font.bold: true
            }
            Text {
                text: description
                color: "#55ffffff"; font.pixelSize: 11
            }
        }

        // 3. CONTROL
        Item {
            id: controlContainer
            width: 160; height: 40
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
        }

        // 4. FLECHA
        Text {
            visible: showArrow
            text: "›"
            color: "#333"; font.pixelSize: 24; font.bold: true
        }
    }

    // LÍNEA DIVISORIA SUTIL
    Rectangle {
        anchors.bottom: parent.bottom; anchors.left: parent.left; anchors.right: parent.right
        anchors.leftMargin: 25; anchors.rightMargin: 25
        height: 1; color: "#08ffffff"
    }

}
