import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Models 1.0
import EmuManager.Controllers 1.0
import "../components"

Item {
    id: libraryRoot
    objectName: "libraryView"
    anchors.fill: parent

    // MainController { id: controller } // USAR EL HEREDADO DE MAIN.QML
    GameListModel { id: gamesModel } 

    property bool showGames: false
    property string activePlatform: "all"

    Rectangle { anchors.fill: parent; color: "#050505" }

    function selectConsole(platform, index) {
        activePlatform = platform
        gamesModel.update_games()
        gamesModel.filter_by_platform(platform)
        showGames = true
    }

    function refreshConsoles() {
        consoleModel.clear()
        if (!mainController) return;
        var summary = mainController.get_consoles_summary()
        console.log("M.A.N.G.O (UI): Cargando " + summary.length + " sistemas en la biblioteca.")
        for (var i = 0; i < summary.length; i++) {
            consoleModel.append(summary[i])
        }
    }

    // No cargar inmediatamente al completar componente para evitar lag inicial
    // Dejamos que el Splash lo dispare cuando el motor esté listo
    Component.onCompleted: {
        if (window.isLoaded) refreshConsoles()
    }

    Connections {
        target: mainController
        function onScanFinished(count) { refreshConsoles() }
        function onGamesUpdated() { refreshConsoles() }
    }

    Connections {
        target: window
        function onIsLoadedChanged() {
            if (window.isLoaded) {
                refreshConsoles()
            }
        }
    }

    ListModel { id: consoleModel }

    // --- CAROUSEL 3D ---
    PathView {
        id: consoleCarousel
        z: 11; anchors.left: parent.left; anchors.right: parent.right
        height: showGames ? 150 : parent.height; y: 0
        opacity: consoleModel.count > 0 ? (showGames ? 1 : 1) : 0
        visible: consoleModel.count > 0
        Behavior on opacity { NumberAnimation { duration: 800 } }
        Behavior on height { NumberAnimation { duration: 600; easing.type: Easing.OutQuint } }

        model: consoleModel; pathItemCount: 5; preferredHighlightBegin: 0.5; preferredHighlightEnd: 0.5; focus: true
        highlightRangeMode: PathView.StrictlyEnforceRange; snapMode: PathView.SnapToItem

        delegate: Item {
            id: delegateRoot; width: libraryRoot.showGames ? 220 : 380; height: libraryRoot.showGames ? 80 : 480
            
            // Atributos de Path manuales para evitar errores de sintaxis
            scale: libraryRoot.showGames ? 1.0 : (delegateRoot.PathView.iconScale || 1.0)
            opacity: delegateRoot.PathView.iconOpacity !== undefined ? delegateRoot.PathView.iconOpacity : 1.0
            z: delegateRoot.PathView.iconZ !== undefined ? delegateRoot.PathView.iconZ : 0

            ConsoleCard {
                anchors.centerIn: parent
                title: model.title; fullName: model.fullName; iconEmoji: model.iconEmoji; accentColor: model.accentColor
                gameCount: model.gameCount; playTime: model.playTime
                emulatorName: model.emulatorName; hasCore: model.hasCore
                isSelected: delegateRoot.PathView.isCurrentItem; minimalMode: libraryRoot.showGames 
                onClicked: {
                    if (index === consoleCarousel.currentIndex) {
                        libraryRoot.selectConsole(model.platform, index)
                    } else {
                        consoleCarousel.currentIndex = index
                    }
                }
            }
        }

        path: Path {
            startX: -50; startY: consoleCarousel.height / 2
            PathAttribute { name: "iconScale"; value: 0.6 }
            PathAttribute { name: "iconOpacity"; value: 0.3 }
            PathAttribute { name: "iconZ"; value: -20 }
            PathLine { x: consoleCarousel.width / 2; y: consoleCarousel.height / 2 }
            PathAttribute { name: "iconScale"; value: 1.15 }
            PathAttribute { name: "iconOpacity"; value: 1.0 }
            PathAttribute { name: "iconZ"; value: 100 }
            PathLine { x: consoleCarousel.width + 50; y: consoleCarousel.height / 2 }
            PathAttribute { name: "iconScale"; value: 0.6 }
            PathAttribute { name: "iconOpacity"; value: 0.3 }
            PathAttribute { name: "iconZ"; value: -20 }
        }
    }

    // --- ESTADO VACÍO (Si no hay sistemas) ---
    ColumnLayout {
        id: emptyView
        anchors.centerIn: parent; spacing: 20
        visible: consoleModel.count === 0 && window.isLoaded
        
        Text {
            text: "📡"
            font.pixelSize: 64; Layout.alignment: Qt.AlignHCenter
            opacity: 0.5
        }
        
        ColumnLayout {
            spacing: 5
            Text {
                text: "BIBLIOTECA VACÍA"
                color: "white"; font.pixelSize: 18; font.bold: true; font.letterSpacing: 2; Layout.alignment: Qt.AlignHCenter
            }
            Text {
                text: "No se han detectado juegos todavía.\\nVe a Configuración para añadir rutas de escaneo."
                color: "#66ffffff"; font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; Layout.alignment: Qt.AlignHCenter
            }
        }
        
        Button {
            text: "CONFIGURAR RUTAS"
            Layout.alignment: Qt.AlignHCenter
            Material.background: "#16a085"; font.bold: true
            onClicked: activeViewId = "settingsView" 
        }
    }

    // --- BARRA DE BÚSQUEDA (M.A.N.G.O FUZZYMATCH) ---
    Rectangle {
        id: searchContainer
        anchors.top: consoleCarousel.bottom
        anchors.left: parent.left; anchors.right: parent.right
        anchors.leftMargin: 40; anchors.rightMargin: 40
        height: showGames ? 60 : 0
        visible: showGames
        opacity: showGames ? 1 : 0
        color: "transparent"
        Behavior on height { NumberAnimation { duration: 400; easing.type: Easing.OutQuint } }
        Behavior on opacity { NumberAnimation { duration: 400 } }

        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            width: parent.width; height: 44; radius: 10
            color: "#0a0a0d"; border.color: searchInput.focus ? "#16a085" : "#33ffffff"; border.width: 1
            Behavior on border.color { ColorAnimation { duration: 200 } }
            
            RowLayout {
                anchors.fill: parent; anchors.leftMargin: 15; anchors.rightMargin: 10; spacing: 15
                Text { text: "🔍"; color: searchInput.focus ? "#16a085" : "#66ffffff"; font.pixelSize: 16 }
                TextField {
                    id: searchInput
                    Layout.fillWidth: true
                    color: "white"
                    placeholderText: "Búsqueda instantánea..."
                    background: Item {} // Remover el subrayado por defecto
                    font.pixelSize: 14; font.letterSpacing: 1
                    onTextEdited: gamesModel.search_games(text, activePlatform)
                }
            }
        }
    }

    // --- GALERÍA DE JUEGOS ---
    GridView {
        id: romGallery
        anchors.top: searchContainer.bottom; anchors.bottom: parent.bottom
        anchors.left: parent.left; anchors.right: parent.right; anchors.margins: 40; anchors.topMargin: 10
        cellWidth: 220; cellHeight: 300; clip: true; visible: showGames; opacity: showGames ? 1 : 0
        model: gamesModel
        delegate: RomCard {
            title: model.title; platform: model.platform
            cover2d: model.cover2dPath; cover3d: model.cover3dPath
            onClicked: mainController.launch_game_by_id(model.gameId)
        }
        Behavior on opacity { NumberAnimation { duration: 500 } }
    }

    // --- BOTÓN VOLVER (Reubicado para no estorbar) ---
    EmuFloatingButton {
        icon: "⟲"; accentColor: "#16a085"; size: 54; visible: showGames
        anchors.bottom: parent.bottom; anchors.bottomMargin: 40
        anchors.right: parent.right; anchors.rightMargin: 40
        onClicked: showGames = false
    }
}
