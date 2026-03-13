import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: card
    property string providerId: ""
    property string name: ""
    property string type: ""
    property bool enabled: false

    Layout.fillWidth: true
    height: 90
    radius: 16
    color: "#16181f"
    border.color: mouseArea.containsMouse ? "#4da6ff" : (card.enabled ? "#2a2d3a" : "#252830")
    border.width: 1
    
    Behavior on border.color { ColorAnimation { duration: 150 } }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16

        Rectangle {
            width: 44
            height: 44
            radius: 12
            color: card.enabled ? Qt.alpha(card.type === "artwork" ? "#4da6ff" : "#7c6ff7", 0.1) : "#1a1c24"
            
            Label {
                anchors.centerIn: parent
                text: card.type === "artwork" ? "🖼️" : "🧩"
                font.pixelSize: 20
                opacity: card.enabled ? 1.0 : 0.3
            }
        }

        ColumnLayout {
            spacing: 2
            Label {
                text: card.name
                font.bold: true
                font.pixelSize: 15
                color: card.enabled ? "white" : "#666677"
            }
            Label {
                text: card.type.toUpperCase()
                font.pixelSize: 10
                font.bold: true
                color: "#555566"
                font.letterSpacing: 1
            }
        }

        Item { Layout.fillWidth: true }

        Button {
            text: bridge.translate("set_btn_configure")
            visible: ["tgdb", "rawg", "steamgriddb", "screenscraper"].includes(card.providerId)
            height: 32
            onClicked: console.log("Configure provider: " + card.providerId)
            
            background: Rectangle {
                color: "#252b3d"
                radius: 6
                border.color: "#353b4d"
                visible: parent.hovered
            }
            contentItem: Text {
                text: parent.text
                color: "#4da6ff"
                font.bold: true
                font.pixelSize: 11
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        Switch {
            id: control
            checked: card.enabled
            onToggled: bridge.toggleProvider(card.providerId, checked)
            
            indicator: Rectangle {
                implicitWidth: 36
                implicitHeight: 20
                x: control.leftPadding
                y: parent.height / 2 - height / 2
                radius: 10
                color: control.checked ? "#4da6ff" : "#252830"

                Rectangle {
                    x: control.checked ? parent.width - width - 4 : 4
                    y: 4
                    width: 12
                    height: 12
                    radius: 6
                    color: "white"
                    Behavior on x { NumberAnimation { duration: 150 } }
                }
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
    }
}
