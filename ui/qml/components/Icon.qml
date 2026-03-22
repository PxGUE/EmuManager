import QtQuick
import QtQuick.Effects

/**
 * Icon.qml — Renders SVG icons with dynamic color and optional neon glow.
 *
 * Usage:
 *   Icon { name: "home"; color: window.neonViolet; size: 24 }
 *   Icon { name: "play"; color: window.neonGold; size: 20; glow: true }
 */
Item {
    id: root

    property string name: ""
    property color color: "white"
    property real size: 24
    property bool glow: false
    property real glowRadius: 0.7      // 0.0–1.0, how spread the glow is
    property real glowOpacity: 0.75   // how strong the glow is

    readonly property url _resolvedSource: name
        ? Qt.resolvedUrl("../../../media/ui/" + name + (name.indexOf(".") > -1 ? "" : ".svg"))
        : ""

    width: size
    height: size

    // Source image (rendered white, invisible — used as input for MultiEffect)
    Image {
        id: img
        anchors.fill: parent
        source: root._resolvedSource
        sourceSize: Qt.size(root.size * 2, root.size * 2)
        fillMode: Image.PreserveAspectFit
        smooth: true
        visible: false
    }

    // Glow bloom layer (rendered behind the colored icon)
    MultiEffect {
        id: glowEffect
        anchors.fill: img
        anchors.margins: -size * 0.5
        source: img
        colorization: 1.0
        colorizationColor: root.color
        blurEnabled: true
        blur: root.glowRadius
        blurMax: 32
        saturation: 0.5
        opacity: root.glowOpacity
        visible: root.glow && img.status === Image.Ready
    }

    // Main colored icon (sharp)
    MultiEffect {
        id: colorEffect
        anchors.fill: img
        source: img
        colorization: 1.0
        colorizationColor: root.color
        opacity: 1.0
        visible: img.status === Image.Ready
    }
}
