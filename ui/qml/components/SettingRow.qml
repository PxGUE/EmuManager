import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects

Item {
    id: settingRowRoot
    property string icon: ""
    property string title: ""
    property string subtitle: ""

    default property alias _content: row.data

    Layout.fillWidth: true
    implicitHeight: 72

    HoverHandler { id: rowHover }

    // Hover shimmer
    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(1, 1, 1, 0.025)
        opacity: rowHover.hovered ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
    }

    // Left accent indicator
    Rectangle {
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        width: 3; height: 36; radius: 2
        color: window.neonViolet
        opacity: rowHover.hovered ? 0.8 : 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
        layer.enabled: rowHover.hovered
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: window.neonViolet
            shadowBlur: 1.2
            shadowOpacity: 0.8
        }
    }

    RowLayout {
        id: row
        anchors.fill: parent
        anchors.leftMargin: 24
        anchors.rightMargin: 24
        spacing: 18

        // Icon box
        Rectangle {
            Layout.preferredWidth: 40; Layout.preferredHeight: 40; radius: 12
            color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, rowHover.hovered ? 0.18 : 0.1)
            border.color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, rowHover.hovered ? 0.35 : 0.15)
            border.width: 1
            Layout.alignment: Qt.AlignVCenter
            Behavior on color { ColorAnimation { duration: 200 } }

            Icon {
                anchors.centerIn: parent
                name: settingRowRoot.icon
                size: 16
                color: rowHover.hovered ? window.neonViolet : "#9090a8"
                opacity: 1.0
                visible: name !== ""
                Behavior on color { ColorAnimation { duration: 200 } }
            }
        }

        ColumnLayout {
            spacing: 0
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter

            Label {
                text: title
                font.pixelSize: 14; font.weight: Font.Medium
                color: rowHover.hovered ? "#f0e8ff" : "white"
                horizontalAlignment: Text.AlignLeft
                Layout.fillWidth: true
                Behavior on color { ColorAnimation { duration: 200 } }
            }
            Label {
                text: subtitle
                font.pixelSize: 10
                color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.55)
                visible: subtitle !== ""
                horizontalAlignment: Text.AlignLeft
                Layout.fillWidth: true
            }
        }
    }
}
