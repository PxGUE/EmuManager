import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: card
    property string providerId: ""
    property string name: ""
    property string type: ""
    property bool enabled: false
    
    signal configureClicked()

    height: 70
    Layout.fillWidth: true

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 69
            spacing: 16

            // Info
            ColumnLayout {
                spacing: 4
                Layout.fillWidth: true
                
                Label {
                    text: card.name
                    font.bold: true
                    font.pixelSize: 15
                    color: card.enabled ? "white" : "#666677"
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }
                
                RowLayout {
                    spacing: 8
                    Rectangle {
                        width: 8; height: 8; radius: 4
                        color: card.type === "artwork" ? "#4da6ff" : "#7c6ff7"
                        opacity: card.enabled ? 0.8 : 0.3
                    }
                    Label {
                        text: card.type.toUpperCase()
                        font.pixelSize: 10
                        font.bold: true
                        color: card.enabled ? "#888899" : "#444455"
                        font.letterSpacing: 1
                    }
                }
            }

            // Actions
            RowLayout {
                spacing: 12
                
                Button {
                    id: cfgBtn
                    text: "Configure"
                    visible: ["tgdb", "rawg", "steamgriddb", "screenscraper", "igdb"].includes(card.providerId)
                    Layout.preferredHeight: 32
                    
                    onClicked: card.configureClicked()
                    
                    background: Rectangle {
                        color: cfgBtn.hovered ? "#303440" : "#252b3d"
                        radius: 6
                        border.color: cfgBtn.hovered ? "#4da6ff" : "transparent"
                        border.width: 1
                    }
                    
                    contentItem: Label {
                        text: bridge ? bridge.translate("set_btn_configure") : "Configure"
                        color: cfgBtn.hovered ? "white" : "#4da6ff"
                        font.pixelSize: 11
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 12
                        rightPadding: 12
                    }
                }

                Switch {
                    id: control
                    checked: card.enabled
                    onToggled: {
                        if (bridge) bridge.toggleProvider(card.providerId, checked)
                    }
                    
                    indicator: Rectangle {
                        implicitWidth: 40
                        implicitHeight: 22
                        radius: 11
                        color: control.checked ? Qt.alpha("#4da6ff", 0.2) : "#1a1c24"
                        border.color: control.checked ? "#4da6ff" : "#353b4d"
                        border.width: 1

                        Rectangle {
                            x: control.checked ? parent.width - width - 4 : 4
                            y: 4
                            width: 14
                            height: 14
                            radius: 7
                            color: control.checked ? "#4da6ff" : "#555566"
                            
                            Behavior on x { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                            Behavior on color { ColorAnimation { duration: 200 } }
                        }
                    }
                }
            }
        }

        // Separator
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#252830"
            opacity: 0.3
        }
    }
}
