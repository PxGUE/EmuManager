import QtQuick
import QtQuick.Layouts
import "../system"

Item {
    id: root
    property string title: ""
    property string description: ""
    property string iconEmoji: ""
    property bool expanded: false
    property alias sectionContent: contentLoader.data
    
    // Altura base del encabezado
    readonly property int headerHeight: 80
    // Altura del contenido calculada automáticamente
    readonly property int contentHeight: contentLoader.childrenRect.height + 50
    
    width: parent.width
    height: expanded ? headerHeight + contentHeight : headerHeight
    Behavior on height { NumberAnimation { duration: 350; easing.type: Easing.InOutQuart } }

    Rectangle {
        anchors.fill: parent
        radius: Theme.radiusMedium
        color: Theme.cardBackground
        border.color: expanded ? Theme.accentColor : Theme.cardBorder
        border.width: Theme.borderThin
        clip: true
        
        Behavior on border.color { ColorAnimation { duration: 300 } }

        // Encabezado Interactivo
        Item {
            id: header
            width: parent.width
            height: root.headerHeight
            
            MouseArea {
                anchors.fill: parent
                onClicked: expanded = !expanded
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onEntered: hoverOverlay.opacity = 0.05
                onExited: hoverOverlay.opacity = 0
            }

            Rectangle {
                id: hoverOverlay
                anchors.fill: parent
                radius: Theme.radiusMedium
                color: Theme.textMain
                opacity: 0
                Behavior on opacity { NumberAnimation { duration: 200 } }
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 25; anchors.rightMargin: 25
                spacing: 20

                // Icono opcional
                Rectangle {
                    width: 45; height: 45; radius: 10
                    color: Theme.controlBackground
                    border.color: Theme.divider; border.width: 1
                    visible: iconEmoji !== ""
                    Text {
                        anchors.centerIn: parent
                        text: iconEmoji
                        font.pixelSize: 22
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    Text {
                        text: title
                        color: Theme.textMain
                        font.bold: true
                        font.pixelSize: Theme.fontHeader
                    }
                    Text {
                        text: description
                        color: Theme.textMuted
                        font.pixelSize: Theme.fontSmall
                        visible: description !== ""
                        elide: Text.ElideRight
                    }
                }

                // Indicador de estado (Flecha animada)
                Text {
                    text: "⌵"
                    color: expanded ? Theme.accentColor : Theme.textMuted
                    font.pixelSize: 24
                    font.bold: true
                    rotation: expanded ? 180 : 0
                    Behavior on rotation { NumberAnimation { duration: 350; easing.type: Easing.InOutBack } }
                    Behavior on color { ColorAnimation { duration: 300 } }
                }
            }
        }

        // Línea divisoria interna (Solo visible si está expandido)
        Rectangle {
            anchors.top: header.bottom
            width: parent.width - 50
            anchors.horizontalCenter: parent.horizontalCenter
            height: 1
            color: Theme.divider
            opacity: expanded ? 0.4 : 0
            visible: opacity > 0
            Behavior on opacity { NumberAnimation { duration: 300 } }
        }

        // Contenedor de contenido
        Item {
            id: contentLoader
            anchors.top: header.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 25
            opacity: expanded ? 1.0 : 0.0
            visible: opacity > 0.01
            
            Behavior on opacity { NumberAnimation { duration: 300 } }
        }
    }
}
