import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: libraryRoot
    
    state: "carousel" // carousel or grid
    
    property string currentConsoleId: ""
    property var currentGames: []

    // --- CAROUSEL VIEW ---
    PathView {
        id: carousel
        anchors.fill: parent
        visible: true
        opacity: 1
        model: bridge.scannedConsoles
        pathItemCount: 5
        preferredHighlightBegin: 0.5
        preferredHighlightEnd: 0.5
        highlightRangeMode: PathView.StrictlyEnforceRange

        path: Path {
            startX: -200; startY: parent.height / 2
            PathAttribute { name: "z"; value: 0 }
            PathAttribute { name: "itemScale"; value: 0.6 }
            PathAttribute { name: "itemOpacity"; value: 0.2 }
            
            PathCubic {
                x: parent.width / 2; y: parent.height / 2
                control1X: 100; control1Y: parent.height / 2
                control2X: 200; control2Y: parent.height / 2
            }
            PathAttribute { name: "z"; value: 100 }
            PathAttribute { name: "itemScale"; value: 1.0 }
            PathAttribute { name: "itemOpacity"; value: 1.0 }
            
            PathCubic {
                x: parent.width + 200; y: parent.height / 2
                control1X: parent.width - 200; control1Y: parent.height / 2
                control2X: parent.width - 100; control2Y: parent.height / 2
            }
            PathAttribute { name: "z"; value: 0 }
            PathAttribute { name: "itemScale"; value: 0.6 }
            PathAttribute { name: "itemOpacity"; value: 0.2 }
        }

        delegate: Item {
            id: delegateRoot
            width: 220
            height: 300
            z: PathView.z
            scale: PathView.itemScale
            opacity: PathView.itemOpacity

            Rectangle {
                anchors.fill: parent
                radius: 24
                color: "#1a1c24"
                border.color: PathView.isCurrentItem ? modelData.color : "#2a2d3a"
                border.width: PathView.isCurrentItem ? 2 : 1
                
                // Content Gradient
                Rectangle {
                    anchors.fill: parent
                    radius: 24
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: Qt.alpha(modelData.color, 0.1) }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 16

                    Item { Layout.fillHeight: true }

                    Rectangle {
                        width: 64
                        height: 64
                        radius: 16
                        color: Qt.alpha(modelData.color, 0.15)
                        Layout.alignment: Qt.AlignCenter
                        
                        Label {
                            anchors.centerIn: parent
                            text: "🎮"
                            font.pixelSize: 32
                        }
                    }

                    ColumnLayout {
                        spacing: 2
                        Layout.fillWidth: true
                        Label {
                            text: modelData.name
                            font.pixelSize: 18
                            font.bold: true
                            color: "white"
                            Layout.alignment: Qt.AlignCenter
                        }
                        Label {
                            text: modelData.count + " " + bridge.translate("nav_library")
                            font.pixelSize: 12
                            color: "#666666"
                            Layout.alignment: Qt.AlignCenter
                        }
                    }

                    Item { Layout.fillHeight: true }
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        if (PathView.isCurrentItem) {
                            libraryRoot.currentConsoleId = modelData.id
                            libraryRoot.currentGames = bridge.getGamesForConsole(modelData.id)
                            libraryRoot.state = "grid"
                        } else {
                            carousel.currentIndex = index
                        }
                    }
                }
            }
        }
    }

    // --- GRID VIEW ---
    ColumnLayout {
        id: gridLayout
        anchors.fill: parent
        anchors.margins: 40
        visible: false
        opacity: 0
        spacing: 20

        RowLayout {
            Layout.fillWidth: true
            Button {
                text: "← Back"
                onClicked: libraryRoot.state = "carousel"
            }
            Label {
                text: libraryRoot.currentConsoleId.toUpperCase()
                font.pixelSize: 24
                font.bold: true
                color: "white"
            }
            Item { Layout.fillWidth: true }
        }

        GridView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            cellWidth: 180
            cellHeight: 260
            model: libraryRoot.currentGames
            clip: true

            delegate: ColumnLayout {
                spacing: 8
                width: 160
                
                Rectangle {
                    width: 160
                    height: 220
                    radius: 8
                    color: "#1a1c24"
                    clip: true
                    
                    Image {
                        anchors.fill: parent
                        source: modelData.cover ? "file:///" + modelData.cover : ""
                        fillMode: Image.PreserveAspectCrop
                        visible: modelData.cover !== ""
                    }
                    
                    Label {
                        anchors.centerIn: parent
                        text: "NO BOX ART"
                        visible: modelData.cover === ""
                        color: "#444"
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: bridge.launchGame(modelData.path, modelData.id_emu)
                    }
                }

                Label {
                    text: modelData.name
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 12
                    color: "white"
                }
            }
        }
    }

    states: [
        State {
            name: "carousel"
            PropertyChanges { target: carousel; opacity: 1; visible: true }
            PropertyChanges { target: gridLayout; opacity: 0; visible: false }
        },
        State {
            name: "grid"
            PropertyChanges { target: carousel; opacity: 0; visible: false }
            PropertyChanges { target: gridLayout; opacity: 1; visible: true }
        }
    ]

    transitions: [
        Transition {
            from: "*"; to: "*"
            NumberAnimation { properties: "opacity"; duration: 250; easing.type: Easing.InOutQuad }
        }
    ]
}
