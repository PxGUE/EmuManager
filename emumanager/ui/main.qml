import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects
import EmuManager.Controllers 1.0
import "components"
import "views"

ApplicationWindow {
    id: window
    visible: true
    width: 1280; height: 800
    title: "EmuManager"
    
    Material.theme: Material.Dark
    Material.accent: Theme.accentColor

    // --- MOTOR DE PROGRESO DE ARRANQUE REAL ---
    property bool isLoaded: false
    property string activeViewId: "dashboardView"
    property real startupProgress: 0.0
    property string startupStatus: I18n.t.initializing
    property color globalAccentColor: Theme.accentColor

    Connections {
        target: controller
        function onStartupProgressChanged(p) { window.startupProgress = p }
        function onStartupStatusChanged(s) { window.startupStatus = I18n.tp(s) }
        function onStartupFinished() { window.isLoaded = true }
    }

    Component.onCompleted: {
        controller.start_startup_sequence()
    }


    // Alias para compatibilidad con las vistas hijas
    // Referencia para compatibilidad con las vistas hijas
    property QtObject controller: mainController

    ListModel {
        id: navModel
        ListElement { key: "dashboard"; icon: "🏠"; file: "views/Dashboard.qml"; viewId: "dashboardView" }
        ListElement { key: "library"; icon: "📚"; file: "views/Library.qml"; viewId: "libraryView" }
        ListElement { key: "downloads"; icon: "📥"; file: "views/Downloads.qml"; viewId: "downloadsView" }
        ListElement { key: "settings"; icon: "⚙️"; file: "views/Settings.qml"; viewId: "settingsView" }
    }

    // --- 1. PANTALLA DE CARGA (Modular + Logo Herencia) ---
    EmuSplash { id: splashScreen; isLoaded: window.isLoaded; progress: window.startupProgress; statusText: window.startupStatus }

    // --- 2. ESTRUCTURA PRINCIPAL (Animación Premium) ---
    RowLayout {
        id: mainLayout
        anchors.fill: parent; spacing: 0
        opacity: isLoaded ? 1 : 0; scale: isLoaded ? 1.0 : 0.98
        Behavior on opacity { NumberAnimation { duration: 800; easing.type: Easing.OutCubic } }
        Behavior on scale { NumberAnimation { duration: 1000; easing.type: Easing.OutBack } }

        layer.enabled: globalDetails.visible
        layer.effect: FastBlur { radius: 32 }
        
        Rectangle {
            id: sidebar; Layout.preferredWidth: 240; Layout.fillHeight: true; color: Theme.sidebarBackground
            // Subtle border to the right (following global accent)
            Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: window.globalAccentColor; opacity: 0.2 }
            
            x: isLoaded ? 0 : -50
            Behavior on x { 
                SequentialAnimation { 
                    PauseAnimation { duration: 200 } 
                    NumberAnimation { duration: 800; easing.type: Easing.OutCubic } 
                } 
            }
            
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 20; spacing: 10
                Item { Layout.preferredHeight: 40 }
                Repeater {
                    model: navModel
                    delegate: Button {
                        Layout.fillWidth: true; Layout.preferredHeight: 50; flat: true; padding: 15
                        highlighted: activeViewId === model.viewId
                        
                        background: Rectangle {
                            radius: 12
                            color: highlighted ? Theme.panelBackground : Theme.transparent
                            opacity: 0.3
                            Behavior on opacity { NumberAnimation { duration: 200 } }
                        }

                        contentItem: RowLayout {
                            spacing: 15
                            Text { text: model.icon; font.pixelSize: 18; opacity: highlighted ? 1.0 : 0.4; color: highlighted ? window.globalAccentColor : Theme.textMain }
                            Text { 
                                text: (I18n.t[model.key] || "").toUpperCase()
                                color: highlighted ? Theme.textMain : Theme.textDim
                                font.pixelSize: 11; font.bold: highlighted; font.letterSpacing: 2 
                            }
                        }
                        onClicked: activeViewId = model.viewId
                    }
                }
                Item { Layout.fillHeight: true }
                Text { text: "v" + mainController.appVersion + "-MANGO"; color: Theme.textMuted; opacity: 0.3; font.pixelSize: 9; Layout.alignment: Qt.AlignHCenter }
            }
        }

        // --- 2. ÁREA CENTRAL (Vistas) ---
        Item {
            Layout.fillWidth: true; Layout.fillHeight: true; clip: true
            Repeater {
                model: navModel
                delegate: Loader {
                    anchors.fill: parent; asynchronous: true; active: true; source: model.file; visible: window.activeViewId === model.viewId
                    opacity: visible ? 1 : 0; scale: visible ? 1 : 0.99
                    Behavior on opacity { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
                }
            }
        }
    }

    // --- 3. MOTOR DE DETALLES GLOBAL (Unificado) ---
    function openGameDetails(gameId) {
        var data = mainController.get_game_details(gameId)
        if (data.id) {
            globalDetails.gameId = data.id
            globalDetails.title = data.title
            globalDetails.platform = data.platform
            globalDetails.developer = data.developer
            globalDetails.genre = data.genre
            globalDetails.releaseDate = data.release_date
            globalDetails.description = data.description
            globalDetails.cover2d = data.cover2d
            globalDetails.cover3d = data.cover3d
            
            // Identidad visual dinámica heredada de Theme.qml
            var plat = data.platform.toLowerCase()
            if (plat.includes("gba")) globalDetails.accentColor = Theme.platGba
            else if (plat.includes("snes") || plat.includes("super nintendo")) globalDetails.accentColor = Theme.platSnes
            else if (plat.includes("n64")) globalDetails.accentColor = Theme.platN64
            else if (plat.includes("ps1")) globalDetails.accentColor = Theme.platPs1
            else if (plat.includes("psp")) globalDetails.accentColor = Theme.platPsp
            else if (plat.includes("ds")) globalDetails.accentColor = Theme.platDs
            else globalDetails.accentColor = Theme.accentColor
            
            globalDetails.visible = true
        }
    }

    GameDetailsView {
        id: globalDetails
        visible: false
        onClosed: visible = false
    }

    // --- 4. SISTEMA DE NOTIFICACIONES GLOBAL (Toast Manager) ---
    function pushNotification(title, sender, message, color) {
        var component = Qt.createComponent("components/NotificationToast.qml")
        
        function createToast() {
            if (component.status === Component.Ready) {
                var props = {
                    "title": title || "Notificación",
                    "sender": sender || "Sistema",
                    "message": message || "",
                    "accentColor": color || Theme.accentColor,
                    "z": 1000
                }
                var toast = component.createObject(toastStack, props)
                if (toast) {
                    toast.closed.connect(function() { toast.destroy() })
                }
            } else if (component.status === Component.Error) {
                console.log("Error cargando NotificationToast:", component.errorString())
            }
        }

        if (component.status === Component.Ready) {
            createToast()
        } else {
            component.statusChanged.connect(createToast)
        }
    }

    Item {
        id: notificationContainer
        anchors.right: parent.right; anchors.bottom: parent.bottom
        anchors.margins: 20; width: 340; height: parent.height
        z: 9999; clip: false

        // Notar: Los Toasts se posicionan por su propia x/y dinámicamente o por ColumnLayout
        // Para simplificar el apilamiento sin romper las animaciones individuales x/y:
        ColumnLayout {
            anchors.bottom: parent.bottom; spacing: 10; width: parent.width
            id: toastStack
            // El contenedor padre del createObject es notificationContainer, 
            // pero podemos moverlos al ColumnLayout si queremos apilamiento vertical real.
            // Para este caso, el pushNotification los crea como hijos de notificationContainer
            // y el toastRoot en NotificationToast.qml maneja su x inicial.
            // Ajustamos pushNotification para que el parent sea toastStack.
        }
    }
}
