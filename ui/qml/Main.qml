import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects
import "./views"
import "./components"

ApplicationWindow {
    id: window
    width: 1100
    height: 720
    visible: true
    title: bridge ? (bridge.appName + " " + bridge.appVersion) : "EmuManager"
    
    // --- CYBERPUNK NEON GLASS THEME ---
    property color themeBg: "#060711"
    property color themeAccent: "#c084fc"        // Violet primary accent
    property color themeCardBg: Qt.rgba(0.07, 0.05, 0.14, 0.68)
    property color themeBorder: Qt.rgba(0.75, 0.32, 0.98, 0.18)
    property color themeTextMain: "#f0e8ff"
    property color themeTextDim: "#7e7a96"
    property color themeSidebarBg: "#040510"

    // --- NEON PALETTE ---
    property color neonViolet: "#c084fc"         // Violet — main glow
    property color neonMagenta: "#e879f9"        // Magenta — secondary glow
    property color neonGold: "#fbbf24"           // Electric gold
    property color neonBlue: "#60a5fa"           // Cool info blue
    property color neonGreen: "#34d399"          // Success / installed
    property color neonRed: "#f87171"            // Danger / error
    // Compatibility aliases
    property color neonCyan: "#818cf8"           // Indigo as cyan replacement
    property color neonPurple: "#c084fc"
    property color neonPink: "#e879f9"
    property color neonYellow: "#fbbf24"
    
    // Sincronizar fullscreen mediante señal
    Connections {
        target: bridge
        function onIsReadyChanged() {
            if (bridge.isReady) {
                // Forzar refresco si fuera necesario
            }
        }
        function onBridgeStateChanged() {
            window.visibility = bridge.isFullScreen ? Window.FullScreen : Window.Windowed
        }
    }
    color: "#060711"

    Shortcut {
        sequence: "F11"
        onActivated: if (bridge) bridge.toggleFullScreen()
    }

    // Helper para traducciones reactivas
    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage // Forza dependencia Reactiva
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    // Fondo base
    Rectangle {
        anchors.fill: parent
        color: themeBg
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // --- SIDEBAR CYBERPUNK ---
        Rectangle {
            id: sidebar
            Layout.fillHeight: true
            Layout.preferredWidth: 220
            color: themeSidebarBg

            // Subtle right gradient border
            Rectangle {
                anchors.right: parent.right; width: 1; height: parent.height
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "transparent" }
                    GradientStop { position: 0.4; color: Qt.rgba(neonViolet.r, neonViolet.g, neonViolet.b, 0.4) }
                    GradientStop { position: 1.0; color: "transparent" }
                }
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 0
                spacing: 0

                // ── Logo ──
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 72
                    Layout.topMargin: 8

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 2

                        Label {
                            text: bridge ? bridge.appName : "EmuManager"
                            Layout.alignment: Qt.AlignHCenter
                            font.pixelSize: 16
                            font.weight: Font.Black
                            font.letterSpacing: 1.5
                            color: neonViolet
                            renderType: Text.NativeRendering
                            layer.enabled: true
                            layer.effect: MultiEffect {
                                shadowEnabled: true
                                shadowColor: neonMagenta
                                shadowBlur: 1.5
                                shadowOpacity: 0.9
                            }
                        }
                        Label {
                            text: "EMULATION MANAGER"
                            Layout.alignment: Qt.AlignHCenter
                            font.pixelSize: 7
                            font.bold: true
                            font.letterSpacing: 3
                            color: Qt.rgba(neonViolet.r, neonViolet.g, neonViolet.b, 0.45)
                        }
                    }
                }

                // Divider
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    Layout.leftMargin: 20
                    Layout.rightMargin: 20
                    Layout.bottomMargin: 8
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "transparent" }
                        GradientStop { position: 0.5; color: Qt.rgba(neonViolet.r, neonViolet.g, neonViolet.b, 0.35) }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }

                // ── Nav Menu ──
                ListView {
                    id: sidebarList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.topMargin: 6
                    model: ListModel {
                        ListElement { name: "nav_home"; icon: "home"; index: 0 }
                        ListElement { name: "nav_library"; icon: "library"; index: 1 }
                        ListElement { name: "nav_downloads"; icon: "downloads"; index: 2 }
                        ListElement { name: "nav_settings"; icon: "settings"; index: 3 }
                    }
                    currentIndex: 0

                    delegate: Item {
                        width: parent.width
                        height: 52

                        // Background pill
                        Rectangle {
                            id: highlightBg
                            anchors.fill: parent
                            anchors.topMargin: 3
                            anchors.bottomMargin: 3
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            radius: 14

                            // Active gradient fill
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop {
                                    position: 0.0
                                    color: sidebarList.currentIndex === index
                                        ? Qt.rgba(neonViolet.r, neonViolet.g, neonViolet.b, 0.28)
                                        : (mouseArea.containsMouse ? Qt.rgba(1,1,1,0.05) : "transparent")
                                }
                                GradientStop {
                                    position: 1.0
                                    color: sidebarList.currentIndex === index
                                        ? Qt.rgba(neonMagenta.r, neonMagenta.g, neonMagenta.b, 0.08)
                                        : "transparent"
                                }
                            }
                            Behavior on color { ColorAnimation { duration: 200 } }

                            // Glow border on active
                            border.color: sidebarList.currentIndex === index
                                ? Qt.rgba(neonViolet.r, neonViolet.g, neonViolet.b, 0.5)
                                : (mouseArea.containsMouse ? Qt.rgba(1,1,1,0.08) : "transparent")
                            border.width: 1
                            Behavior on border.color { ColorAnimation { duration: 180 } }
                        }

                        // Left accent bar
                        Rectangle {
                            anchors.left: parent.left
                            anchors.leftMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            width: 3; height: 22; radius: 2
                            color: neonMagenta
                            visible: sidebarList.currentIndex === index
                            layer.enabled: true
                            layer.effect: MultiEffect {
                                shadowEnabled: true
                                shadowColor: neonMagenta
                                shadowBlur: 1.5
                                shadowOpacity: 1.0
                            }
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 30
                            anchors.rightMargin: 16
                            spacing: 13

                            Icon {
                                name: model.icon
                                size: 20
                                color: sidebarList.currentIndex === index ? neonViolet : Qt.rgba(1,1,1,0.35)
                                glow: sidebarList.currentIndex === index
                                glowOpacity: 0.6
                                Behavior on color { ColorAnimation { duration: 200 } }
                            }

                            Text {
                                Layout.fillWidth: true
                                text: tr(model.name)
                                color: sidebarList.currentIndex === index ? themeTextMain : themeTextDim
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 13
                                font.weight: sidebarList.currentIndex === index ? Font.DemiBold : Font.Normal
                                font.letterSpacing: 0.5
                                Behavior on color { ColorAnimation { duration: 200 } }
                            }
                        }

                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: sidebarList.currentIndex = index
                        }
                    }
                }

                // ── Version ──
                Label {
                    text: bridge ? "v" + bridge.appVersion : ""
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    color: Qt.rgba(neonViolet.r, neonViolet.g, neonViolet.b, 0.2)
                    font.pixelSize: 10
                    font.letterSpacing: 1
                    Layout.bottomMargin: 14
                }
            }
        }

        // --- CONTENIDO PRINCIPAL (Con Animaciones Premium) ---
        Item {
            id: mainContentArea
            Layout.fillWidth: true
            Layout.fillHeight: parent
            clip: true // Importante para que el slide no se salga
            
            readonly property int activeIndex: sidebarList.currentIndex

            // Definimos un helper para la animación común
            // Nota: En QML puro dentro de Main, aplicamos la lógica a cada vista
            
            Dashboard { 
                id: dashView
                anchors.fill: parent
                visible: opacity > 0
                opacity: mainContentArea.activeIndex === 0 ? 1 : 0
                // Efecto de desplazamiento: viene desde un pequeño offset
                x: mainContentArea.activeIndex === 0 ? 0 : -40
                
                Behavior on opacity { NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                Behavior on x { NumberAnimation { duration: 500; easing.type: Easing.OutBack } }
            }
            
            Library { 
                id: libraryView
                anchors.fill: parent
                visible: opacity > 0
                opacity: mainContentArea.activeIndex === 1 ? 1 : 0
                x: mainContentArea.activeIndex === 1 ? 0 : -40
                
                Behavior on opacity { NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                Behavior on x { NumberAnimation { duration: 500; easing.type: Easing.OutBack } }
            }
            
            Downloads { 
                id: downloadsView
                anchors.fill: parent
                visible: opacity > 0
                opacity: mainContentArea.activeIndex === 2 ? 1 : 0
                x: mainContentArea.activeIndex === 2 ? 0 : -40
                
                Behavior on opacity { NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                Behavior on x { NumberAnimation { duration: 500; easing.type: Easing.OutBack } }
            }
            
            Settings { 
                id: settingsView
                anchors.fill: parent
                visible: opacity > 0
                opacity: mainContentArea.activeIndex === 3 ? 1 : 0
                x: mainContentArea.activeIndex === 3 ? 0 : -40
                
                Behavior on opacity { NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                Behavior on x { NumberAnimation { duration: 500; easing.type: Easing.OutBack } }
            }
        }
    }

    // --- SISTEMA DE DIÁLOGOS GLOBALES ---
    property var pendingLaunch: null

    function requestLaunch(game_path, emu_id, game_name) {
        if (!bridge) return;
        
        let state = bridge.lib.checkLaunchState(game_path)
        
        if (state === 0) {
            // Caso 0: Nada ejecutándose, lanzar directo
            bridge.lib.launchGame(game_path, emu_id)
        } 
        else if (state === 2) {
            // Caso 2: Es el mismo juego que ya está abierto
            globalDialog.title = tr("dlg_session_title")
            globalDialog.message = tr("dlg_session_playing", game_name)
            globalDialog.isInfoOnly = true
            globalDialog.accentColor = "#4da6ff"
            globalDialog.open()
        } 
        else {
            // Caso 1: Hay OTRO juego abierto
            pendingLaunch = { path: game_path, id: emu_id }
            globalDialog.title = tr("dlg_warn_title")
            globalDialog.message = tr("dlg_warn_msg", bridge.activeGameName, game_name)
            globalDialog.isInfoOnly = false
            globalDialog.confirmText = tr("dlg_btn_change")
            globalDialog.accentColor = "#ff4d4d"
            globalDialog.open()
        }
    }

    CustomDialog {
        id: globalDialog
        anchors.centerIn: parent
        z: 9999
        onConfirmed: {
            if (pendingLaunch) {
                bridge.lib.forceLaunchGame(pendingLaunch.path, pendingLaunch.id)
                pendingLaunch = null
            }
        }
        onCancelled: {
            pendingLaunch = null
        }
    }

    Rectangle {
        id: splashScreen
        anchors.fill: parent
        z: 10000
        color: themeBg

        property real currentProgress: 0
        property bool isFinished: false

        visible: opacity > 0
        opacity: isFinished ? 0 : 1
        Behavior on opacity { NumberAnimation { duration: 700; easing.type: Easing.InOutQuad } }

        // Ambient orb glow
        Rectangle {
            anchors.centerIn: parent
            width: 600; height: 600; radius: 300
            opacity: 0.07
            gradient: Gradient {
                GradientStop { position: 0.0; color: neonViolet }
                GradientStop { position: 0.5; color: neonMagenta }
                GradientStop { position: 1.0; color: "transparent" }
            }
            SequentialAnimation on scale {
                loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: 1.3; duration: 4000; easing.type: Easing.InOutSine }
                NumberAnimation { from: 1.3; to: 1.0; duration: 4000; easing.type: Easing.InOutSine }
            }
        }

        NumberAnimation on currentProgress {
            id: loadingAnim
            from: 0; to: 0.85; duration: 5000; easing.type: Easing.OutCubic
            running: bridge ? !bridge.isReady : true
        }
        Connections {
            target: bridge
            function onIsReadyChanged() {
                if (bridge && bridge.isReady) { loadingAnim.stop(); finishAnim.start() }
            }
        }
        NumberAnimation on currentProgress {
            id: finishAnim
            to: 1.0; duration: 400; easing.type: Easing.OutQuad
            running: false
            onFinished: splashScreen.isFinished = true
        }

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 44

            // ── Logo ──
            Item {
                Layout.alignment: Qt.AlignHCenter
                width: 160; height: 160

                // Outer pulsing ring
                Rectangle {
                    anchors.centerIn: parent
                    width: 190; height: 190; radius: 95
                    color: "transparent"
                    border.color: neonViolet
                    border.width: 2
                    opacity: 0.3
                    z: -1
                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        NumberAnimation { from: 1.0; to: 1.25; duration: 2200; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.25; to: 1.0; duration: 2200; easing.type: Easing.InOutSine }
                    }
                }
                // Glow orb
                Rectangle {
                    anchors.centerIn: parent
                    width: 160; height: 160; radius: 80
                    opacity: 0.18
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: neonViolet }
                        GradientStop { position: 1.0; color: neonMagenta }
                    }
                    z: -1
                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        NumberAnimation { from: 0.12; to: 0.25; duration: 2000; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 0.25; to: 0.12; duration: 2000; easing.type: Easing.InOutSine }
                    }
                }
                // Logo box
                Rectangle {
                    anchors.centerIn: parent
                    width: 128; height: 128; radius: 42
                    color: Qt.rgba(0.1, 0.07, 0.2, 0.9)
                    border.color: Qt.rgba(neonViolet.r, neonViolet.g, neonViolet.b, 0.6)
                    border.width: 1.5
                    layer.enabled: true
                    layer.effect: MultiEffect {
                        shadowEnabled: true; shadowColor: neonViolet
                        shadowBlur: 1.5; shadowOpacity: 0.6
                    }
                    Image {
                        anchors.fill: parent; anchors.margins: 22
                        source: bridge ? bridge.logoPath : ""
                        fillMode: Image.PreserveAspectFit; smooth: true
                    }
                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        NumberAnimation { from: 1.0; to: 1.04; duration: 1800; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.04; to: 1.0; duration: 1800; easing.type: Easing.InOutSine }
                    }
                }
            }

            ColumnLayout {
                spacing: 4
                Layout.alignment: Qt.AlignHCenter
                Label {
                    text: bridge ? bridge.appName : "EmuManager"
                    font.pixelSize: 68; font.weight: Font.Black
                    color: "white"; font.letterSpacing: -1.5
                    Layout.alignment: Qt.AlignHCenter
                    layer.enabled: true
                    layer.effect: MultiEffect {
                        shadowEnabled: true; shadowColor: neonViolet
                        shadowBlur: 1.2; shadowOpacity: 0.6
                    }
                }
                Label {
                    text: bridge ? bridge.loadingMessage.toUpperCase() : ""
                    font.pixelSize: 10; font.bold: true
                    color: neonMagenta; font.letterSpacing: 3
                    opacity: 0.85
                    Layout.alignment: Qt.AlignHCenter
                    Layout.topMargin: 8
                }
            }

            // ── Progress Bar ──
            Item {
                Layout.preferredWidth: 320; Layout.preferredHeight: 6
                Layout.alignment: Qt.AlignHCenter
                Rectangle {
                    anchors.fill: parent; radius: 3
                    color: Qt.rgba(1,1,1,0.06)
                }
                Rectangle {
                    id: progressFill
                    height: parent.height; radius: 3
                    width: parent.width * splashScreen.currentProgress
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: neonViolet }
                        GradientStop { position: 1.0; color: neonMagenta }
                    }
                    layer.enabled: true
                    layer.effect: MultiEffect {
                        shadowEnabled: true; shadowColor: neonViolet
                        shadowBlur: 1.0; shadowOpacity: 0.8
                    }
                }
            }
        }
    }
}
