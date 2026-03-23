import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Rectangle {
    id: romCard
    
    // Propiedades de Datos (Consumidas desde el Modelo)
    property string title: ""
    property string platform: ""
    property string coverPath: ""
    property color accentColor: "#16a085"
    
    // Estados Visuales
    property bool isHovered: mouseArea.containsMouse
    property bool carouselMode: false 

    width: carouselMode ? 320 : 180
    height: carouselMode ? 460 : 260
    radius: carouselMode ? 20 : 12
    color: "#1a1a1f"
    border.color: isHovered ? accentColor : "#25252b"
    border.width: isHovered ? 2 : 1
    clip: true
    
    signal clicked()

    Behavior on border.color { ColorAnimation { duration: 200 } }
    Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
    scale: isHovered ? 1.05 : 1.0

    // --- 1. CONTENEDOR DE CARÁTULA ---
    Rectangle {
        id: coverContainer
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        height: carouselMode ? (parent.height * 0.7) : (parent.height - 70)
        color: "#141417"
        
        // Imagen Real (Si existe) o Gradiente de Placeholder
        Image {
            anchors.fill: parent
            source: coverPath ? "file:///" + coverPath : ""
            fillMode: Image.PreserveAspectCrop
            visible: coverPath !== ""
            asynchronous: true
        }

        Rectangle {
            anchors.fill: parent
            visible: coverPath === ""
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.1) }
                GradientStop { position: 1.0; color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.3) }
            }
            Text {
                anchors.centerIn: parent
                text: "🎮"
                font.pixelSize: carouselMode ? 90 : 45
                opacity: 0.25
            }
        }
        
        // Etiqueta de Plataforma (Flotante)
        Rectangle {
            anchors.top: parent.top; anchors.right: parent.right; anchors.margins: 8
            width: 45; height: 18; radius: 4; color: "#cc000000"
            border.color: "#33ffffff"; border.width: 1
            Text { 
                anchors.centerIn: parent; text: platform.toUpperCase(); color: "white"
                font.pixelSize: 8; font.bold: true; font.letterSpacing: 1 
            }
        }
    }

    // --- 2. INFO DEL JUEGO ---
    Column {
        anchors.top: coverContainer.bottom; anchors.left: parent.left; anchors.right: parent.right
        anchors.bottom: parent.bottom; anchors.margins: 12
        spacing: 2

        Text {
            width: parent.width
            text: title
            color: "white"; font.pixelSize: 13; font.bold: true
            elide: Text.ElideRight
        }

        Text {
            width: parent.width
            text: "LANZAR JUEGO"
            color: isHovered ? accentColor : "#66ffffff"
            font.pixelSize: 9; font.bold: true; font.letterSpacing: 1
            opacity: isHovered ? 1 : 0.6
            Behavior on color { ColorAnimation { duration: 200 } }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: romCard.clicked()
    }
}
