import QtQuick
import ".."
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects

Item {
    id: consoleCardRoot
    
    // --- DATOS ---
    property string title: "Console"
    property string fullName: "Full Console Name"
    property string emulatorName: "Emulator"
    property string gameCount: "0"
    property string playTime: "0h"
    property string iconEmoji: "🎮"
    property var accentColor: undefined
    readonly property color resolvedAccent: Theme.resolveColor(accentColor, title)
    
    // --- ESTADOS ---
    property bool isSelected: false
    property bool isFocused: isSelected || mainMA.containsMouse
    property bool minimalMode: true 
    property bool hasCore: true 

    // --- DIMENSIONES ---
    width: minimalMode ? 260 : 640 
    height: minimalMode ? 65 : 380
    
    Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
    Behavior on height { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }

    signal clicked()

    // --- CAPA DE EFECTOS (External Glow — Sutil y Optimizado) ---
    DropShadow {
        id: externalGlow
        anchors.fill: body; radius: isFocused ? 30 : 12; samples: 14
        color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, isFocused ? 0.4 : 0.12)
        source: body; visible: true; z: -1; transparentBorder: true
        Behavior on radius { NumberAnimation { duration: 400 } }
        Behavior on color { ColorAnimation { duration: 400 } }
    }

    // --- CUERPO PRINCIPAL ---
    Rectangle {
        id: body
        anchors.fill: parent
        radius: minimalMode ? Theme.radiusMedium : Theme.radiusLarge
        color: Theme.cardBackground
        border.color: isFocused ? Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.6) : Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.2)
        border.width: isFocused ? Theme.borderThick : Theme.borderThin
        clip: true

        Behavior on border.color { ColorAnimation { duration: 300 } }

        // ── NEBULA ATMOSPHERE LAYERS (Solo Full Mode) ──
        
        // Layer 1: Accent Radial Glow (Bottom-Left emanation)
        Rectangle {
            anchors.fill: parent
            radius: body.radius
            visible: !minimalMode
            opacity: isFocused ? 0.2 : 0.1
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.4) }
                GradientStop { position: 0.6; color: Theme.transparent }
            }
            Behavior on opacity { NumberAnimation { duration: 500 } }
        }

        // Layer 2: Bottom atmospheric glow
        Rectangle {
            anchors.fill: parent
            radius: body.radius
            visible: !minimalMode
            opacity: isFocused ? 0.15 : 0.06
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.transparent }
                GradientStop { position: 0.6; color: Theme.transparent }
                GradientStop { position: 1.0; color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.35) }
            }
            Behavior on opacity { NumberAnimation { duration: 500 } }
        }

        // Layer 3: Inner highlight (Top rim light)
        Rectangle {
            anchors.fill: parent
            radius: body.radius
            visible: !minimalMode
            opacity: 0.08
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.textMain }
                GradientStop { position: 0.15; color: Theme.transparent }
            }
        }

        // Minimal Mode: Accent atmosphere (subtle)
        Rectangle {
            anchors.fill: parent
            radius: body.radius
            visible: minimalMode
            opacity: isFocused ? 0.12 : 0.04
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.3) }
                GradientStop { position: 0.7; color: Theme.transparent }
            }
            Behavior on opacity { NumberAnimation { duration: 300 } }
        }

        // ── MOUSE AREA ──
        MouseArea { 
            id: mainMA; anchors.fill: parent; hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: consoleCardRoot.clicked() 
        }

        // ══════════════════════════════════════════════
        // ── CONTENIDO: MODALIDAD MÍNIMA (Chip compacto) ──
        // ══════════════════════════════════════════════
        Row {
            anchors.fill: parent; anchors.margins: Theme.spaceMedium; visible: minimalMode; spacing: Theme.spaceLarge

            Rectangle {
                width: 38; height: 38; radius: Theme.radiusSmall
                color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, isFocused ? 0.25 : 0.15)
                border.color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, isFocused ? 0.6 : 0.3)
                border.width: Theme.borderThin; anchors.verticalCenter: parent.verticalCenter
                Behavior on color { ColorAnimation { duration: 250 } }
                Behavior on border.color { ColorAnimation { duration: 250 } }
                Text { text: iconEmoji; anchors.centerIn: parent; font.pixelSize: Theme.fontHeader }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter; spacing: 2
                Text { text: title.toUpperCase(); color: Theme.textMain; font.pixelSize: Theme.fontBody; font.bold: true; font.letterSpacing: 2 }
                Text { text: gameCount + " " + I18n.t.games_suffix; color: Theme.textMuted; font.pixelSize: Theme.fontMicro; font.bold: true }
            }
        }

        // Minimal Mode: Accent indicator line (bottom edge)
        Rectangle {
            anchors.bottom: parent.bottom; anchors.horizontalCenter: parent.horizontalCenter
            width: isFocused ? parent.width * 0.6 : 0; height: 2; radius: 1
            color: resolvedAccent; visible: minimalMode
            opacity: isFocused ? 0.8 : 0
            Behavior on width { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
            Behavior on opacity { NumberAnimation { duration: 300 } }
        }

        // ══════════════════════════════════════════════
        // ── CONTENIDO: FULL MODE — NEBULA REACTOR HUD ──
        // ══════════════════════════════════════════════
        RowLayout {
            anchors.fill: parent; anchors.margins: 0; spacing: 0; visible: !minimalMode

            // ── LEFT: HERO ZONE (Reactor Core + Title) ──
            Item {
                Layout.fillHeight: true; Layout.preferredWidth: parent.width * 0.38
                
                // Ghost Emoji (Ultra-sutil background texture)
                Text {
                    text: iconEmoji; font.pixelSize: 200; opacity: 0.03
                    anchors.centerIn: parent; anchors.verticalCenterOffset: -20
                }

                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 30; spacing: 12

                    Item { Layout.fillHeight: true; Layout.preferredHeight: 1 }

                    // ── REACTOR CORE ──
                    Item {
                        Layout.alignment: Qt.AlignHCenter
                        Layout.preferredWidth: 120; Layout.preferredHeight: 120

                        // Orbital Halo 1 (Circle — slow rotation)
                        Rectangle {
                            anchors.centerIn: parent; width: 110; height: 110; radius: 55
                            color: Theme.transparent; border.color: resolvedAccent; border.width: 1.5; opacity: 0.2
                            RotationAnimation on rotation { from: 0; to: 360; duration: 15000; loops: Animation.Infinite }
                        }

                        // Orbital Halo 2 (Square — counter-rotation)
                        Rectangle {
                            anchors.centerIn: parent; width: 100; height: 100; radius: 18
                            color: Theme.transparent; border.color: resolvedAccent; border.width: 1.5; opacity: 0.12
                            RotationAnimation on rotation { from: 360; to: 0; duration: 20000; loops: Animation.Infinite }
                        }

                        // Core Glow (Pulsating energy)
                        Rectangle {
                            anchors.centerIn: parent; width: 70; height: 70; radius: 35
                            color: resolvedAccent; opacity: 0.08
                            SequentialAnimation on opacity {
                                loops: Animation.Infinite
                                NumberAnimation { from: 0.05; to: 0.15; duration: 2500; easing.type: Easing.InOutSine }
                                NumberAnimation { from: 0.15; to: 0.05; duration: 2500; easing.type: Easing.InOutSine }
                            }
                        }

                        // Icon Container (Solid backing)
                        Rectangle {
                            anchors.centerIn: parent; width: 80; height: 80; radius: 40
                            color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.08)
                            border.color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.25)
                            border.width: 1.5
                            
                            Text { text: iconEmoji; anchors.centerIn: parent; font.pixelSize: 42 }
                        }
                    }

                    // ── CONSOLE TITLE ──
                    ColumnLayout {
                        spacing: 8; Layout.fillWidth: true; Layout.topMargin: 5
                        
                        Text {
                            Layout.fillWidth: true; text: (I18n.t[fullName] || fullName).toUpperCase(); color: Theme.textMain
                            font.pixelSize: 17; font.bold: true; horizontalAlignment: Text.AlignHCenter
                            font.letterSpacing: 3; wrapMode: Text.WordWrap; maximumLineCount: 2
                        }
                        
                        // Accent Divider Line
                        Item {
                            Layout.alignment: Qt.AlignHCenter; Layout.preferredHeight: 3
                            Layout.preferredWidth: isFocused ? 50 : 30

                            Rectangle {
                                anchors.fill: parent; radius: 1.5
                                gradient: Gradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop { position: 0.0; color: Theme.transparent }
                                    GradientStop { position: 0.3; color: resolvedAccent }
                                    GradientStop { position: 0.7; color: resolvedAccent }
                                    GradientStop { position: 1.0; color: Theme.transparent }
                                }
                            }

                            Behavior on Layout.preferredWidth { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
                        }
                    }
                    
                    Item { Layout.fillHeight: true; Layout.preferredHeight: 1 }
                }
            }

            // ── SEPARATOR (Vertical accent line) ──
            Rectangle { 
                Layout.fillHeight: true; Layout.topMargin: 35; Layout.bottomMargin: 35
                width: 1; opacity: 0.15; visible: !minimalMode
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Theme.transparent }
                    GradientStop { position: 0.3; color: resolvedAccent }
                    GradientStop { position: 0.7; color: resolvedAccent }
                    GradientStop { position: 1.0; color: Theme.transparent }
                }
            }

            // ── RIGHT: DATA HUD ──
            ColumnLayout {
                Layout.fillWidth: true; Layout.fillHeight: true
                Layout.margins: 30; Layout.leftMargin: 35; spacing: 18
                visible: !minimalMode

                // 1. EMULATOR/CORE INFO
                ColumnLayout {
                    spacing: 10
                    Text { 
                        text: I18n.t.config_active_caps
                        color: Theme.textMuted; font.pixelSize: 9; font.bold: true; font.letterSpacing: 2; opacity: 0.8
                    }
                    Flow {
                        Layout.fillWidth: true; spacing: 8
                        Repeater {
                            model: hasCore ? emulatorName.split(" | ") : []
                            delegate: Rectangle {
                                height: 30; radius: 15; implicitWidth: emuRow.width + 30
                                color: Theme.backgroundPod
                                border.color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.25)
                                border.width: 1
                                
                                Row {
                                    id: emuRow; anchors.centerIn: parent; spacing: 8
                                    
                                    // LED Status Dot
                                    Rectangle { 
                                        width: 6; height: 6; radius: 3; color: resolvedAccent
                                        anchors.verticalCenter: parent.verticalCenter
                                        
                                        // Subtle glow around dot
                                        Rectangle {
                                            anchors.centerIn: parent; width: 14; height: 14; radius: 7
                                            color: resolvedAccent; opacity: 0.15; z: -1
                                        }
                                    }
                                    Text { 
                                        text: modelData; color: Theme.textMain
                                        font.pixelSize: 11; font.bold: true; font.letterSpacing: 0.5
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                }
                            }
                        }
                    }
                    
                    // No-core warning
                    Text {
                        visible: !hasCore
                        text: "⚠ " + I18n.t.core_available
                        color: Theme.statusWarning; font.pixelSize: 11; font.bold: true
                        opacity: 0.7
                    }
                }

                // 2. DATA PODS (Stats — Dashboard aesthetic)
                RowLayout {
                    spacing: 15; Layout.fillWidth: true; Layout.topMargin: 5

                    // Games Pod
                    Rectangle {
                        Layout.fillWidth: true; height: 70; radius: 14
                        color: Theme.backgroundPod
                        border.color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, isFocused ? 0.2 : 0.08)
                        border.width: 1

                        ColumnLayout {
                            anchors.centerIn: parent; spacing: -1
                            Text { 
                                text: I18n.t.library.toUpperCase()
                                color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 2
                                Layout.alignment: Qt.AlignHCenter
                            }
                            Text {
                                text: gameCount
                                color: Theme.textMain; font.pixelSize: 32; font.bold: true
                                Layout.alignment: Qt.AlignHCenter
                            }
                            Text { 
                                text: I18n.t.games_abbr
                                color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.7)
                                font.pixelSize: 9; font.bold: true; font.letterSpacing: 1
                                Layout.alignment: Qt.AlignHCenter
                            }
                        }

                        Behavior on border.color { ColorAnimation { duration: 300 } }
                    }

                    // Play Time Pod
                    Rectangle {
                        Layout.fillWidth: true; height: 70; radius: 14
                        color: Theme.backgroundPod
                        border.color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, isFocused ? 0.2 : 0.08)
                        border.width: 1

                        ColumnLayout {
                            anchors.centerIn: parent; spacing: -1
                            Text { 
                                text: I18n.t.play_time_abbr.toUpperCase()
                                color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 2
                                Layout.alignment: Qt.AlignHCenter
                            }
                            Text {
                                text: playTime
                                color: Theme.textMain; font.pixelSize: 32; font.bold: true
                                Layout.alignment: Qt.AlignHCenter
                            }
                            Text { 
                                text: "⏱"
                                color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.5)
                                font.pixelSize: 9
                                Layout.alignment: Qt.AlignHCenter
                            }
                        }

                        Behavior on border.color { ColorAnimation { duration: 300 } }
                    }
                }

                Item { Layout.fillHeight: true }
                
                // 3. CTA BUTTON — "ENTER LIBRARY"
                Rectangle {
                    Layout.fillWidth: true; height: 50; radius: 12
                    color: Theme.transparent
                    border.color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, isFocused ? 0.5 : 0.25)
                    border.width: 1.5

                    // Gradient fill on hover
                    Rectangle {
                        anchors.fill: parent; radius: parent.radius
                        opacity: isFocused ? 1.0 : 0
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.2) }
                            GradientStop { position: 1.0; color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.05) }
                        }
                        Behavior on opacity { NumberAnimation { duration: 300 } }
                    }

                    // Button content
                    RowLayout {
                        anchors.centerIn: parent; spacing: 10
                        Text {
                            text: I18n.t.enter_library_caps
                            color: isFocused ? Theme.textMain : Theme.textDim
                            font.bold: true; font.letterSpacing: 2; font.pixelSize: 11
                            Behavior on color { ColorAnimation { duration: 250 } }
                        }
                    }

                    // Bottom accent line (progress-like indicator)
                    Rectangle {
                        anchors.bottom: parent.bottom; anchors.bottomMargin: 4
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: isFocused ? parent.width * 0.4 : 0; height: 2; radius: 1
                        color: resolvedAccent; opacity: isFocused ? 0.6 : 0
                        Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
                        Behavior on opacity { NumberAnimation { duration: 300 } }
                    }
                    
                    Behavior on border.color { ColorAnimation { duration: 300 } }
                }
            }
        }
    }
}
