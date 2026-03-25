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

    Connections { 
        target: mainController
        function onScanProgressChanged(p) { 
            mangoMonitor.scanProgressVal = p
            mangoMonitor.isEngineBusy = (p > 0 && p < 1.0)
        }
        function onScanStatusChanged(s) { 
            mangoMonitor.engineStatusText = s.toUpperCase()
        }
        function onGamesUpdated() {
            // Refrescar el contador de juegos cuando la DB cambie
            dashboardRoot.updateStats()
            dashboardRoot.refreshConsoles()
        }
    }
    
    // Referencia para compatibilidad local
    property QtObject mainCtrl: mainController

    property int totalGames: 0
    function updateStats() {
        totalGames = mainCtrl ? mainCtrl.get_games_count() : 0
    }

    ListModel { id: consoleModel }

    function refreshConsoles() {
        consoleModel.clear()
        if (!mainController) return;
        var summary = mainController.get_consoles_summary()
        for (var i = 0; i < summary.length; i++) {
            consoleModel.append(summary[i])
        }
    }

    Component.onCompleted: {
        updateStats()
        refreshConsoles()
    }

    // --- VIEW SWITCHER ---
    StackLayout {
        anchors.fill: parent
        currentIndex: totalGames > 0 ? 1 : 0
        
        // --- 1. EMPTY STATE (THE "SPLASH" THE USER IS LOOKING FOR) ---
        ColumnLayout {
            Layout.fillWidth: true; Layout.fillHeight: true
            spacing: 35
            
            Item { Layout.fillHeight: true }
            
            // Icono Animado / Splash con Glow
            Item {
                Layout.alignment: Qt.AlignCenter
                width: 240; height: 240
                
                // Resplandor Ambiental
                Rectangle {
                    anchors.centerIn: parent
                    width: 180; height: 180; radius: 90
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: Qt.rgba(0.086, 0.627, 0.522, 0.15) } // #16a085 con opacidad
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }
                
                Text {
                    text: "🛰️"
                    font.pixelSize: 100; anchors.centerIn: parent
                    opacity: 0.9
                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        NumberAnimation { from: 1; to: 1.15; duration: 3000; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.15; to: 1; duration: 3000; easing.type: Easing.InOutSine }
                    }
                }
            }
            
            ColumnLayout {
                Layout.alignment: Qt.AlignCenter
                Layout.preferredWidth: parent.width * 0.8
                spacing: 12
                
                Text {
                    Layout.fillWidth: true
                    text: "SISTEMA INICIALIZADO. SIN DATOS."; color: "white"
                    font.pixelSize: 26; font.bold: true; font.letterSpacing: 4
                    horizontalAlignment: Text.AlignHCenter 
                }
                Text {
                    Layout.fillWidth: true
                    text: "Bienvenido, Comandante. El catálogo está actualmente vacío.\nConfigura tus rutas de escaneo para iniciar la misión."; color: "#88ffffff"
                    font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter
                    lineHeight: 1.5; opacity: 0.7
                }
            }

            Item { Layout.preferredHeight: 15 }
            
            Button {
                text: "CONFIGURAR BIBLIOTECA"
                Layout.alignment: Qt.AlignCenter; Layout.preferredHeight: 52; Layout.preferredWidth: 280
                Material.background: "#16a085"; Material.foreground: "white"
                font.bold: true; font.letterSpacing: 2
                onClicked: activeViewId = "settingsView"
                
                Rectangle {
                    anchors.fill: parent; radius: 4; color: "white"; opacity: parent.hovered ? 0.05 : 0
                    Behavior on opacity { NumberAnimation { duration: 150 } }
                }
            }
            
            Item { Layout.fillHeight: true }
        }

        // --- 2. ACTIVE DASHBOARD ---
        Item {
            Item {
                anchors.fill: parent; anchors.margins: 40
                ColumnLayout {
                    anchors.fill: parent; spacing: 30

                    // --- HEADER ---
                    ColumnLayout {
                        spacing: 5
                        Text { text: "BIENVENIDO, COMANDANTE"; color: "white"; font.pixelSize: 28; font.bold: true; font.letterSpacing: 2 }
                        Text { text: "M.A.N.G.O Engine reportando: Todo el hardware operativo."; color: "#66ffffff"; font.pixelSize: 12; font.bold: true; font.letterSpacing: 1 }
                    }

                    // --- WIDGET GRID ---
                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        columnSpacing: 25
                        rowSpacing: 25

                        // Card 1: ESTADÍSTICAS RÁPIDAS
                        Rectangle {
                            Layout.fillWidth: true; Layout.preferredHeight: 180; radius: 24; color: "#0a0a0c"; border.color: "#1a1a1f"
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 25; spacing: 5
                                Text { text: "VISTA RÁPIDA"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
                                Text { text: "CATÁLOGO TOTAL"; color: "#44ffffff"; font.pixelSize: 11; font.bold: true }
                                Text { text: dashboardRoot.totalGames + " JUEGOS"; color: "white"; font.pixelSize: 32; font.bold: true }
                                Item { Layout.fillHeight: true }
                                Text { text: "Estadísticas actualizadas en tiempo real."; color: "#66ffffff"; font.pixelSize: 10 }
                            }
                        }

                        // Card 2: M.A.N.G.O MONITOR
                        Rectangle {
                            id: mangoMonitor
                            Layout.fillWidth: true; Layout.preferredHeight: 180; radius: 24; color: "#0a0a0c"; border.color: "#1a1a1f"
                            
                            property bool isEngineBusy: false
                            property string engineStatusText: "REPOSO"
                            property real scanProgressVal: 0.0

                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 25; spacing: 5
                                RowLayout {
                                    Text { text: "MOTOR M.A.N.G.O"; color: "#f39c12"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
                                    Item { Layout.fillWidth: true }
                                    Text { text: "🥭 v0.1.4-RUST core"; color: "#22ffffff"; font.pixelSize: 8; font.bold: true }
                                }
                                
                                Item { Layout.fillHeight: true }
                                
                                RowLayout {
                                    spacing: 15
                                    Rectangle { 
                                        width: 8; height: 8; radius: 4; color: mangoMonitor.isEngineBusy ? "#f39c12" : "#16a085"
                                        opacity: 1.0
                                        SequentialAnimation on opacity {
                                            loops: Animation.Infinite; running: mangoMonitor.isEngineBusy
                                            NumberAnimation { from: 1; to: 0.3; duration: 600 }
                                            NumberAnimation { from: 0.3; to: 1; duration: 600 }
                                        }
                                    }
                                    Text { 
                                        text: mangoMonitor.isEngineBusy ? "PROCESANDO" : "EJECUTANDO"
                                        color: "white"; font.pixelSize: 16; font.bold: true; font.letterSpacing: 1 
                                    }
                                }
                                
                                Text {
                                    id: statusTxt
                                    text: "ESTADO: " + mangoMonitor.engineStatusText
                                    color: "#66ffffff"; font.pixelSize: 11; Layout.fillWidth: true; wrapMode: Text.WordWrap; elide: Text.ElideRight
                                }

                                ProgressBar {
                                    Layout.fillWidth: true; height: 2; value: mangoMonitor.scanProgressVal
                                    visible: mangoMonitor.isEngineBusy; Material.accent: "#f39c12"
                                }
                            }
                        }
                    }

                    // --- CONSOLE QUICK VIEW ---
                    ColumnLayout {
                        Layout.fillHeight: true; Layout.fillWidth: true; spacing: 15
                        Text { text: "ACCESO RÁPIDO"; color: "white"; font.pixelSize: 14; font.bold: true; font.letterSpacing: 3; opacity: 0.8 }
                        
                        ListView {
                            id: recentConsoles
                            Layout.fillHeight: true; Layout.fillWidth: true
                            orientation: ListView.Horizontal; spacing: 20; clip: true
                            model: consoleModel
                            delegate: ConsoleCard {
                                title: model.title; fullName: model.fullName; iconEmoji: model.iconEmoji; accentColor: model.accentColor
                                gameCount: model.gameCount; playTime: model.playTime; minimalMode: true
                                onClicked: {
                                    activeViewId = "libraryView"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
