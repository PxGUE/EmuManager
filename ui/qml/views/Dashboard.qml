import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: dashboardRoot
    
    Component.onCompleted: bridge.refreshDashboard()

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        
        ColumnLayout {
            width: parent.width
            spacing: 32
            Layout.margins: 40

            // 1. HERO PANEL
            Rectangle {
                Layout.fillWidth: true
                height: 180
                radius: 20
                clip: true
                color: "#1a1c24"
                
                // Animated Gradient Background
                Rectangle {
                    anchors.fill: parent
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "#1a1c24" }
                        GradientStop { position: 0.8; color: "#1e2b4a" }
                    }
                    
                    Rectangle {
                        anchors.right: parent.right
                        anchors.top: parent.top
                        width: 300
                        height: 300
                        radius: 150
                        color: "#4da6ff"
                        opacity: 0.05
                        anchors.rightMargin: -100
                        anchors.topMargin: -100
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 40
                    anchors.rightMargin: 40
                    spacing: 20

                    ColumnLayout {
                        spacing: 8
                        Layout.alignment: Qt.AlignVCenter

                        Rectangle {
                            width: 80
                            height: 22
                            radius: 11
                            color: Qt.alpha("#4da6ff", 0.15)
                            
                            Label {
                                anchors.centerIn: parent
                                text: bridge.translate("dash_greeting").toUpperCase()
                                font.pixelSize: 9
                                font.bold: true
                                color: "#4da6ff"
                                font.letterSpacing: 1
                            }
                        }

                        Label {
                            text: bridge.appName
                            font.pixelSize: 44
                            font.weight: Font.Black
                            color: "#ffffff"
                        }
                        
                        RowLayout {
                            spacing: 8
                            Label {
                                text: bridge.translateWithArg("dash_tagline", "") 
                                font.pixelSize: 14
                                color: "#888899"
                            }
                            Label {
                                text: bridge.appVersion
                                font.pixelSize: 14
                                font.bold: true
                                color: "#4da6ff"
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Decorative Icon
                    Label {
                        text: "🚀"
                        font.pixelSize: 80
                        opacity: 0.15
                        rotation: -15
                        Layout.alignment: Qt.AlignVCenter
                    }
                }
                
                border.color: "#2a2d3a"
                border.width: 1
            }

            // 2. STATS ROW
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 12
                
                Label {
                    text: bridge.translate("dash_stats_title")
                    font.pixelSize: 12
                    font.bold: true
                    color: "#4da6ff"
                    font.letterSpacing: 2
                }

                RowLayout {
                    spacing: 16
                    Layout.fillWidth: true

                    StatCard {
                        icon: "🎯"
                        value: bridge.dashboardStats.installed
                        label: bridge.translate("dash_stat_installed")
                        accentColor: "#4da6ff"
                    }
                    StatCard {
                        icon: "📀"
                        value: bridge.dashboardStats.totalRoms
                        label: bridge.translate("dash_stat_roms")
                        accentColor: "#7c6ff7"
                    }
                    StatCard {
                        icon: "🖥️"
                        value: bridge.dashboardStats.totalConsoles
                        label: bridge.translate("dash_stat_consoles")
                        accentColor: "#4dc6a6"
                    }
                    StatCard {
                        icon: "⏱️"
                        value: bridge.dashboardStats.totalHours
                        label: bridge.translate("dash_stat_hours")
                        accentColor: "#f0a040"
                    }
                    Item { Layout.fillWidth: true }
                }
            }

            // 3. CONTENT (RECENT & STATUS)
            RowLayout {
                Layout.fillWidth: true
                spacing: 24
                Layout.alignment: Qt.AlignTop

                // Recent Activity
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 3
                    spacing: 12
                    Layout.alignment: Qt.AlignTop

                    Label {
                        text: bridge.translate("dash_recent_title")
                        font.pixelSize: 12
                        font.bold: true
                        color: "#4da6ff"
                        font.letterSpacing: 2
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.minimumHeight: 200
                        radius: 14
                        color: "#1a1c24"
                        border.color: "#2a2d3a"
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 0
                            spacing: 0

                            Repeater {
                                model: bridge.recentActivity
                                delegate: Item {
                                    Layout.fillWidth: true
                                    height: 52
                                    property bool hovered: false
                                    
                                    Rectangle {
                                        anchors.fill: parent
                                        color: parent.hovered ? "#1f2230" : "transparent"
                                        radius: 8
                                        visible: mouseArea.containsMouse
                                    }

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 12
                                        anchors.rightMargin: 12
                                        
                                        Label {
                                            text: "●"
                                            color: modelData.color
                                            font.pixelSize: 10
                                        }

                                        ColumnLayout {
                                            spacing: 1
                                            Label {
                                                text: modelData.name
                                                color: "#e0e0e0"
                                                font.pixelSize: 13
                                                font.bold: true
                                            }
                                            Label {
                                                text: modelData.console
                                                color: "#666666"
                                                font.pixelSize: 11
                                            }
                                        }
                                        Item { Layout.fillWidth: true }
                                        Label {
                                            text: modelData.playtime
                                            color: modelData.color
                                            font.pixelSize: 11
                                            font.bold: true
                                        }
                                    }
                                    
                                    MouseArea {
                                        id: mouseArea
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onEntered: parent.hovered = true
                                        onExited: parent.hovered = false
                                    }
                                }
                            }

                            Label {
                                visible: bridge.recentActivity.length === 0
                                text: bridge.translate("dash_empty_recent")
                                color: "#555566"
                                font.pixelSize: 13
                                Layout.alignment: Qt.AlignCenter
                                Layout.margins: 40
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                }

                // System Status
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 2
                    spacing: 12
                    Layout.alignment: Qt.AlignTop

                    Label {
                        text: bridge.translate("dash_status_title_panel")
                        font.pixelSize: 12
                        font.bold: true
                        color: "#4da6ff"
                        font.letterSpacing: 2
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.minimumHeight: 300
                        radius: 14
                        color: "#1a1c24"
                        border.color: "#2a2d3a"
                        border.width: 1

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 20
                            spacing: 16

                            // Paths
                            StatusRow {
                                title: bridge.translate("dash_status_path_emus")
                                path: bridge.systemStatus.emusPath
                                exists: bridge.systemStatus.emusPathExists
                            }
                            StatusRow {
                                title: bridge.translate("dash_status_path_roms")
                                path: bridge.systemStatus.romsPath
                                exists: bridge.systemStatus.romsPathExists
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: "#2a2d3a"
                            }

                            Label {
                                text: bridge.translate("dash_stat_installed")
                                font.pixelSize: 11
                                color: "#666666"
                                font.bold: true
                            }

                            ColumnLayout {
                                spacing: 8
                                Repeater {
                                    model: bridge.systemStatus.installedEmus
                                    delegate: RowLayout {
                                        Layout.fillWidth: true
                                        Label { text: "●"; color: modelData.color; font.pixelSize: 9 }
                                        Label { text: modelData.name; color: "#c0c0c0"; font.pixelSize: 12 }
                                        Item { Layout.fillWidth: true }
                                        Label { text: modelData.console; color: "#555555"; font.pixelSize: 10 }
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
