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

    // --- MANGO ENGINE STATE ---
    property bool isEngineBusy: false
    property string engineStatusText: I18n.t.idle
    property real scanProgress: 0.0

    Connections { 
        target: mainController
        function onScanProgressChanged(p) { 
            dashboardRoot.scanProgress = p
            dashboardRoot.isEngineBusy = (p > 0 && p < 1.0)
        }
        function onScanStatusChanged(s) { 
            dashboardRoot.engineStatusText = I18n.tp(s).toUpperCase()
        }
        function onGamesUpdated() {
            dashboardRoot.refreshAll()
        }
    }
    function refreshAll() {
        if (!mainController) return;

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
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 35
                
                // Icono Satélite Animado
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

                // Textos
                ColumnLayout {
                    Layout.alignment: Qt.AlignCenter; spacing: 12
                    Text { text: I18n.t.empty_library; color: "white"; font.pixelSize: 26; font.bold: true; font.letterSpacing: 4; horizontalAlignment: Text.AlignHCenter }
                    Text { text: I18n.t.empty_library_desc; color: "#88ffffff"; font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter; lineHeight: 1.5; opacity: 0.7 }
                }

                Button { 
                    text: I18n.t.configure_paths_btn
                    Layout.alignment: Qt.AlignCenter; Layout.preferredHeight: 52; Layout.preferredWidth: 280
                    Material.background: "#16a085"; onClicked: activeViewId = "settingsView"; font.bold: true 
                }
            }
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
                    
                    // --- MANGO ENGINE PILOT STATUS (NEW SUBTLE DESIGN) ---
                    Rectangle {
                        id: enginePill
                        Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        width: 200; height: 48; radius: 24; color: "#0d0d12"; border.color: "#1a1a1f"
                        
                        RowLayout {
                            anchors.fill: parent; anchors.leftMargin: 20; anchors.rightMargin: 10; spacing: 12
                            
                            // Indicador de Pulso
                            Rectangle {
                                id: pulseDot
                                width: 10; height: 10; radius: 5
                                color: dashboardRoot.isEngineBusy ? "#f39c12" : "#16a085"
                                
                                SequentialAnimation {
                                    running: true; loops: Animation.Infinite
                                    NumberAnimation { target: pulseDot; property: "opacity"; from: 1; to: 0.3; duration: 800; easing.type: Easing.InOutSine }
                                    NumberAnimation { target: pulseDot; property: "opacity"; from: 0.3; to: 1; duration: 800; easing.type: Easing.InOutSine }
                                }
                                layer.enabled: true
                            }

                            ColumnLayout {
                                spacing: 1
                                Text { 
                                    text: "M.A.N.G.O"
                                    color: "white"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2
                                }
                                Text { 
                                    text: dashboardRoot.isEngineBusy ? (Math.round(dashboardRoot.scanProgress * 100) + "%") : I18n.t.operational.toUpperCase()
                                    color: dashboardRoot.isEngineBusy ? "#f39c12" : "#16a085"
                                    font.pixelSize: 9; font.bold: true; font.letterSpacing: 1
                                }
                            }
                            
                            Item { Layout.fillWidth: true }
                            
                            // Icono o Logo pequeño de Motor
                            Text { 
                                text: "🥭"
                                font.pixelSize: 16
                                opacity: dashboardRoot.isEngineBusy ? 1 : 0.3
                                Behavior on opacity { NumberAnimation { duration: 300 } }
                            }
                        }
                        
                        ToolTip {
                            visible: engineMouse.containsMouse
                            text: I18n.tp("engine_tool_tip|" + dashboardRoot.engineStatusText)
                            delay: 500
                        }
                        
                        MouseArea {
                            id: engineMouse
                            anchors.fill: parent; hoverEnabled: true
                        }
                    }
                    
                    ColumnLayout {
                        Layout.alignment: Qt.AlignRight
                        Text { text: new Date().toLocaleDateString(Qt.locale(), "dd/MM/yyyy"); color: "white"; font.pixelSize: 14; opacity: 0.4 }
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

                    // Stats 4: Favoritos
                    DashboardStatCard {
                        width: 280; label: I18n.t.stats_favorites; value: statsData.total_favorites; subLabel: ""; icon: "❤️"; accentColor: "#e74c3c"
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
