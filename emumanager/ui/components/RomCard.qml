import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Rectangle {
    id: romCard
    
    // Propiedades de Datos (Roles del Modelo)
    property string title: ""
    property string platform: ""
    property string cover2d: ""
    property string cover3d: ""
    property color accentColor: "#16a085"
    
    // Estados Visuales
    property bool isHovered: mouseArea.containsMouse
    property bool has3d: cover3d !== ""
    property bool carouselMode: false 

    width: 200; height: 260; radius: 12
    color: "#1a1a1f"
    border.color: isHovered ? accentColor : "#25252b"
    border.width: isHovered ? 2 : 1
    clip: true
    
    signal clicked()

    Behavior on border.color { ColorAnimation { duration: 200 } }
    Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
    scale: isHovered ? 1.05 : 1.0

    // --- 1. CONTENEDOR DE CARÁTULA ---
    Item {
        id: coverContainer
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        height: parent.height - 70
        clip: true
        
        // --- CAPA 1: PORTADA 2D (Base) ---
        Image {
            anchors.fill: parent
            source: cover2d ? "file:///" + cover2d : ""
            fillMode: Image.PreserveAspectCrop
            visible: cover2d !== ""
            asynchronous: true
            opacity: (has3d && isHovered) ? 0 : 1
            Behavior on opacity { NumberAnimation { duration: 400 } }
        }

        // --- CAPA 2: PORTADA 3D (Hover) ---
        Image {
            anchors.fill: parent
            source: cover3d ? "file:///" + cover3d : ""
            fillMode: Image.PreserveAspectCrop
            visible: has3d
            asynchronous: true
            opacity: isHovered ? 1 : 0
            scale: isHovered ? 1.1 : 1.0
            Behavior on opacity { NumberAnimation { duration: 450 } }
            Behavior on scale { NumberAnimation { duration: 1000; easing.type: Easing.OutBack } }
        }

        // Placeholder si no hay nada
        Rectangle {
            anchors.fill: parent
            visible: cover2d === "" && cover3d === ""
            color: "#141417"
            Text {
                anchors.centerIn: parent; text: "🎮"; font.pixelSize: 45; opacity: 0.2
            }
        }
    }

    // --- 2. INFO DEL JUEGO ---
    Column {
        anchors.top: coverContainer.bottom; anchors.left: parent.left; anchors.right: parent.right
        anchors.bottom: parent.bottom; anchors.margins: 12
        spacing: 2

        Text {
            width: parent.width; text: title
            color: "white"; font.pixelSize: 13; font.bold: true; elide: Text.ElideRight
        }

        Text {
            width: parent.width; text: "LANZAR JUEGO"
            color: isHovered ? accentColor : "#66ffffff"
            font.pixelSize: 9; font.bold: true; font.letterSpacing: 1; opacity: isHovered ? 1 : 0.6
        }
    }

    MouseArea {
        id: mouseArea; anchors.fill: parent; hoverEnabled: true
        cursorShape: Qt.PointingHandCursor; onClicked: romCard.clicked()
    }
}
