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
    Material.accent: "#16a085"

    // --- MOTOR DE PROGRESO DE ARRANQUE REAL ---
    property bool isLoaded: false
    property string activeViewId: "dashboardView"
    property real startupProgress: 0.0
    property string startupStatus: "INICIALIZANDO..."

    Connections {
        target: controller
        function onStartupProgressChanged(p) { window.startupProgress = p }
        function onStartupStatusChanged(s) { window.startupStatus = s }
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
        ListElement { name: "DASHBOARD"; icon: "🏠"; file: "views/Dashboard.qml"; viewId: "dashboardView" }
        ListElement { name: "BIBLIOTECA"; icon: "📚"; file: "views/Library.qml"; viewId: "libraryView" }
        ListElement { name: "DESCARGAS"; icon: "📥"; file: "views/Downloads.qml"; viewId: "downloadsView" }
        ListElement { name: "CONFIGURACIÓN"; icon: "⚙️"; file: "views/Settings.qml"; viewId: "settingsView" }
    }

    // --- 1. PANTALLA DE CARGA (Modular + Logo Herencia) ---
    EmuSplash { id: splashScreen; isLoaded: window.isLoaded; progress: window.startupProgress; statusText: window.startupStatus }

    // --- 2. ESTRUCTURA PRINCIPAL (Animación Premium) ---
    RowLayout {
        anchors.fill: parent; spacing: 0
        opacity: isLoaded ? 1 : 0; scale: isLoaded ? 1.0 : 0.98
        Behavior on opacity { NumberAnimation { duration: 800; easing.type: Easing.OutCubic } }
        Behavior on scale { NumberAnimation { duration: 1000; easing.type: Easing.OutBack } }

        // Sidebar
        Rectangle {
            id: sidebar; Layout.preferredWidth: 240; Layout.fillHeight: true; color: "#0a0a0c"
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
                        contentItem: RowLayout {
                            spacing: 15
                            Text { text: model.icon; font.pixelSize: 18; opacity: highlighted ? 1.0 : 0.5 }
                            Text { text: model.name; color: highlighted ? "white" : "#66ffffff"; font.pixelSize: 11; font.bold: highlighted; font.letterSpacing: 2 }
                        }
                        onClicked: activeViewId = model.viewId
                    }
                }
                Item { Layout.fillHeight: true }
                Text { text: "v0.1.0-alpha"; color: "#22ffffff"; font.pixelSize: 9; Layout.alignment: Qt.AlignHCenter }
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
