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
    
    flags: Qt.Window | Qt.FramelessWindowHint
    
    // Forzamos padding cero para evitar huecos en los bordes
    leftPadding: 0; rightPadding: 0; topPadding: 0; bottomPadding: 0
    
    background: Rectangle { color: Theme.sidebarBackground } // Fondo base sólido para evitar fugas de color
    
    Material.theme: Material.Dark
    Material.accent: Theme.accentColor

    // --- CUSTOM TITLE BAR (PREMIUM ARCHITECTURE) ---
    header: Rectangle {
        id: titleBar
        height: 40
        color: Theme.sidebarBackground
        z: 9999

        RowLayout {
            anchors.fill: parent
            spacing: 0

            // 1. ÁREA DE IZQUIERDA (Logo + Título)
            RowLayout {
                Layout.fillHeight: true
                Layout.leftMargin: 20
                spacing: 15
                
                Item {
                    Layout.preferredWidth: 22; Layout.preferredHeight: 22
                    Image {
                        source: "assets/logo.svg"
                        anchors.fill: parent
                        fillMode: Image.PreserveAspectFit
                        smooth: true; opacity: 0.9
                    }
                    Rectangle {
                        anchors.centerIn: parent; width: 14; height: 14
                        radius: 7; color: Theme.accentColor; z: -1; opacity: 0.15
                        layer.enabled: true
                        layer.effect: FastBlur { radius: 8 }
                    }
                }
                
                Text {
                    text: window.title.toUpperCase()
                    color: Theme.textMain
                    font.pixelSize: 10; font.letterSpacing: 3; font.bold: true
                    opacity: 0.6
                }
            }

            // 2. ÁREA DE ARRASTRE (Flexible Space)
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                DragHandler {
                    id: titleDragHandler
                    onActiveChanged: if (active) window.startSystemMove()
                }
                
                // Área interactiva expandida para el arrastre
                TapHandler {
                    acceptedButtons: Qt.LeftButton
                    onDoubleTapped: window.visibility === Window.Maximized ? window.showNormal() : window.showMaximized()
                }
            }

            // 3. CONTROLES DE VENTANA (Edge-to-Edge)
            Row {
                id: windowControls
                Layout.fillHeight: true
                spacing: 0
                
                component WinButton : Rectangle {
                    id: btnRoot
                    property string icon: ""
                    property color hoverColor: Theme.accentColor
                    property color hoverBg: "#1affffff"
                    property int pixelSize: 16
                    property bool isQuit: false
                    signal clicked()
                    
                    width: 46; height: 40 // Medida estándar balanceada
                    color: hoverHandler.hovered ? (isQuit ? Theme.statusDanger : btnRoot.hoverBg) : "transparent"
                    
                    Text {
                        anchors.centerIn: parent
                        text: btnRoot.icon
                        color: hoverHandler.hovered ? (isQuit ? "#ffffff" : btnRoot.hoverColor) : Theme.textMain
                        font.pixelSize: btnRoot.pixelSize
                        opacity: hoverHandler.hovered ? 1.0 : 0.6
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                    
                    HoverHandler { id: hoverHandler }
                    TapHandler { onTapped: btnRoot.clicked() }
                    
                    Behavior on color { ColorAnimation { duration: 200 } }
                }

                WinButton { 
                    icon: "−"; pixelSize: 20
                    onClicked: window.showMinimized() 
                }
                
                WinButton { 
                    id: maximizeBtn
                    onClicked: window.visibility === Window.Maximized ? window.showNormal() : window.showMaximized() 
                    
                    Item {
                        anchors.centerIn: parent; width: 10; height: 10
                        Rectangle {
                            visible: window.visibility !== Window.Maximized
                            anchors.fill: parent; color: "transparent"; border.width: 1.2
                            border.color: maximizeBtn.hovered ? Theme.accentColor : Theme.textMain
                            opacity: maximizeBtn.hovered ? 1.0 : 0.6
                        }
                        Item {
                            visible: window.visibility === Window.Maximized
                            anchors.fill: parent
                            Rectangle {
                                width: 8; height: 8; anchors.right: parent.right; anchors.top: parent.top
                                color: "transparent"; border.width: 1.2
                                border.color: maximizeBtn.hovered ? Theme.accentColor : Theme.textMain
                            }
                            Rectangle {
                                width: 8; height: 8; anchors.left: parent.left; anchors.bottom: parent.bottom
                                color: Theme.sidebarBackground; border.width: 1.2 
                                border.color: maximizeBtn.hovered ? Theme.accentColor : Theme.textMain
                            }
                        }
                    }
                }

                WinButton { 
                    icon: "✕"; pixelSize: 14; isQuit: true
                    onClicked: window.close() 
                }
            }
        }
        
        // Línea divisoria elegante
        Rectangle {
            anchors.bottom: parent.bottom; width: parent.width; height: 1
            color: Theme.divider; opacity: 0.1
        }
    }

    // --- RESIZING HANDLERS ---
    MouseArea {
        id: topResize; height: 4; anchors { top: parent.top; left: parent.left; right: parent.right }
        cursorShape: Qt.SizeVerCursor
        onPressed: window.startSystemResize(Qt.TopEdge)
    }
    MouseArea {
        id: bottomResize; height: 4; anchors { bottom: parent.bottom; left: parent.left; right: parent.right }
        cursorShape: Qt.SizeVerCursor
        onPressed: window.startSystemResize(Qt.BottomEdge)
    }
    MouseArea {
        id: leftResize; width: 4; anchors { top: parent.top; bottom: parent.bottom; left: parent.left }
        cursorShape: Qt.SizeHorCursor
        onPressed: window.startSystemResize(Qt.LeftEdge)
    }
    MouseArea {
        id: rightResize; width: 4; anchors { top: parent.top; bottom: parent.bottom; right: parent.right }
        cursorShape: Qt.SizeHorCursor
        onPressed: window.startSystemResize(Qt.RightEdge)
    }
    MouseArea {
        id: bottomRightResize; width: 8; height: 8; anchors { bottom: parent.bottom; right: parent.right }
        cursorShape: Qt.SizeFDiagCursor
        onPressed: window.startSystemResize(Qt.RightEdge | Qt.BottomEdge)
    }

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
        
        // --- MOTOR DE NOTIFICACIONES SYNC ---
        function onNotificationRequested(title, message, type) {
            var color = Theme.statusInfo
            if (type === "success") color = Theme.statusSuccess
            else if (type === "error") color = Theme.statusDanger
            
            let tTitle = I18n.t[title] || title
            let tMessage = I18n.tp(message)
            window.pushNotification(tTitle, "M.A.N.G.O Sync", tMessage, color)
        }
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
        opacity: splashScreen.isActuallyDone ? 1 : 0; scale: splashScreen.isActuallyDone ? 1.0 : 0.98
        Behavior on opacity { NumberAnimation { duration: 1000; easing.type: Easing.OutCubic } }
        Behavior on scale { NumberAnimation { duration: 1200; easing.type: Easing.OutBack } }

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
                Text { text: I18n.tp("app_version_label|" + mainController.appVersion) + "-MANGO"; color: Theme.textMuted; opacity: 0.3; font.pixelSize: 9; Layout.alignment: Qt.AlignHCenter }
            }
        }

        // --- 2. ÁREA CENTRAL (Vistas) ---
        Item {
            Layout.fillWidth: true; Layout.fillHeight: true; clip: true
            Repeater {
                model: navModel
                delegate: Loader {
                    anchors.fill: parent; asynchronous: false; active: true; source: model.file; visible: window.activeViewId === model.viewId
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
