import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "../components"
import "../components/cards"
import "../components/system"
import "../components/effects"

Item {
    id: discoveryRoot
    anchors.fill: parent
    
    property var discoveryData: ({ "on_this_day": [], "hidden_gems": [], "random_batch": [] })
    property bool isLoading: true

    function refresh() {
        isLoading = true
        if (mainController && mainController.statsController) {
            discoveryData = mainController.statsController.get_discovery_data()
        }
        isLoading = false
    }

    Component.onCompleted: refresh()

    // --- 1. THE KINETIC VAULT BACKGROUND (Cinematic Atmosphere) ---
    NebulaBackground {
        accentColor: Theme.accentElectric
        interactiveForce: 0.1
    }

    // --- 2. MAIN STRUCTURE ---
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 45
        spacing: 30

        // A. HEADER (Always at the top)
        RowLayout {
            Layout.fillWidth: true; Layout.preferredHeight: 80
            ColumnLayout {
                spacing: 0
                Text { 
                    text: I18n.t.vault_title.toUpperCase(); 
                    color: Theme.textMain; font.pixelSize: 48; font.weight: Font.Black; font.letterSpacing: -2 
                }
                Text { 
                    text: I18n.t.vault_subtitle; 
                    color: Theme.accentElectric; font.pixelSize: 12; font.bold: true; font.letterSpacing: 4; opacity: 0.8
                }
            }
            Item { Layout.fillWidth: true }
            GlassPanel {
                width: 140; height: 50; radius: 12
                content: ColumnLayout {
                    anchors.centerIn: parent; spacing: -2
                    Text { text: I18n.t.vault_status; color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1; Layout.alignment: Qt.AlignCenter }
                    Text { text: I18n.t.vault_sync_ok; color: Theme.statusSuccess; font.pixelSize: 12; font.bold: true; Layout.alignment: Qt.AlignCenter }
                }
            }
        }

        // B. CONTENT AREA (Fills exactly the remaining space)
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            // --- C. DYNAMIC STATE SWITCHER ---
            StackLayout {
                anchors.fill: parent
                currentIndex: (!isLoading && discoveryData.random_batch && discoveryData.random_batch.length > 0) ? 1 : 0
                
                // STATE 0: CINEMATIC SPLASH (When empty)
                VaultSplash {
                    accentColor: Theme.accentElectric
                }

                // STATE 1: VAULT HUB (When data available)
                Flickable {
                    id: vaultScroll
                    contentWidth: width; contentHeight: vaultContent.implicitHeight; clip: true
                    flickableDirection: Flickable.VerticalFlick
                    
                    ScrollBar.vertical: ScrollBar { 
                        width: 4; policy: ScrollBar.AsNeeded; active: true
                        contentItem: Rectangle { color: Theme.accentElectric; radius: 2; opacity: 0.3 }
                    }

                    ColumnLayout {
                        id: vaultContent
                        width: parent.width; spacing: 50
                        
                        // HERO SECTION (DYNAMIC SPOTLIGHT)
                        Item {
                            id: heroSection
                            Layout.fillWidth: true; Layout.preferredHeight: 320
                            
                            property bool isAnniversary: discoveryData.on_this_day && discoveryData.on_this_day.length > 0
                            property bool isGem: !isAnniversary && discoveryData.hidden_gems && discoveryData.hidden_gems.length > 0
                            property var heroGame: isAnniversary ? discoveryData.on_this_day[0] : (isGem ? discoveryData.hidden_gems[0] : (discoveryData.random_batch ? discoveryData.random_batch[0] : null))
                            property string heroCategory: isAnniversary ? I18n.t.vault_anniversary : (isGem ? I18n.t.vault_hidden_gem : I18n.t.vault_discovery)
                            property color categoryColor: isAnniversary ? Theme.accentElectric : (isGem ? Theme.statusInfo : Theme.accentColor)

                            GlassPanel {
                                anchors.fill: parent; radius: 24; glassOpacity: 0.3
                                borderColor: heroSection.categoryColor; borderWidth: 2
                                
                                RowLayout {
                                    anchors.fill: parent; anchors.margins: 30; spacing: 40
                                    Item {
                                        Layout.preferredWidth: 180; Layout.fillHeight: true
                                        Rectangle {
                                            anchors.fill: parent; radius: 15; color: Theme.backgroundVoid; clip: true; 
                                            Image {
                                                anchors.fill: parent; source: heroSection.heroGame ? "file:///" + (heroSection.heroGame.cover_2d_path || heroSection.heroGame.cover) : ""; 
                                                fillMode: Image.PreserveAspectCrop; asynchronous: true
                                            }
                                        }
                                    }
                                    ColumnLayout {
                                        Layout.fillWidth: true; spacing: 15; Layout.alignment: Qt.AlignVCenter
                                        Rectangle {
                                            width: 140; height: 26; radius: 13; color: heroSection.categoryColor
                                            Text { anchors.centerIn: parent; text: heroSection.heroCategory; color: Theme.white; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
                                        }
                                        Text { text: heroSection.heroGame ? heroSection.heroGame.title : "..."; color: Theme.textMain; font.pixelSize: 32; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }
                                        Text { 
                                            text: heroSection.heroGame ? (heroSection.heroGame.description || I18n.t.vault_explore_desc) : ""; color: Theme.textMuted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true; opacity: 0.8; maximumLineCount: 5; elide: Text.ElideRight; lineHeight: 1.2
                                        }
                                        Button { 
                                            text: heroSection.heroGame && heroSection.isAnniversary ? I18n.t.vault_play_history : I18n.t.vault_play; 
                                            Layout.preferredWidth: 220; Layout.preferredHeight: 48; Material.background: heroSection.categoryColor
                                            onClicked: if(heroSection.heroGame) mainController.launch_game_by_id(heroSection.heroGame.id)
                                        }
                                    }
                                }
                            }
                        }

                        // GAME MIX
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 20; Layout.bottomMargin: 60
                            RowLayout {
                                Layout.fillWidth: true
                                Text { text: I18n.t.vault_game_mix; color: Theme.textMain; font.pixelSize: 22; font.weight: Font.Black; font.letterSpacing: 2 }
                                Rectangle { Layout.fillWidth: true; height: 1; color: Theme.accentElectric; opacity: 0.3; Layout.leftMargin: 20 }
                            }
                            Text { 
                                text: I18n.t.vault_game_mix_desc; 
                                color: Theme.accentElectric; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2; opacity: 0.7;
                                Layout.topMargin: -15
                            }
                            GridLayout {
                                id: mosaicGrid; Layout.fillWidth: true; columns: Math.max(1, Math.floor(width / 122)); columnSpacing: 12; rowSpacing: 12
                                Repeater {
                                    model: discoveryData.random_batch ? discoveryData.random_batch.slice(0, 20) : []
                                    delegate: Rectangle {
                                        Layout.fillWidth: true; Layout.preferredHeight: width * 1.45; radius: 10; color: Theme.backgroundVoid
                                        border.color: wallMA.containsMouse ? Theme.accentElectric : Theme.transparent; border.width: 2; clip: true; scale: wallMA.containsMouse ? 1.05 : 1.0
                                        Behavior on scale { NumberAnimation { duration: 150 } }
                                        Image { anchors.fill: parent; source: modelData.cover ? "file:///" + modelData.cover : ""; fillMode: Image.PreserveAspectCrop; asynchronous: true; opacity: wallMA.containsMouse ? 1.0 : 0.6 }
                                        MouseArea { id: wallMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: window.openGameDetails(modelData.id) }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
