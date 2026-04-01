import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import QtQuick.Effects
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
    property string engineStatusKey: "status_system_idle"
    property alias isScanning: mainController.isScanning
    property alias isScraping: mainController.isScraping
    property alias isEngineBusy: mainController.isEngineBusy
    property alias scanProgress: mainController.scanProgress

    function launchGame(id) { mainController ? mainController.launch_game_by_id(id) : null }

    Connections { 
        target: mainController
        function onStartupProgressChanged(p) { if (p > 0 && p < 1.0) dashboardRoot.engineStatusKey = "initializing" }
        function onStartupStatusChanged(s) { dashboardRoot.engineStatusKey = s }
        function onStartupFinished() { 
            dashboardRoot.engineStatusKey = "status_system_idle"
            dashboardRoot.refreshAll() 
        }
        function onScanStatusChanged(s) { dashboardRoot.engineStatusKey = s }
        function onScanFinished(n) { dashboardRoot.engineStatusKey = "status_system_idle" }
        function onScrapeStatusChanged(s) { dashboardRoot.engineStatusKey = s }
        function onScrapeFinished(n) { dashboardRoot.engineStatusKey = "status_system_idle" }
        function onCoreDownloadStatusChanged(id, s) { dashboardRoot.engineStatusKey = s }
        function onCoreDownloadFinished(id, p) { dashboardRoot.engineStatusKey = "status_system_idle" }
        function onGamesUpdated() { dashboardRoot.refreshAll() }
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
                GradientStop { position: 1.0; color: Theme.transparent }
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

                // 1. FLAGSHIP COMMAND HUD (MONUMENTAL VERSION)
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: 100; spacing: 50
                    
                    // --- THE REACTOR LOGO (Protagonista Gigante) ---
                    RowLayout {
                        spacing: 25
                        Item {
                            width: 64; height: 64
                            
                            // 1. Halo base Cian
                            Rectangle {
                                anchors.centerIn: parent; width: 58; height: 58; radius: 29
                                color: Theme.transparent; border.color: Theme.accentElectric; border.width: 2; opacity: 0.3
                            }
                            
                            // 2. Cuadrado Orbital Giratorio
                            Rectangle {
                                anchors.centerIn: parent; width: 62; height: 62; radius: 14
                                color: Theme.transparent; border.color: Theme.accentElectric; border.width: 2; opacity: 0.2
                                RotationAnimation on rotation { from: 0; to: 360; duration: 9000; loops: Animation.Infinite }
                            }
                            
                            // 3. Glow Central
                            Rectangle {
                                anchors.centerIn: parent; width: 40; height: 40; radius: 20
                                color: Theme.accentElectric; opacity: 0.1
                                SequentialAnimation on opacity { loops: Animation.Infinite; NumberAnimation { from: 0.05; to: 0.2; duration: 2500; easing.type: Easing.InOutSine } NumberAnimation { from: 0.2; to: 0.05; duration: 2500; easing.type: Easing.InOutSine } }
                            }

                            Image { source: "../assets/logo.svg"; anchors.fill: parent; anchors.margins: 8; fillMode: Image.PreserveAspectFit; smooth: true }
                        }
                        
                        ColumnLayout {
                            spacing: 2 // Espacio positivo para que respire
                            Text { 
                                text: I18n.t.app_name; color: Theme.textMain; 
                                font.pixelSize: 42; font.weight: Font.Black; font.letterSpacing: -1.5 
                            }
                                text: I18n.tp("app_version_label|" + mainController.appVersion); color: Theme.accentElectric; 
                                font.pixelSize: 12; font.bold: true; font.letterSpacing: 5; opacity: 0.9 
                            }
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    // --- KINETIC STATS HUD ---
                    RowLayout {
                        spacing: 16; Layout.alignment: Qt.AlignVCenter
                        
                        // Collection Pod
                        Rectangle {
                            width: 130; height: 50; radius: 14; color: Theme.backgroundPod; border.color: Qt.alpha(Theme.accentElectric, 0.15); border.width: 1
                            ColumnLayout {
                                anchors.centerIn: parent; spacing: -2
                                Text { text: I18n.t.stats_total_games; color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1; Layout.alignment: Qt.AlignCenter }
                                Text { text: totalGames + " " + I18n.t.games_abbr; color: Theme.textMain; font.pixelSize: 18; font.bold: true; Layout.alignment: Qt.AlignCenter }
                            }
                        }
                        
                        // Time Pod
                        Rectangle {
                            width: 130; height: 50; radius: 14; color: Theme.backgroundPod; border.color: Qt.alpha(Theme.accentElectric, 0.15); border.width: 1
                            ColumnLayout {
                                anchors.centerIn: parent; spacing: -2
                                Text { text: I18n.t.stats_play_time; color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1; Layout.alignment: Qt.AlignCenter }
                                Text { text: statsData.total_play_time || "0h 0m"; color: Theme.textMain; font.pixelSize: 18; font.bold: true; Layout.alignment: Qt.AlignCenter }
                            }
                        }

                        // --- SUBTLE STATUS HUD ---
                        Rectangle {
                            id: statusSubtle
                            width: 180; height: 50; radius: 14; 
                            color: Theme.backgroundPod
                            border.color: isEngineBusy ? Qt.alpha(Theme.accentElectric, 0.4) : Qt.alpha(Theme.accentElectric, 0.15)
                            border.width: 1
                            
                            RowLayout {
                                anchors.fill: parent; anchors.leftMargin: 15; anchors.rightMargin: 15; spacing: 12
                                
                                // Discrete Status Dot
                                Rectangle {
                                    width: 8; height: 8; radius: 4; 
                                    color: Theme.accentElectric
                                    opacity: isEngineBusy ? 1.0 : 0.3
                                    
                                    SequentialAnimation on opacity {
                                        running: isEngineBusy; loops: Animation.Infinite
                                        NumberAnimation { from: 1.0; to: 0.2; duration: 1200; easing.type: Easing.InOutSine }
                                        NumberAnimation { from: 0.2; to: 1.0; duration: 1200; easing.type: Easing.InOutSine }
                                    }

                                    // Subtle Glow
                                    Rectangle {
                                        anchors.centerIn: parent; width: parent.width * 2.5; height: width; radius: width/2
                                        color: Theme.accentElectric; opacity: isEngineBusy ? 0.2 : 0.0
                                    }
                                }
                                
                                ColumnLayout {
                                    spacing: -2; Layout.fillWidth: true
                                    Text { 
                                        text: I18n.t.engine_name || "M.A.N.G.O"; 
                                        color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1; Layout.alignment: Qt.AlignLeft 
                                    }
                                    Text { 
                                        text: (I18n.tp(engineStatusKey)).toUpperCase(); 
                                        color: Theme.textMain; 
                                        font.pixelSize: 10; font.bold: true; font.letterSpacing: 1
                                        elide: Text.ElideRight; Layout.fillWidth: true
                                    }
                                }
                            }

                            // Thin Progress Line (only when busy)
                            Rectangle {
                                anchors.bottom: parent.bottom; anchors.bottomMargin: 4; anchors.horizontalCenter: parent.horizontalCenter
                                width: parent.width - 30; height: 2; radius: 1; color: Theme.accentElectric; opacity: isEngineBusy ? 0.5 : 0.0
                                visible: isEngineBusy
                            }
                        }
                    }
                }

                // 2. ULTRA-CINEMATIC HERO (ULTIMAVIAJE) - FULL WIDTH DESIGN
                Item {
                    id: heroBox
                    Layout.fillWidth: true
                    Layout.preferredHeight: 400
                    Layout.leftMargin: -45 // Neutralizamos el margen del ColumnLayout para ir de lado a lado
                    Layout.rightMargin: -45
                    
                    property bool hasGame: statsData.last_game !== null && statsData.last_game !== undefined
                    readonly property color heroAccent: hasGame ? Theme.colorForPlatform(statsData.last_game.platform) : Theme.accentColor

                    // --- FONDO CINEMÁTICO EXTENDIDO ---
                    Rectangle {
                        anchors.fill: parent
                        color: Theme.backgroundVoid // Fondo base ultra oscuro
                        
                        // Imagen de Fondo con Fade lateral
                        Image {
                            anchors.fill: parent
                            source: (heroBox.hasGame && statsData.last_game.cover) ? "file:///" + statsData.last_game.cover : ""
                            fillMode: Image.PreserveAspectCrop; asynchronous: true; opacity: 0.3
                            visible: heroBox.hasGame
                        }
                        
                        // Gradiente de Desvanecimiento Lateral (Side Fades)
                        Rectangle {
                            anchors.fill: parent
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0.0; color: Theme.viewBackground }
                                GradientStop { position: 0.15; color: Theme.transparent }
                                GradientStop { position: 0.85; color: Theme.transparent }
                                GradientStop { position: 1.0; color: Theme.viewBackground }
                            }
                        }
                        
                        // Gradiente de Desvanecimiento Central (Para legibilidad de texto)
                        Rectangle {
                            anchors.fill: parent
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0.0; color: Theme.overlayBackground }
                                GradientStop { position: 0.45; color: Theme.overlayBackground }
                                GradientStop { position: 0.8; color: Theme.transparent }
                            }
                        }

                        // Línea de Identidad Dinámica (Subrayado Premium)
                        Rectangle {
                            anchors.bottom: parent.bottom; width: parent.width; height: 3
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0.0; color: Theme.transparent }
                                GradientStop { position: 0.5; color: heroBox.heroAccent }
                                GradientStop { position: 1.0; color: Theme.transparent }
                            }
                            opacity: 0.6
                        }
                    }

                    // --- CONTENIDO REAL (Alineado con el dashboard) ---
                    Item {
                        anchors.fill: parent
                        anchors.leftMargin: 45; anchors.rightMargin: 45 // Devolvemos el margen interno
                        
                        RowLayout {
                            anchors.fill: parent; spacing: 0
                            
                            ColumnLayout {
                                Layout.fillWidth: true; Layout.fillHeight: true; Layout.leftMargin: 15; spacing: 12
                                Layout.alignment: Qt.AlignVCenter
                                
                                RowLayout {
                                    spacing: 15
                                    Rectangle {
                                        width: recentLabel.implicitWidth + 16; height: 20; radius: 4; color: heroBox.heroAccent
                                        Text { id: recentLabel; anchors.centerIn: parent; text: I18n.t.recent_activity; color: Theme.white; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1 }
                                    }
                                    Text { text: heroBox.hasGame ? statsData.last_game.platform.toUpperCase() : ""; color: heroBox.heroAccent; font.pixelSize: 14; font.bold: true; font.letterSpacing: 2 }
                                }
                                
                                Text { 
                                    text: heroBox.hasGame ? (statsData.last_game.display_name || statsData.last_game.displayName || statsData.last_game.title) : "COLECCIÓN LISTA"
                                    color: Theme.white; font.pixelSize: 48; font.bold: true; font.letterSpacing: -1
                                    elide: Text.ElideRight; maximumLineCount: 2; wrapMode: Text.WordWrap; Layout.fillWidth: true
                                }
                                
                                Text { 
                                    text: heroBox.hasGame ? I18n.t.hero_subtitle_resume : I18n.t.hero_subtitle_empty
                                    color: Theme.textDim; font.pixelSize: 16; font.letterSpacing: 1
                                    Layout.fillWidth: true; wrapMode: Text.WordWrap; opacity: 0.8
                                }
                                
                                Item { Layout.preferredHeight: 20 }
                                
                                Button {
                                    id: playHero
                                    Layout.preferredWidth: 260; Layout.preferredHeight: 56
                                    enabled: heroBox.hasGame
                                    contentItem: Text { 
                                        text: I18n.t.resume_mission
                                        color: Theme.white; font.bold: true; 
                                        font.pixelSize: 18; font.letterSpacing: 2
                                        horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                                    }
                                    background: Rectangle { 
                                        radius: 12; color: playHero.hovered ? Qt.lighter(heroBox.heroAccent, 1.1) : heroBox.heroAccent
                                        opacity: playHero.enabled ? 1.0 : 0.3
                                        Rectangle { anchors.fill: parent; radius: 12; color: Theme.transparent; border.color: Theme.white; border.width: 1; opacity: 0.2 }
                                    }
                                    onClicked: if(heroBox.hasGame) launchGame(statsData.last_game.id)
                                }
                            }
                            
                            // Floating Box Art (Alineado a la derecha)
                            Item {
                                Layout.preferredWidth: 340; Layout.fillHeight: true
                                Item {
                                    anchors.centerIn: parent; width: 220; height: 300
                                    rotation: 5
                                    Rectangle {
                                        anchors.fill: parent; radius: 12; color: Theme.surfaceBackground; border.color: Theme.cardBorder; border.width: 1; clip: true
                                        Image {
                                            anchors.fill: parent; source: (heroBox.hasGame && statsData.last_game.cover) ? "file:///" + statsData.last_game.cover : ""
                                            fillMode: Image.PreserveAspectCrop; asynchronous: true
                                        }
                                    }
                                    Rectangle {
                                        anchors.fill: parent; radius: 12; z: -1; color: heroBox.heroAccent; opacity: 0.15; scale: 1.05
                                    }
                                }
                            }
                        }
                    }
                }

                // 3. RECENT ACTIVITY LIST (HORIZONTAL STYLE)
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 12; visible: statsData.recent_games && statsData.recent_games.length > 0
                    
                    RowLayout {
                        Layout.fillWidth: true; Layout.bottomMargin: 8
                        Text { text: I18n.t.others_recent_titles; color: Theme.textMain; font.pixelSize: Theme.fontHeader; font.bold: true; font.letterSpacing: 2 }
                    }
                    
                    ColumnLayout {
                        Layout.fillWidth: true; spacing: 8
                        Repeater {
                            model: statsData.recent_games || []
                            delegate: RecentGameCard {
                        gameId: modelData.id
                        title: modelData.display_name || modelData.displayName || modelData.title
                        platform: modelData.platform
                                cover: modelData.cover
                                playTime: modelData.playTime
                                onLaunchRequested: (id) => launchGame(id)
                                onDetailsRequested: (id) => window.openGameDetails(id)
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
