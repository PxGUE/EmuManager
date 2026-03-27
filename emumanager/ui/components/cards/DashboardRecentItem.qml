import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: root
    property string title: ""
    property string platform: ""
    property string cover: ""
    property string gameId: ""
    signal clicked(string id)
    
    Layout.fillWidth: true; height: 75
    
    Rectangle {
        anchors.fill: parent; radius: 14; color: mouseArea.containsMouse ? Theme.panelBackground : Theme.cardBackground
        border.color: mouseArea.containsMouse ? Theme.accentColor : "transparent"
        border.width: 1
        
        Behavior on color { ColorAnimation { duration: 200 } }
        
        RowLayout {
            anchors.fill: parent; anchors.margins: 12; spacing: 15
            
            Rectangle {
                width: 50; height: 50; radius: 8; color: Theme.cardBackground; clip: true
                Image { 
                    anchors.fill: parent; source: cover ? ("file:///" + cover) : ""; fillMode: Image.PreserveAspectCrop
                    opacity: status === Image.Ready ? 1.0 : 0.0
                    Behavior on opacity { NumberAnimation { duration: 300 } }
                }
            }
            
            ColumnLayout {
                spacing: -2
                Text { text: title; color: Theme.textMain; font.pixelSize: 13; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }
                Text { text: platform.toUpperCase(); color: Theme.accentColor; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
            }
            
            Item { Layout.fillWidth: true }
            
            Text { text: "▶"; color: Theme.accentColor; font.pixelSize: 14; visible: mouseArea.containsMouse }
        }
    }
    
    MouseArea {
        id: mouseArea; anchors.fill: parent; hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked(root.gameId)
    }
}
