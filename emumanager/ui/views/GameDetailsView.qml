import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "../components"

Item {
    id: detailsRoot
    anchors.fill: parent
    z: 5000
    
    // --- DATOS DEL JUEGO ---
    property int gameId: 0
    property string title: I18n.t.loading
    property string platform: ""
    property string developer: ""
    property string genre: ""
    property string releaseDate: ""
    property string description: ""
    property string cover2d: ""
    property string cover3d: ""
    property color accentColor: Theme.colorForPlatform(platform)
    
    property bool has3d: cover3d !== ""
    property bool has2d: cover2d !== ""
    
    signal closed()
    signal launched()

    // --- 1. FONDO DE ATENUACIÓN (Dimmer) ---
    Rectangle {
        anchors.fill: parent; color: Theme.glassPlain
        opacity: detailsRoot.visible ? 0.4 : 0
        Behavior on opacity { NumberAnimation { duration: 400 } }
        MouseArea { 
            anchors.fill: parent; onClicked: detailsRoot.closed() 
            // Esto captura el ratón y evita que "atraviese" a las capas inferiores
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

        ColumnLayout {
            anchors.fill: parent; spacing: 0
            
            // CABECERA: SHOWCASE 3D (Estilo Minimalista Premium)
            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: parent.height * 0.4
                color: Theme.sidebarBackground; clip: true
                
                // GRADIENTE ATMOSFÉRICO (Luz ambiental profunda)
                RadialGradient {
                    anchors.fill: parent; opacity: 0.12
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: accentColor }
                        GradientStop { position: 0.8; color: Theme.transparent }
                    }
                }

                GameBox3D {
                    id: exhibitBox; anchors.centerIn: parent; width: 220; height: 320
                    sourceImage: detailsRoot.has3d ? detailsRoot.cover3d : detailsRoot.cover2d
                    platform: detailsRoot.platform; isHovered: true; accentColor: detailsRoot.accentColor; z: 10
                    
                    // Rotación automática muy lenta
                    property real animTime: 0
                    NumberAnimation on animTime { from: 0; to: 360; duration: 25000; loops: Animation.Infinite; running: detailsRoot.visible }
                    dynamicTiltY: Math.sin(animTime * Math.PI / 180) * 15
                    dynamicTiltX: Math.cos(animTime * Math.PI / 180) * 10
                }

                // Botón Cerrar: Estética Glass Minimalista
                Button {
                    id: closeXBtn
                    anchors.top: parent.top; anchors.right: parent.right; anchors.margins: 25
                    width: 32; height: 32; flat: true; onClicked: detailsRoot.closed(); z: 100
                    
                    background: Rectangle { 
                        radius: 16
                        color: closeXBtn.hovered ? accentColor : Theme.glassLight
                        opacity: closeXBtn.hovered ? 0.8 : 0.4
                        border.color: closeXBtn.hovered ? accentColor : Theme.glassStrong
                        border.width: 1
                        
                        Behavior on color { ColorAnimation { duration: 300 } }
                        Behavior on border.color { ColorAnimation { duration: 300 } }
                        Behavior on opacity { NumberAnimation { duration: 300 } }
                    }

                    contentItem: Text { 
                        text: "✕"; color: Theme.textMain; font.pixelSize: 14; font.weight: Font.Light
                        horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                        anchors.centerIn: parent 
                    }
                }
            }

            // INFO Y METADATOS
            Item {
                Layout.fillWidth: true; Layout.fillHeight: true
                
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 40; spacing: Theme.spaceLarge
                    
                    Column {
                        spacing: 12; Layout.fillWidth: true
                        Text { text: detailsRoot.platform.toUpperCase(); color: accentColor; font.pixelSize: 10; font.bold: true; font.letterSpacing: 4 }
                        Text { 
                            text: detailsRoot.title; color: Theme.textMain; width: parent.width; wrapMode: Text.WrapAnywhere
                            font.pixelSize: text.length > 35 ? 19 : 26
                            font.bold: true; font.weight: Font.Black; font.letterSpacing: -0.5
                            lineHeight: 0.95
                            Behavior on font.pixelSize { NumberAnimation { duration: 200 } }
                        }
                    }

                    // Stats Rápidos
                    Row {
                        spacing: 12
                        Repeater {
                            model: [detailsRoot.genre, detailsRoot.releaseDate]
                            delegate: Rectangle {
                                height: 22; radius: 11; width: stext.width + 24; color: Theme.controlBackground; border.color: Theme.cardBorder; border.width: 1
                                visible: modelData !== "" && modelData !== "----"
                                Text { id: stext; anchors.centerIn: parent; text: modelData; color: Theme.textMain; font.pixelSize: 9; font.bold: true; opacity: 0.7 }
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
                        
                        ScrollBar.vertical: ScrollBar { width: 4; policy: ScrollBar.AsNeeded; contentItem: Rectangle { color: accentColor; radius: 2; opacity: 0.2 } }
                        
                        Text {
                            id: descText
                            width: descScroll.availableWidth
                            wrapMode: Text.WordWrap
                            text: detailsRoot.description !== "Sin descripción disponible." ? detailsRoot.description : I18n.t.no_description_template.arg(detailsRoot.platform.toUpperCase())
                            color: Theme.textMuted; font.pixelSize: 14; lineHeight: 1.5; horizontalAlignment: Text.AlignJustify
                        }
                    }

                    // ACCIONES
                    Button {
                        id: launchBigBtn
                        Layout.fillWidth: true; Layout.preferredHeight: 60; Layout.topMargin: 20
                        flat: true; onClicked: { detailsRoot.launched(); mainController.launch_game_by_id(detailsRoot.gameId); detailsRoot.closed(); }

                        background: Rectangle {
                            radius: 12
                            color: launchBigBtn.hovered ? accentColor : Theme.transparent
                            border.color: accentColor; border.width: 2
                            Behavior on color { ColorAnimation { duration: 250 } }
                            
                            // Glow sutil
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
}
