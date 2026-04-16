import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "../components"
import "../components/cards"
import "../components/system"
import "../components/effects"

Item {
    id: discoveryRoot
    anchors.fill: parent
    
    property var discoveryData: ({ "on_this_day": [], "hidden_gems": [], "random_batch": [] })
    property bool isLoading: true

    function refresh() {
        isLoading = true
        discoveryData = mainController.statsController.get_discovery_data()
        isLoading = false
    }

    Component.onCompleted: refresh()

    // --- 1. THE KINETIC VAULT BACKGROUND ---
    NebulaBackground {
        accentColor: Theme.accentElectric
        interactiveForce: 0.1
    }

    // --- 2. MAIN HUB ---
    Flickable {
        id: vaultScroll
        anchors.fill: parent
        anchors.topMargin: 0
        clip: true
        
        contentWidth: width; contentHeight: vaultContent.height
        flickableDirection: Flickable.VerticalFlick
        boundsBehavior: Flickable.StopAtBounds
        
        ScrollBar.vertical: ScrollBar { 
            width: 4; policy: ScrollBar.AsNeeded; active: true
            contentItem: Rectangle { color: Theme.accentElectric; radius: 2; opacity: 0.3 }
        }

        ColumnLayout {
            id: vaultContent
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 45
            anchors.rightMargin: 45
            spacing: 50
            
            Item { Layout.preferredHeight: 60 } // Top Padding

            // --- A. MISSION TITLE & ENGINE STATUS ---
            RowLayout {
                Layout.fillWidth: true
                ColumnLayout {
                    spacing: 0
                    Text { 
                        text: I18n.t.vault_title.toUpperCase(); 
                        color: Theme.textMain; font.pixelSize: 48; font.weight: Font.Black; font.letterSpacing: -2 
                    }
                    Text { 
                        text: "EXPLORA LOS SECRETOS DE TU COLECCIÓN"; 
                        color: Theme.accentElectric; font.pixelSize: 12; font.bold: true; font.letterSpacing: 4; opacity: 0.8
                    }
                }
                Item { Layout.fillWidth: true }
                GlassPanel {
                    width: 140; height: 50; radius: 12
                    content: ColumnLayout {
                        anchors.centerIn: parent; spacing: -2
                        Text { text: "ESTADO"; color: Theme.textMuted; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1; Layout.alignment: Qt.AlignCenter }
                        Text { text: "SINCRO OK"; color: Theme.statusSuccess; font.pixelSize: 12; font.bold: true; Layout.alignment: Qt.AlignCenter }
                    }
                }
            }

            // --- B. HERO SECTION (DYNAMIC SPOTLIGHT) ---
            Item {
                id: heroSection
                Layout.fillWidth: true; Layout.preferredHeight: 320
                
                property bool isAnniversary: discoveryData.on_this_day && discoveryData.on_this_day.length > 0
                property bool isGem: !isAnniversary && discoveryData.hidden_gems && discoveryData.hidden_gems.length > 0
                
                property var heroGame: {
                    if (isAnniversary) return discoveryData.on_this_day[0];
                    if (isGem) return discoveryData.hidden_gems[0];
                    if (discoveryData.random_batch && discoveryData.random_batch.length > 0) return discoveryData.random_batch[0];
                    return null;
                }
                
                property string heroCategory: isAnniversary ? "EFEMÉRIDES" : (isGem ? "JOYA OCULTA" : "DESCUBRIMIENTO")
                property color categoryColor: isAnniversary ? Theme.accentElectric : (isGem ? Theme.statusInfo : Theme.accentColor)

                GlassPanel {
                    anchors.fill: parent; radius: 24; glassOpacity: 0.3
                    borderColor: heroSection.categoryColor; borderWidth: 2
                    
                    RowLayout {
                        anchors.fill: parent; anchors.margins: 30; spacing: 40
                        
                        Item {
                            Layout.preferredWidth: heroSection.heroGame ? 180 : 120; Layout.fillHeight: true
                            Layout.alignment: Qt.AlignVCenter
                            
                            Rectangle {
                                anchors.fill: parent; radius: 15; color: Theme.backgroundVoid; clip: true; 
                                visible: heroSection.heroGame !== null
                                Image {
                                    anchors.fill: parent; 
                                    source: heroSection.heroGame ? "file:///" + (heroSection.heroGame.cover_2d_path || heroSection.heroGame.cover) : ""; 
                                    fillMode: Image.PreserveAspectCrop; asynchronous: true; opacity: status === Image.Ready ? 1.0 : 0.2
                                }
                            }
                            Text { anchors.centerIn: parent; text: "🎲"; font.pixelSize: 80; opacity: 0.15; visible: !heroSection.heroGame }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 15; Layout.alignment: Qt.AlignVCenter
                            
                            Rectangle {
                                width: 140; height: 26; radius: 13; color: heroSection.categoryColor
                                Text { anchors.centerIn: parent; text: heroSection.heroCategory; color: Theme.white; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
                            }
                            
                            Text { 
                                text: heroSection.heroGame ? heroSection.heroGame.title : "PREPARANDO MISIÓN..."
                                color: Theme.textMain; font.pixelSize: 32; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true 
                            }
                            
                            Text { 
                                id: descText
                                text: {
                                    if (!heroSection.heroGame) return "";
                                    if (heroSection.isAnniversary) {
                                        let date = heroSection.heroGame.release_date || "";
                                        let year = date.includes("-") ? date.split("-")[0] : date;
                                        return year !== "" ? "Un día como hoy en " + year + ", este clásico llegaba a las tiendas. ¿Listo para revivir la historia?" : "Un día como hoy celebrábamos el lanzamiento de este clásico.";
                                    }
                                    
                                    let d = heroSection.heroGame.description || "";
                                    return d !== "" ? d : "Explora los rincones más profundos de tu biblioteca. Hoy te recomendamos redescubrir este título.";
                                }
                                color: Theme.textMuted
                                font.pixelSize: 15
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                                opacity: 0.8
                                visible: heroSection.heroGame !== null
                                maximumLineCount: 5
                                elide: Text.ElideRight
                                lineHeight: 1.2
                            }

                            Text {
                                text: "No hemos encontrado nada especial hoy. Sigue escaneando y jugando para que M.A.N.G.O pueda darte mejores recomendaciones."; 
                                color: Theme.textMuted; font.pixelSize: 14; Layout.fillWidth: true; visible: heroSection.heroGame === null
                            }
                            
                            Item { Layout.preferredHeight: 10 }
                            
                            Button { 
                                text: heroSection.heroGame ? (heroSection.isAnniversary ? "REVIVIR HISTORIA" : "JUGAR") : "IR A LA BIBLIOTECA"; 
                                Layout.preferredWidth: 220; Layout.preferredHeight: 48; 
                                Material.background: heroSection.categoryColor
                                onClicked: heroSection.heroGame ? mainController.launch_game_by_id(heroSection.heroGame.id) : activeViewId = "libraryView" 
                            }
                        }
                    }
                }
            }

            // --- C. GAME MIX (STRICT GRID) ---
            ColumnLayout {
                Layout.fillWidth: true; spacing: 20; Layout.bottomMargin: 100
                
                ColumnLayout {
                    spacing: 4; Layout.fillWidth: true
                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "GAME MIX"; color: Theme.textMain; font.pixelSize: 22; font.weight: Font.Black; font.letterSpacing: 2 }
                        Rectangle { Layout.fillWidth: true; height: 1; color: Theme.accentElectric; opacity: 0.3; Layout.leftMargin: 20 }
                    }
                    Text { 
                        text: "LISTA ALEATORIA DE 20 JUEGOS DE TODAS LAS CONSOLAS. CADA DÍA SE GENERARÁ UNA SELECCIÓN NUEVA."; 
                        color: Theme.accentElectric; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2; opacity: 0.7
                    }
                }

                GridLayout {
                    id: mosaicGrid; Layout.fillWidth: true; 
                    columns: Math.max(1, Math.floor(width / 122)); columnSpacing: 12; rowSpacing: 12
                    
                    Repeater {
                        model: discoveryData.random_batch ? discoveryData.random_batch.slice(0, 20) : []
                        delegate: Rectangle {
                            id: wallItem; Layout.fillWidth: true; Layout.preferredHeight: width * 1.45; radius: 10; color: Theme.backgroundVoid
                            border.color: wallMA.containsMouse ? Theme.accentElectric : Theme.transparent; border.width: 2
                            clip: true; scale: wallMA.containsMouse ? 1.05 : 1.0; z: wallMA.containsMouse ? 10 : 1
                            Behavior on scale { NumberAnimation { duration: 150 } }
                            
                            Image { 
                                anchors.fill: parent; source: modelData.cover ? "file:///" + modelData.cover : ""; fillMode: Image.PreserveAspectCrop; asynchronous: true
                                opacity: wallMA.containsMouse ? 1.0 : 0.6; Behavior on opacity { NumberAnimation { duration: 250 } }
                            }
                            MouseArea { id: wallMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: window.openGameDetails(modelData.id) }
                        }
                    }
                }
            }
        }
    }
}
