import QtQuick
import QtQuick.Effects

/**
 * Icon.qml — Componente para renderizar iconos SVG con soporte de color dinámico.
 */
Item {
    id: root
    
    property string name: ""
    property color color: "white"
    property real size: 24
    
    // Internal source resolution
    readonly property url _resolvedSource: name ? Qt.resolvedUrl("../../../media/ui/" + name + (name.indexOf(".") > -1 ? "" : ".svg")) : ""
    
    width: size
    height: size
    
    Image {
        id: img
        anchors.fill: parent
        source: root._resolvedSource
        sourceSize: Qt.size(root.width, root.height)
        fillMode: Image.PreserveAspectFit
        smooth: true
        visible: false
    }
    
    MultiEffect {
        anchors.fill: img
        source: img
        colorization: 1.0
        colorizationColor: root.color
        opacity: img.opacity
        visible: img.status === Image.Ready
    }
}
