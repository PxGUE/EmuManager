import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Models 1.0
import EmuManager.Controllers 1.0
import "../components"
import "../components/cards"
import "../components/system"

Item {
    id: dashboardRoot
    objectName: "dashboardView"

    property var statsData: ({})
    property int totalGames: 0
    property bool isScanning: false
    property bool isScraping: false
    property bool isEngineBusy: isScanning || isScraping
    property real scanProgress: 0.0

    function launchGame(id) { mainController.launch_game_by_id(id) }

    Connections { 
        target: mainController
        function onScanProgressChanged(p) { 
            dashboardRoot.scanProgress = p
            dashboardRoot.isScanning = (p > 0 && p < 1.0) 
        }
        function onScrapeProgressChanged(p) {
            dashboardRoot.isScraping = (p > 0 && p < 1.0)
        }
        function onGamesUpdated() { dashboardRoot.refreshAll() }
    }

    function refreshAll() {
        if (!mainController) return;
        statsData = mainController.get_dashboard_stats()
        totalGames = statsData.total_games || 0
    }

    Component.onCompleted: refreshAll()

    // --- PREMIUM OBSIDIAN BACKGROUND ---
    Rectangle {
        anchors.fill: parent; color: Theme.viewBackground
        
        // Deep Ambient Glow
        Rectangle {
            id: pulseOne
            width: parent.width * 1.8; height: parent.width * 1.8; radius: width/2
            anchors.centerIn: parent; opacity: Theme.glowOpacity
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.cardGlow }
                GradientStop { position: 1.0; color: "transparent" }
            }
            NumberAnimation on rotation { from: 0; to: 360; duration: 120000; loops: Animation.Infinite }
        }
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: totalGames > 0 ? 1 : 0

        Item {
            ColumnLayout {
                anchors.centerIn: parent; spacing: 20
                Text { text: "🌌"; font.pixelSize: 48; Layout.alignment: Qt.AlignCenter }
                Text { text: I18n.t.empty_library; color: Theme.textMain; font.pixelSize: 24; font.bold: true; Layout.alignment: Qt.AlignCenter }
                Button { text: I18n.t.configure_paths_btn; Material.background: Theme.accentColor; onClicked: activeViewId = "settingsView"; Layout.alignment: Qt.AlignCenter }
            }
        }

        Flickable {
            id: mainFlickable; Layout.fillWidth: true; Layout.fillHeight: true
            contentWidth: width; contentHeight: mainContentLayout.implicitHeight
            boundsBehavior: Flickable.DragAndOvershootBounds
            flickableDirection: Flickable.VerticalFlick; flickDeceleration: 1500
            pressDelay: 100; interactive: true; clip: true

            ScrollBar.vertical: ScrollBar { 
                parent: mainFlickable; x: mainFlickable.width - width - 5; y: 40; height: mainFlickable.height - 100; active: mainFlickable.moving
            }
            
            ColumnLayout {
                id: mainContentLayout
                anchors.left: parent.left; anchors.right: parent.right
                anchors.leftMargin: 45; anchors.rightMargin: 45
                spacing: Theme.spaceExtraLarge
                
                Item { Layout.preferredHeight: 40 } // Top Padding

                // 1. DYNAMIC COMMAND HEADER (REFINED)
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: 60; spacing: Theme.spaceLarge
                    
                    RowLayout {
                        spacing: Theme.spaceMedium
                        Image { 
                            source: "../assets/logo.svg"; Layout.preferredWidth: 32; Layout.preferredHeight: 32; 
                            fillMode: Image.PreserveAspectFit; smooth: true
                        }
                        ColumnLayout {
                            spacing: -2
                            Text { 
                                text: "EmuManager"; color: Theme.textMain; 
                                font.pixelSize: 22; font.bold: true; font.letterSpacing: 1
                            }
                            Text { 
                                text: "OPERATIONAL ECOSYSTEM v0.9.5"; color: Theme.accentColor; 
                                font.pixelSize: 9; font.bold: true; font.letterSpacing: 2; opacity: 0.7 
                            }
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    // Top Bar Stats (User likes these better than tiles)
                    RowLayout {
                        spacing: Theme.spaceExtraLarge; Layout.alignment: Qt.AlignVCenter
                        
                        ColumnLayout {
                            spacing: -3; Layout.alignment: Qt.AlignRight
                            Text { text: I18n.t.stats_total_games; color: Theme.textMuted; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                            Text { text: totalGames + " " + I18n.t.games_abbr; color: Theme.textMain; font.pixelSize: 18; font.bold: true }
                        }
                        
                        Rectangle { width: 1; height: 25; color: Theme.divider; opacity: 0.5 }
                        
                        ColumnLayout {
                            spacing: -3; Layout.alignment: Qt.AlignRight
                            Text { text: I18n.t.stats_play_time; color: Theme.textMuted; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                            Text { text: statsData.total_play_time || "0h 0m"; color: Theme.textMain; font.pixelSize: 18; font.bold: true }
                        }
                        
                        Rectangle { width: 1; height: 25; color: Theme.divider; opacity: 0.5 }

                        Rectangle {
                            width: 130; height: 32; radius: 6; color: "transparent"; border.color: Theme.cardBorder
                            RowLayout {
                                anchors.centerIn: parent; spacing: 8
                                Rectangle { 
                                    width: 6; height: 6; radius: 3; color: isEngineBusy ? Theme.accentColor : Theme.statusSuccess
                                    SequentialAnimation on opacity { loops: Animation.Infinite; NumberAnimation { from: 1; to: 0.3; duration: 1500 } NumberAnimation { from: 0.3; to: 1; duration: 1500 } }
                                }
                                Text { text: isEngineBusy ? "M.A.N.G.O LIVE" : "SYSTEM IDLE"; color: Theme.textMain; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                            }
                        }
                    }
                }

                // 2. ULTRA-CINEMATIC HERO (ULTIMAVIAJE)
                Item {
                    id: heroBox; Layout.fillWidth: true; Layout.preferredHeight: 380
                    property bool hasGame: statsData.last_game !== null && statsData.last_game !== undefined

                    GlassPanel {
                        anchors.fill: parent; radius: Theme.radiusExtraLarge; glassOpacity: 0.85; borderColor: Theme.cardBorder
                        backgroundColor: "#08080c"
                        
                        content: Item {
                            anchors.fill: parent
                            
                            // Cinematic Extended Art
                            Image {
                                anchors.fill: parent; source: (heroBox.hasGame && statsData.last_game.cover) ? "file:///" + statsData.last_game.cover : ""
                                fillMode: Image.PreserveAspectCrop; asynchronous: true; opacity: status === Image.Ready ? 0.35 : 0
                                Behavior on opacity { NumberAnimation { duration: 800 } }
                            }
                            
                            Rectangle {
                                anchors.fill: parent; radius: Theme.radiusExtraLarge
                                gradient: Gradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop { position: 0.0; color: "#08080c" }
                                    GradientStop { position: 0.4; color: "#08080c" }
                                    GradientStop { position: 1.0; color: "transparent" }
                                }
                            }

                            RowLayout {
                                anchors.fill: parent; spacing: 0
                                
                                ColumnLayout {
                                    Layout.fillWidth: true; Layout.fillHeight: true; Layout.leftMargin: 60; spacing: 10
                                    Layout.alignment: Qt.AlignVCenter
                                    
                                    RowLayout {
                                        spacing: 15
                                        Rectangle {
                                            width: recentLabel.implicitWidth + 16; height: 20; radius: 4; color: Theme.accentColor
                                            Text { id: recentLabel; anchors.centerIn: parent; text: I18n.t.recent_activity; color: Theme.textMain; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1 }
                                        }
                                        Text { text: heroBox.hasGame ? statsData.last_game.platform.toUpperCase() : ""; color: Theme.textAccent; font.pixelSize: 14; font.bold: true; font.letterSpacing: 2 }
                                    }
                                    
                                    Text { 
                                        text: heroBox.hasGame ? statsData.last_game.title : "COLECCIÓN LISTA"
                                        color: Theme.textMain; font.pixelSize: 52; font.bold: true; font.letterSpacing: -2
                                        elide: Text.ElideRight; maximumLineCount: 2; wrapMode: Text.WordWrap; Layout.fillWidth: true
                                        font.weight: Font.Black
                                    }
                                    
                                    Text { 
                                        text: heroBox.hasGame ? I18n.t.hero_subtitle_resume : I18n.t.hero_subtitle_empty
                                        color: Theme.textDim; font.pixelSize: Theme.fontHeader; font.letterSpacing: 2
                                        Layout.fillWidth: true; wrapMode: Text.WordWrap; opacity: 0.8; font.bold: true
                                    }
                                    
                                    Item { Layout.preferredHeight: 30 }
                                    
                                    Button {
                                        id: playHero
                                        Layout.preferredWidth: 280; Layout.preferredHeight: 64
                                        enabled: heroBox.hasGame
                                        contentItem: Text { 
                                            text: I18n.t.resume_mission
                                            color: Theme.textMain; font.bold: true; 
                                            font.pixelSize: 22; font.letterSpacing: 2
                                            horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                                        }
                                        background: Rectangle { 
                                            radius: 12; color: playHero.hovered ? Qt.lighter(Theme.accentColor, 1.1) : Theme.accentColor
                                            opacity: playHero.enabled ? 1.0 : 0.3
                                            Rectangle { anchors.fill: parent; radius: 12; color: "transparent"; border.color: "white"; border.width: 1; opacity: 0.2 }
                                        }
                                        onClicked: if(heroBox.hasGame) launchGame(statsData.last_game.id)
                                        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; acceptedButtons: Qt.NoButton }
                                    }
                                }
                                
                                // Floating Box Art (Overlap Effect)
                                Item {
                                    Layout.preferredWidth: 340; Layout.fillHeight: true
                                    Item {
                                        anchors.centerIn: parent; width: 240; height: 320
                                        rotation: 5
                                        scale: 0.95
                                        
                                        Rectangle {
                                            anchors.fill: parent; radius: 15; color: Theme.surfaceBackground; border.color: Theme.cardBorder; border.width: 1
                                            clip: true
                                            
                                            Text {
                                                anchors.centerIn: parent; text: "🎮"; font.pixelSize: 100; opacity: 0.1
                                                visible: !heroBox.hasGame || !statsData.last_game.cover
                                            }
 
                                            Image {
                                                anchors.fill: parent; source: (heroBox.hasGame && statsData.last_game.cover) ? "file:///" + statsData.last_game.cover : ""
                                                fillMode: Image.PreserveAspectCrop; asynchronous: true
                                            }
                                        }
                                        
                                        // Glow behind car
                                        Rectangle {
                                            anchors.fill: parent; radius: 15; z: -1; color: Theme.accentColor; opacity: 0.15
                                            scale: 1.05
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // 3. RECENT ACTIVITY LIST (HORIZONTAL STYLE)
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 12; visible: statsData.recent_games && statsData.recent_games.length > 1
                    
                    RowLayout {
                        Layout.fillWidth: true; Layout.bottomMargin: 8
                        Text { text: I18n.t.others_recent_titles; color: Theme.textMain; font.pixelSize: Theme.fontHeader; font.bold: true; font.letterSpacing: 2 }
                    }
                    
                    ColumnLayout {
                        Layout.fillWidth: true; spacing: 8
                        Repeater {
                            model: statsData.recent_games ? statsData.recent_games.slice(1, 6) : []
                            delegate: RecentGameCard {
                                gameId: modelData.id
                                title: modelData.title
                                platform: modelData.platform
                                cover: modelData.cover
                                playTime: modelData.playTime
                                onLaunchRequested: (id) => launchGame(id)
                            }
                        }
                    }
                }

                // 4. ACTION TILES (CLEANED)
                RowLayout {
                    Layout.fillWidth: true; spacing: Theme.spaceLarge; Layout.preferredHeight: 110
                    Repeater {
                        model: [
                            { icon: "🎲", label: "DESCUBRIMIENTO", desc: "Lanzar título aleatorio", value: "", action: function(){ mainController.launch_random_game() } }
                        ]
                        delegate: GlassPanel {
                            Layout.fillWidth: true; Layout.fillHeight: true; radius: Theme.radiusLarge; glassOpacity: 0.45; borderColor: Theme.cardBorder
                            content: Item {
                                anchors.fill: parent
                                RowLayout {
                                    anchors.centerIn: parent; spacing: 15
                                    Text { text: modelData.icon; font.pixelSize: 28 }
                                    ColumnLayout {
                                        spacing: 0
                                        Text { text: modelData.value ? modelData.value : modelData.label; color: Theme.textMain; font.pixelSize: 14; font.bold: true }
                                        Text { text: modelData.value ? modelData.label : modelData.desc; color: Theme.textMuted; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                                    }
                                }
                                MouseArea { anchors.fill: parent; enabled: modelData.action !== null; cursorShape: Qt.PointingHandCursor; onClicked: if(modelData.action) modelData.action(); preventStealing: false; propagateComposedEvents: true }
                            }
                        }
                    }
                }
                
                Item { Layout.preferredHeight: 60 } // Bottom Padding
            }
        }
    }
}
