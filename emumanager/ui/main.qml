import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0
import "components"

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
        anchors.fill: parent; spacing: 0
        opacity: isLoaded ? 1 : 0; scale: isLoaded ? 1.0 : 0.98
        Behavior on opacity { NumberAnimation { duration: 800; easing.type: Easing.OutCubic } }
        Behavior on scale { NumberAnimation { duration: 1000; easing.type: Easing.OutBack } }

        Rectangle {
            id: sidebar; Layout.preferredWidth: 240; Layout.fillHeight: true; color: Theme.sidebarBackground
            // Subtle border to the right
            Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: Theme.cardBorder }
            
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
                            color: highlighted ? Theme.panelBackground : "transparent"
                            opacity: 0.3
                            Behavior on opacity { NumberAnimation { duration: 200 } }
                        }

                        contentItem: RowLayout {
                            spacing: 15
                            Text { text: model.icon; font.pixelSize: 18; opacity: highlighted ? 1.0 : 0.4; color: highlighted ? Theme.accentColor : Theme.textMain }
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
                Text { text: "v0.9.5-MANGO"; color: Theme.textMuted; opacity: 0.3; font.pixelSize: 9; Layout.alignment: Qt.AlignHCenter }
            }
        }

        // Área Central (Precarga MEMORIA)
        Item {
            Layout.fillWidth: true; Layout.fillHeight: true; clip: true
            Repeater {
                model: navModel
                delegate: Loader {
                    anchors.fill: parent; asynchronous: true; active: true; source: model.file; visible: activeViewId === model.viewId
                    opacity: visible ? 1 : 0; scale: visible ? 1 : 0.99
                    Behavior on opacity { NumberAnimation { duration: 250; easing.type: Easing.OutCubic } }
                    Behavior on scale { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
                }
            }
        }
    }
}
