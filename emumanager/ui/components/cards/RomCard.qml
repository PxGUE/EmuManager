import QtQuick
import ".."
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
    property bool isFavorite: false
    property var accentColor: undefined
    readonly property color resolvedAccent: Theme.resolveColor(accentColor, platform)
    
    // --- ESTADOS ---
    property bool isHovered: mouseArea.containsMouse || infoMA.containsMouse || favMA.containsMouse
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
        anchors.fill: body; radius: isHovered ? Theme.glowRadius : 0; samples: Theme.glowSamples
        color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.4)
        source: body; visible: isHovered; z: -1; transparentBorder: true
        Behavior on radius { NumberAnimation { duration: 250 } }
    }

    // --- CUERPO "OBSIDIAN GLASS" ---
    Rectangle {
        id: body
        anchors.fill: parent; radius: Theme.radiusLarge
        color: isHovered ? Theme.panelBackground : Theme.cardBackground
        border.color: isHovered ? resolvedAccent : Qt.alpha(resolvedAccent, 0.6)
        border.width: isHovered ? Theme.borderThick : Theme.borderThin
        
        // Efecto de profundidad (gradiente interno)
        Rectangle {
            anchors.fill: parent; radius: parent.radius; opacity: isHovered ? 0.35 : 0.25
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: resolvedAccent }
                GradientStop { position: 0.4; color: "transparent" }
            }
        }
    }

    // --- CONTENIDO: SHOWCASE 3D ---
    Item {
        id: showcaseContainer
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        height: 220; anchors.margins: Theme.spaceMedium
        
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
            
            layer.enabled: isHovered; layer.effect: DropShadow { radius: 15; color: Theme.viewBackground; samples: 10 }
        }

        // 2. GENERADOR 3D DINÁMICO (Para 2D o para Placeholder Vacío)
        GameBox3D {
            anchors.centerIn: parent
            sourceImage: cover2d; platform: romCardRoot.platform
            visible: !has3d; isHovered: romCardRoot.isHovered
            accentColor: romCardRoot.resolvedAccent
            
            // PASAMOS EL TILT
            dynamicTiltX: tiltX
            dynamicTiltY: tiltY
            
            scale: isHovered ? 1.1 : 1.0
            Behavior on scale { NumberAnimation { duration: 600; easing.type: Easing.OutBack } }
        }
    }

    // --- INFO DEL JUEGO (Sobre el cristal) ---
    Column {
        anchors.bottom: parent.bottom; anchors.bottomMargin: Theme.spaceLarge
        anchors.left: parent.left; anchors.right: parent.right
        anchors.margins: Theme.spaceMedium; spacing: Theme.spaceSmall
        z: 6

        Text {
            width: parent.width; text: title.toUpperCase(); color: Theme.textMain
            font.pixelSize: Theme.fontBody; font.bold: true; horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight; font.letterSpacing: 1.5
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter; width: 30; height: 1.5; radius: 1
            color: resolvedAccent; opacity: isHovered ? 1 : 0.2
            Behavior on opacity { NumberAnimation { duration: 300 } }
        }

        Text {
            width: parent.width; text: isHovered ? I18n.t.launch_adventure : I18n.t.library
            color: isHovered ? Theme.textMain : Theme.textMuted
            font.pixelSize: Theme.fontMicro; font.bold: true; horizontalAlignment: Text.AlignHCenter
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
        anchors.top: parent.top; anchors.right: parent.right; anchors.margins: Theme.spaceMedium
        width: 32; height: 32; radius: Theme.radiusCircle
        color: infoMA.containsMouse ? resolvedAccent : Theme.cardBorder
        opacity: isHovered ? 1 : 0
        visible: opacity > 0
        z: 50
        
        Text {
            text: "ⓘ"; anchors.centerIn: parent; color: infoMA.containsMouse ? Theme.viewBackground : Theme.textMain
            font.pixelSize: Theme.fontBody; font.bold: true
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

    // --- INDICADOR DE FAVORITO (❤️) ---
    Text {
        id: favIndicator
        text: isFavorite ? "❤️" : "🤍"
        anchors.top: parent.top; anchors.left: parent.left; anchors.margins: Theme.spaceMedium
        font.pixelSize: Theme.fontHeader
        opacity: isFavorite ? 1.0 : (isHovered ? 0.4 : 0)
        visible: opacity > 0
        z: 50
        
        Behavior on opacity { NumberAnimation { duration: 300 } }
        
        MouseArea {
            id: favMA
            anchors.fill: parent; hoverEnabled: true
            onClicked: (mouse) => {
                mouse.accepted = true
                mainController.toggle_favorite(gameId, !isFavorite)
            }
        }
    }
}
