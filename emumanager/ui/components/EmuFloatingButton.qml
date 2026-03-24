import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Rectangle {
    id: floatingBtn
    
    // Propiedades Configurables
    property string icon: "⟲"
    property color accentColor: "#16a085"
    property real size: 50
    property bool isHovered: mouseArea.containsMouse
    
    signal clicked()

    width: size; height: size; radius: size / 2
    color: isHovered ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.2) : "#121216"
    border.color: isHovered ? accentColor : "#25252b"
    border.width: 1
    
    Behavior on color { ColorAnimation { duration: 300 } }
    Behavior on border.color { ColorAnimation { duration: 300 } }
    Behavior on scale { NumberAnimation { duration: 400; easing.type: Easing.OutBack } }

    // Capa de Brillo (Glassmorphism)
    Rectangle {
        anchors.fill: parent; radius: parent.radius; opacity: 0.05
        color: "white"
    }

    // Efecto de Resplandor (Glow)
    Rectangle {
        anchors.fill: parent; radius: parent.radius; z: -1
        color: accentColor; opacity: isHovered ? 0.2 : 0
        scale: isHovered ? 1.2 : 1.0
        Behavior on opacity { NumberAnimation { duration: 400 } }
        Behavior on scale { NumberAnimation { duration: 400 } }
    }

    Text {
        anchors.centerIn: parent
        text: floatingBtn.icon
        color: isHovered ? "white" : accentColor
        font.pixelSize: size * 0.4
        font.bold: true
        Behavior on color { ColorAnimation { duration: 300 } }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: floatingBtn.clicked()
    }
}
