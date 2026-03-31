import QtQuick
import ".."
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Rectangle {
    id: splashRoot
    anchors.fill: parent
    color: Theme.viewBackground
    z: 100
    
    // Propiedades de Control Externo
    property bool isLoaded: false
    property string statusText: I18n.t.initializing
    property real progress: 0.0
    
    // Transición de Salida Cinematográfica
    visible: opacity > 0
    opacity: isLoaded ? 0 : 1
    Behavior on opacity { NumberAnimation { duration: 1000; easing.type: Easing.InOutQuad } }

    ColumnLayout {
        id: splashContent
        anchors.centerIn: parent
        spacing: 30
        
        // Efecto de Zoom Out al terminar la carga
        scale: isLoaded ? 1.2 : 1.0
        opacity: isLoaded ? 0 : 1
        Behavior on scale { NumberAnimation { duration: 1200; easing.type: Easing.OutCubic } }
        Behavior on opacity { NumberAnimation { duration: 800 } }

        // --- EL NUEVO LOGO PREMIUM ---
        ColumnLayout {
            Layout.alignment: Qt.AlignCenter; spacing: 4
            
            Image {
                source: "../../assets/logo.svg"
                Layout.preferredWidth: 80; Layout.preferredHeight: 80
                Layout.alignment: Qt.AlignCenter
                fillMode: Image.PreserveAspectFit
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
                text: I18n.t.app_name
                color: Theme.textMain; font.pixelSize: 20; font.bold: true
                font.letterSpacing: 4; Layout.alignment: Qt.AlignHCenter
            }
        }

        // CONTROL DE CARGA
        Column {
            Layout.alignment: Qt.AlignCenter; spacing: 12; width: 180
            
            Rectangle {
                width: parent.width; height: 4; radius: 2; color: Theme.cardBackground
                clip: true
                Rectangle {
                    width: Math.max(2, parent.width * progress); height: parent.height; radius: 2; color: Theme.accentColor
                    Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
                }
            }
            
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: statusText.toUpperCase()
                color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 2
            }
        }
    }
}
