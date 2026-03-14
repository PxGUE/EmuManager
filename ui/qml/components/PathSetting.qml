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
    height: 100

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 15

            ColumnLayout {
                spacing: 2
                Layout.fillWidth: true
                Label {
                    text: title
                    font.pixelSize: 16
                    font.bold: true
                    color: "white"
                }
                Label {
                    text: subtitle
                    font.pixelSize: 12
                    color: "#888899"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                    opacity: 0.8
                }
            }

            Button {
                id: browseBtn
                text: bridge ? bridge.translate("set_btn_select") : "Select"
                onClicked: browse()
                Layout.preferredHeight: 36
                Layout.preferredWidth: 110
                
                background: Rectangle {
                    color: browseBtn.pressed ? "#1a1c24" : (browseBtn.hovered ? "#303440" : "#252b3d")
                    radius: 8
                    border.color: browseBtn.hovered ? "#4da6ff" : "transparent"
                    border.width: 1
                    Behavior on color { ColorAnimation { duration: 150 } }
                }
                contentItem: Label {
                    text: browseBtn.text
                    color: browseBtn.hovered ? "white" : "#4da6ff"
                    font.bold: true
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }

        // Path Display Container
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            radius: 10
            color: "#16181f"
            border.color: "#252830"
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 15
                anchors.rightMargin: 15
                spacing: 10
                
                Label {
                    text: "PATH"
                    font.pixelSize: 9
                    font.bold: true
                    color: "#4da6ff"
                    opacity: 0.6
                    font.letterSpacing: 1
                }

                Rectangle { width: 1; height: 14; color: "#252830" }

                Label {
                    id: pathLabel
                    Layout.fillWidth: true
                    text: path || (bridge ? bridge.translate("dash_missing") : "Not configured")
                    color: path ? "#c0c0c0" : "#ff4d4d"
                    font.pixelSize: 11
                    font.family: "JetBrains Mono, Fira Code, Monospace"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideMiddle
                }
                
                Label {
                    text: path ? "✓" : "!"
                    color: path ? "#4dc6a6" : "#ff4d4d"
                    font.bold: true
                    font.pixelSize: 14
                }
            }
        }
    }
}
