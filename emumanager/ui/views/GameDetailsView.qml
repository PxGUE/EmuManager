import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "../components"
import "../components/dialogs"
import "../components/items"

Item {
    id: detailsRoot
    anchors.fill: parent
    z: 5000
    
    // --- DATOS DEL JUEGO ---
    property int gameId: 0
    property string title: I18n.t.loading
    property string platform: ""
    property string developer: ""
    property string publisher: ""
    property string genre: ""
    property string releaseDate: ""
    property string description: ""
    property string cover2d: ""
    property string cover3d: ""
    property bool loaded: false
    
    // Identidad visual: Color de plataforma (fallback) + Color adaptativo (Chameleon)
    property color platformColor: Theme.accentColor
    property color accentColor: !chameleon.isDefault ? chameleon.adaptiveColor : platformColor
    
    onVisibleChanged: {
        if (visible) {
            if (cover2d !== "") {
                chameleon.adaptTo(cover2d)
            }
        } else {
            chameleon.reset()
        }
    }

    onCover2dChanged: {
        if (visible && cover2d !== "") {
            chameleon.adaptTo(cover2d)
        }
    }
    
    property bool has3d: cover3d !== ""
    property bool has2d: cover2d !== ""
    
    signal closed()
    signal launched()

    // --- 1. FONDO DE ATENUACIÓN (Dimmer) ---
    Rectangle {
        anchors.fill: parent; color: Theme.glassPlain
        opacity: detailsRoot.visible ? 0.4 : 0
        visible: opacity > 0 // Evita que bloquee cuando es totalmente transparente
        Behavior on opacity { NumberAnimation { duration: 400 } }
        
        MouseArea { 
            anchors.fill: parent
            hoverEnabled: true // CAPTURA EL HOVER PARA QUE NO PASE A LAS CARDS
            onClicked: detailsRoot.closed() 
            onWheel: (wheel) => wheel.accepted = true // Bloquea el scroll de la lista de fondo
        }
    }

    // --- 2. LA HOJA LATERAL (SIDE-BLADE) ---
    Rectangle {
        id: sideBlade
        width: 600; height: parent.height
        x: detailsRoot.visible ? parent.width - width : parent.width
        color: Theme.cardBackground; clip: true
        
        Behavior on x { NumberAnimation { duration: 550; easing.type: Easing.OutQuint } }

        // Borde izquierdo con glow reactivo
        Rectangle { width: 1; height: parent.height; anchors.left: parent.left; color: accentColor; opacity: 0.3 }

        // BOTÓN CERRAR: FLOTANTE (Para que no se recorte)
        Button {
            id: closeXBtn
            anchors.top: parent.top; anchors.right: parent.right; anchors.topMargin: 50; anchors.rightMargin: 30
            width: 44; height: 44; flat: true; onClicked: detailsRoot.closed(); z: 2000
            
            background: Rectangle { 
                radius: 20
                color: closeXBtn.hovered ? Theme.accentElectric : Theme.glassStrong
                opacity: closeXBtn.hovered ? 1.0 : 0.7
                border.color: closeXBtn.hovered ? Theme.white : Theme.glassStrong
                border.width: 1
                layer.enabled: true
                layer.effect: DropShadow { radius: 8; color: Theme.black; opacity: 0.5 }
            }

            contentItem: Text { 
                text: "✕"; color: Theme.white; font.pixelSize: 16; font.weight: Font.Bold
                horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
            }
        }

        ColumnLayout {
            anchors.fill: parent; spacing: 0
            
            // CABECERA: SHOWCASE 3D (Estilo Atmosférico Nebula)
            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: parent.height * 0.45
                color: Theme.backgroundVoid
                clip: true

                // 1. Fondo de Arte desenfocado (Atmósfera)
                SmartImage {
                    id: bgArt
                    anchors.fill: parent
                    source: detailsRoot.cover2d
                    fillMode: Image.PreserveAspectCrop
                    opacity: 0.3
                    asynchronous: true
                }

                FastBlur {
                    anchors.fill: bgArt
                    source: bgArt
                    radius: 80
                    transparentBorder: true
                }

                // 2. Degradado base (Vignette) para fundir con la info
                LinearGradient {
                    anchors.fill: parent
                    start: Qt.point(0, 0)
                    end: Qt.point(0, height)
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: Theme.transparent }
                        GradientStop { position: 0.7; color: Theme.transparent }
                        GradientStop { position: 1.0; color: Theme.cardBackground }
                    }
                }

                // 3. La caja 3D principal
                GameBox3D {
                    id: exhibitBox
                    anchors.centerIn: parent
                    anchors.verticalCenterOffset: 10
                    width: 250; height: 350
                    sourceImage: detailsRoot.has3d ? (detailsRoot.cover3d.indexOf(":") !== -1 && !detailsRoot.cover3d.startsWith("file://") ? "file:///" + detailsRoot.cover3d : detailsRoot.cover3d) : (detailsRoot.cover2d.indexOf(":") !== -1 && !detailsRoot.cover2d.startsWith("file://") ? "file:///" + detailsRoot.cover2d : detailsRoot.cover2d)
                    platform: detailsRoot.platform
                    isHovered: true
                    accentColor: detailsRoot.accentColor
                    z: 10
                    
                    property real animTime: 0
                    NumberAnimation on animTime { 
                        from: 0; to: 360; duration: 25000; 
                        loops: Animation.Infinite; running: detailsRoot.visible 
                    }
                    dynamicTiltY: Math.sin(animTime * Math.PI / 180) * 12
                    dynamicTiltX: Math.cos(animTime * Math.PI / 180) * 8
                }
            }

            // INFO Y METADATOS
            Item {
                Layout.fillWidth: true; Layout.fillHeight: true
                
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 40; spacing: Theme.spaceLarge
                    
                    Column {
                        spacing: 12; Layout.fillWidth: true
                        Text { 
                            text: detailsRoot.platform.toUpperCase()
                            color: accentColor
                            font.pixelSize: 10
                            font.bold: true
                            font.letterSpacing: 4 
                        }
                        Text { 
                            text: detailsRoot.title
                            color: Theme.textMain
                            width: parent.width
                            wrapMode: Text.WrapAnywhere
                            font.pixelSize: text.length > 35 ? 19 : 26
                            font.bold: true
                            font.weight: Font.Black
                            lineHeight: 0.95
                            Behavior on font.pixelSize { NumberAnimation { duration: 200 } }
                        }
                    }

                    // BOTÓN EDITAR (Sutil)
                    Button {
                        id: editBtn
                        Layout.preferredHeight: 30; Layout.preferredWidth: 100
                        text: "✏️ " + I18n.t.edit_metadata
                        flat: true; opacity: editBtn.hovered ? 1.0 : 0.6
                        font.pixelSize: 10; font.bold: true
                        Material.accent: accentColor
                        onClicked: {
                            manualEditor.syncData({
                                "gameId": detailsRoot.gameId,
                                "title": detailsRoot.title,
                                "platform": detailsRoot.platform,
                                "developer": detailsRoot.developer,
                                "publisher": detailsRoot.publisher,
                                "releaseDate": detailsRoot.releaseDate,
                                "genre": detailsRoot.genre,
                                "description": detailsRoot.description,
                                "cover2d": detailsRoot.cover2d,
                                "cover3d": detailsRoot.cover3d
                            })
                            manualEditor.open()
                        }
                    }

                    // Metadata Row
                    Row {
                        spacing: 12
                        Layout.fillWidth: true

                        Repeater {
                            model: [detailsRoot.genre, detailsRoot.releaseDate, detailsRoot.developer]
                            delegate: Rectangle {
                                height: 26; radius: 13
                                width: pillLabels.width + 24
                                color: Theme.controlBackground; border.color: Theme.cardBorder; border.width: 1
                                visible: modelData !== "" && modelData !== "----"
                                
                                Text { 
                                    id: pillLabels
                                    anchors.centerIn: parent
                                    text: modelData
                                    color: Theme.textMain
                                    font.pixelSize: 10
                                    font.bold: true
                                    opacity: 0.7 
                                }
                            }
                        }
                    }

                    // Separador
                    Rectangle { Layout.fillWidth: true; height: 1; color: Theme.cardBorder; opacity: 0.3 }

                    // Scroll de Descripción
                    ScrollView {
                        id: descScroll
                        Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                        contentWidth: availableWidth
                        
                        ScrollBar.vertical: ScrollBar { 
                            width: 4
                            policy: ScrollBar.AsNeeded
                            contentItem: Rectangle { color: accentColor; radius: 2; opacity: 0.2 } 
                        }
                        
                        Text {
                            id: descText
                            width: descScroll.availableWidth
                            wrapMode: Text.WordWrap
                            text: (detailsRoot.description && detailsRoot.description !== "") ? detailsRoot.description : I18n.t.no_description_template.arg(detailsRoot.platform.toUpperCase())
                            color: Theme.textMuted
                            font.pixelSize: 14
                            lineHeight: 1.5
                            horizontalAlignment: Text.AlignJustify
                        }
                    }

                    // Acciones Principales
                    Button {
                        id: launchBigBtn
                        Layout.fillWidth: true; Layout.preferredHeight: 60; Layout.topMargin: 20
                        flat: true
                        onClicked: { 
                            detailsRoot.launched(); 
                            mainController.launch_game_by_id(detailsRoot.gameId); 
                            detailsRoot.closed(); 
                        }

                        background: Rectangle {
                            radius: 12
                            color: launchBigBtn.hovered ? accentColor : Theme.transparent
                            border.color: accentColor; border.width: 2
                            Behavior on color { ColorAnimation { duration: 250 } }
                            
                            layer.enabled: launchBigBtn.hovered
                            layer.effect: DropShadow { radius: 10; color: accentColor; opacity: 0.4 }
                        }
                        
                        contentItem: Text {
                            text: I18n.t.launch_adventure.toUpperCase()
                            color: launchBigBtn.hovered ? Theme.viewBackground : Theme.textMain
                            font.bold: true; font.letterSpacing: 3; font.pixelSize: 12
                            horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }
        }
    }

    signal refreshRequested()

    ManualEditor {
        id: manualEditor
        onMetadataUpdated: detailsRoot.refreshRequested()
    }
}
