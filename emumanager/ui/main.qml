import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0

ApplicationWindow {
    visible: true
    width: 1024
    height: 768
    title: "EmuManager"
    
    Material.theme: Material.Dark
    Material.accent: Material.Purple

    // Instancia Global del Controlador Python -> QML
    MainController {
        id: mainCtrl
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // Sidebar de Navegación
        Rectangle {
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            color: "#1e1e1e"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 15

                Text {
                    text: "EmuManager"
                    font.pixelSize: 22
                    font.bold: true
                    color: "white"
                    Layout.alignment: Qt.AlignHCenter
                    Layout.bottomMargin: 20
                }

                Button {
                    text: "Dashboard"
                    Layout.fillWidth: true
                    highlighted: stackView.currentItem.objectName === "dashboardView"
                    onClicked: stackView.replace("views/Dashboard.qml", {objectName: "dashboardView"})
                }

                Button {
                    text: "Settings"
                    Layout.fillWidth: true
                    highlighted: stackView.currentItem.objectName === "settingsView"
                    onClicked: stackView.replace("views/Settings.qml", {objectName: "settingsView"})
                }

                Item {
                    Layout.fillHeight: true // Retainer / Spacer
                }
            }
        }

        // Área Principal de Vistas
        StackView {
            id: stackView
            Layout.fillWidth: true
            Layout.fillHeight: true
            initialItem: "views/Settings.qml"
        }
    }
}
