import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Models 1.0
import EmuManager.Controllers 1.0
import "../components"

Item {
    id: dashboardRoot
    objectName: "dashboardView"

    property var statsData: ({})
    property int totalGames: 0

    Connections { 
        target: mainController
        function onScanProgressChanged(p) { 
            mangoMonitor.scanProgressVal = p
            mangoMonitor.isEngineBusy = (p > 0 && p < 1.0)
        }
        function onScanStatusChanged(s) { 
            mangoMonitor.engineStatusText = I18n.tp(s).toUpperCase()
        }
        function onGamesUpdated() {
            dashboardRoot.refreshAll()
        }
    }
    
    ListModel { id: consoleModel }

    function refreshAll() {
        consoleModel.clear()
        if (!mainController) return;
        
        // Cargar Consolas
        var summary = mainController.get_consoles_summary()
        for (var i = 0; i < summary.length; i++) {
            consoleModel.append(summary[i])
        }

        // Cargar Stats Dashboard
        statsData = mainController.get_dashboard_stats()
        totalGames = statsData.total_games || 0
    }

    Component.onCompleted: {
        refreshAll()
    }

    // --- GRADIENTE DE FONDO PROFUNDO ---
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0a0a0c" }
            GradientStop { position: 1.0; color: "#050510" }
        }
    }

    // --- VIEW SWITCHER ---
    StackLayout {
        anchors.fill: parent
        currentIndex: totalGames > 0 ? 1 : 0
        
        // --- 1. EMPTY STATE ---
        ColumnLayout {
            // (Se mantiene tu diseño de splash premium para bibliotecas vacías)
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 35
            Item { Layout.fillHeight: true }
            Item {
                Layout.alignment: Qt.AlignCenter; width: 240; height: 240
                Rectangle {
                    anchors.centerIn: parent; width: 180; height: 180; radius: 90
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: Qt.rgba(0.086, 0.627, 0.522, 0.15) }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }
                Text {
                    text: "🛰️"; font.pixelSize: 100; anchors.centerIn: parent; opacity: 0.9
                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        NumberAnimation { from: 1; to: 1.15; duration: 3000; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.15; to: 1; duration: 3000; easing.type: Easing.InOutSine }
                    }
                }
            }
            ColumnLayout {
                Layout.alignment: Qt.AlignCenter; Layout.preferredWidth: parent.width * 0.8; spacing: 12
                Text { text: I18n.t.empty_library; color: "white"; font.pixelSize: 26; font.bold: true; font.letterSpacing: 4; horizontalAlignment: Text.AlignHCenter }
                Text { text: I18n.t.empty_library_desc; color: "#88ffffff"; font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter; lineHeight: 1.5; opacity: 0.7 }
            }
            Button { text: I18n.t.configure_paths_btn; Layout.alignment: Qt.AlignCenter; Layout.preferredHeight: 52; Layout.preferredWidth: 280; Material.background: "#16a085"; onClicked: activeViewId = "settingsView"; font.bold: true }
            Item { Layout.fillHeight: true }
        }

        // --- 2. ACTIVE DASHBOARD (EL NUEVO DISEÑO WOW) ---
        Flickable {
            id: mainFlickable
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: width
            contentHeight: mainLayout.implicitHeight + 80 // Margen inferior
            clip: true
            
            // --- NAVEGACIÓN TÁCTIL (KINETIC) ---
            boundsBehavior: Flickable.DragAndOvershootBounds
            interactive: true
            flickableDirection: Flickable.VerticalFlick
            pressDelay: 100

            ColumnLayout {
                id: mainLayout
                width: parent.width
                spacing: 40
                
                // --- HEADER PREMIUM CON LOGO ---
                RowLayout {
                    Layout.fillWidth: true; Layout.margins: 40; spacing: 25
                    
                    // Logo con resplandor suave
                    Item {
                        width: 80; height: 80
                        Image {
                            anchors.fill: parent; source: "../assets/logo.svg"; fillMode: Image.PreserveAspectFit
                            layer.enabled: true
                        }
                    }

                    ColumnLayout {
                        spacing: 0
                        Text { 
                            text: "EmuManager"
                            color: "white"; font.pixelSize: 42; font.bold: true; font.letterSpacing: -1
                        }
                        Text { 
                            text: I18n.t.command_center
                            color: "#16a085"; font.pixelSize: 12; font.bold: true; font.letterSpacing: 6 
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    ColumnLayout {
                        Layout.alignment: Qt.AlignRight
                        Text { text: new Date().toLocaleDateString(Qt.locale(), "dd/MM/yyyy"); color: "white"; font.pixelSize: 14; opacity: 0.6 }
                        Text { text: I18n.t.operational; color: "#16a085"; font.pixelSize: 10; font.bold: true; Layout.alignment: Qt.AlignRight }
                    }
                }

                // --- HERO SECTION: ÚLTIMA MISIÓN --- (Solo visible si hay un juego reciente)
                Rectangle {
                    visible: statsData.last_game !== null && statsData.last_game !== undefined
                    Layout.fillWidth: true; Layout.preferredHeight: 320; Layout.margins: 40
                    radius: 30; clip: true; color: "#0a0a0c"; border.color: "#1a1a1f"
                    
                    // Imagen de fondo con Desenfoque
                    Image {
                        anchors.fill: parent; opacity: 0.15; fillMode: Image.PreserveAspectCrop
                        source: statsData.last_game ? "file://" + statsData.last_game.cover : ""
                    }
                    
                    Rectangle {
                        anchors.fill: parent
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "#0c0c0f" }
                            GradientStop { position: 0.7; color: "transparent" }
                        }
                    }

                    RowLayout {
                        anchors.fill: parent; anchors.margins: 40; spacing: 40
                        
                        // Carátula Relevante
                        Rectangle {
                            width: 160; height: 240; radius: 15; clip: true; color: "#050505"
                            Image { anchors.fill: parent; source: statsData.last_game ? "file://" + statsData.last_game.cover : ""; fillMode: Image.PreserveAspectCrop }
                            Rectangle { anchors.fill: parent; radius: 15; border.color: "#33ffffff"; border.width: 1; color: "transparent" }
                        }
                        
                        ColumnLayout {
                            spacing: 12
                            Text { text: I18n.t.next_challenge; color: "#f39c12"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 3 }
                            Text { 
                                text: statsData.last_game ? statsData.last_game.title : ""
                                color: "white"; font.pixelSize: 42; font.bold: true; font.letterSpacing: -1
                                elide: Text.ElideRight; Layout.preferredWidth: 400
                            }
                            Text { 
                                text: I18n.t.platform_prefix + (statsData.last_game ? statsData.last_game.platform : "N/A")
                                color: "#88ffffff"; font.pixelSize: 14; font.bold: true 
                            }
                            
                            Item { Layout.preferredHeight: 20 }
                            
                            Button {
                                text: I18n.t.resume_mission
                                Layout.preferredHeight: 52; Layout.preferredWidth: 220; Material.background: "#f39c12"
                                font.bold: true; font.pixelSize: 14
                                onClicked: mainController.launch_game_by_id(statsData.last_game.id)
                            }
                        }
                    }
                }

                // --- GRID DE ESTADÍSTICAS AVANZADAS ---
                Flow {
                    Layout.fillWidth: true; Layout.margins: 40; spacing: 25
                    
                    DashboardStatCard {
                        width: 280; label: I18n.t.stats_total_games; value: totalGames; subLabel: ""; icon: "📦"; accentColor: "#16a085"
                    }
                    
                    // Stats 2: Tiempo de Misión
                    DashboardStatCard {
                        width: 280; label: I18n.t.stats_play_time; value: statsData.total_play_time; subLabel: ""; icon: "⏳"; accentColor: "#9d50bb"
                    }

                    // Stats 3: Sistema Host
                    DashboardStatCard {
                        width: 280; label: I18n.t.stats_most_played; value: statsData.most_played_system; subLabel: ""; icon: "🛡️"; accentColor: "#3a7bd5"
                    }

                    // Stats 4: Monitor M.A.N.G.O (Integrado)
                    Rectangle {
                        id: mangoMonitor
                        width: 450; height: 160; radius: 24; color: "#0d0d12"; border.color: "#1a1a1f"
                        property bool isEngineBusy: false
                        property string engineStatusText: I18n.t.idle
                        property real scanProgressVal: 0.0

                        ColumnLayout {
                            anchors.fill: parent; anchors.margins: 25; spacing: 5
                            RowLayout {
                                Text { text: I18n.t.mango_monitor; color: "#f39c12"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
                                Item { Layout.fillWidth: true }
                                Text { text: "🥭 MOTOR NATIVO"; color: "#22ffffff"; font.pixelSize: 8; font.bold: true }
                            }
                            Item { Layout.fillHeight: true }
                            RowLayout {
                                spacing: 15
                                Rectangle { 
                                    width: 8; height: 8; radius: 4; color: mangoMonitor.isEngineBusy ? "#f39c12" : "#16a085"
                                    SequentialAnimation on opacity { 
                                        loops: Animation.Infinite
                                        running: mangoMonitor.isEngineBusy
                                        NumberAnimation { from: 1; to: 0.3; duration: 600 }
                                        NumberAnimation { from: 0.3; to: 1; duration: 600 }
                                    }
                                }
                                Text { text: mangoMonitor.isEngineBusy ? I18n.t.processing_caps : I18n.t.running_caps; color: "white"; font.pixelSize: 16; font.bold: true; font.letterSpacing: 1 }
                            }
                            Text { text: I18n.t.status_prefix + mangoMonitor.engineStatusText; color: "#66ffffff"; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
                            ProgressBar { Layout.fillWidth: true; height: 3; value: mangoMonitor.scanProgressVal; visible: mangoMonitor.isEngineBusy; Material.accent: "#f39c12" }
                        }
                    }
                }

                // --- ACCESO RÁPIDO A ESCUADRONES (CONSOLAS) ---
                ColumnLayout {
                    Layout.fillWidth: true; Layout.margins: 40; spacing: 20
                    Text { text: I18n.t.explore.toUpperCase(); color: "white"; font.pixelSize: 16; font.bold: true; font.letterSpacing: 3; opacity: 0.7 }
                    
                    ListView {
                        id: recentConsoles
                        Layout.fillWidth: true; Layout.preferredHeight: 180; orientation: ListView.Horizontal; spacing: 20; clip: true
                        model: consoleModel
                        delegate: ConsoleCard {
                            title: model.title; fullName: model.fullName; iconEmoji: model.iconEmoji; accentColor: model.accentColor
                            gameCount: model.gameCount; playTime: model.playTime; minimalMode: true
                            onClicked: { activeViewId = "libraryView" }
                        }
                    }
                }
                
                Item { Layout.preferredHeight: 40 }
            }
            
            ScrollBar.vertical: ScrollBar { 
                policy: ScrollBar.AsNeeded
                active: mainFlickable.moving || mainFlickable.flicking
            }
        }
    }
}
