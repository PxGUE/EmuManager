import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects

Popup {
    id: root
    anchors.centerIn: parent; width: 600; height: 500; modal: true; focus: true
    padding: 0; background: Item {} 

    // Referencia al controlador de la Main UI
    property var controller: null

    // Señales recibidas desde el Connections global (se vinculan externamente)
    function updateProgress(core_id, p) {
        for(var i=0; i < coresModel.count; i++) {
            if(coresModel.get(i).id === core_id) {
                coresModel.setProperty(i, "progress", p)
                break
            }
        }
    }

    function markFinished(core_id) {
        for(var i=0; i < coresModel.count; i++) {
            if(coresModel.get(i).id === core_id) {
                coresModel.setProperty(i, "progress", 1.0)
                coresModel.setProperty(i, "isDownloading", false)
                coresModel.setProperty(i, "isInstalled", true)
                break
            }
        }
    }

    Rectangle {
        anchors.fill: parent; radius: 24; color: "#0d0d12"; border.color: "#3316a085"; border.width: 1

        ColumnLayout {
            anchors.fill: parent; anchors.margins: 25; spacing: 15
            
            RowLayout {
                Layout.fillWidth: true
                ColumnLayout {
                    Text { text: "AJUSTES: RETROARCH"; color: "white"; font.pixelSize: 18; font.bold: true; font.letterSpacing: 1.5 }
                    Text { text: "Gestión avanzada de núcleos y dependencias de sistema"; color: "#16a085"; font.pixelSize: 9; font.bold: true }
                }
                Item { Layout.fillWidth: true }
                Button {
                    text: "✕"; flat: true; onClicked: root.close()
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: "#1a1a1f" }

            ListView {
                id: coresList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 10
                model: ListModel { id: coresModel }

                delegate: Rectangle {
                    width: coresList.width - 10; height: 75; radius: 15; color: "#16161c"
                    
                    RowLayout {
                        anchors.fill: parent; anchors.margins: 15; spacing: 15
                        
                        Rectangle { width: 45; height: 45; radius: 10; color: "#10ffffff"
                            Text { anchors.centerIn: parent; text: "🧩"; font.pixelSize: 22 }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 2
                            Text { text: model.name; color: "white"; font.pixelSize: 13; font.bold: true }
                            Text { text: "Listo para jugar a " + model.name.split(' ')[0]; color: "#66ffffff"; font.pixelSize: 9 }
                            
                            // Barra de progreso individual
                            Rectangle {
                                visible: model.isDownloading; Layout.fillWidth: true; height: 3; color: "#0a0a0c"; radius: 1.5
                                Rectangle { width: parent.width * model.progress; height: 3; color: "#16a085"; radius: 1.5 }
                            }
                        }

                        Button {
                            implicitWidth: 100; implicitHeight: 32
                            text: model.isInstalled ? "LISTO ✓" : (model.isDownloading ? "..." : "DESCARGAR")
                            enabled: !model.isDownloading && !model.isInstalled
                            Material.background: model.isInstalled ? "transparent" : "#16a085"
                            Material.foreground: model.isInstalled ? "#16a085" : "white"
                            font.pixelSize: 9; font.bold: true
                            onClicked: {
                                model.isDownloading = true
                                root.controller.start_core_download(model.id)
                            }
                        }
                    }
                }
            }
        }
    }

    onOpened: {
        coresModel.clear()
        if (root.controller) {
            var clist = root.controller.fetch_available_cores()
            for(var i=0; i < clist.length; i++) {
                coresModel.append({
                    "id": clist[i].id,
                    "name": clist[i].name,
                    "progress": 0.0,
                    "isDownloading": false,
                    "isInstalled": false 
                })
            }
        }
    }
}
