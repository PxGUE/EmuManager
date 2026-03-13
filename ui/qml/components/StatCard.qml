import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: card
    property string icon: "🎯"
    property int value: 0
    property string label: "Stat"
    property color accentColor: "#4da6ff"

    Layout.preferredWidth: 200
    Layout.preferredHeight: 120
    radius: 16
    color: "#1a1c24"
    border.color: mouseArea.containsMouse ? accentColor : "#2a2d3a"
    border.width: 1
    
    scale: mouseArea.containsMouse ? 1.02 : 1.0
    
    Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutBack } }
    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on border.color { ColorAnimation { duration: 150 } }

    // Glow background
    Rectangle {
        anchors.fill: parent
        radius: 16
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.alpha(accentColor, 0.05) }
            GradientStop { position: 1.0; color: "transparent" }
        }
        visible: mouseArea.containsMouse
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 2

        Rectangle {
            width: 36
            height: 36
            radius: 10
            color: Qt.alpha(card.accentColor, 0.1)
            
            Label {
                anchors.centerIn: parent
                text: card.icon
                font.pixelSize: 18
            }
        }

        Item { Layout.preferredHeight: 4 }

        Label {
            text: card.value
            font.pixelSize: 32
            font.weight: Font.Black
            color: "white"
        }

        Label {
            text: card.label
            font.pixelSize: 11
            font.bold: true
            color: "#666666"
            textFormat: Text.PlainText
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
    }
}
