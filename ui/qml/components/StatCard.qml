import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects

Item {
    id: cardRoot
    property string icon: "🎯"
    property var value: 0
    property string label: "Stat"
    property color accentColor: "#4da6ff"

    Layout.preferredWidth: 220
    Layout.preferredHeight: 140
    
    property bool isHovered: mouseArea.containsMouse

    // Sombra / Glow de fondo
    Rectangle {
        anchors.fill: cardBody
        anchors.margins: -10
        radius: 32
        color: Qt.alpha(accentColor, 0.15)
        visible: isHovered
        layer.enabled: true
        layer.effect: MultiEffect { blurEnabled: true; blur: 0.8; blurMax: 60 }
    }

    Rectangle {
        id: cardBody
        anchors.fill: parent
        radius: 28
        color: "#161823"
        border.color: isHovered ? accentColor : "#2a2d3a"
        border.width: isHovered ? 2 : 1
        
        scale: isHovered ? 1.05 : 1.0
        Behavior on scale { NumberAnimation { duration: 400; easing.type: Easing.OutBack } }
        Behavior on border.color { ColorAnimation { duration: 300 } }

        // Gradiente interno Glassmorphism
        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 27
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#1affffff" }
                GradientStop { position: 1.0; color: "transparent" }
            }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 22
            spacing: 0

            Rectangle {
                width: 44
                height: 44
                radius: 14
                color: Qt.alpha(cardRoot.accentColor, 0.12)
                border.color: Qt.alpha(cardRoot.accentColor, 0.2)
                border.width: 1
                
                Label {
                    anchors.centerIn: parent
                    text: cardRoot.icon
                    font.pixelSize: 22
                }
            }

            Item { Layout.fillHeight: true }

            Label {
                text: cardRoot.value
                font.pixelSize: 36
                font.weight: Font.Black
                color: "white"
                font.letterSpacing: -0.5
            }

            Label {
                text: cardRoot.label.toUpperCase()
                font.pixelSize: 10
                font.bold: true
                color: "#888899"
                font.letterSpacing: 1.5
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
    }
}
