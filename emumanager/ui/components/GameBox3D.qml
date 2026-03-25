import QtQuick
import QtQuick.Controls

Item {
    id: gameBoxRoot
    
    property string sourceImage: ""
    property string platform: "other"
    property bool isHovered: false
    property color accentColor: "#8e44ad"

    property real dynamicTiltX: 0
    property real dynamicTiltY: 0

    width: 160; height: 220
    
    // --- LÓGICA DE DIMENSIONES POR PLATAFORMA ---
    readonly property real boxThick: {
        if (platform === "gba" || platform === "snes" || platform === "n64") return 15; // Cartuchos gruesos
        if (platform === "psx" || platform === "dreamcast") return 10; // Cajas CD
        return 8; // Genérico
    }

    // --- SOMBRA DE CONTACTO ---
    Rectangle {
        id: contactShadow
        anchors.bottom: parent.bottom; anchors.bottomMargin: -12
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width * 0.8; height: 10; radius: 5
        color: "black"
        z: -1
        
        // Solo visible en hover y con una opacidad muy suave para que parezca sombra, no barra
        opacity: isHovered ? 0.4 : 0
        scale: isHovered ? 1.1 : 1.0
        
        transform: [
            Rotation { origin.x: width/2; origin.y: height/2; axis { x: 1; y: 0; z: 0 } angle: 65 }
        ]
        
        // La sombra se mueve sutilmente en dirección opuesta a la inclinación
        x: (parent.width - width)/2 - (dynamicTiltY * 0.3)
        
        Behavior on opacity { NumberAnimation { duration: 400 } }
        Behavior on x { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
    }

    // --- CONTENEDOR 3D (TRUCO 2.5D) ---
    Item {
        anchors.fill: parent
        
        transform: [
            Rotation { 
                id: rotY; origin.x: width/2; origin.y: height/2; axis { x: 0; y: 1; z: 0 } 
                angle: (isHovered ? -12 : 0) + (isHovered ? dynamicTiltY : 0)
                Behavior on angle { NumberAnimation { duration: 600; easing.type: Easing.OutCubic } }
            },
            Rotation { 
                id: rotX; origin.x: width/2; origin.y: height/2; axis { x: 1; y: 0; z: 0 } 
                angle: (isHovered ? 5 : 0) + (isHovered ? dynamicTiltX : 0)
                Behavior on angle { NumberAnimation { duration: 600; easing.type: Easing.OutCubic } }
            }
        ]

        // CARA FRONTAL: Placeholder Vacío (Solo si no hay imagen en absoluto)
        Rectangle {
            anchors.fill: parent; color: "#0d0d12"; z: 1
            opacity: 0.3; border.color: "#25ffffff"; border.width: 1
            visible: sourceImage === ""
            Text { anchors.centerIn: parent; text: "🎮"; font.pixelSize: 50; opacity: 0.15 }
        }

        Image {
            id: frontCover
            anchors.fill: parent
            source: sourceImage ? "file:///" + sourceImage : ""
            fillMode: Image.PreserveAspectFit
            asynchronous: true
            z: 2
            visible: sourceImage !== ""
            
            // ELIMINADO: El borde de color que no gustaba
        }

        // CARA LATERAL (Lomo / Spine) - Simulada con un rectángulo sombreado
        Rectangle {
            id: spine
            anchors.right: parent.right; anchors.top: parent.top; anchors.bottom: parent.bottom
            width: boxThick; x: parent.width - (width/2)
            z: 1; color: "#000000"; opacity: isHovered ? 0.8 : 0
            
            // Gradiente para dar sensación de profundidad
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "#000000" }
                GradientStop { position: 1.0; color: "#2a2a2a" }
            }

            transform: [
                Rotation { axis { x: 0; y: 1; z: 0 } angle: 90 }
            ]
        }
        
        // Brillo reflectante premium (Solo sobre la imagen si existe)
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            width: sourceImage !== "" ? frontCover.paintedWidth : parent.width
            height: sourceImage !== "" ? frontCover.paintedHeight : parent.height
            z: 5; opacity: isHovered ? 0.2 : 0.05
            
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: "#ffffff" }
                GradientStop { position: 0.4; color: "transparent" }
            }
            Behavior on opacity { NumberAnimation { duration: 300 } }
        }
    }
}
