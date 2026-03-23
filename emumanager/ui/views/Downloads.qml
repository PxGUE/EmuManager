import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import "../components"

Item {
    id: downloadsRoot
    objectName: "downloadsView"

    // Propiedad para el estado de automatización (Persistente)
    property bool autoDownloadEnabled: true

    // Modelo de Prueba con estados para el auto-limpiado
    ListModel {
        id: downloadsModel
        ListElement { name: "Mupen64Plus_Next"; type: "CORE"; platform: "N64"; progress: 0.65; size: "15.4 MB"; status: "Downloading"; speed: "1.2 MB/s"; accent: "#16a085" }
        ListElement { name: "Dolphin Standalone"; type: "EMULATOR"; platform: "GC"; progress: 0.20; size: "142 MB"; status: "Downloading"; speed: "4.5 MB/s"; accent: "#8e44ad" }
        ListElement { name: "Beetle PSX HW"; type: "CORE"; platform: "PS1"; progress: 1.0; size: "8.2 MB"; status: "Completed"; speed: "0 KB/s"; accent: "#2980b9" }
    }

    // Fondo base
    Rectangle {
        anchors.fill: parent
        color: "#050505"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 40
        spacing: 35

        // CABECERA EVOLUCIONADA (Control de Automatización)
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 4
                Text {
                    text: "GESTOR DE DESCARGAS"
                    color: "white"; font.pixelSize: 28; font.bold: true; font.letterSpacing: 2
                }
                Text {
                    text: "Control inteligente de núcleos y emuladores"
                    color: "#66ffffff"; font.pixelSize: 14; font.bold: true
                }
            }
            Item { Layout.fillWidth: true }
            
            // Switch de Descargas Automáticas (Control del Usuario)
            RowLayout {
                spacing: 15
                Text {
                    text: "DESCARGAS AUTOMÁTICAS"
                    color: autoDownloadEnabled ? "white" : "#44ffffff"
                    font.pixelSize: 10; font.bold: true; font.letterSpacing: 1
                    Behavior on color { ColorAnimation { duration: 200 } }
                }
                Switch {
                    id: autoDownloadSwitch
                    checked: downloadsRoot.autoDownloadEnabled
                    onCheckedChanged: downloadsRoot.autoDownloadEnabled = checked
                    Material.accent: "#16a085"
                }
            }
        }

        // LISTA DE DESCARGAS (Con margen superior para la nueva cabecera)
        Flickable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: width
            contentHeight: downloadsList.implicitHeight
            clip: true
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            Column {
                id: downloadsList
                width: parent.width
                spacing: 16

                Repeater {
                    model: downloadsModel
                    delegate: DownloadItem {
                        width: parent.width
                        itemName: model.name
                        itemType: model.type
                        platform: model.platform
                        progressValue: model.progress
                        totalSize: model.size
                        statusText: model.status
                        downloadSpeed: model.speed
                        accentColor: model.accent
                        
                        // Lógica de auto-limpieza visual (simulada)
                        onProgressValueChanged: {
                            if (progressValue >= 1.0) {
                                // En una app real, aquí se llamaría al backend para quitar de la lista
                                console.log("Descarga completada: " + itemName + " - Auto-limpieza en marcha")
                            }
                        }
                    }
                }
            }
        }
        
        // Estado de "Lista Vacía" (Solo visual para el diseño)
        Text {
            visible: downloadsModel.count === 0
            text: "No hay descargas activas en este momento."
            color: "#33ffffff"
            font.pixelSize: 16; font.bold: true
            Layout.alignment: Qt.AlignCenter
        }
    }
}
