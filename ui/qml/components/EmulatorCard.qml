import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: card
    property string name: "Emulator"
    property string consoleName: "System"
    property string description: ""
    property string github: ""
    property bool isInstalled: false
    property color accentColor: "#4da6ff"
    property real downloadProgress: 0
    property bool isDownloading: false

    width: 260
    height: 340
    radius: 20
    color: "#16181f"
    border.color: mouseArea.containsMouse ? accentColor : "#252830"
    border.width: 1
    
    scale: mouseArea.containsMouse ? 1.02 : 1.0
    Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutBack } }
    Behavior on border.color { ColorAnimation { duration: 150 } }

    // Banner
    Rectangle {
        width: parent.width
        height: 120
        radius: 20
        color: "#1a2035"
        anchors.top: parent.top
        clip: true
        
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.lighter(accentColor, 1.2) }
                GradientStop { position: 1.0; color: accentColor }
            }
            opacity: 0.2
        }

        Label {
            anchors.centerIn: parent
            text: card.consoleName
            font.pixelSize: 20
            font.weight: Font.Black
            color: "white"
            opacity: 0.8
        }
        
        // Glass effect overlay
        Rectangle {
            anchors.fill: parent
            color: "white"
            opacity: 0.03
            visible: mouseArea.containsMouse
        }
    }

    ColumnLayout {
        anchors.top: parent.top
        anchors.topMargin: 130
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20
        spacing: 12

        ColumnLayout {
            spacing: 2
            Label {
                text: card.name
                font.pixelSize: 18
                font.bold: true
                color: "white"
                Layout.fillWidth: true
                elide: Text.ElideRight
            }

            Label {
                text: card.description
                font.pixelSize: 12
                color: "#666677"
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }
        }

        Item { Layout.fillHeight: true }

        // Progress bar
        ColumnLayout {
            visible: card.isDownloading
            Layout.fillWidth: true
            spacing: 4
            
            ProgressBar {
                id: pbar
                value: card.downloadProgress
                Layout.fillWidth: true
                to: 1.0
                
                background: Rectangle {
                    implicitWidth: 200
                    implicitHeight: 6
                    color: "#1a1c24"
                    radius: 3
                }
                
                contentItem: Item {
                    implicitWidth: 200
                    implicitHeight: 6

                    Rectangle {
                        width: pbar.visualPosition * parent.width
                        height: parent.height
                        radius: 3
                        color: card.accentColor
                    }
                }
            }
            
            Label {
                text: Math.round(card.downloadProgress * 100) + "%"
                font.pixelSize: 10
                color: card.accentColor
                Layout.alignment: Qt.AlignRight
            }
        }

        Button {
            id: actionBtn
            Layout.fillWidth: true
            text: card.isInstalled ? bridge.translate("dl_btn_uninstall") : bridge.translate("dl_btn_install")
            height: 44
            enabled: !card.isDownloading
            
            contentItem: Text {
                text: actionBtn.text
                color: card.isInstalled ? "#888899" : "black"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.bold: true
                font.pixelSize: 13
            }

            background: Rectangle {
                color: card.isInstalled ? "#2d3436" : card.accentColor
                radius: 10
                opacity: actionBtn.down ? 0.8 : 1.0
            }

            onClicked: {
                if (card.isInstalled) {
                    bridge.uninstallEmulator(card.github)
                } else {
                    card.isDownloading = true
                    bridge.installEmulator(card.github)
                }
            }
        }
    }

    // Connect to global progress
    Connections {
        target: bridge
        function onDownloadProgress(url, p) {
            if (url === card.github) {
                card.downloadProgress = p
                card.isDownloading = true
            }
        }
        function onDownloadFinished(url, success, msg) {
            if (url === card.github) {
                card.isDownloading = false
                card.downloadProgress = 0
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
    }
}
