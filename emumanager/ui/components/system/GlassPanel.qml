import QtQuick
import QtQuick.Effects

/**
 * GlassPanel.qml
 * Componente core para el diseño Obsidian Glass.
 * Proporciona un contenedor con desenfoque, bordes de luz y degradados suaves.
 */
Item {
    id: glassRoot

    property alias content: contentItem.data
    property real radius: 24
    property color borderColor: Theme.cardBorder
    property real borderWidth: 1
    property color glowColor: Theme.controlBackground
    property color backgroundColor: Theme.panelBackground
    property real glassOpacity: 0.6
    property bool showHighlight: true

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: glassRoot.radius
        color: glassRoot.backgroundColor
        opacity: glassRoot.glassOpacity
        
        // Inner lighting effect (Rim light)
        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: glassRoot.radius
            color: Theme.transparent
            border.color: glassRoot.glowColor
            border.width: 1
            opacity: 0.15
        }
    }

    // Outer Border
    Rectangle {
        anchors.fill: parent
        radius: glassRoot.radius
        color: Theme.transparent
        border.color: glassRoot.borderColor
        border.width: glassRoot.borderWidth
        z: 100 // Aseguramos que el borde esté siempre encima
    }

    // Degradado interno sutil (Highlight)
    Rectangle {
        anchors.fill: parent
        radius: glassRoot.radius
        opacity: 0.1
        gradient: Gradient {
            GradientStop { position: 0.0; color: Theme.textMain }
            GradientStop { position: 1.0; color: Theme.transparent }
        }
        visible: glassRoot.showHighlight
    }

    Item {
        id: contentItem
        anchors.fill: parent
        anchors.margins: 1
        clip: true
    }
}
