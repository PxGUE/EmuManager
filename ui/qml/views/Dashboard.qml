import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: dashboardRoot
    
    property bool isEmpty: bridge ? (bridge.dashboardStats.installed === 0 && bridge.dashboardStats.totalRoms === 0) : true
    property color currentAccentColor: "#4da6ff"

    Component.onCompleted: if (bridge) bridge.refreshDashboard()

    // --- FONDO ATMOSFÉRICO ---
    Rectangle {
        anchors.fill: parent
        color: "#0a0b12"
        z: -2
        
        // Glow ambiental animado
        Rectangle {
            id: backgroundBlur
            anchors.centerIn: parent
            width: parent.width * 1.5
            height: parent.height * 1.5
            radius: width / 2
            opacity: 0.1
            
            gradient: Gradient {
                GradientStop { position: 0.0; color: currentAccentColor }
                GradientStop { position: 0.5; color: "transparent" }
            }
            
            SequentialAnimation on color {
                loops: Animation.Infinite
                ColorAnimation { from: "#4da6ff"; to: "#7c6ff7"; duration: 10000; easing.type: Easing.InOutSine }
                ColorAnimation { from: "#7c6ff7"; to: "#4dc6a6"; duration: 10000; easing.type: Easing.InOutSine }
                ColorAnimation { from: "#4dc6a6"; to: "#4da6ff"; duration: 10000; easing.type: Easing.InOutSine }
            }
        }
    }

    // --- EMPTY STATE ---
    Rectangle {
        id: emptyState
        anchors.centerIn: parent
        width: 480
        height: 400
        radius: 40
        color: "#12141d"
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
                        NumberAnimation { from: 1.0; to: 1.2; duration: 4000; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.2; to: 1.0; duration: 4000; easing.type: Easing.InOutSine }
                    }
                }
            }

            ColumnLayout {
                spacing: 8
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
                    font.letterSpacing: 4
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
            Layout.topMargin: 30
            Layout.bottomMargin: 60

            // 1. HERO SECTION
            Item {
                Layout.fillWidth: true
                height: 300
                
                Rectangle {
                    anchors.fill: parent
                    color: "#0f111a"
                    opacity: 0.5
                    border.color: "#1d1f2b"
                    border.width: 1
                }

                Item {
                    anchors.fill: parent
                    z: -1
                    Rectangle {
                        anchors.fill: parent
                        opacity: 0.2
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: currentAccentColor }
                            GradientStop { position: 0.8; color: "transparent" }
                        }
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 60
                    anchors.rightMargin: 60
                    spacing: 40

                    ColumnLayout {
                        spacing: 12
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignVCenter

                        Rectangle {
                            height: 28; width: childrenRect.width + 24; radius: 14
                            color: Qt.alpha(currentAccentColor, 0.15)
                            border.color: Qt.alpha(currentAccentColor, 0.3)
                            Label {
                                x: 12; anchors.verticalCenter: parent.verticalCenter
                                text: (bridge && bridge.currentLanguage) ? bridge.translate("dash_greeting").toUpperCase() : "BIENVENIDO"
                                font.pixelSize: 11; font.bold: true; color: currentAccentColor; font.letterSpacing: 2
                            }
                        }

                        Label {
                            text: bridge ? bridge.appName : "EmuManager"
                            font.pixelSize: 72; font.weight: Font.Black; color: "#ffffff"
                            font.letterSpacing: -2
                        }
                        
                        Label {
                            text: (bridge && bridge.currentLanguage ? bridge.translateWithArg("dash_tagline", "") : "Tu centro de emulación retro") + " • v" + (bridge ? bridge.appVersion : "1.0")
                            font.pixelSize: 18; color: "#9494a5"; font.weight: Font.Light
                        }
                    }

                    Item {
                        Layout.preferredWidth: 160; Layout.preferredHeight: 160; Layout.alignment: Qt.AlignVCenter
                        Rectangle {
                            anchors.centerIn: parent
                            width: 140; height: 140; radius: 45; opacity: 0.12
                            gradient: Gradient {
                                GradientStop { position: 0.0; color: currentAccentColor }
                                GradientStop { position: 1.0; color: "transparent" }
                            }
                        }
                        Rectangle {
                            id: logoBox
                            anchors.centerIn: parent
                            width: 124; height: 124; radius: 40; color: "#161825"
                            border.color: Qt.alpha(currentAccentColor, 0.4); border.width: 1
                            Image {
                                anchors.fill: parent; anchors.margins: 22
                                source: bridge ? bridge.logoPath : ""; fillMode: Image.PreserveAspectFit; opacity: 0.95
                            }
                        }
                        SequentialAnimation on anchors.verticalCenterOffset {
                            loops: Animation.Infinite
                            NumberAnimation { from: -10; to: 10; duration: 3500; easing.type: Easing.InOutQuad }
                            NumberAnimation { from: 10; to: -10; duration: 3500; easing.type: Easing.InOutQuad }
                        }
                    }
                }
            }

            // 2. STATS SECTION
            RowLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 40
                Layout.rightMargin: 40
                spacing: 15
                
                StatCard {
                    icon: "🚀"; label: (bridge && bridge.currentLanguage) ? bridge.translate("dash_stat_installed") : "INSTALADOS"; accentColor: "#4da6ff"
                    value: (bridge && bridge.dashboardStats) ? bridge.dashboardStats.installed : 0
                    Layout.fillWidth: true
                }
                StatCard {
                    icon: "🎮"; label: (bridge && bridge.currentLanguage) ? bridge.translate("dash_stat_roms") : "NÚMERO DE ROMS"; accentColor: "#7c6ff7"
                    value: (bridge && bridge.dashboardStats) ? bridge.dashboardStats.totalRoms : 0
                    Layout.fillWidth: true
                }
                StatCard {
                    icon: "🕹️"; label: (bridge && bridge.currentLanguage) ? bridge.translate("dash_stat_consoles") : "CONSOLAS"; accentColor: "#4dc6a6"
                    value: (bridge && bridge.dashboardStats) ? bridge.dashboardStats.totalConsoles : 0
                    Layout.fillWidth: true
                }
                StatCard {
                    icon: "⏳"; label: (bridge && bridge.currentLanguage) ? bridge.translate("dash_stat_hours") : "TIEMPO JUGADO"; accentColor: "#f0a040"
                    value: (bridge && bridge.dashboardStats) ? bridge.dashboardStats.totalHours : 0
                    Layout.fillWidth: true
                }
            }

            // 3. MAIN CONTENT (Side by Side)
            RowLayout {
                Layout.fillWidth: true; Layout.leftMargin: 60; Layout.rightMargin: 60; spacing: 40
                Layout.topMargin: 20; Layout.alignment: Qt.AlignTop

                // Activity Panel
                ColumnLayout {
                    Layout.fillWidth: true; Layout.preferredWidth: 4; spacing: 15; Layout.alignment: Qt.AlignTop
                    Label {
                        text: (bridge && bridge.currentLanguage ? bridge.translate("dash_recent_title") : "ACTIVIDAD RECIENTE").toUpperCase()
                        font.pixelSize: 12; font.bold: true; color: "#6e7282"; font.letterSpacing: 2
                        Layout.leftMargin: 5
                    }
                    Rectangle {
                        Layout.fillWidth: true; Layout.preferredHeight: 380; radius: 28
                        color: "#141621"; border.color: "#252835"; border.width: 1
                        ColumnLayout {
                            anchors.fill: parent; anchors.margins: 15; spacing: 0
                            Repeater {
                                model: bridge ? bridge.recentActivity : []
                                delegate: Item {
                                    Layout.fillWidth: true; height: 72
                                    Rectangle {
                                        anchors.fill: parent; anchors.margins: 4; radius: 20
                                        color: "#1c1f2e"; visible: mouseAreaAct.containsMouse
                                    }
                                    RowLayout {
                                        anchors.fill: parent; anchors.leftMargin: 15; anchors.rightMargin: 15; spacing: 15
                                        Rectangle {
                                            width: 44; height: 44; radius: 12; color: Qt.alpha(modelData.color, 0.1)
                                            border.color: Qt.alpha(modelData.color, 0.2); border.width: 1
                                            Label { anchors.centerIn: parent; text: "🎮"; font.pixelSize: 20 }
                                        }
                                        ColumnLayout {
                                            spacing: 2
                                            Label { text: modelData.name; color: "#ffffff"; font.pixelSize: 15; font.weight: Font.Bold; elide: Text.ElideRight; Layout.fillWidth: true }
                                            Label { text: modelData.console.toUpperCase(); color: "#6e7282"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1 }
                                        }
                                        Item { Layout.fillWidth: true }
                                        Label { text: modelData.playtime; color: modelData.color; font.pixelSize: 13; font.weight: Font.DemiBold }
                                    }
                                    MouseArea { id: mouseAreaAct; anchors.fill: parent; hoverEnabled: true }
                                }
                            }
                            Label {
                                visible: bridge ? bridge.recentActivity.length === 0 : true
                                text: (bridge && bridge.currentLanguage) ? bridge.translate("dash_empty_recent") : "Sin actividad reciente"
                                color: "#4a4d63"; font.pixelSize: 16; Layout.alignment: Qt.AlignCenter; Layout.topMargin: 100
                            }
                        }
                    }
                }

                // Right Side: Multi-Card Column
                ColumnLayout {
                    Layout.fillWidth: true; Layout.preferredWidth: 2; spacing: 30; Layout.alignment: Qt.AlignTop
                    
                    // Card 1: System Paths
                    ColumnLayout {
                        spacing: 12; Layout.fillWidth: true
                        Label {
                            text: (bridge && bridge.currentLanguage ? bridge.translate("dash_status_title_panel") : "ESTADO DEL SISTEMA").toUpperCase()
                            font.pixelSize: 11; font.bold: true; color: "#6e7282"; font.letterSpacing: 2; Layout.leftMargin: 5
                        }
                        Rectangle {
                            Layout.fillWidth: true; implicitHeight: pathCol.implicitHeight + 40
                            radius: 24; color: "#141621"; border.color: "#252835"; border.width: 1
                            ColumnLayout {
                                id: pathCol; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 20; spacing: 18
                                StatusRow {
                                    title: (bridge && bridge.currentLanguage) ? bridge.translate("dash_status_path_emus") : "Ruta Emuladores"
                                    path: (bridge && bridge.systemStatus) ? bridge.systemStatus.emusPath : ""
                                    exists: (bridge && bridge.systemStatus) ? bridge.systemStatus.emusPathExists : false
                                }
                                StatusRow {
                                    title: (bridge && bridge.currentLanguage) ? bridge.translate("dash_status_path_roms") : "Ruta ROMs"
                                    path: (bridge && bridge.systemStatus) ? bridge.systemStatus.romsPath : ""
                                    exists: (bridge && bridge.systemStatus) ? bridge.systemStatus.romsPathExists : false
                                }
                            }
                        }
                    }

                    ColumnLayout {
                        spacing: 12; Layout.fillWidth: true
                        Label {
                            text: (bridge && bridge.currentLanguage ? bridge.translate("dash_available_systems") : "SISTEMAS DISPONIBLES")
                            font.pixelSize: 11; font.bold: true; color: "#6e7282"; font.letterSpacing: 2; Layout.leftMargin: 5
                        }
                        Rectangle {
                            Layout.fillWidth: true; implicitHeight: emuCol.implicitHeight + 40
                            radius: 24; color: "#141621"; border.color: "#252835"; border.width: 1
                            ColumnLayout {
                                id: emuCol; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 20; spacing: 15
                                Repeater {
                                    model: (bridge && bridge.systemStatus) ? bridge.systemStatus.installedEmus : []
                                    delegate: RowLayout {
                                        Layout.fillWidth: true; spacing: 10
                                        Rectangle { width: 8; height: 8; radius: 4; color: modelData.color; opacity: 0.8; Layout.alignment: Qt.AlignVCenter }
                                        Label { 
                                            text: modelData.name; color: "#e0e0e0"; font.pixelSize: 13; font.weight: Font.Medium; 
                                            Layout.fillWidth: true; elide: Text.ElideRight 
                                        }
                                        Label { 
                                            text: modelData.console.toUpperCase(); color: "#5a5e70"; font.pixelSize: 9; font.bold: true; 
                                            Layout.alignment: Qt.AlignVCenter 
                                        }
                                    }
                                }
                                Label {
                                    visible: !bridge || bridge.systemStatus.installedEmus.length === 0
                                    text: (bridge && bridge.currentLanguage) ? bridge.translate("dash_no_systems") : "Ningún sistema listo"; color: "#4a4d63"; font.pixelSize: 13; Layout.alignment: Qt.AlignCenter; Layout.topMargin: 5
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
