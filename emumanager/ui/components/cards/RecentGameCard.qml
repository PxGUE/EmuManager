import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../system"

GlassPanel {
    id: root
    
    // Properties
    property int gameId: 0
    property string title: ""
    property string platform: ""
    property string cover: ""
    property string playTime: ""
    
    // Signals
    signal launchRequested(int id)
    signal detailsRequested(int id)
    
    Layout.fillWidth: true
    Layout.preferredHeight: 80
    radius: 12
    glassOpacity: 0.65
    showHighlight: true
    borderColor: hovered ? accentColor : Qt.alpha(accentColor, 0.25)
    backgroundColor: Theme.cardBackground
    
    readonly property color accentColor: Theme.colorForPlatform(platform)
    
    // Interaction State
    property bool hovered: false

    content: MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered: root.hovered = true
        onExited: root.hovered = false
        onClicked: root.detailsRequested(root.gameId)
        cursorShape: Qt.PointingHandCursor
        preventStealing: false
        propagateComposedEvents: true
        
        // --- FONDO ATMOSFÉRICO (Degradado sutil de consola) ---
        Rectangle {
            anchors.fill: parent; radius: root.radius; z: -1
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: root.accentColor }
                GradientStop { position: 0.8; color: Theme.transparent }
            }
            opacity: root.hovered ? 0.12 : 0.05
            Behavior on opacity { NumberAnimation { duration: 300 } }
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 20
            spacing: 20

            // 1. CARÁTULA (Miniatura)
            Rectangle {
                Layout.preferredWidth: 56; Layout.preferredHeight: 56; radius: 6; color: Theme.viewBackground; clip: true
                Image {
                    anchors.fill: parent
                    source: root.cover ? "file:///" + root.cover : ""
                    fillMode: Image.PreserveAspectCrop; asynchronous: true
                    opacity: status === Image.Ready ? 1 : 0
                    Behavior on opacity { NumberAnimation { duration: 300 } }
                }
                
                // Icono de respaldo
                Text {
                    anchors.centerIn: parent; text: "🎮"; font.pixelSize: 24; opacity: 0.2
                    visible: !root.cover
                }
            }

            // 2. TÍTULO Y CONSOLA
            ColumnLayout {
                Layout.fillWidth: true; spacing: 2
                Text {
                    text: root.title; color: Theme.textMain; font.pixelSize: 18; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true
                }
                Text {
                    text: root.platform.toUpperCase(); color: root.accentColor; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1.5; opacity: 0.9
                }
            }

            // 3. SWITCHER: TIEMPO JUGADO / BOTÓN REANUDAR
            Item {
                Layout.preferredWidth: 160; Layout.fillHeight: true
                
                // Tiempo Jugado
                Text {
                    anchors.centerIn: parent
                    text: root.playTime; color: Theme.textDim; font.pixelSize: 14; font.bold: true
                    opacity: root.hovered ? 0 : 1
                    scale: root.hovered ? 0.9 : 1
                    Behavior on opacity { NumberAnimation { duration: 250 } }
                    Behavior on scale { NumberAnimation { duration: 250; easing.type: Easing.OutBack } }
                }
                
                // Botón Reanudar
                Button {
                    id: resumeBtn
                    anchors.centerIn: parent
                    width: 140; height: 44
                    opacity: root.hovered ? 1 : 0
                    scale: root.hovered ? 1 : 0.8
                    enabled: root.hovered
                    
                    contentItem: Text {
                        text: I18n.t.resume_mission
                        color: Theme.white; font.bold: true; font.pixelSize: 11; font.letterSpacing: 1
                        horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                    }
                    
                    background: Rectangle {
                        radius: 8; color: root.accentColor
                        Rectangle {
                            anchors.fill: parent; radius: 8; color: Theme.white; opacity: resumeBtn.pressed ? 0.2 : 0
                        }
                    }
                    
                    onClicked: root.launchRequested(root.gameId)
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; acceptedButtons: Qt.NoButton }
                    
                    Behavior on opacity { NumberAnimation { duration: 250 } }
                    Behavior on scale { NumberAnimation { duration: 250; easing.type: Easing.OutBack } }
                }
            }
        }
    }
    
    // Glow sutil en hover
    Rectangle {
        anchors.fill: parent; radius: root.radius; z: -1
        gradient: Gradient {
            GradientStop { position: 0; color: root.accentColor }
            GradientStop { position: 1; color: Theme.transparent }
        }
        opacity: root.hovered ? 0.1 : 0
        Behavior on opacity { NumberAnimation { duration: 400 } }
    }
}
