import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Popup {
    id: editorPopup
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: 650
    height: 580
    modal: true
    focus: true
    padding: 0
    
    property var gameData: null
    
    // Señal para avisar a la vista que refresque
    signal metadataSaved()

    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    onOpened: {
        if (gameData) {
            titleField.text = gameData.title || gameData.name
            descField.text = gameData.description || ""
            devField.text = gameData.developer || ""
            yearField.text = gameData.year || ""
            genreField.text = gameData.genre || ""
        }
    }

    background: Rectangle {
        color: window.themeSidebarBg
        radius: 30
        border.color: window.themeBorder
        border.width: 1
        
        // Efecto de brillo superior
        Rectangle {
            anchors.top: parent.top
            width: parent.width; height: 100; radius: 30; opacity: 0.1
            gradient: Gradient {
                GradientStop { position: 0.0; color: window.themeAccent }
                GradientStop { position: 1.0; color: "transparent" }
            }
        }
    }

    contentItem: ColumnLayout {
        anchors.fill: parent
        anchors.margins: 35
        spacing: 25

        // Header
        RowLayout {
            spacing: 15
            Rectangle {
                width: 48; height: 48; radius: 14; color: window.themeCardBg
                border.color: window.themeBorder; border.width: 1
                Icon { anchors.centerIn: parent; name: "edit"; size: 20; color: "white" }
            }
            ColumnLayout {
                spacing: 2
                Label {
                    text: tr("set_dlg_config_title", tr("nav_library"))
                    font.pixelSize: 22; font.bold: true; color: "white"
                }
                Label {
                    text: tr("lib_status_processing").toUpperCase()
                    font.pixelSize: 10; font.bold: true; color: "#4da6ff"; font.letterSpacing: 2
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 30

            // Izquierda: Previsualización
            ColumnLayout {
                Layout.preferredWidth: 200
                spacing: 15
                
                Rectangle {
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: 280
                    color: "#0dffffff"
                    radius: 15
                    clip: true
                    border.color: "#252835"
                    
                    Image {
                        anchors.fill: parent
                        source: gameData ? gameData.cover : ""
                        fillMode: Image.PreserveAspectCrop
                        opacity: status === Image.Ready ? 1 : 0
                        Behavior on opacity { NumberAnimation { duration: 300 } }
                    }
                    
                    Rectangle {
                        anchors.fill: parent
                        visible: !gameData || !gameData.cover
                        color: "transparent"
                        Icon { anchors.centerIn: parent; name: "library"; size: 40; color: "white"; opacity: 0.1 }
                    }
                }
                
                Label {
                    text: gameData ? gameData.console : ""
                    font.pixelSize: 12; font.bold: true; color: "#666677"
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Item { Layout.fillHeight: true }
            }

            // Derecha: Formulario
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentWidth: availableWidth
                clip: true

                ColumnLayout {
                    width: parent.width
                    spacing: 20

                    // Título
                    ColumnLayout {
                        spacing: 8; Layout.fillWidth: true
                        Label { text: tr("lib_title"); font.pixelSize: 12; color: "#888899" }
                        TextField {
                            id: titleField
                            Layout.fillWidth: true; selectByMouse: true
                            placeholderText: "Nombre del juego..."
                            color: "white"
                            background: Rectangle { color: "#0f111a"; radius: 10; border.color: parent.activeFocus ? window.themeAccent : window.themeBorder }
                        }
                    }

                    // Otros campos en Grid
                    GridLayout {
                        columns: 2
                        columnSpacing: 15; rowSpacing: 20
                        Layout.fillWidth: true

                        ColumnLayout {
                            spacing: 8; Layout.fillWidth: true
                            Label { text: tr("lib_year"); font.pixelSize: 12; color: "#888899" }
                            TextField {
                                id: yearField
                                Layout.fillWidth: true; selectByMouse: true
                                placeholderText: "Ej: 1998"
                                color: "white"
                                background: Rectangle { color: "#0f111a"; radius: 10; border.color: parent.activeFocus ? window.themeAccent : window.themeBorder }
                            }
                        }

                        ColumnLayout {
                            spacing: 8; Layout.fillWidth: true
                            Label { text: tr("lib_genre"); font.pixelSize: 12; color: "#888899" }
                            TextField {
                                id: genreField
                                Layout.fillWidth: true; selectByMouse: true
                                placeholderText: "Ej: RPG"
                                color: "white"
                                background: Rectangle { color: "#0f111a"; radius: 10; border.color: parent.activeFocus ? window.themeAccent : window.themeBorder }
                            }
                        }

                        ColumnLayout {
                            spacing: 8; Layout.fillWidth: true; Layout.columnSpan: 2
                            Label { text: tr("lib_developer"); font.pixelSize: 12; color: "#888899" }
                            TextField {
                                id: devField
                                Layout.fillWidth: true; selectByMouse: true
                                color: "white"
                                background: Rectangle { color: "#0f111a"; radius: 10; border.color: parent.activeFocus ? window.themeAccent : window.themeBorder }
                            }
                        }
                    }

                    // Descripción
                    ColumnLayout {
                        spacing: 8; Layout.fillWidth: true
                        Label { text: tr("lib_desc"); font.pixelSize: 12; color: "#888899" }
                        TextArea {
                            id: descField
                            Layout.fillWidth: true; Layout.preferredHeight: 120
                            wrapMode: TextEdit.WordWrap; selectByMouse: true
                            placeholderText: "Escribe la historia del juego..."
                            color: "white"
                            background: Rectangle { color: "#0f111a"; radius: 10; border.color: parent.activeFocus ? window.themeAccent : window.themeBorder }
                        }
                    }
                }
            }
        }

        // Footer Actions
        RowLayout {
            Layout.fillWidth: true
            spacing: 15
            
            Button {
                id: btnCancel
                text: tr("set_btn_close")
                Layout.preferredWidth: 120; Layout.preferredHeight: 44
                onClicked: editorPopup.close()
                background: Rectangle { color: "transparent"; radius: 12; border.color: btnCancel.hovered ? "#ff4d4d" : "#2a2d3a"; border.width: 1 }
                contentItem: Label { text: parent.text; color: btnCancel.hovered ? "#ff4d4d" : "#888899"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }

            Item { Layout.fillWidth: true }

            Button {
                id: btnSave
                text: tr("set_btn_save")
                Layout.preferredWidth: 160; Layout.preferredHeight: 44
                onClicked: {
                    if (bridge && gameData) {
                        let newMeta = {
                            "title": titleField.text,
                            "description": descField.text,
                            "developer": devField.text,
                            "year": yearField.text,
                            "genre": genreField.text,
                            "rating": gameData.rating // Mantener el rating original
                        }
                        bridge.lib.saveMetadata(gameData.path, newMeta)
                        editorPopup.metadataSaved()
                        editorPopup.close()
                    }
                }
                background: Rectangle {
                    radius: 12
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: window.themeAccent }
                        GradientStop { position: 1.0; color: "#b36ff7" } // Variación violeta
                    }
                    opacity: btnSave.pressed ? 0.8 : 1.0
                }
                contentItem: Label { text: parent.text; color: "white"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }
        }
    }
}
