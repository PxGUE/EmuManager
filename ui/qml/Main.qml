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
    title: ((bridge ? bridge.currentLanguage : ""), (bridge ? bridge.appName : "EmuManager") + " " + (bridge ? bridge.appVersion : ""))
    color: "#0f111a"

    // Helper para traducciones reactivas
    function tr(key, arg) {
        if (!bridge) return key
        var _ = bridge.currentLanguage // Fuerza dependencia
        if (arg !== undefined) return bridge.translateWithArg(key, String(arg))
        return bridge.translate(key)
    }

    // Fondo base
    Rectangle {
        anchors.fill: parent
        color: "#0f111a"
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // --- SIDEBAR ---
        Rectangle {
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
        
        let state = bridge.checkLaunchState(game_path)
        
        if (state === 0) {
            // Caso 0: Nada ejecutándose, lanzar directo
            bridge.launchGame(game_path, emu_id)
        } 
        else if (state === 2) {
            // Caso 2: Es el mismo juego que ya está abierto
            globalDialog.title = "JUEGO EN CURSO"
            globalDialog.message = "¡" + game_name + " ya se está ejecutando! Vuelve a la ventana del emulador para continuar jugando."
            globalDialog.isInfoOnly = true
            globalDialog.accentColor = "#4da6ff"
            globalDialog.open()
        } 
        else {
            // Caso 1: Hay OTRO juego abierto
            pendingLaunch = { path: game_path, id: emu_id }
            globalDialog.title = "ADVERTENCIA DE SESIÓN"
            globalDialog.message = "Actualmente tienes una partida activa en \"" + bridge.activeGameName + "\".\n\n¿Estás seguro de que quieres cerrar la sesión actual para iniciar \"" + game_name + "\"? Se perderá cualquier progreso que no hayas guardado."
            globalDialog.isInfoOnly = false
            globalDialog.confirmText = "SÍ, CERRAR Y CAMBIAR"
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
                bridge.forceLaunchGame(pendingLaunch.path, pendingLaunch.id)
                pendingLaunch = null
            }
        }
        onCancelled: {
            pendingLaunch = null
        }
    }
}
