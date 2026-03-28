import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: root
    property string title: ""
    property string platform: ""
    property string cover: ""
    property int gameId: 0
    property string playTime: ""
    
    readonly property color accentColor: Theme.colorForPlatform(platform)
    
    signal detailsRequested(int id)
    signal launchRequested(int id)
    
    Layout.fillWidth: true; height: 75
    
    Rectangle {
        anchors.fill: parent; radius: 14; color: mouseArea.containsMouse ? Theme.panelBackground : Theme.cardBackground
        border.color: mouseArea.containsMouse ? accentColor : "transparent"
        border.width: mouseArea.containsMouse ? 1.5 : 0 // Borde solo en hover pero con el color de la consola
        
        Behavior on color { ColorAnimation { duration: 200 } }
        Behavior on border.color { ColorAnimation { duration: 200 } }
        
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
                RowLayout {
                    spacing: 8
                    Text { text: platform.toUpperCase(); color: root.accentColor; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                    Text { text: "•"; color: Theme.textDim; font.pixelSize: 9 }
                    Text { text: playTime; color: Theme.textDim; font.pixelSize: 9 }
                }
            }
            
            Item { Layout.fillWidth: true }
            
            // BOTÓN DE PLAY (Lanzamiento Directo)
            Rectangle {
                id: playBtn
                width: 32; height: 32; radius: 16
                color: playMouse.containsMouse ? root.accentColor : Theme.controlBackground
                visible: mouseArea.containsMouse
                
                Text { 
                    anchors.centerIn: parent; anchors.horizontalCenterOffset: 1
                    text: "▶"; color: playMouse.containsMouse ? Theme.viewBackground : root.accentColor
                    font.pixelSize: 12 
                }
                
                MouseArea {
                    id: playMouse; anchors.fill: parent; hoverEnabled: true
                    onClicked: { root.launchRequested(root.gameId) }
                }
                
                Behavior on color { ColorAnimation { duration: 150 } }
                scale: playMouse.containsMouse ? 1.1 : 1.0
                Behavior on scale { NumberAnimation { duration: 100 } }
            }
        }
    }
    
    // ÁREA GENERAL (Acceso a Detalles)
    MouseArea {
        id: mouseArea; anchors.fill: parent; hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.detailsRequested(root.gameId)
    }
}
