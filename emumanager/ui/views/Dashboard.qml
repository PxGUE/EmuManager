import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

Item {
    id: dashboardRoot
    objectName: "dashboardView"

    // Simulación de estado de datos
    property bool hasData: false 

    Rectangle {
        anchors.fill: parent
        color: "#050505"
    }

    // --- ESTADO VACÍO: SPLASH ESPECTACULAR ---
    Item {
        id: splashArea
        anchors.fill: parent
        visible: !hasData

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 20

            // 1. LOGO CON GLOW (EmuManager)
            Item {
                Layout.preferredWidth: 400; Layout.preferredHeight: 150
                Layout.alignment: Qt.AlignCenter

                Text {
                    id: logoMain
                    anchors.centerIn: parent
                    text: "EmuManager"
                    color: "white"
                    font.pixelSize: 64; font.bold: true; font.letterSpacing: 4
                    opacity: 0.9
                }

                // Efecto de resplandor suave corregido
                MultiEffect {
                    source: logoMain
                    anchors.fill: logoMain
                    blurEnabled: true
                    blur: 0.7
                    shadowEnabled: true
                    shadowColor: "#20ffffff" // Propiedad correcta corregida
                    shadowBlur: 1.0
                    shadowHorizontalOffset: 0
                    shadowVerticalOffset: 0
                }
            }

            // 2. TEXTO DE BIENVENIDA ANIMADO
            Text {
                text: "TU PRÓXIMA AVENTURA COMIENZA AQUÍ"
                color: "#44ffffff"
                font.pixelSize: 14; font.bold: true; font.letterSpacing: 6
                Layout.alignment: Qt.AlignCenter
                
                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    NumberAnimation { from: 0.3; to: 0.8; duration: 2500; easing.type: Easing.InOutQuad }
                    NumberAnimation { from: 0.8; to: 0.3; duration: 2500; easing.type: Easing.InOutQuad }
                }
            }
        }
    }

    // --- ESTADO CON DATOS ---
    Item {
        anchors.fill: parent
        visible: hasData
        Text { anchors.centerIn: parent; text: "Dashboard Activo"; color: "white" }
    }
}
