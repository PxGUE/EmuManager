import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import "../../components/system"

Item {
    id: splashRoot
    implicitWidth: 800
    implicitHeight: 600

    property color accentColor: Theme.accentElectric

    // Estructura de centro total - REESCRITA DESDE CERO
    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(splashRoot.width * 0.9, 600)
        spacing: 35

        // 1. EL NÚCLEO (DICE + ANIMACIÓN)
        Item {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 200
            Layout.preferredHeight: 200
            
            Rectangle {
                anchors.centerIn: parent
                width: 160; height: 160; radius: 80
                color: "transparent"; border.color: splashRoot.accentColor; border.width: 1; opacity: 0.15
                RotationAnimation on rotation { from: 0; to: 360; duration: 25000; loops: Animation.Infinite }
            }

            Rectangle {
                anchors.centerIn: parent
                width: 185; height: 185; radius: 45; rotation: 45
                color: "transparent"; border.color: splashRoot.accentColor; border.width: 1; opacity: 0.1
                RotationAnimation on rotation { from: 45; to: 405; duration: 40000; loops: Animation.Infinite }
            }

            Rectangle {
                id: core
                anchors.centerIn: parent; width: 80; height: 80; radius: 40; color: splashRoot.accentColor
                opacity: 0.2
                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    NumberAnimation { from: 0.1; to: 0.35; duration: 2500; easing.type: Easing.InOutSine }
                    NumberAnimation { from: 0.35; to: 0.1; duration: 2500; easing.type: Easing.InOutSine }
                }
            }
            
            Glow {
                anchors.fill: core; radius: 30; samples: 20; color: splashRoot.accentColor; source: core; opacity: 0.4
            }

            Text { 
                anchors.centerIn: parent; text: "🎲"; font.pixelSize: 64; opacity: 0.8
                SequentialAnimation on y {
                    loops: Animation.Infinite
                    NumberAnimation { from: 60; to: 75; duration: 4000; easing.type: Easing.InOutQuad }
                    NumberAnimation { from: 75; to: 60; duration: 4000; easing.type: Easing.InOutQuad }
                }
            }
        }

        // 2. TEXTOS (PLANOS EN EL LAYOUT PRINCIPAL)
        Text {
            Layout.fillWidth: true
            text: I18n.t.vault_algorithms_idle
            color: splashRoot.accentColor; font.pixelSize: 13; font.bold: true; font.letterSpacing: 8
            horizontalAlignment: Text.AlignHCenter; opacity: 0.6
        }
        
        Text {
            Layout.fillWidth: true
            text: I18n.t.vault_preparing
            color: Theme.textMain; font.pixelSize: 32; font.weight: Font.Black; font.letterSpacing: -1
            horizontalAlignment: Text.AlignHCenter
        }
        
        Text {
            Layout.fillWidth: true
            text: I18n.t.vault_no_info
            color: Theme.textMuted; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter; opacity: 0.8; lineHeight: 1.4
        }

        Item { Layout.preferredHeight: 15 } // Espacio extra antes del botón

        // 3. BOTÓN
        Button {
            id: mainBtn
            text: I18n.t.vault_goto_library
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 240; Layout.preferredHeight: 54
            
            contentItem: Text {
                text: mainBtn.text; color: Theme.white; font.bold: true; font.letterSpacing: 1.5; font.pixelSize: 14;
                horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
            }
            
            background: Rectangle {
                radius: 12; color: mainBtn.hovered ? splashRoot.accentColor : "transparent"
                border.color: splashRoot.accentColor; border.width: 2
                Behavior on color { ColorAnimation { duration: 200 } }
                Rectangle { anchors.fill: parent; radius: 12; color: "white"; opacity: mainBtn.hovered ? 0.1 : 0 }
            }
            
            onClicked: activeViewId = "libraryView"
        }
    }
}
