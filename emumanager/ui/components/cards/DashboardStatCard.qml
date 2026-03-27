import QtQuick
import ".."
import QtQuick.Controls 
import QtQuick.Layouts
import "../system"

Item {
    id: root
    implicitHeight: 140
    
    property string label: "STAT"
    property string value: "0"
    property string subLabel: ""
    property string icon: "🕹️"
    property color accent: Theme.accentColor

    Rectangle {
        anchors.fill: parent; radius: 24; color: Theme.cardBackground; border.color: mouseArea.containsMouse ? root.accent : Theme.divider
        border.width: 1
        
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 22; spacing: 5
            
            RowLayout {
                Text { text: root.label; color: root.accent; font.pixelSize: 9; font.bold: true; font.letterSpacing: 2 }
                Item { Layout.fillWidth: true }
                Text { text: root.icon; font.pixelSize: 22; opacity: 0.2; color: Theme.textMain }
            }
            
            Item { Layout.fillHeight: true }
            
            Text { 
                text: root.value.toString(); color: Theme.textMain; font.pixelSize: 28; font.bold: true 
                elide: Text.ElideRight; Layout.fillWidth: true
            }

            Rectangle { width: 30; height: 2; radius: 1; color: root.accent }
        }
    }

    MouseArea {
        id: mouseArea; anchors.fill: parent; hoverEnabled: true
        onEntered: { root.scale = 1.05 }
        onExited: { root.scale = 1.0 }
    }

    Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutQuint } }
}
