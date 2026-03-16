import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: pathSettingRoot
    property string title: ""
    property string subtitle: ""
    property string path: ""
    signal browse()

    Layout.fillWidth: true
    implicitHeight: 64

    // Fondo con efecto hover
    Rectangle {
        anchors.fill: parent
        anchors.margins: 2
        radius: 12
        color: hoverTracker.hovered ? "#0cffffff" : "transparent"
        Behavior on color { ColorAnimation { duration: 150 } }
        HoverHandler { id: hoverTracker }
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 20
        spacing: 20

        // Icono de Carpeta Minimalista
        Rectangle {
            Layout.preferredWidth: 32; Layout.preferredHeight: 32; radius: 8
            color: "#1affffff"
            Text {
                anchors.centerIn: parent
                text: "📂"
                font.pixelSize: 14; opacity: 0.8
            }
        }

        ColumnLayout {
            spacing: 0
            Layout.fillWidth: true
            Label {
                text: title
                font.pixelSize: 14; font.weight: Font.Medium; color: "white"
            }
            Label {
                text: path || (bridge ? bridge.translate("dash_missing") : "Not configured")
                font.pixelSize: 10; color: path ? "#666677" : "#ff4d4d"
                elide: Text.ElideMiddle; Layout.fillWidth: true
                font.family: "JetBrains Mono, Monospace"
                opacity: 0.8
            }
        }

        Button {
            id: browseBtn
            text: bridge ? bridge.translate("set_btn_select") : "SELECT"
            onClicked: browse()
            Layout.preferredHeight: 30
            
            // Para el cursor de mano en botones, usualmente se hace via MouseArea
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                propagateComposedEvents: true
                onPressed: (mouse) => { mouse.accepted = false; }
            }
            
            background: Rectangle {
                color: browseBtn.pressed ? "#4da6ff" : (browseBtn.hovered ? "#33ffffff" : "#1affffff")
                radius: 6
                border.color: browseBtn.hovered ? "#4dffffff" : "transparent"
                border.width: 1
                Behavior on color { ColorAnimation { duration: 150 } }
            }
            contentItem: Label {
                text: browseBtn.text
                color: browseBtn.pressed ? "black" : "white"
                font.pixelSize: 11; font.weight: Font.Medium
                horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                leftPadding: 16; rightPadding: 16
            }
        }
    }
}
