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

    width: Math.min(800, parent.width * 0.9)
    height: Math.min(720, parent.height * 0.9)
    anchors.centerIn: Overlay.overlay
    modal: true
    focus: true
    
    signal metadataUpdated()
    
    // Márgenes internos nativos del Popup
    padding: 40
    
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    
    // Función para sincronizar datos al abrir (Evita que se rompan los bindings)
    function syncData(data) {
        gameId = data.gameId || 0
        title = data.title || ""
        platform = data.platform || ""
        developer = data.developer || ""
        publisher = data.publisher || ""
        releaseDate = data.releaseDate || ""
        genre = data.genre || ""
        description = data.description || ""
        cover2d = data.cover2d || ""
        cover3d = data.cover3d || ""
    }

    enter: Transition {
        NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 300; easing.type: Easing.OutCubic }
        NumberAnimation { property: "scale"; from: 0.9; to: 1.0; duration: 300; easing.type: Easing.OutBack }
    }
    
    exit: Transition {
        NumberAnimation { property: "opacity"; from: 1.0; to: 0.0; duration: 200; easing.type: Easing.InCubic }
        NumberAnimation { property: "scale"; from: 1.0; to: 0.9; duration: 200; easing.type: Easing.InCubic }
    }

    background: Item {
        Rectangle {
            id: bgRect
            anchors.fill: parent
            radius: Theme.radiusLarge
            color: Theme.cardBackground
            border.color: Theme.glassStrong
            border.width: 1
            opacity: 0.98
            
            Rectangle {
                anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
                height: 50; radius: Theme.radiusLarge; color: "transparent"
                border.color: Theme.glassStrong; border.width: 1; clip: true
                Rectangle { anchors.fill: parent; color: "black"; anchors.topMargin: 1 }
            }
        }
        
        DropShadow {
            anchors.fill: bgRect; horizontalOffset: 0; verticalOffset: 20
            radius: 40; samples: 25; color: Qt.rgba(0,0,0,0.8); source: bgRect; z: -1
        }
    }

    contentItem: ColumnLayout {
        spacing: 25

        // CABECERA
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 4
                Text {
                    text: I18n.t.metadata_editor.toUpperCase()
                    color: Theme.accentColor
                    font.pixelSize: 11; font.bold: true; font.letterSpacing: 4
                }
                Text {
                    text: editorPopup.title || "---"
                    color: Theme.textMain
                    font.pixelSize: 22; font.bold: true
                    Layout.maximumWidth: 500; elide: Text.ElideRight
                }
            }
            Item { Layout.fillWidth: true }
            
            Rectangle {
                width: 36; height: 36; radius: 18
                color: closeMouse.containsMouse ? Theme.glassStrong : "transparent"
                Behavior on color { ColorAnimation { duration: 200 } }
                Text { anchors.centerIn: parent; text: "✕"; color: Theme.textMuted; font.pixelSize: 18 }
                MouseArea { id: closeMouse; anchors.fill: parent; hoverEnabled: true; onClicked: editorPopup.close() }
            }
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider; opacity: 0.2 }

        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 35

            // COLUMNA IZQUIERDA: Portada
            ColumnLayout {
                Layout.preferredWidth: 200; Layout.alignment: Qt.AlignTop; spacing: 20
                
                Text { 
                    text: I18n.t.visual_identity.toUpperCase()
                    color: Theme.textMuted; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2
                }
                
                Item {
                    Layout.preferredWidth: 180; Layout.preferredHeight: 250
                    
                    Rectangle {
                        id: imageFrame
                        anchors.fill: parent; radius: 12
                        color: Theme.controlBackground; border.color: Theme.glassStrong; border.width: 1; clip: true
                        
                        Image {
                            id: mainCover
                            anchors.fill: parent; fillMode: Image.PreserveAspectCrop
                            source: editorPopup.cover2d ? (editorPopup.cover2d.startsWith("file://") ? editorPopup.cover2d : "file:///" + editorPopup.cover2d) : ""
                            asynchronous: true; opacity: status === Image.Ready ? 1 : 0
                            Behavior on opacity { NumberAnimation { duration: 300 } }
                        }
                        
                        Rectangle { anchors.fill: parent; color: "#000"; opacity: 0.3; visible: mainCover.status !== Image.Ready }
                        Text { anchors.centerIn: parent; text: "🎮"; font.pixelSize: 40; visible: mainCover.status !== Image.Ready }
                    }
                    
                    DropShadow { anchors.fill: imageFrame; radius: 15; samples: 15; color: Qt.rgba(0,0,0,0.5); source: imageFrame; z: -1 }
                }
                
                Button {
                    id: changeArtBtn
                    text: I18n.t.change_cover; Layout.fillWidth: true; Layout.preferredHeight: 36
                    flat: true
                    contentItem: Text {
                        text: parent.text; color: changeArtBtn.hovered ? Theme.textMain : Theme.textAccent
                        horizontalAlignment: Text.AlignHCenter; font.bold: true; font.pixelSize: 11
                    }
                    background: Rectangle {
                        radius: 8; color: changeArtBtn.hovered ? Theme.accentColor : "transparent"
                        border.color: Theme.accentColor; border.width: 1
                        Behavior on color { ColorAnimation { duration: 200 } }
                    }
                    onClicked: artFileDialog.open()
                }
                Item { Layout.fillHeight: true }
            }

            // COLUMNA DERECHA: ScrollView corregido
            ScrollView {
                Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                ScrollBar.vertical.policy: ScrollBar.AsNeeded
                contentWidth: availableWidth
                contentHeight: rightColumn.implicitHeight
                
                ColumnLayout {
                    id: rightColumn
                    width: parent.width; spacing: 20
                    
                    CustomInput { 
                        label: I18n.t.game_title; text: editorPopup.title
                        onTextUpdated: (val) => editorPopup.title = val 
                    }
                    
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
                        Layout.fillWidth: true; spacing: 8
                        Text { 
                            text: I18n.t.desc_synopsis.toUpperCase()
                            color: Theme.textMuted; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1.5
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.max(150, descArea.implicitHeight + 20)
                            color: descArea.activeFocus ? Theme.cardHoverBackground : Theme.controlBackground
                            radius: Theme.radiusSmall; border.color: descArea.activeFocus ? Theme.accentColor : Theme.cardBorder; border.width: 1.5
                            Behavior on color { ColorAnimation { duration: 200 } }
                            Behavior on border.color { ColorAnimation { duration: 200 } }

                            TextArea {
                                id: descArea
                                anchors.fill: parent; anchors.margins: 10
                                text: editorPopup.description
                                color: Theme.textMain; font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                background: null
                                onTextChanged: editorPopup.description = text
                                placeholderText: "Escribe una descripción..."
                                placeholderTextColor: Theme.textMuted
                                selectByMouse: true
                            }
                        }
                    }
                }
            }
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider; opacity: 0.2 }

        // BOTONES DE ACCIÓN
        RowLayout {
            Layout.fillWidth: true; spacing: 20
            Item { Layout.fillWidth: true }
            
            Button {
                id: cancelBtn
                text: I18n.t.cancel; flat: true; onClicked: editorPopup.close()
                contentItem: Text {
                    text: cancelBtn.text; color: cancelBtn.hovered ? Theme.textMain : Theme.textMuted
                    font.bold: true; font.pixelSize: 14
                }
            }
            
            Button {
                id: saveBtn
                text: I18n.t.save_changes; Layout.preferredWidth: 180; Layout.preferredHeight: 45
                contentItem: Text {
                    text: saveBtn.text; color: Theme.black
                    font.bold: true; font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    radius: 8; color: saveBtn.hovered ? Qt.lighter(Theme.accentColor, 1.1) : Theme.accentColor
                    LinearGradient {
                        anchors.fill: parent; start: Qt.point(0, 0); end: Qt.point(0, height); opacity: 0.2
                        gradient: Gradient { 
                            GradientStop { position: 0.0; color: "#ffffff" } 
                            GradientStop { position: 1.0; color: "transparent" } 
                        }
                    }
                    Behavior on color { ColorAnimation { duration: 200 } }
                }
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
                    if (success) {
                        editorPopup.metadataUpdated()
                        editorPopup.close()
                    }
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
            if (path.startsWith("file:///")) { path = path.substring(8) }
            editorPopup.cover2d = path
        }
    }
}


