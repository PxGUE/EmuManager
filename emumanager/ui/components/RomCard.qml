import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects

Item {
    id: romCardRoot
    
    // --- DATOS (Roles del Modelo) ---
    property string title: ""
    property string platform: ""
    property string cover2d: ""
    property string cover3d: ""
    property string gameId: ""
    property color accentColor: "#8e44ad"
    
    // --- ESTADOS ---
    property bool isHovered: mouseArea.containsMouse || infoMA.containsMouse
    property bool has3d: cover3d !== ""
    property bool has2d: cover2d !== ""
    
    // Propiedades internas para el TILT (Inclinación sutil)
    property real tiltX: isHovered ? (mouseArea.mouseY - height/2) / (height/2) * -12 : 0
    property real tiltY: isHovered ? (mouseArea.mouseX - width/2) / (width/2) * 12 : 0

    // --- DIMENSIONES ---
    width: 210; height: 320 
    
    signal clicked()
    signal infoClicked()

    // --- CAPA DE EFECTOS (GLOW) ---
    DropShadow {
        id: externalGlow
        anchors.fill: body; radius: isHovered ? 20 : 0; samples: 14
        color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.4)
        source: body; visible: isHovered; z: -1; transparentBorder: true
        Behavior on radius { NumberAnimation { duration: 250 } }
    }

    // --- CUERPO "OBSIDIAN GLASS" ---
    Rectangle {
        id: body
        anchors.fill: parent; radius: 24
        color: isHovered ? "#1a1a26" : "#0d0d12"
        border.color: isHovered ? accentColor : "#252535"
        border.width: isHovered ? 2 : 1
        
        // Efecto de profundidad (gradiente interno)
        Rectangle {
            anchors.fill: parent; radius: parent.radius; opacity: isHovered ? 0.25 : 0.1
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: accentColor }
                GradientStop { position: 0.5; color: "transparent" }
            }
        }
    }

    // --- CONTENIDO: SHOWCASE 3D ---
    Item {
        id: showcaseContainer
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        height: 220; anchors.margins: 15
        
        // 1. CARÁTULA 3D REAL (Si existe)
        Image {
            anchors.centerIn: parent; width: 150; height: 200
            source: has3d ? "file:///" + cover3d : ""
            fillMode: Image.PreserveAspectFit
            visible: has3d
            asynchronous: true
            scale: isHovered ? 1.15 : 1.0
            
            // EFECTO TILT DINÁMICO
            transform: [
                Rotation { origin.x: 75; origin.y: 100; axis { x: 1; y: 0; z: 0 } angle: tiltX },
                Rotation { origin.x: 75; origin.y: 100; axis { x: 0; y: 1; z: 0 } angle: tiltY }
            ]

            Behavior on scale { NumberAnimation { duration: 600; easing.type: Easing.OutBack } }
            
            layer.enabled: isHovered; layer.effect: DropShadow { radius: 15; color: "black"; samples: 10 }
        }

        // 2. GENERADOR 3D DINÁMICO (Para 2D o para Placeholder Vacío)
        GameBox3D {
            anchors.centerIn: parent
            sourceImage: cover2d; platform: romCardRoot.platform
            visible: !has3d; isHovered: romCardRoot.isHovered
            accentColor: romCardRoot.accentColor
            
            // PASAMOS EL TILT
            dynamicTiltX: tiltX
            dynamicTiltY: tiltY
            
            scale: isHovered ? 1.1 : 1.0
            Behavior on scale { NumberAnimation { duration: 600; easing.type: Easing.OutBack } }
        }
    }

    // --- INFO DEL JUEGO (Sobre el cristal) ---
    Column {
        anchors.bottom: parent.bottom; anchors.bottomMargin: 20
        anchors.left: parent.left; anchors.right: parent.right
        anchors.margins: 15; spacing: 5
        z: 6

        Text {
            width: parent.width; text: title.toUpperCase(); color: "white"
            font.pixelSize: 13; font.bold: true; horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight; font.letterSpacing: 1.5
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter; width: 30; height: 1.5; radius: 1
            color: accentColor; opacity: isHovered ? 1 : 0.2
            Behavior on opacity { NumberAnimation { duration: 300 } }
        }

        Text {
            width: parent.width; text: isHovered ? I18n.t.launch_adventure : I18n.t.library
            color: isHovered ? "white" : "#66ffffff"
            font.pixelSize: 8; font.bold: true; horizontalAlignment: Text.AlignHCenter
            font.letterSpacing: 2
            Behavior on color { ColorAnimation { duration: 250 } }
        }
    }

    MouseArea {
        id: mouseArea; anchors.fill: parent; hoverEnabled: true
        cursorShape: Qt.PointingHandCursor; onClicked: romCardRoot.clicked()
    }

    // --- BOTÓN DE INFORMACIÓN (ⓘ) ---
    Rectangle {
        id: infoBtn
        anchors.top: parent.top; anchors.right: parent.right; anchors.margins: 12
        width: 32; height: 32; radius: 16
        color: infoMA.containsMouse ? accentColor : "#25ffffff"
        opacity: isHovered ? 1 : 0
        visible: opacity > 0
        z: 50
        
        Text {
            text: "ⓘ"; anchors.centerIn: parent; color: infoMA.containsMouse ? "black" : "white"
            font.pixelSize: 14; font.bold: true
        }
        
        Behavior on opacity { NumberAnimation { duration: 250 } }
        Behavior on color { ColorAnimation { duration: 150 } }

        MouseArea {
            id: infoMA; anchors.fill: parent; hoverEnabled: true; propagateComposedEvents: false
            cursorShape: Qt.PointingHandCursor
            onClicked: (mouse) => {
                mouse.accepted = true
                romCardRoot.infoClicked()
            }
        }
    }
}
