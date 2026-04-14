import QtQuick
import Qt5Compat.GraphicalEffects
import "../system"

Item {
    id: nebulaRoot
    anchors.fill: parent
    z: -1
    
    // Properties
    property color accentColor: Theme.accentElectric
    property real interactiveForce: 0.1
    property bool isLoaded: false

    Component.onCompleted: isLoaded = true

    // --- 1. DEEP VOID BASE ---
    Rectangle {
        anchors.fill: parent
        color: Theme.backgroundVoid
    }

    // --- 2. THE KINETIC CORE (Reactive Glows) ---
    Item {
        id: kineticContainer
        anchors.fill: parent
        opacity: isLoaded ? 0.3 : 0
        Behavior on opacity { NumberAnimation { duration: 2000 } }

        // Glow A (Primary)
        Rectangle {
            id: mainGlow
            width: parent.width * 1.5; height: width; radius: width/2
            color: Theme.transparent
            visible: isLoaded

            // Interactive X/Y offset based on mouse
            x: (mainMouseArea.mouseX - width/2) * interactiveForce
            y: (mainMouseArea.mouseY - height/2) * interactiveForce
            
            gradient: Gradient {
                GradientStop { position: 0.0; color: accentColor }
                GradientStop { position: 0.6; color: Theme.transparent }
            }
            
            Behavior on x { NumberAnimation { duration: 3000; easing.type: Easing.OutCubic } }
            Behavior on y { NumberAnimation { duration: 3000; easing.type: Easing.OutCubic } }
            
            layer.enabled: true
            layer.effect: GaussianBlur { radius: 100; samples: 24 }

            // Slow idle rotation
            RotationAnimation on rotation {
                from: 0; to: 360; duration: 120000; loops: Animation.Infinite
            }
        }

        // Glow B (Secondary Accent)
        Rectangle {
            id: secondaryGlow
            width: parent.width * 1.2; height: width; radius: width/2
            color: Theme.transparent
            
            // Anchored to bottom right but reacts inversely
            x: parent.width - width * 0.8 - (mainMouseArea.mouseX * interactiveForce * 0.5)
            y: parent.height - height * 0.8 - (mainMouseArea.mouseY * interactiveForce * 0.5)
            
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.accentColor }
                GradientStop { position: 0.5; color: Theme.transparent }
            }
            
            Behavior on x { NumberAnimation { duration: 4500; easing.type: Easing.OutCubic } }
            Behavior on y { NumberAnimation { duration: 4500; easing.type: Easing.OutCubic } }

            RotationAnimation on rotation {
                from: 360; to: 0; duration: 180000; loops: Animation.Infinite
            }
        }
    }

    // Mouse Area to capture movement across the whole background
    MouseArea {
        id: mainMouseArea
        anchors.fill: parent
        hoverEnabled: true
        propagateComposedEvents: true
        onPositionChanged: (mouse) => { mouse.accepted = false }
    }
}
