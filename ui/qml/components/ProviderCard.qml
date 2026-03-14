import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: cardRoot
    property string providerId: ""
    property string name: ""
    property string type: "" // metadata, artworks, hybrid
    property bool enabled: false
    
    signal configureClicked()

    Layout.preferredHeight: 100
    Layout.fillWidth: true
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true

        Rectangle {
            id: bg
            anchors.fill: parent
            radius: 20
            color: mouseArea.containsMouse ? "#1c1f2e" : "#141621"
            border.color: mouseArea.containsMouse ? "#4da6ff" : "#252835"
            border.width: 1
            Behavior on color { ColorAnimation { duration: 250 } }
            Behavior on border.color { ColorAnimation { duration: 250 } }

            // Glow de fondo dinámico Premium
            Rectangle {
                anchors.centerIn: parent
                width: parent.width * 1.1; height: parent.height * 1.3
                radius: 40
                opacity: mouseArea.containsMouse ? 0.25 : 0.0
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: "transparent" }
                    GradientStop { position: 0.5; color: "#4da6ff" }
                    GradientStop { position: 1.0; color: "transparent" }
                }
                Behavior on opacity { NumberAnimation { duration: 400 } }
            }
        }

        RowLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 20

            Rectangle {
                width: 50; height: 50; radius: 15
                color: Qt.alpha("#4da6ff", 0.1)
                Label {
                    anchors.centerIn: parent
                    text: type === "metadata" ? "📝" : (type === "artworks" ? "🖼️" : "🧩")
                    font.pixelSize: 22
                }
            }

            ColumnLayout {
                spacing: 2
                Label { text: name; font.pixelSize: 16; font.bold: true; color: "white" }
                Label { 
                    text: type.toUpperCase()
                    font.pixelSize: 10; font.bold: true; color: "#6e7282"; font.letterSpacing: 1.5
                }
            }

            Item { Layout.fillWidth: true }

            RowLayout {
                spacing: 12
                
                Button {
                    text: "⚙️"
                    onClicked: cardRoot.configureClicked()
                    visible: providerId !== "local"
                    background: Rectangle { 
                        implicitWidth: 40; implicitHeight: 40; radius: 10
                        color: parent.hovered ? "#2a2d3e" : "transparent"
                        border.color: parent.hovered ? "#4da6ff" : "transparent"
                    }
                    contentItem: Label { text: parent.text; font.pixelSize: 18; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }

                Switch {
                    id: providerSwitch
                    checked: enabled
                    onToggled: {
                        if (bridge) bridge.toggleProvider(providerId, checked)
                    }
                }
            }
        }
    }
}
