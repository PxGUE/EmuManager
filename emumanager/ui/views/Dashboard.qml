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
        }
    }
    
    // Referencia para compatibilidad local
    property QtObject mainCtrl: mainController

    property int totalGames: 0
    function updateStats() {
        totalGames = mainCtrl ? mainCtrl.get_games_count() : 0
    }

    Component.onCompleted: updateStats()

    Item {
        anchors.fill: parent
        anchors.margins: 40

        ColumnLayout {
            anchors.fill: parent
            spacing: 30

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
                        Text { text: "0h de juego totales registrados."; color: "#66ffffff"; font.pixelSize: 10 }
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

            // --- CONSOLE CAROUSEL PLACEHOLDER ---
            ColumnLayout {
                Layout.fillHeight: true; Layout.fillWidth: true; spacing: 15
                Text { text: "TUS CONSOLAS"; color: "white"; font.pixelSize: 14; font.bold: true; font.letterSpacing: 3; opacity: 0.8 }
                Item { Layout.fillHeight: true }
            }
        }
    }
}
