import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects
import "../components"

Item {
    id: dashboardRoot
    
    property bool isEmpty: bridge ? (bridge.lib.dashboardStats.installed === 0 && bridge.lib.dashboardStats.totalRoms === 0) : true
    property color currentAccentColor: window.themeAccent
    
    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    Component.onCompleted: if (bridge) bridge.refreshDashboard()

    // --- FONDO ATMOSFÉRICO ---
    Rectangle {
        anchors.fill: parent
        color: window.themeBg
        z: -2

        // Animated ambient orb
        Rectangle {
            id: backgroundBlur
            anchors.centerIn: parent
            width: parent.width * 1.6
            height: parent.height * 1.6
            radius: width / 2
            opacity: 0.1

            gradient: Gradient {
                GradientStop { position: 0.0; color: window.neonViolet }
                GradientStop { position: 0.4; color: window.neonMagenta }
                GradientStop { position: 0.85; color: "transparent" }
            }

            SequentialAnimation on opacity {
                loops: Animation.Infinite
                NumberAnimation { from: 0.08; to: 0.14; duration: 8000; easing.type: Easing.InOutSine }
                NumberAnimation { from: 0.14; to: 0.08; duration: 8000; easing.type: Easing.InOutSine }
            }
        }
    }

    // --- EMPTY STATE ---
    Rectangle {
        id: emptyState
        anchors.centerIn: parent
        width: 480; height: 420; radius: 44
        color: Qt.rgba(0.08, 0.05, 0.18, 0.8)
        border.color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.3)
        border.width: 1
        visible: isEmpty
        opacity: visible ? 1.0 : 0.0
        scale: visible ? 1.0 : 0.9
        Behavior on opacity { NumberAnimation { duration: 600; easing.type: Easing.OutCubic } }
        Behavior on scale { NumberAnimation { duration: 600; easing.type: Easing.OutBack } }

        ColumnLayout {
            anchors.centerIn: parent; spacing: 32

            Item {
                Layout.preferredWidth: 140; Layout.preferredHeight: 140
                Layout.alignment: Qt.AlignHCenter
                Image {
                    anchors.fill: parent; source: bridge ? bridge.logoPath : ""
                    fillMode: Image.PreserveAspectFit; smooth: true
                }
                Rectangle {
                    anchors.centerIn: parent; width: 170; height: 170; radius: 85
                    opacity: 0.0; z: -1
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: window.neonViolet }
                        GradientStop { position: 1.0; color: window.neonMagenta }
                    }
                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        NumberAnimation { from: 0.06; to: 0.14; duration: 3500; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 0.14; to: 0.06; duration: 3500; easing.type: Easing.InOutSine }
                    }
                }
            }

            ColumnLayout {
                spacing: 6; Layout.alignment: Qt.AlignHCenter
                Label {
                    text: bridge ? bridge.appName : "EmuManager"
                    font.pixelSize: 40; font.weight: Font.Black; color: "#f0e8ff"
                    Layout.alignment: Qt.AlignHCenter
                    layer.enabled: true
                    layer.effect: MultiEffect {
                        shadowEnabled: true; shadowColor: window.neonViolet
                        shadowBlur: 0.8; shadowOpacity: 0.5
                    }
                }
                Label {
                    text: bridge ? bridge.appVersion : "1.0"
                    font.pixelSize: 11; font.bold: true; color: window.neonViolet
                    font.letterSpacing: 4; Layout.alignment: Qt.AlignHCenter
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
                
                // We can remove the solid hero background rectangle for a cleaner look
                // matching the reference image.
                Item {
                    anchors.fill: parent
                    z: -1
                    Rectangle {
                        anchors.fill: parent
                        opacity: 0.15
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: window.neonCyan }
                            GradientStop { position: 0.5; color: "transparent" }
                            GradientStop { position: 1.0; color: window.neonPurple }
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
                            height: 28; width: childrenRect.width + 28; radius: 14
                            color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.15)
                            border.color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.4)
                            border.width: 1
                            Label {
                                x: 14; anchors.verticalCenter: parent.verticalCenter
                                text: tr("dash_greeting").toUpperCase()
                                font.pixelSize: 11; font.bold: true
                                color: window.neonViolet; font.letterSpacing: 2.5
                            }
                        }

                        Label {
                            text: bridge ? bridge.appName : "EmuManager"
                            font.pixelSize: 82; font.weight: Font.Black; color: "#f0e8ff"
                            font.letterSpacing: -2.5

                            layer.enabled: true
                            layer.effect: MultiEffect {
                                autoPaddingEnabled: true
                                shadowEnabled: true
                                shadowColor: window.neonViolet
                                shadowBlur: 1.5
                                shadowHorizontalOffset: 0
                                shadowVerticalOffset: 0
                                shadowOpacity: 0.65
                            }
                        }
                        
                        Label {
                            text: tr("dash_tagline", (bridge ? bridge.appVersion : "1.0"))
                            font.pixelSize: 17; color: "#7e7a96"; font.weight: Font.Light
                        }
                    }

                    Item {
                        Layout.preferredWidth: 170; Layout.preferredHeight: 170; Layout.alignment: Qt.AlignVCenter
                        // Outer pulsing ring — igual que el splash
                         Rectangle {
                             anchors.centerIn: parent; width: 175; height: 175; radius: 88
                             color: "transparent"
                             border.color: window.neonViolet
                             border.width: 2
                             opacity: 0.3
                             z: -1
                             SequentialAnimation on scale {
                                 loops: Animation.Infinite
                                 NumberAnimation { from: 1.0; to: 1.25; duration: 2200; easing.type: Easing.InOutSine }
                                 NumberAnimation { from: 1.25; to: 1.0; duration: 2200; easing.type: Easing.InOutSine }
                             }
                         }
                         // Second inner ring for depth
                         Rectangle {
                             anchors.centerIn: parent; width: 148; height: 148; radius: 74
                             color: "transparent"
                             border.color: window.neonMagenta
                             border.width: 1
                             opacity: 0.15
                             z: -1
                             SequentialAnimation on scale {
                                 loops: Animation.Infinite
                                 NumberAnimation { from: 1.08; to: 0.9; duration: 2800; easing.type: Easing.InOutSine }
                                 NumberAnimation { from: 0.9; to: 1.08; duration: 2800; easing.type: Easing.InOutSine }
                             }
                         }
                         // Glow orb — pulsa en opacidad
                         Rectangle {
                             anchors.centerIn: parent; width: 140; height: 140; radius: 70
                             z: -1
                             gradient: Gradient {
                                 GradientStop { position: 0.0; color: window.neonViolet }
                                 GradientStop { position: 1.0; color: window.neonMagenta }
                             }
                             SequentialAnimation on opacity {
                                 loops: Animation.Infinite
                                 NumberAnimation { from: 0.12; to: 0.28; duration: 2000; easing.type: Easing.InOutSine }
                                 NumberAnimation { from: 0.28; to: 0.12; duration: 2000; easing.type: Easing.InOutSine }
                             }
                         }
                         // Logo box — respira ligeramente en escala
                         Rectangle {
                             id: logoBox
                             anchors.centerIn: parent
                             width: 126; height: 126; radius: 42
                             color: Qt.rgba(0.1, 0.07, 0.2, 0.9)
                             border.color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.55)
                             border.width: 1.5
                             layer.enabled: true
                             layer.effect: MultiEffect {
                                 shadowEnabled: true; shadowColor: window.neonViolet
                                 shadowBlur: 1.5; shadowOpacity: 0.65
                             }
                             Image {
                                 anchors.fill: parent; anchors.margins: 22
                                 source: bridge ? bridge.logoPath : ""
                                 fillMode: Image.PreserveAspectFit; smooth: true; opacity: 0.95
                             }
                             SequentialAnimation on scale {
                                 loops: Animation.Infinite
                                 NumberAnimation { from: 1.0; to: 1.04; duration: 1800; easing.type: Easing.InOutSine }
                                 NumberAnimation { from: 1.04; to: 1.0; duration: 1800; easing.type: Easing.InOutSine }
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
                spacing: 20
                                StatCard {
                    icon: "install"; label: tr("dash_stat_installed"); accentColor: window.neonViolet
                    value: (bridge && bridge.lib.dashboardStats) ? bridge.lib.dashboardStats.installed : 0
                    Layout.fillWidth: true
                }
                StatCard {
                    icon: "games"; label: tr("dash_stat_roms"); accentColor: window.neonMagenta
                    value: (bridge && bridge.lib.dashboardStats) ? bridge.lib.dashboardStats.totalRoms : 0
                    Layout.fillWidth: true
                }
                StatCard {
                    icon: "consoles"; label: tr("dash_stat_consoles"); accentColor: window.neonGold
                    value: (bridge && bridge.lib.dashboardStats) ? bridge.lib.dashboardStats.totalConsoles : 0
                    Layout.fillWidth: true
                }
                StatCard {
                    icon: "clock"; label: tr("dash_stat_hours"); accentColor: window.neonGreen
                    value: (bridge && bridge.lib.dashboardStats) ? bridge.lib.dashboardStats.totalHours : 0
                    textValue: (bridge && bridge.lib.dashboardStats) ? bridge.lib.dashboardStats.totalTimeDisplay : "0h"
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
                        text: tr("dash_recent_title").toUpperCase()
                        font.pixelSize: 11; font.bold: true
                        color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.55)
                        font.letterSpacing: 2.5; Layout.leftMargin: 5
                    }
                    Rectangle {
                        Layout.fillWidth: true; Layout.preferredHeight: actContent.implicitHeight + 30; radius: 26
                        color: Qt.rgba(0.07, 0.04, 0.15, 0.72)
                        border.color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.18)
                        border.width: 1

                        layer.enabled: true
                        layer.effect: MultiEffect {
                            shadowEnabled: true; shadowColor: window.neonViolet
                            shadowBlur: 0.8; shadowOpacity: 0.15; shadowVerticalOffset: 4
                        }

                        Rectangle {
                            anchors.fill: parent; anchors.margins: 1; radius: 25
                            color: "transparent"
                            border.color: Qt.rgba(1,1,1,0.04); border.width: 1
                        }

                        ColumnLayout {
                            id: actContent
                            anchors.fill: parent; anchors.margins: 15; spacing: 0
                            Repeater {
                                model: bridge ? bridge.lib.recentActivity : []
                                delegate: Item {
                                    Layout.fillWidth: true; height: 72
                                    // Hover pill
                                    Rectangle {
                                        anchors.fill: parent; anchors.margins: 2; radius: 16
                                        color: Qt.rgba(modelData.color.r, modelData.color.g, modelData.color.b, 0.1)
                                        visible: mouseAreaAct.containsMouse
                                        border.color: Qt.rgba(modelData.color.r, modelData.color.g, modelData.color.b, 0.2)
                                        border.width: 1
                                    }
                                    // Left accent bar on hover
                                    Rectangle {
                                        anchors.left: parent.left; anchors.leftMargin: 6
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 3; height: 28; radius: 2
                                        color: modelData.color
                                        visible: mouseAreaAct.containsMouse
                                        layer.enabled: true
                                        layer.effect: MultiEffect {
                                            shadowEnabled: true; shadowColor: modelData.color
                                            shadowBlur: 0.8; shadowOpacity: 0.7
                                        }
                                    }
                                    RowLayout {
                                        anchors.fill: parent; anchors.leftMargin: 18; anchors.rightMargin: 15; spacing: 15
                                        // Mini Carátula
                                        Rectangle {
                                            width: 40; height: 52; radius: 10
                                            color: Qt.rgba(0, 0, 0, 0.5)
                                            clip: true
                                            border.color: mouseAreaAct.containsMouse ? modelData.color : Qt.rgba(1,1,1,0.08)
                                            border.width: 1
                                            Behavior on border.color { ColorAnimation { duration: 200 } }

                                            layer.enabled: mouseAreaAct.containsMouse
                                            layer.effect: MultiEffect {
                                                shadowEnabled: true; shadowColor: modelData.color
                                                shadowBlur: 1.0; shadowOpacity: 0.7
                                            }

                                            Image {
                                                anchors.fill: parent
                                                source: modelData.cover
                                                fillMode: Image.PreserveAspectCrop
                                                opacity: mouseAreaAct.containsMouse ? 1.0 : 0.8
                                                visible: modelData.cover !== ""
                                                Behavior on opacity { NumberAnimation { duration: 200 } }
                                            }
                                            Rectangle {
                                                anchors.fill: parent; color: modelData.color; opacity: 0.1
                                                visible: modelData.cover === ""
                                            }
                                            Icon {
                                                anchors.centerIn: parent; name: "library"; size: 18
                                                color: modelData.color; opacity: 0.5
                                                visible: modelData.cover === "" || modelData.cover.status !== Image.Ready
                                            }
                                        }

                                        ColumnLayout {
                                            spacing: 0
                                            Layout.fillWidth: true
                                            Label { 
                                                text: modelData.name; color: mouseAreaAct.containsMouse ? "#ffffff" : "#e0e0e0"
                                                font.pixelSize: 15; font.weight: Font.Bold; elide: Text.ElideRight; Layout.fillWidth: true 
                                                Behavior on color { ColorAnimation { duration: 200 } }
                                            }
                                            Label { 
                                                text: modelData.console.toUpperCase(); color: "#6e7282"; font.pixelSize: 9
                                                font.bold: true; font.letterSpacing: 1.5 
                                            }
                                        }

                                        RowLayout {
                                            spacing: 8
                                            visible: mouseAreaAct.containsMouse
                                            Label { text: "▶"; color: modelData.color; font.pixelSize: 12 }
                                            Label { 
                                                text: tr("lib_play").toUpperCase()
                                                color: modelData.color; font.pixelSize: 11; font.bold: true; font.letterSpacing: 1
                                            }
                                        }

                                        Label { 
                                            text: modelData.playtime; color: mouseAreaAct.containsMouse ? modelData.color : "#6e7282"
                                            font.pixelSize: 13; font.weight: Font.DemiBold
                                            visible: !mouseAreaAct.containsMouse
                                        }
                                    }
                                    MouseArea { 
                                        id: mouseAreaAct; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            if (window && window.requestLaunch)
                                                window.requestLaunch(modelData.path, modelData.id_emu, modelData.name)
                                        }
                                    }
                                }
                            }
                            ColumnLayout {
                                visible: bridge ? bridge.lib.recentActivity.length === 0 : true
                                Layout.alignment: Qt.AlignCenter
                                Layout.topMargin: 100
                                spacing: 20
                                Icon {
                                    name: "library"
                                    size: 64
                                    color: "#4a4d63"
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                Label {
                                    text: tr("dash_empty_recent")
                                    color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.4)
                                    font.pixelSize: 16; Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true; Layout.preferredWidth: 2; spacing: 30; Layout.alignment: Qt.AlignTop
                    
                    // Card 1: System Paths
                    ColumnLayout {
                        spacing: 12; Layout.fillWidth: true
                        RowLayout {
                            spacing: 8; Layout.leftMargin: 5
                            Icon { name: "monitor"; size: 14; color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.55) }
                            Label {
                                text: tr("dash_status_title_panel").toUpperCase()
                                font.pixelSize: 11; font.bold: true
                                color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.55)
                                font.letterSpacing: 2.5
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true; implicitHeight: pathCol.implicitHeight + 40
                            radius: 26
                            color: Qt.rgba(0.07, 0.04, 0.15, 0.72)
                            border.color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.18)
                            border.width: 1
                            layer.enabled: true
                            layer.effect: MultiEffect {
                                shadowEnabled: true; shadowColor: window.neonViolet; shadowBlur: 0.6; shadowOpacity: 0.15; shadowVerticalOffset: 4
                            }
                            Rectangle { anchors.fill: parent; anchors.margins: 1; radius: 25; color: "transparent"; border.color: Qt.rgba(1,1,1,0.04); border.width: 1 }
                            ColumnLayout {
                                id: pathCol; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 20; spacing: 18
                                StatusRow {
                                    title: tr("dash_status_path_emus")
                                    path: (bridge && bridge.systemStatus) ? bridge.systemStatus.emusPath : ""
                                    exists: (bridge && bridge.systemStatus) ? bridge.systemStatus.emusPathExists : false
                                }
                                StatusRow {
                                    title: tr("dash_status_path_roms")
                                    path: (bridge && bridge.systemStatus) ? bridge.systemStatus.romsPath : ""
                                    exists: (bridge && bridge.systemStatus) ? bridge.systemStatus.romsPathExists : false
                                }
                            }
                        }
                    }

                    ColumnLayout {
                        spacing: 12; Layout.fillWidth: true
                        Label {
                            text: tr("dash_available_systems").toUpperCase()
                            font.pixelSize: 11; font.bold: true
                            color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.55)
                            font.letterSpacing: 2.5; Layout.leftMargin: 5
                        }
                        Rectangle {
                            Layout.fillWidth: true; implicitHeight: emuCol.implicitHeight + 40
                            radius: 26
                            color: Qt.rgba(0.07, 0.04, 0.15, 0.72)
                            border.color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.18)
                            border.width: 1
                            layer.enabled: true
                            layer.effect: MultiEffect {
                                shadowEnabled: true; shadowColor: window.neonViolet; shadowBlur: 0.6; shadowOpacity: 0.15; shadowVerticalOffset: 4
                            }
                            Rectangle { anchors.fill: parent; anchors.margins: 1; radius: 25; color: "transparent"; border.color: Qt.rgba(1,1,1,0.04); border.width: 1 }
                            ColumnLayout {
                                id: emuCol; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 20; spacing: 16
                                Repeater {
                                    model: (bridge && bridge.systemStatus) ? bridge.systemStatus.installedEmus : []
                                    delegate: RowLayout {
                                        Layout.fillWidth: true; spacing: 12
                                        // Colored dot with glow
                                        Rectangle {
                                            width: 8; height: 8; radius: 4; color: modelData.color
                                            Layout.alignment: Qt.AlignVCenter
                                            layer.enabled: true
                                            layer.effect: MultiEffect { shadowEnabled: true; shadowColor: modelData.color; shadowBlur: 0.8; shadowOpacity: 0.9 }
                                        }
                                        Label {
                                            text: modelData.name; color: "#d0c8e8"
                                            font.pixelSize: 13; font.weight: Font.Medium
                                            Layout.fillWidth: true; elide: Text.ElideRight
                                        }
                                        // Console badge pill
                                        Rectangle {
                                            implicitWidth: consoleLbl.implicitWidth + 12; height: 20; radius: 10
                                            color: Qt.rgba(modelData.color.r, modelData.color.g, modelData.color.b, 0.15)
                                            border.color: Qt.rgba(modelData.color.r, modelData.color.g, modelData.color.b, 0.3)
                                            border.width: 1
                                            Layout.alignment: Qt.AlignVCenter
                                            Label {
                                                id: consoleLbl
                                                anchors.centerIn: parent
                                                text: modelData.console.toUpperCase()
                                                color: modelData.color; font.pixelSize: 9; font.bold: true; font.letterSpacing: 0.5
                                            }
                                        }
                                    }
                                }
                                Label {
                                    visible: !bridge || bridge.systemStatus.installedEmus.length === 0
                                    text: tr("dash_no_systems")
                                    color: Qt.rgba(window.neonViolet.r, window.neonViolet.g, window.neonViolet.b, 0.4)
                                    font.pixelSize: 13
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
