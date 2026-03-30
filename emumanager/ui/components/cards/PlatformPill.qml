import QtQuick
import QtQuick.Layouts
import ".."

Rectangle {
    id: root
    property string platformId: ""
    property int count: 0
    property string icon: "🕹️"
    property color accent: Theme.colorForPlatform(platformId)

    width: 65; height: 100
    color: Theme.transparent

    ColumnLayout {
        anchors.fill: parent; spacing: 8
        
        // Círculo con Icono
        Rectangle {
            id: circle
            Layout.preferredWidth: 60; Layout.preferredHeight: 60; radius: 30
            color: mouseArea.containsMouse ? Theme.panelBackground : Theme.cardBackground
            border.color: mouseArea.containsMouse ? accent : Theme.cardBorder
            border.width: mouseArea.containsMouse ? 2 : 1
            
            Text {
                anchors.centerIn: parent
                text: root.icon; font.pixelSize: 24
                opacity: mouseArea.containsMouse ? 1.0 : 0.7
                Behavior on opacity { NumberAnimation { duration: 200 } }
            }
            
            Behavior on color { ColorAnimation { duration: 200 } }
            Behavior on border.color { ColorAnimation { duration: 200 } }
        }

        // Contador
        ColumnLayout {
            spacing: 2
            Text { 
                text: platformId.toUpperCase(); color: mouseArea.containsMouse ? accent : Theme.textMuted
                font.pixelSize: 8; font.bold: true; font.letterSpacing: 1; Layout.alignment: Qt.AlignCenter
            }
            Text { 
                text: count; color: Theme.textMain; font.pixelSize: 11; font.bold: true; Layout.alignment: Qt.AlignCenter
            }
        }
    }

    MouseArea {
        id: mouseArea; anchors.fill: parent; hoverEnabled: true
        onClicked: {
            // Ir a la biblioteca filtrando por esta plataforma
            // mainController.set_library_filter(platformId)
            // activeViewId = "libraryView"
        }
    }
}
