import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: downloadsRoot
    
    property string activeGroup: "all"
    property string searchText: ""

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 40
        spacing: 24

        // HEADER
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 4
                Label {
                    text: bridge.translate("nav_downloads")
                    font.pixelSize: 32
                    font.bold: true
                    color: "white"
                }
                Label {
                    text: bridge.translate("dl_list_sub")
                    font.pixelSize: 14
                    color: "#888899"
                }
            }
            Item { Layout.fillWidth: true }
            
            // Search (simplified for now)
            TextField {
                id: searchInput
                placeholderText: bridge.translate("search_placeholder")
                width: 250
                onTextChanged: searchText = text
            }
        }

        // GRID
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: availableWidth
            clip: true

            Flow {
                width: parent.width
                spacing: 24
                padding: 10
                
                add: Transition {
                    NumberAnimation { properties: "opacity,scale"; from: 0; to: 1; duration: 300; easing.type: Easing.OutCubic }
                }

                Repeater {
                    model: bridge.allEmulators
                    delegate: EmulatorCard {
                        visible: (activeGroup === "all" || modelData.consoleId === activeGroup) && 
                                 (searchText === "" || modelData.name.toLowerCase().includes(searchText.toLowerCase()))
                        
                        name: modelData.name
                        consoleName: modelData.console
                        description: modelData.description
                        github: modelData.github
                        isInstalled: modelData.isInstalled
                        accentColor: modelData.color
                    }
                }
            }
        }
    }
}
