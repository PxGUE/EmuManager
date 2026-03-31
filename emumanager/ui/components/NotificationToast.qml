import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "system"

/**
 * NotificationToast.qml
 * Sistema de notificaciones premium para EmuManager.
 */
Item {
    id: toastRoot
    width: 320; height: 110
    Layout.preferredWidth: 320; Layout.preferredHeight: 110
    Layout.alignment: Qt.AlignRight
    
    property string title: "Notificación"
    property string sender: "Sistema"
    property string message: ""
    property color accentColor: Theme.accentColor
    
    signal closed()

    // Sombra para profundidad
    RectangularGlow {
        anchors.fill: container
        glowRadius: 10; spread: 0.2; color: Theme.backgroundVoid; opacity: 0.5
    }

    Rectangle {
        id: container
        anchors.fill: parent
        radius: Theme.radiusMedium
        color: Theme.backgroundVoid
        border.color: Theme.cardBorder; border.width: 1
        clip: true

        // Efecto Kinetic Nebula (Gradient sutil)
        Rectangle {
            anchors.fill: parent
            opacity: 0.1
            gradient: Gradient {
                GradientStop { position: 0.0; color: toastRoot.accentColor }
                GradientStop { position: 1.0; color: Theme.transparent }
            }
        }

        RowLayout {
            anchors.fill: parent; anchors.margins: 15; spacing: 12

            // Icono / Indicador de responsable
            Rectangle {
                width: 40; height: 40; radius: 10
                color: toastRoot.accentColor; opacity: 0.15
                Text {
                    anchors.centerIn: parent
                    text: toastRoot.sender === "MANGO" ? "🥭" : "🔔"
                    font.pixelSize: 20
                }
            }

            ColumnLayout {
                Layout.fillWidth: true; spacing: 2
                RowLayout {
                    Text { 
                        text: toastRoot.title; color: Theme.textMain; 
                        font.pixelSize: 12; font.bold: true; font.letterSpacing: 1 
                    }
                    Item { Layout.fillWidth: true }
                    Text { 
                        text: toastRoot.sender.toUpperCase(); color: toastRoot.accentColor; 
                        font.pixelSize: 8; font.bold: true; opacity: 0.8 
                    }
                }
                Text {
                    text: toastRoot.message
                    color: Theme.textDim; font.pixelSize: 10
                    Layout.fillWidth: true; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight
                }
            }

            Button {
                id: closeBtn
                text: I18n.t.ok_btn
                implicitWidth: 45; implicitHeight: 28
                flat: true
                Layout.alignment: Qt.AlignTop
                
                contentItem: Text {
                    text: closeBtn.text; color: Theme.accentColor; font.pixelSize: 10; font.bold: true
                    horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    color: closeBtn.hovered ? Theme.accentColor + "22" : Theme.transparent
                    border.color: Theme.accentColor; border.width: 1; radius: 6
                }
                
                onClicked: toastRoot.dismiss()
            }
        }

        // Barra de progreso de auto-cierre (sutil)
        Rectangle {
            anchors.bottom: parent.bottom; anchors.left: parent.left
            height: 2; color: toastRoot.accentColor
            Timer {
                id: lifeTimer; interval: 8000; running: true; onTriggered: toastRoot.dismiss()
            }
            PropertyAnimation on width {
                from: container.width; to: 0; duration: 8000; running: lifeTimer.running
            }
        }
    }

    // Animaciones
    function show() {
        showAnim.start()
    }

    function dismiss() {
        hideAnim.start()
    }

    ParallelAnimation {
        id: showAnim
        NumberAnimation { target: toastRoot; property: "opacity"; from: 0; to: 1; duration: 400; easing.type: Easing.OutCubic }
        NumberAnimation { target: toastRoot; property: "x"; from: toastRoot.width; to: 0; duration: 500; easing.type: Easing.OutBack }
    }

    ParallelAnimation {
        id: hideAnim
        NumberAnimation { target: toastRoot; property: "opacity"; to: 0; duration: 300 }
        NumberAnimation { target: toastRoot; property: "scale"; to: 0.9; duration: 300 }
        onFinished: toastRoot.closed()
    }

    Component.onCompleted: show()
}
