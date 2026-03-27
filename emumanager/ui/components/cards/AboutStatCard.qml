import QtQuick
import ".."
import QtQuick.Layouts

Rectangle {
    id: root
    property string title: ""
    property string value: ""
    property string icon: ""
    property color valueColor: Theme.textMain

    width: 170
    height: 80
    radius: 12
    color: Theme.cardBackground
    border.color: Theme.cardBorder
    border.width: 1


    Column {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 5

        Row {
            spacing: 8
            Text {
                text: icon; font.pixelSize: 14; opacity: 0.8
            }
            Text {
                text: title; color: Theme.textMuted
                font.pixelSize: 8; font.bold: true; font.letterSpacing: 1
            }
        }

        Text { 
            text: value; color: valueColor
            font.pixelSize: 11; font.bold: true
            width: parent.width; wrapMode: Text.WrapAnywhere
            elide: Text.ElideRight
            maximumLineCount: 2
        }
    }
}
