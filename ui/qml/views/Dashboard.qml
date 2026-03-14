import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects
import "../components"

Item {
    id: dashboardRoot
    
    property bool isEmpty: bridge ? (bridge.dashboardStats.installed === 0 && bridge.dashboardStats.totalRoms === 0) : true
    property color currentAccentColor: "#4da6ff"

    Component.onCompleted: if (bridge) bridge.refreshDashboard()

    // --- FONDO ATMOSFÉRICO PREMIUM ---
    Rectangle {
        anchors.fill: parent
        color: "#07080c"
        z: -2
        
        Rectangle {
            id: backgroundBlur
            anchors.centerIn: parent
            width: parent.width * 1.5
            height: parent.height * 1.5
            radius: width / 2
            opacity: 0.12
            color: currentAccentColor
            
            SequentialAnimation on color {
                loops: Animation.Infinite
                ColorAnimation { from: "#4da6ff"; to: "#7c6ff7"; duration: 8000; easing.type: Easing.InOutSine }
                ColorAnimation { from: "#7c6ff7"; to: "#4dc6a6"; duration: 8000; easing.type: Easing.InOutSine }
                ColorAnimation { from: "#4dc6a6"; to: "#4da6ff"; duration: 8000; easing.type: Easing.InOutSine }
            }

            layer.enabled: true
            layer.effect: MultiEffect { blurEnabled: true; blur: 1.0; blurMax: 100 }
        }
    }

    // --- EMPTY STATE ---
    Rectangle {
        id: emptyState
        anchors.centerIn: parent
        width: 480
        height: 380
        radius: 40
        color: "#11131a"
        border.color: "#252835"
        border.width: 1
        visible: isEmpty
        opacity: visible ? 1.0 : 0.0
        scale: visible ? 1.0 : 0.9

        Behavior on opacity { NumberAnimation { duration: 600; easing.type: Easing.OutCubic } }
        Behavior on scale { NumberAnimation { duration: 600; easing.type: Easing.OutBack } }

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 32

            Item {
                Layout.preferredWidth: 140
                Layout.preferredHeight: 140
                Layout.alignment: Qt.AlignHCenter
                
                Image {
                    anchors.fill: parent
                    source: bridge ? bridge.logoPath : ""
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                }
                
                Rectangle {
                    anchors.centerIn: parent
                    width: 160; height: 160; radius: 80
                    color: currentAccentColor
                    opacity: 0.1
                    z: -1
                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        NumberAnimation { from: 1.0; to: 1.2; duration: 3000; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.2; to: 1.0; duration: 3000; easing.type: Easing.InOutSine }
                    }
                }
            }

            ColumnLayout {
                spacing: 4
                Layout.alignment: Qt.AlignHCenter

                Label {
                    text: bridge ? bridge.appName : "EmuManager"
                    font.pixelSize: 42
                    font.weight: Font.Black
                    color: "#ffffff"
                    Layout.alignment: Qt.AlignHCenter
                }

                Label {
                    text: bridge ? bridge.appVersion : "1.0"
                    font.pixelSize: 12
                    font.bold: true
                    color: currentAccentColor
                    font.letterSpacing: 2
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
    }

    ScrollView {
        id: mainScroll
        anchors.fill: parent
        visible: !isEmpty
        contentWidth: availableWidth
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        
        ColumnLayout {
            width: parent.width
            spacing: 40
            Layout.margins: 40
            Layout.topMargin: 20

            // 1. HERO PANEL LUXURY
            Item {
                Layout.fillWidth: true
                height: 240
                
                Rectangle {
                    anchors.fill: parent
                    radius: 35
                    color: "#161823"
                    border.color: "#2a2d3a"
                    border.width: 1
                    clip: true

                    // Interior Glow
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 1
                        radius: 34
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "#0fffffff" }
                            GradientStop { position: 1.0; color: "transparent" }
                        }
                    }

                    // Background Pattern/Decorative Circle
                    Rectangle {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        width: 400; height: 400; radius: 200
                        color: currentAccentColor
                        opacity: 0.04
                        anchors.rightMargin: -100
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 50
                    anchors.rightMargin: 50
                    spacing: 30

                    ColumnLayout {
                        spacing: 12
                        Layout.alignment: Qt.AlignVCenter

                        Rectangle {
                            width: 100; height: 26; radius: 13
                            color: Qt.alpha(currentAccentColor, 0.15)
                            border.color: Qt.alpha(currentAccentColor, 0.3)
                            border.width: 1
                            
                            Label {
                                anchors.centerIn: parent
                                text: bridge ? bridge.translate("dash_greeting").toUpperCase() : "BIENVENIDO"
                                font.pixelSize: 10; font.bold: true; color: currentAccentColor; font.letterSpacing: 1.5
                            }
                        }

                        Label {
                            text: bridge ? bridge.appName : "EmuManager"
                            font.pixelSize: 56; font.weight: Font.Black; color: "#ffffff"
                            font.letterSpacing: -1
                        }
                        
                        Label {
                            text: (bridge ? bridge.translateWithArg("dash_tagline", "") : "Tu centro de emulación retro") + " • v" + (bridge ? bridge.appVersion : "1.0")
                            font.pixelSize: 16; color: "#888899"
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Decorative Floating Icon
                    Label {
                        text: "👾"
                        font.pixelSize: 100
                        opacity: 0.12
                        rotation: -10
                        Layout.alignment: Qt.AlignVCenter
                        
                        SequentialAnimation on anchors.verticalCenterOffset {
                            loops: Animation.Infinite
                            NumberAnimation { from: -10; to: 10; duration: 3000; easing.type: Easing.InOutQuad }
                            NumberAnimation { from: 10; to: -10; duration: 3000; easing.type: Easing.InOutQuad }
                        }
                    }
                }
            }

            // 2. STATS ROW
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 18
                
                Label {
                    text: (bridge ? bridge.translate("dash_stats_title") : "ESTADÍSTICAS").toUpperCase()
                    font.pixelSize: 11; font.bold: true; color: currentAccentColor; font.letterSpacing: 3
                }

                RowLayout {
                    spacing: 24
                    Layout.fillWidth: true

                    StatCard {
                        icon: "🚀"
                        value: (bridge && bridge.dashboardStats) ? bridge.dashboardStats.installed : 0
                        label: bridge ? bridge.translate("dash_stat_installed") : "Instalados"
                        accentColor: "#4da6ff"
                    }
                    StatCard {
                        icon: "🎮"
                        value: (bridge && bridge.dashboardStats) ? bridge.dashboardStats.totalRoms : 0
                        label: bridge ? bridge.translate("dash_stat_roms") : "ROMs"
                        accentColor: "#7c6ff7"
                    }
                    StatCard {
                        icon: "🕹️"
                        value: (bridge && bridge.dashboardStats) ? bridge.dashboardStats.totalConsoles : 0
                        label: bridge ? bridge.translate("dash_stat_consoles") : "Consolas"
                        accentColor: "#4dc6a6"
                    }
                    StatCard {
                        icon: "⏳"
                        value: (bridge && bridge.dashboardStats) ? bridge.dashboardStats.totalHours : 0
                        label: bridge ? bridge.translate("dash_stat_hours") : "Horas"
                        accentColor: "#f0a040"
                    }
                    Item { Layout.fillWidth: true }
                }
            }

            // 3. CONTENT PANELS
            RowLayout {
                Layout.fillWidth: true
                spacing: 30
                Layout.alignment: Qt.AlignTop

                // Recent Activity
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 3
                    spacing: 18
                    Layout.alignment: Qt.AlignTop

                    Label {
                        text: (bridge ? bridge.translate("dash_recent_title") : "ACTIVIDAD RECIENTE").toUpperCase()
                        font.pixelSize: 11; font.bold: true; color: currentAccentColor; font.letterSpacing: 3
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 320
                        radius: 28
                        color: "#161823"
                        border.color: "#2a2d3a"
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 0

                            Repeater {
                                model: bridge ? bridge.recentActivity : []
                                delegate: Item {
                                    Layout.fillWidth: true
                                    height: 64
                                    
                                    Rectangle {
                                        anchors.fill: parent
                                        anchors.margins: 4
                                        radius: 18
                                        color: "#202336"
                                        visible: mouseArea.containsMouse
                                        opacity: 0.5
                                    }

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 20
                                        anchors.rightMargin: 20
                                        spacing: 15
                                        
                                        Rectangle {
                                            width: 40; height: 40; radius: 20
                                            color: Qt.alpha(modelData.color, 0.15)
                                            Label { anchors.centerIn: parent; text: "🕹️"; font.pixelSize: 18 }
                                        }

                                        ColumnLayout {
                                            spacing: 1
                                            Label {
                                                text: modelData.name
                                                color: "#ffffff"; font.pixelSize: 14; font.bold: true
                                            }
                                            Label {
                                                text: modelData.console.toUpperCase()
                                                color: "#666677"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1
                                            }
                                        }
                                        Item { Layout.fillWidth: true }
                                        Label {
                                            text: modelData.playtime
                                            color: modelData.color; font.pixelSize: 12; font.bold: true
                                        }
                                    }
                                    
                                    MouseArea {
                                        id: mouseArea
                                        anchors.fill: parent
                                        hoverEnabled: true
                                    }
                                }
                            }

                            Label {
                                visible: bridge ? bridge.recentActivity.length === 0 : true
                                text: bridge ? bridge.translate("dash_empty_recent") : "Sin actividad reciente"
                                color: "#555566"; font.pixelSize: 14; Layout.alignment: Qt.AlignCenter
                                Layout.margins: 60; horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                }

                // System Status
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 2
                    spacing: 18
                    Layout.alignment: Qt.AlignTop

                    Label {
                        text: (bridge ? bridge.translate("dash_status_title_panel") : "ESTADO DEL SISTEMA").toUpperCase()
                        font.pixelSize: 11; font.bold: true; color: currentAccentColor; font.letterSpacing: 3
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 320
                        radius: 28
                        color: "#161823"
                        border.color: "#2a2d3a"
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 25
                            spacing: 15

                            StatusRow {
                                title: bridge ? bridge.translate("dash_status_path_emus") : "Ruta Emuladores"
                                path: (bridge && bridge.systemStatus) ? bridge.systemStatus.emusPath : ""
                                exists: (bridge && bridge.systemStatus) ? bridge.systemStatus.emusPathExists : false
                            }
                            StatusRow {
                                title: bridge ? bridge.translate("dash_status_path_roms") : "Ruta ROMs"
                                path: (bridge && bridge.systemStatus) ? bridge.systemStatus.romsPath : ""
                                exists: (bridge && bridge.systemStatus) ? bridge.systemStatus.romsPathExists : false
                            }

                            Rectangle {
                                Layout.fillWidth: true; height: 1; color: "#2a2d3a"
                            }

                            Label {
                                text: "EMULADORES INSTALADOS"
                                font.pixelSize: 10; color: "#555566"; font.bold: true; font.letterSpacing: 1.5
                            }

                            ColumnLayout {
                                spacing: 10
                                clip: true
                                Repeater {
                                    model: (bridge && bridge.systemStatus) ? bridge.systemStatus.installedEmus : []
                                    delegate: RowLayout {
                                        Layout.fillWidth: true
                                        Rectangle { width: 8; height: 8; radius: 4; color: modelData.color }
                                        Label { text: modelData.name; color: "#d0d0d0"; font.pixelSize: 13; font.weight: Font.Medium }
                                        Item { Layout.fillWidth: true }
                                        Label { text: modelData.console.toUpperCase(); color: "#555566"; font.pixelSize: 9; font.bold: true }
                                    }
                                }
                            }
                            
                            Item { Layout.fillHeight: true }
                        }
                    }
                }
            }
        }
    }
}
