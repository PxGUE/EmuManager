import QtQuick
import ".."
import QtQuick.Controls

Item {
    id: gameBoxRoot
    
    property string sourceImage: ""
    property string platform: "other"
    property bool isHovered: false
    property color accentColor: Theme.accentColor

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
        color: Theme.viewBackground
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

        // CARA FRONTAL
        Image {
            id: frontCover
            anchors.fill: parent
            source: sourceImage ? "file:///" + sourceImage : ""
            fillMode: Image.PreserveAspectFit
            asynchronous: true
            z: 2
            visible: sourceImage !== ""
        }

        // PLACEHOLDER: Mensaje amigable si no hay imagen (Scraping en curso)
        Column {
            anchors.centerIn: parent; width: parent.width * 0.8
            spacing: Theme.spaceSmall; visible: sourceImage === ""
            z: 3
            
            Text {
                text: "✨"; font.pixelSize: 32; anchors.horizontalCenter: parent.horizontalCenter
                opacity: 0.5
            }
            Text {
                text: I18n.t.scrape_friendly
                color: Theme.textMuted; font.pixelSize: 8 // Muy pequeño para que quepa en la caja
                horizontalAlignment: Text.AlignHCenter; width: parent.width
                wrapMode: Text.WordWrap; font.letterSpacing: 1
                lineHeight: 1.2
            }
        }

        // CARA LATERAL (Lomo / Spine) - Simulada con un rectángulo sombreado
        Rectangle {
            id: spine
            anchors.right: parent.right; anchors.top: parent.top; anchors.bottom: parent.bottom
            width: boxThick; x: parent.width - (width/2)
            z: 1; color: Theme.viewBackground; opacity: isHovered ? 0.7 : 0
            
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: Theme.viewBackground }
                GradientStop { position: 1.0; color: Theme.panelBackground }
            }

            transform: [
                Rotation { axis { x: 0; y: 1; z: 0 } angle: 90 }
            ]
        }
    }
}
