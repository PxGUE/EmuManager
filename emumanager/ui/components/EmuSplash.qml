import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Rectangle {
    id: splashRoot
    anchors.fill: parent
    color: "#050505"
    z: 100
    
    // Propiedades de Control Externo
    property bool isLoaded: false
    property string statusText: "INICIALIZANDO..."
    property real progress: 0.0
    
    // Transición de Salida Cinematográfica
    visible: opacity > 0
    opacity: isLoaded ? 0 : 1
    Behavior on opacity { NumberAnimation { duration: 1000; easing.type: Easing.InOutQuad } }

    ColumnLayout {
        id: splashContent
        anchors.centerIn: parent
        spacing: 40
        
        // Efecto de Zoom Out al terminar la carga
        scale: isLoaded ? 1.5 : 1.0
        opacity: isLoaded ? 0 : 1
        Behavior on scale { NumberAnimation { duration: 1200; easing.type: Easing.OutCubic } }
        Behavior on opacity { NumberAnimation { duration: 800 } }

        // --- EL NUEVO LOGO PREMIUM ---
        Column {
            Layout.alignment: Qt.AlignCenter; spacing: 20
            
            Image {
                source: "../assets/logo.svg"
                Layout.preferredWidth: 200; Layout.preferredHeight: 200
                Layout.alignment: Qt.AlignCenter
                smooth: true; antialiasing: true
                asynchronous: true
                
                // Sutil respiro del logo
                SequentialAnimation on scale {
                    running: !isLoaded; loops: Animation.Infinite
                    NumberAnimation { from: 1.0; to: 1.05; duration: 2000; easing.type: Easing.InOutQuad }
                    NumberAnimation { from: 1.05; to: 1.0; duration: 2000; easing.type: Easing.InOutQuad }
                }
            }
            
            Text {
                text: "EmuManager"
                color: "white"; font.pixelSize: 42; font.bold: true
                font.letterSpacing: 10; anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        // CONTROL DE CARGA
        Column {
            Layout.alignment: Qt.AlignCenter; spacing: 25; width: 300
            
            Rectangle {
                width: parent.width; height: 4; radius: 2; color: "#111111"
                clip: true
                Rectangle {
                    width: parent.width * progress; height: parent.height; radius: 2; color: "#16a085"
                    Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
                }
            }
            
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: statusText.toUpperCase()
                color: "#44ffffff"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 3
            }
        }
    }
}
