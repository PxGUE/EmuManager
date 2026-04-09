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
    
    // Estados Internos de la Animación Cinematográfica
    readonly property bool isActuallyDone: isLoaded && introTimer.finished
    property bool introPhase: false
    
    onProgressChanged: {
        if (progress >= 1.0 && !introPhase) {
            introPhase = true
            introTimer.start()
        }
    }

    // Transición de Salida Final (Revelación del Dashboard)
    visible: opacity > 0
    opacity: isActuallyDone ? 0 : 1
    Behavior on opacity { NumberAnimation { duration: 1500; easing.type: Easing.InOutCubic } }

    ColumnLayout {
        id: splashContent
        anchors.centerIn: parent
        spacing: 40
        
        // --- SECCIÓN LOGO (Atemporal y Sobrio) ---
        ColumnLayout {
            Layout.alignment: Qt.AlignCenter; spacing: 15
            
            Image {
                source: "../../assets/logo.svg"
                Layout.preferredWidth: 80; Layout.preferredHeight: 80
                Layout.alignment: Qt.AlignCenter
                fillMode: Image.PreserveAspectFit
                smooth: true; antialiasing: true
                opacity: introPhase ? 0.4 : 1.0
                Behavior on opacity { NumberAnimation { duration: 1000 } }
                
                // Respiración muy sutil durante carga
                SequentialAnimation on scale {
                    running: !introPhase; loops: Animation.Infinite
                    NumberAnimation { from: 1.0; to: 1.02; duration: 3000; easing.type: Easing.InOutQuad }
                    NumberAnimation { from: 1.02; to: 1.0; duration: 3000; easing.type: Easing.InOutQuad }
                }
            }

            // --- TEXTO DE BIENVENIDA (Minimalista) ---
            Text {
                text: "WELCOME"
                color: Theme.textMain
                font.pixelSize: 14
                font.bold: true
                font.letterSpacing: 12
                Layout.alignment: Qt.AlignHCenter
                opacity: introPhase ? 1.0 : 0.0
                scale: introPhase ? 1.0 : 0.95
                
                Behavior on opacity { NumberAnimation { duration: 1200; easing.type: Easing.InOutQuad } }
                Behavior on scale { NumberAnimation { duration: 2000; easing.type: Easing.OutCubic } }
            }
        }

        // --- SECCIÓN CONTROL DE CARGA (Desvanecimiento Elegante) ---
        Column {
            id: loadingControls
            Layout.alignment: Qt.AlignCenter; spacing: 15; width: 240
            opacity: introPhase ? 0 : 1
            visible: opacity > 0
            Behavior on opacity { NumberAnimation { duration: 800 } }
            
            Rectangle {
                width: parent.width; height: 2; radius: 1; color: Theme.cardBackground
                clip: true
                Rectangle {
                    width: Math.max(4, parent.width * progress); height: parent.height; color: Theme.accentColor
                    Behavior on width { NumberAnimation { duration: 600; easing.type: Easing.OutQuint } }
                }
            }
            
            Text {
                width: parent.width; horizontalAlignment: Text.AlignHCenter
                text: statusText.toUpperCase()
                color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 4
            }
        }
    }

    // Temporizador para controlar la duración de la bienvenida
    Timer {
        id: introTimer
        property bool finished: false
        interval: 2000 // Tiempo justo para leer el mensaje sin cansar
        repeat: false
        onTriggered: finished = true
    }
}
