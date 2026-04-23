import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects
import "../system"
import "../items"
import QtQuick.Dialogs

Popup {
    id: editorPopup
    
    property int gameId: 0
    property string title: ""
    property string platform: ""
    property string developer: ""
    property string publisher: ""
    property string releaseDate: ""
    property string genre: ""
    property string description: ""
    property string cover2d: ""
    property string cover3d: ""

    width: 700; height: 600
    anchors.centerIn: Overlay.overlay
    modal: true
    focus: true
    
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    
    background: Item {
        Rectangle {
            id: bgRect
            anchors.fill: parent; radius: Theme.radiusLarge
            color: Theme.cardBackground
            border.color: Theme.accentColor; border.width: 1
        }
        
        DropShadow {
            anchors.fill: bgRect; radius: 25; samples: 20
            color: Qt.rgba(0,0,0,0.5); source: bgRect; z: -1
        }
    }

    contentItem: Item {
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 30
            spacing: 20

            // CABECERA
            RowLayout {
                Layout.fillWidth: true
                Text {
                    text: I18n.t.metadata_editor
                    color: Theme.accentColor
                    font.pixelSize: 12; font.bold: true; font.letterSpacing: 4
                }
                Item { Layout.fillWidth: true }
                Button {
                    text: "✕"; flat: true; onClicked: editorPopup.close()
                    font.pixelSize: 18; Material.foreground: Theme.textMuted
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider; opacity: 0.1 }

            RowLayout {
                Layout.fillWidth: true; Layout.fillHeight: true; spacing: 30

                // COLUMNA IZQUIERDA: Portadas
                ColumnLayout {
                    Layout.preferredWidth: 200; spacing: 15
                    
                    Text { text: I18n.t.visual_identity; color: Theme.textMuted; font.pixelSize: 10; font.bold: true }
                    
                    Rectangle {
                        Layout.preferredWidth: 160; Layout.preferredHeight: 220; radius: 8
                        color: Theme.controlBackground; border.color: Theme.cardBorder
                        clip: true
                        
                        Image {
                            anchors.fill: parent; fillMode: Image.PreserveAspectFit
                            source: editorPopup.cover2d ? (editorPopup.cover2d.startsWith("file://") ? editorPopup.cover2d : "file:///" + editorPopup.cover2d) : ""
                            asynchronous: true
                        }
                        
                        Text {
                            anchors.centerIn: parent; text: "🖼️"; font.pixelSize: 32; opacity: parent.children[0].status !== Image.Ready ? 0.3 : 0
                        }
                    }
                    
                    Button {
                        text: I18n.t.change_cover; Layout.fillWidth: true; highlighted: true
                        font.pixelSize: 10; Material.accent: Theme.accentColor
                        onClicked: artFileDialog.open()
                    }
                }

                // COLUMNA DERECHA: Campos de texto
                ScrollView {
                    Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                    contentWidth: availableWidth
                    
                    ColumnLayout {
                        width: parent.width; spacing: 15
                        
                        CustomInput { label: I18n.t.game_title; text: editorPopup.title; onTextUpdated: (val) => editorPopup.title = val }
                        
                        RowLayout {
                            spacing: 15
                            CustomInput { label: I18n.t.developer; text: editorPopup.developer; onTextUpdated: (val) => editorPopup.developer = val; Layout.fillWidth: true }
                            CustomInput { label: I18n.t.release_date; text: editorPopup.releaseDate; onTextUpdated: (val) => editorPopup.releaseDate = val; Layout.preferredWidth: 120 }
                        }

                        RowLayout {
                            spacing: 15
                            CustomInput { label: I18n.t.publisher; text: editorPopup.publisher; onTextUpdated: (val) => editorPopup.publisher = val; Layout.fillWidth: true }
                            CustomInput { label: I18n.t.genre; text: editorPopup.genre; onTextUpdated: (val) => editorPopup.genre = val; Layout.preferredWidth: 150 }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 5
                            Text { text: I18n.t.desc_synopsis; color: Theme.textMuted; font.pixelSize: 10; font.bold: true }
                            TextArea {
                                Layout.fillWidth: true; Layout.preferredHeight: 150
                                text: editorPopup.description
                                color: Theme.textMain; font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                background: Rectangle { color: Theme.controlBackground; radius: 8; border.color: parent.focus ? Theme.accentColor : Theme.cardBorder }
                                onTextChanged: editorPopup.description = text
                            }
                        }
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider; opacity: 0.1 }

            // BOTONES DE ACCIÓN
            RowLayout {
                Layout.fillWidth: true; spacing: 15
                Item { Layout.fillWidth: true }
                
                Button {
                    text: I18n.t.cancel; flat: true; onClicked: editorPopup.close()
                    Material.foreground: Theme.textMuted
                }
                
                Button {
                    id: saveBtn
                    text: I18n.t.save_changes; highlighted: true
                    Material.background: Theme.accentColor; font.bold: true
                    onClicked: {
                        var success = mainController.update_game_metadata(editorPopup.gameId, {
                            "title": editorPopup.title,
                            "developer": editorPopup.developer,
                            "publisher": editorPopup.publisher,
                            "releaseDate": editorPopup.releaseDate,
                            "genre": editorPopup.genre,
                            "description": editorPopup.description,
                            "cover2d": editorPopup.cover2d,
                            "cover3d": editorPopup.cover3d
                        })
                        if (success) editorPopup.close()
                    }
                }
            }
        }

        FileDialog {
            id: artFileDialog
            title: I18n.t.select_cover
            nameFilters: ["Imágenes (*.jpg *.png *.jpeg *.webp)"]
            onAccepted: {
                var path = selectedFile.toString()
                // Limpiar el prefijo file:/// si es necesario para la DB
                if (path.startsWith("file:///")) {
                    path = path.substring(8)
                }
                editorPopup.cover2d = path
            }
        }
    }
}
