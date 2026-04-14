import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import "../system"

Item {
    id: hudRoot
    anchors.fill: parent
    z: 10000 // Siempre por encima de todo
    
    property bool active: false
    property string sessionTime: "00:00:00"
    property int cpuThreads: 0
    property string localTime: ""

    // Actualizador de datos
    Timer {
        interval: 1000; running: hudRoot.active; repeat: true
        onTriggered: {
            hudRoot.sessionTime = mainController.get_session_time()
            var now = new Date()
            hudRoot.localTime = now.toLocaleTimeString(Qt.locale(), "HH:mm:ss")
            var sysInfo = mainController.statsController.get_system_info()
            hudRoot.cpuThreads = sysInfo.cpu_threads
        }
    }

    // --- 1. FONDO DE ATENUACIÓN SUTIL ---
    Rectangle {
        anchors.fill: parent
        color: Theme.backgroundVoid
        opacity: hudRoot.active ? 0.3 : 0
        Behavior on opacity { NumberAnimation { duration: 400 } }
        MouseArea { anchors.fill: parent; enabled: hudRoot.active; onClicked: hudRoot.active = false }
    }

    // --- 2. EL HUD POD (The Capsule) ---
    Rectangle {
        id: capsule
        width: 600; height: 70; radius: 35
        anchors.horizontalCenter: parent.horizontalCenter
        y: hudRoot.active ? 40 : -height - 10
        color: Theme.cardBackground
        border.color: Theme.accentElectric
        border.width: 1.5
        clip: true

        Behavior on y { NumberAnimation { duration: 600; easing.type: Easing.OutBack } }

        // Glow Efecto Respiración
        layer.enabled: true
        layer.effect: DropShadow {
            radius: 15; samples: 20; color: Theme.accentElectric; opacity: 0.3
        }

        RowLayout {
            anchors.fill: parent; anchors.leftMargin: 30; anchors.rightMargin: 30; spacing: 0
            
            // Sección: Tiempo Local
            ColumnLayout {
                spacing: -2; Layout.preferredWidth: 120
                Text { text: "LOCAL TIME"; color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1 }
                Text { text: hudRoot.localTime; color: Theme.textMain; font.pixelSize: 18; font.bold: true; font.family: "Monospace" }
            }

            Rectangle { width: 1; height: 30; color: Theme.cardBorder; opacity: 0.3 }

            // Sección: Sesión
            ColumnLayout {
                spacing: -2; Layout.fillWidth: true; Layout.leftMargin: 20
                Text { text: "SESSION DURATION"; color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1; Layout.alignment: Qt.AlignCenter }
                Text { text: hudRoot.sessionTime; color: Theme.accentElectric; font.pixelSize: 22; font.bold: true; Layout.alignment: Qt.AlignCenter; font.family: "Monospace" }
            }

            Rectangle { width: 1; height: 30; color: Theme.cardBorder; opacity: 0.3 }

            // Sección: M.A.N.G.O Health
            RowLayout {
                Layout.preferredWidth: 140; Layout.leftMargin: 20; spacing: 12
                ColumnLayout {
                    spacing: -2
                    Text { text: "M.A.N.G.O"; color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1 }
                    Text { text: "SHIELD ACTIVE"; color: Theme.statusSuccess; font.pixelSize: 10; font.bold: true }
                }
                
                // Icono de Escudo con pulso
                Text { 
                    text: "🛡️"; font.pixelSize: 24 
                    opacity: 0.8
                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        NumberAnimation { from: 0.8; to: 0.4; duration: 1500; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 0.4; to: 0.8; duration: 1500; easing.type: Easing.InOutSine }
                    }
                }
            }
        }
    }

    // Atajo de teclado para PC (F1 o Tab)
    Shortcut {
        sequence: "Tab"
        onActivated: hudRoot.active = !hudRoot.active
    }
}
