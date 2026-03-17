import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: pathSettingRoot
    property string title: ""
    property string subtitle: ""
    property string path: ""
    signal browse()
    
    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

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
            spacing: 2
            Layout.fillWidth: true
            Label {
                text: title
                font.pixelSize: 13; font.weight: Font.DemiBold; color: "white"
            }
            Label {
                text: subtitle
                font.pixelSize: 10; color: "#6e7282"; Layout.fillWidth: true
                visible: subtitle !== ""
            }
            Item { Layout.preferredHeight: 4 }
            Label {
                text: pathSettingRoot.path ? pathSettingRoot.path : tr("dash_missing")
                font.pixelSize: 10; color: path ? "#4da6ff" : "#ff4d4d"
                elide: Text.ElideMiddle; Layout.fillWidth: true
                font.family: "JetBrains Mono, Monospace"
                opacity: 0.8
            }
        }

        Button {
            id: browseBtn
            text: tr("set_btn_select")
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
