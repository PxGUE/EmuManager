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
    property color accentColor: "#16a085"
    
    property bool has3d: cover3d !== ""
    property bool has2d: cover2d !== ""
    
    signal closed()
    signal launched()

    // --- 1. FONDO DE ATENUACIÓN (Dimmer) ---
    Rectangle {
        anchors.fill: parent; color: "#000000"; opacity: 0.85
        MouseArea { 
            anchors.fill: parent; hoverEnabled: true; onClicked: detailsRoot.closed() 
            // Esto captura el ratón y evita que "atraviese" a las capas inferiores
        }
    }

    // --- 2. LA TARJETA EXPANDIDA (800x480) ---
    Rectangle {
        id: expandedCard
        anchors.centerIn: parent
        width: 820; height: 500
        color: "#0d0d12"; radius: 24; clip: true
        border.color: "#25ffffff"; border.width: 1
        
        layer.enabled: true; layer.effect: DropShadow { radius: 30; color: "#cc000000"; samples: 20 }

        Row {
            anchors.fill: parent

            // MITAD IZQUIERDA: CARÁTULA (Showcase)
            Rectangle {
                width: parent.width * 0.45; height: parent.height
                color: "#050508"
                
                // Brillo de fondo con el color de consola
                RadialGradient {
                    anchors.fill: parent; opacity: 0.15
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: accentColor }
                        GradientStop { position: 0.8; color: "transparent" }
                    }
                }

                GameBox3D {
                    id: exhibitBox; anchors.centerIn: parent; width: 230; height: 340
                    sourceImage: detailsRoot.has3d ? detailsRoot.cover3d : detailsRoot.cover2d
                    platform: detailsRoot.platform; isHovered: true; accentColor: detailsRoot.accentColor
                    
                    // Rotación automática muy lenta
                    property real animTime: 0
                    NumberAnimation on animTime { from: 0; to: 360; duration: 25000; loops: Animation.Infinite; running: true }
                    dynamicTiltY: Math.sin(animTime * Math.PI / 180) * 15
                    dynamicTiltX: Math.cos(animTime * Math.PI / 180) * 10
                }
            }

            // MITAD DERECHA: INFO Y BOTÓN
            Item {
                width: parent.width * 0.55; height: parent.height
                
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 40; spacing: 20
                    
                    // Cabecera Interna
                    Column {
                        spacing: 4; Layout.fillWidth: true
                        Text { text: detailsRoot.platform.toUpperCase(); color: accentColor; font.pixelSize: 11; font.bold: true; font.letterSpacing: 4 }
                        Text { 
                            text: detailsRoot.title; color: "white"; font.pixelSize: 32; font.bold: true; width: 400; wrapMode: Text.WordWrap
                        }
                    }

                    // Stats Rápidos
                    Row {
                        spacing: 10
                        Repeater {
                            model: [detailsRoot.genre, detailsRoot.releaseDate]
                            delegate: Rectangle {
                                height: 24; radius: 12; width: stext.width + 20; color: "#15ffffff"
                                visible: modelData !== "" && modelData !== "----"
                                Text { id: stext; anchors.centerIn: parent; text: modelData; color: "white"; font.pixelSize: 9; font.bold: true; opacity: 0.6 }
                            }
                        }
                    }

                    ScrollView {
                        Layout.fillWidth: true; Layout.fillHeight: true
                        ScrollBar.vertical: ScrollBar { width: 3; contentItem: Rectangle { color: accentColor; radius: 2; opacity: 0.3 } }
                        Text {
                            width: 380; wrapMode: Text.WordWrap
                            text: detailsRoot.description !== "Sin descripción disponible." ? detailsRoot.description : I18n.t.no_description_template.arg(detailsRoot.platform.toUpperCase())
                            color: "#99ffffff"; font.pixelSize: 14; lineHeight: 1.4
                        }
                    }

                    // Botón LANZAR (Grande)
                    Button {
                        id: launchBigBtn
                        Layout.fillWidth: true; Layout.preferredHeight: 64; Layout.topMargin: 10
                        flat: true; onClicked: { detailsRoot.launched(); mainController.launch_game_by_id(detailsRoot.gameId); detailsRoot.closed(); }

                        background: Rectangle {
                            radius: 12; color: launchBigBtn.hovered ? accentColor : "transparent"
                            border.color: accentColor; border.width: 2
                            Behavior on color { ColorAnimation { duration: 200 } }
                        }
                        contentItem: Text {
                            text: I18n.t.launch_adventure; color: launchBigBtn.hovered ? "black" : "white"
                            font.bold: true; font.letterSpacing: 2; font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }
        }

        // --- ICONO DE CERRAR SUPERIOR ---
        Button {
            id: closeXBtn
            anchors.top: parent.top; anchors.right: parent.right; anchors.margins: 15
            width: 40; height: 40; flat: true; onClicked: detailsRoot.closed()
            background: Rectangle { radius: 20; color: closeXBtn.hovered ? "#30ffffff" : "transparent" }
            contentItem: Text { text: "✕"; color: "white"; font.pixelSize: 20; horizontalAlignment: Text.AlignHCenter; anchors.centerIn: parent }
        }
    }

    // ANIMACIÓN DE EXPANSIÓN
    opacity: 0; scale: 0.9
    SequentialAnimation {
        running: true
        ParallelAnimation {
            NumberAnimation { target: detailsRoot; property: "opacity"; from: 0; to: 1; duration: 400; easing.type: Easing.OutCubic }
            NumberAnimation { target: detailsRoot; property: "scale"; from: 0.9; to: 1.0; duration: 500; easing.type: Easing.OutBack }
        }
    }
}
