import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "./views"
import "./components"

ApplicationWindow {
    id: window
    width: 1100
    height: 720
    visible: true
    title: bridge ? (bridge.appName + " " + bridge.appVersion) : "EmuManager"
    
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
    color: "#0d0f17"

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
        color: "#0d0f17"
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // --- SIDEBAR ---
        Rectangle {
            id: sidebar
            Layout.fillHeight: parent
            Layout.preferredWidth: 200
            color: "#161922"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 0
                spacing: 0

                // Logo/Nombre
                Label {
                    text: bridge ? bridge.appName : "EmuManager"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 15
                    font.weight: Font.Black
                    color: "#4da6ff"
                    Layout.topMargin: 24
                    Layout.bottomMargin: 8
                    renderType: Text.NativeRendering
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#1a1c24"
                    Layout.leftMargin: 16
                    Layout.rightMargin: 16
                }

                Item { Layout.preferredHeight: 10 }

                // Menú
                ListView {
                    id: sidebarList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: ListModel {
                        ListElement { name: "nav_home"; icon: "🏠"; index: 0 }
                        ListElement { name: "nav_library"; icon: "📚"; index: 1 }
                        ListElement { name: "nav_downloads"; icon: "📥"; index: 2 }
                        ListElement { name: "nav_settings"; icon: "⚙️"; index: 3 }
                    }
                    currentIndex: 0
                    
                    delegate: Item {
                        width: parent.width
                        height: 50
                        
                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: 4
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            radius: 8
                            color: sidebarList.currentIndex === index ? "#2a2f45" : 
                                   (mouseArea.containsMouse ? "#1c1f2b" : "transparent")
                            
                            Behavior on color { ColorAnimation { duration: 150 } }

                            Rectangle {
                                anchors.left: parent.left
                                anchors.verticalCenter: parent.verticalCenter
                                width: 3
                                height: 16
                                radius: 2
                                color: "#4da6ff"
                                visible: sidebarList.currentIndex === index
                            }
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 28
                            spacing: 12

                            Text {
                                text: model.icon
                                font.pixelSize: 14
                                opacity: sidebarList.currentIndex === index ? 1.0 : 0.5
                            }

                            Text {
                                Layout.fillWidth: true
                                text: tr(model.name)
                                color: sidebarList.currentIndex === index ? "white" : "#888899"
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 13
                                font.bold: sidebarList.currentIndex === index
                            }
                        }

                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: sidebarList.currentIndex = index
                        }
                    }
                }

                // Versión
                Label {
                    text: bridge ? "v" + bridge.appVersion : ""
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    color: "#333344"
                    font.pixelSize: 10
                    Layout.bottomMargin: 12
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
        z: 10000 // Por encima de todo
        color: "#0d0f17"
        
        property real currentProgress: 0
        property bool isFinished: false
        
        visible: opacity > 0
        opacity: isFinished ? 0 : 1
        
        Behavior on opacity { 
            NumberAnimation { duration: 600; easing.type: Easing.InOutQuad } 
        }

        // 1. Animación de carga inicial (hasta el 90%)
        NumberAnimation on currentProgress {
            id: loadingAnim
            from: 0; to: 0.85; duration: 5000; easing.type: Easing.OutCubic
            running: bridge ? !bridge.isReady : true
        }

        // 2. Detectar cuando el bridge está listo para terminar la barra
        Connections {
            target: bridge
            function onIsReadyChanged() {
                if (bridge && bridge.isReady) {
                    loadingAnim.stop()
                    finishAnim.start()
                }
            }
        }

        // 3. Animación de cierre (de donde esté al 100%)
        NumberAnimation on currentProgress {
            id: finishAnim
            to: 1.0; duration: 400; easing.type: Easing.OutQuad
            running: false
            onFinished: splashScreen.isFinished = true
        }

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 40
            
            // Logo Oficial Animado
            Item {
                Layout.alignment: Qt.AlignHCenter
                width: 160; height: 160
                
                // Glow ambiental
                Rectangle {
                    anchors.centerIn: parent
                    width: 180; height: 180; radius: 90
                    color: "#4da6ff"
                    opacity: 0.15
                    z: -1
                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        NumberAnimation { from: 1.0; to: 1.2; duration: 2000; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.2; to: 1.0; duration: 2000; easing.type: Easing.InOutSine }
                    }
                }

                Rectangle {
                    anchors.centerIn: parent
                    width: 130; height: 130; radius: 42
                    color: "#161922"
                    border.color: "#4da6ff"
                    border.width: 1
                    
                    Image { 
                        anchors.fill: parent
                        anchors.margins: 25
                        source: bridge ? bridge.logoPath : ""
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                    }
                    
                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        NumberAnimation { from: 1.0; to: 1.05; duration: 1500; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.05; to: 1.0; duration: 1500; easing.type: Easing.InOutSine }
                    }
                }
            }

            ColumnLayout {
                spacing: 0
                Layout.alignment: Qt.AlignHCenter
                Label {
                    text: bridge ? bridge.appName : "EmuManager"
                    font.pixelSize: 72
                    font.weight: Font.Black
                    color: "white"
                    font.letterSpacing: -2
                    Layout.alignment: Qt.AlignHCenter
                }
                Label {
                    text: bridge ? bridge.loadingMessage.toUpperCase() : ""
                    font.pixelSize: 10
                    font.bold: true
                    color: "#4da6ff"
                    font.letterSpacing: 2
                    opacity: 0.8
                    Layout.alignment: Qt.AlignHCenter
                    Layout.topMargin: 10
                }
            }

            // Barra de Carga Minimalista (Sincronizada)
            Rectangle {
                Layout.preferredWidth: 300; Layout.preferredHeight: 2
                color: "#1a1c24"; radius: 1
                Layout.alignment: Qt.AlignHCenter
                Rectangle {
                    id: progressFill
                    height: parent.height; color: "#4da6ff"; radius: 1
                    width: parent.width * splashScreen.currentProgress
                }
            }
        }
    }
}
