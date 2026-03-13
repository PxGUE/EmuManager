import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    property string title: ""
    property string subtitle: ""
    property string path: ""
    signal browse()

    Layout.fillWidth: true
    height: 100
    radius: 16
    color: "#16181f"
    border.color: "#252830"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 2
                Label {
                    text: title
                    font.pixelSize: 14
                    font.bold: true
                    color: "white"
                }
                Label {
                    text: subtitle
                    font.pixelSize: 11
                    color: "#666677"
                }
            }
            Item { Layout.fillWidth: true }
            Button {
                text: bridge.translate("set_btn_select")
                onClicked: browse()
                height: 32
                
                background: Rectangle {
                    color: "#252b3d"
                    radius: 6
                    border.color: "#353b4d"
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
        }

        Rectangle {
            Layout.fillWidth: true
            height: 32
            radius: 8
            color: "#0f111a"
            border.color: "#1a1c24"
            
            Label {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                text: path || "No path selected"
                color: path ? "#888899" : "#444455"
                font.pixelSize: 11
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideMiddle
            }
        }
    }
}
