import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import "../system"

Item {
    id: root
    width: 360
    height: 420
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
    }
    
    // ... (propiedades iguales)
    property string title: "Extension"
    property string description: "Description here"
    property string icon: "✨"
    property bool isReady: false
    property bool isDownloading: false
    property real downloadProgress: 0.0
    property string statusLabel: isReady ? I18n.t.status_installed : I18n.t.status_available
    
    signal installClicked()
    signal uninstallClicked()

    Rectangle {
        id: cardBg
        width: 320
        height: 380
        anchors.centerIn: parent
        radius: Theme.radiusMedium
        color: Theme.cardBackground
        border.color: mouseArea.containsMouse ? Theme.accentColor : Theme.cardBorder
        border.width: Theme.borderThin
        opacity: Theme.cardOpacity

        // Animación de escala interna para evitar recortes por el contenedor padre
        scale: mouseArea.containsMouse ? 1.02 : 1.0
        Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutQuint } }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 25
            spacing: 15

            // --- HEADER ---
            RowLayout {
                spacing: 15
                Rectangle {
                    width: 50; height: 50; radius: 25
                    color: Theme.accentColor; opacity: 0.1
                    Text { anchors.centerIn: parent; text: root.icon; font.pixelSize: 24 }
                }
                ColumnLayout {
                    spacing: 2
                    Text { text: root.title; color: Theme.textMain; font.pixelSize: Theme.fontHeader; font.bold: true }
                    Rectangle {
                        height: 18; width: statusText.width + 12; radius: 9
                        color: root.isReady ? Theme.statusSuccess : Theme.transparent
                        border.color: root.isReady ? Theme.transparent : Theme.divider
                        border.width: 1; opacity: root.isReady ? 0.2 : 0.5
                        Text { 
                            id: statusText; anchors.centerIn: parent; text: root.statusLabel
                            color: root.isReady ? Theme.statusSuccess : Theme.textMuted
                            font.pixelSize: 9; font.bold: true; font.letterSpacing: 1
                        }
                    }
                }
            }

            // --- BODY ---
            Text {
                Layout.fillWidth: true
                Layout.fillHeight: true
                text: root.description
                color: Theme.textMain
                opacity: 0.7
                font.pixelSize: Theme.fontBody
                wrapMode: Text.WordWrap
                lineHeight: 1.4
                elide: Text.ElideRight
            }

            // --- FOOTER / ACTIONS ---
            Item { Layout.fillHeight: true } // Spacer

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 10
                visible: !root.isDownloading

                Button {
                    Layout.fillWidth: true
                    height: 44
                    text: root.isReady ? I18n.t.btn_uninstall : I18n.t.btn_install
                    highlighted: !root.isReady
                    Material.accent: root.isReady ? Theme.danger : Theme.accentColor
                    onClicked: root.isReady ? root.uninstallClicked() : root.installClicked()
                }
            }

            // --- PROGRESS AREA ---
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 10
                visible: root.isDownloading

                ProgressBar {
                    Layout.fillWidth: true
                    value: root.downloadProgress
                }
                Text { 
                    text: (root.downloadProgress * 100).toFixed(0) + "%"; 
                    color: Theme.textMuted; font.pixelSize: 9; Layout.alignment: Qt.AlignHCenter 
                }
            }
        }
    }

}
