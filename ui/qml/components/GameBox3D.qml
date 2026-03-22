import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects

Item {
    id: root3d
    property string source: ""
    property color accentColor: "#c084fc"
    property real tiltX: 0
    property real tiltY: 0
    property real pathRotation: 0
    property bool showShadow: true
    property bool showGlow: false

    onShowGlowChanged: {
        if (!showGlow) { tiltX = 0; tiltY = 0 }
    }

    Behavior on tiltX { NumberAnimation { duration: 300 } }
    Behavior on tiltY { NumberAnimation { duration: 300 } }

    implicitWidth: 380
    implicitHeight: 540

    MouseArea {
        id: sensorArea
        anchors.fill: parent
        hoverEnabled: true
        z: 1000
        enabled: root3d.showGlow
        onPositionChanged: (mouse) => {
            root3d.tiltX = (mouse.x / width) * 2 - 1
            root3d.tiltY = (mouse.y / height) * 2 - 1
        }
        onExited: { root3d.tiltX = 0; root3d.tiltY = 0 }
    }

    Item {
        id: visualContent
        anchors.fill: parent

        property real combinedAngle: (-root3d.tiltX * 40) + root3d.pathRotation

        transform: [
            Rotation {
                origin.x: visualContent.width / 2; origin.y: visualContent.height / 2
                axis { x: 1; y: 0; z: 0 }
                angle: root3d.tiltY * 20
            },
            Rotation {
                origin.x: visualContent.width / 2; origin.y: visualContent.height / 2
                axis { x: 0; y: 1; z: 0 }
                angle: visualContent.combinedAngle
            }
        ]

        // Shadow
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom; anchors.bottomMargin: -45
            width: parent.width * 0.88; height: 30; radius: 100
            color: "#120020"
            opacity: root3d.showShadow ? 0.75 : 0
            layer.enabled: true
            layer.effect: MultiEffect { blurEnabled: true; blur: 1.0 }
            x: -root3d.tiltX * 22
            scale: 1.0 - (Math.abs(root3d.tiltX) * 0.2)
        }

        // Neon backglow
        Rectangle {
            anchors.fill: parent; anchors.margins: -12; radius: 28
            color: "transparent"
            border.color: accentColor; border.width: 12
            opacity: root3d.showGlow ? 0.45 : (sensorArea.containsMouse ? 0.2 : 0)
            layer.enabled: true
            layer.effect: MultiEffect { blurEnabled: true; blur: 0.9 }
            SequentialAnimation on opacity {
                running: root3d.showGlow; loops: Animation.Infinite
                NumberAnimation { from: 0.25; to: 0.55; duration: 2500; easing.type: Easing.InOutSine }
                NumberAnimation { from: 0.55; to: 0.25; duration: 2500; easing.type: Easing.InOutSine }
            }
        }

        // Box
        Item {
            anchors.fill: parent

            // Spine
            Rectangle {
                id: spine
                width: 35; height: parent.height
                anchors.right: mainBox.left; anchors.rightMargin: -1
                visible: visualContent.combinedAngle > 0.5
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Qt.rgba(0.25, 0.15, 0.4, 1.0) }
                    GradientStop { position: 1.0; color: Qt.rgba(0.04, 0.02, 0.08, 1.0) }
                }
                transform: Rotation {
                    origin.x: 35; origin.y: parent.height / 2
                    axis { x: 0; y: 1; z: 0 }
                    angle: -90
                }
            }

            // Main frame
            Rectangle {
                id: mainBox
                anchors.fill: parent; radius: 18
                color: Qt.rgba(0.05, 0.03, 0.12, 1.0)
                border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.5)
                border.width: 2; clip: true

                Image {
                    anchors.fill: parent; anchors.margins: 12
                    source: root3d.source
                    fillMode: Image.PreserveAspectCrop; asynchronous: true

                    // Light sheen sweep
                    Rectangle {
                        anchors.fill: parent
                        opacity: 0.45 * Math.abs(root3d.tiltX)
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 0.5; color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.3) }
                            GradientStop { position: 1.0; color: "transparent" }
                        }
                        x: root3d.tiltX * 220
                    }
                }

                // Top glass highlight
                Rectangle {
                    anchors.fill: parent; radius: 18
                    opacity: 0.1
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#ffffff" }
                        GradientStop { position: 0.15; color: "transparent" }
                        GradientStop { position: 1.0; color: "#000000" }
                    }
                }
            }
        }
    }
}
