import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects
import "../components"

Popup {
    id: root
    anchors.centerIn: parent; width: 600; height: 500; modal: true; focus: true
    padding: 0; background: Item {} 

    // Referencia al controlador de la Main UI
    property var controller: null
    property bool isRetroArchInstalled: false
    property bool isGlobalBusy: false

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
        anchors.fill: parent; radius: 24; color: Theme.cardBackground; border.color: Theme.accentColor; border.width: 1; opacity: 0.95

        ColumnLayout {
            anchors.fill: parent; anchors.margins: 25; spacing: 15
            
            RowLayout {
                Layout.fillWidth: true
                ColumnLayout {
                    Text { text: I18n.t.ra_settings; color: Theme.textMain; font.pixelSize: 18; font.bold: true; font.letterSpacing: 1.5 }
                    Text { 
                        text: isRetroArchInstalled ? I18n.t.ra_management : I18n.t.ra_not_detected
                        color: isRetroArchInstalled ? Theme.accentColor : Theme.danger
                        font.pixelSize: 9; font.bold: true 
                    }
                }
                Item { Layout.fillWidth: true }
                Button {
                    text: "✕"; flat: true; onClicked: root.close()
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

            // Warning Banner
            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: 40; radius: 10
                color: Theme.danger; opacity: 0.1; border.color: Theme.danger; border.width: 1; visible: !isRetroArchInstalled
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 15; spacing: 10
                    Text { text: "ℹ️"; font.pixelSize: 14 }
                    Text { 
                        text: I18n.t.ra_install_warning; 
                        color: Theme.danger; font.pixelSize: 10; font.bold: true 
                    }
                }
            }

            ListView {
                id: coresList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 10
                model: ListModel { id: coresModel }
                opacity: (isRetroArchInstalled && !isGlobalBusy) ? 1.0 : 0.4
                enabled: isRetroArchInstalled && !isGlobalBusy

                delegate: Rectangle {
                    width: coresList.width - 10; height: 75; radius: 15; color: Theme.controlBackground
                    
                    RowLayout {
                        anchors.fill: parent; anchors.margins: 15; spacing: 15
                        
                        Rectangle { width: 45; height: 45; radius: 10; color: Theme.cardBorder
                            Text { anchors.centerIn: parent; text: "🧩"; font.pixelSize: 22 }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 2
                            Text { 
                                text: model.name; color: Theme.textMain; font.pixelSize: 13; font.bold: true
                                elide: Text.ElideRight; Layout.fillWidth: true
                            }
                            Text { 
                                text: model.isInstalled ? I18n.t.core_ready : I18n.t.core_available
                                color: Theme.textMuted; font.pixelSize: 9 
                            }
                            
                            // Barra de progreso individual
                            Rectangle {
                                visible: model.isDownloading; Layout.fillWidth: true; height: 3; color: Theme.viewBackground; radius: 1.5
                                Rectangle { width: parent.width * model.progress; height: 3; color: Theme.accentColor; radius: 1.5 }
                            }
                        }

                        Button {
                            id: actionBtn
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            implicitWidth: 100; implicitHeight: 32
                            text: {
                                if (model.isDownloading) return "..."
                                if (model.isInstalled) return I18n.t.btn_delete
                                return I18n.t.btn_install
                            }
                            
                            enabled: !model.isDownloading
                            
                            background: Rectangle {
                                color: {
                                    if (model.isInstalled) return (actionBtn.hovered && actionBtn.enabled) ? Theme.danger + "33" : Theme.transparent
                                    return (actionBtn.hovered && actionBtn.enabled) ? Theme.accentColor + "33" : Theme.accentColor
                                }
                                border.color: actionBtn.enabled ? (model.isInstalled ? Theme.danger : Theme.accentColor) : Theme.cardBorder
                                border.width: 1; radius: 10
                                opacity: actionBtn.enabled ? 1.0 : 0.3
                            }
                            
                            contentItem: Text {
                                text: actionBtn.text; color: Theme.textMain; font.pixelSize: 9; font.bold: true
                                horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                            }

                            onClicked: {
                                if (model.isInstalled) {
                                    root.controller.uninstall_core(model.id)
                                    model.isInstalled = false
                                } else {
                                    model.isDownloading = true
                                    root.controller.start_core_download(model.id)
                                }
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
            isRetroArchInstalled = root.controller.is_emulator_installed("retroarch")
            var clist = root.controller.fetch_available_cores()
            for(var i=0; i < clist.length; i++) {
                coresModel.append({
                    "id": clist[i].id,
                    "name": clist[i].name,
                    "progress": 0.0,
                    "isDownloading": false,
                    "isInstalled": clist[i].isInstalled 
                })
            }
        }
    }
}
