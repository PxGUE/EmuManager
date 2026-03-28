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
    property var activeAccentColor: Theme.accentColor
    readonly property color resolvedActiveAccent: (typeof activeAccentColor === "string" && Theme[activeAccentColor] !== undefined) ? Theme[activeAccentColor] : activeAccentColor

    Rectangle { anchors.fill: parent; color: Theme.viewBackground }

    function selectConsole(platform, index, color) {
        activePlatform = platform
        activeAccentColor = color || Theme.accentColor
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
    // Dejamos que el controlador la cargue cuando la DB esté lista (gamesUpdated)
    Component.onCompleted: {
        if (window.isLoaded) refreshConsoles()
    }

    Connections {
        target: mainController
        function onScanFinished(count) { refreshConsoles() }
        function onGamesUpdated() { 
            refreshConsoles() 
            if (libraryRoot.showGames) gamesModel.filter_by_platform(libraryRoot.activePlatform)
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
                        libraryRoot.selectConsole(model.platform, index, model.accentColor)
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
        anchors.centerIn: parent; spacing: Theme.spaceLarge
        visible: consoleModel.count === 0 && window.isLoaded
        
        Text {
            text: "📡"
            font.pixelSize: 64; Layout.alignment: Qt.AlignHCenter
            opacity: 0.5
        }
        
        ColumnLayout {
            spacing: Theme.spaceSmall
            Text {
                text: I18n.t.empty_library
                color: Theme.textMain; font.pixelSize: Theme.fontHeader; font.bold: true; font.letterSpacing: 2; Layout.alignment: Qt.AlignHCenter
            }
            Text {
                text: I18n.t.empty_library_desc
                color: Theme.textMuted; font.pixelSize: Theme.fontBody; horizontalAlignment: Text.AlignHCenter; Layout.alignment: Qt.AlignHCenter
            }
        }
        
        Button {
            text: I18n.t.configure_paths_btn
            Layout.alignment: Qt.AlignHCenter
            Material.background: Theme.accentColor; font.bold: true
            onClicked: activeViewId = "settingsView" 
        }
    }

    // --- BARRA DE BÚSQUEDA (M.A.N.G.O FUZZYMATCH) ---
    Rectangle {
        id: searchContainer
        anchors.top: consoleCarousel.bottom
        anchors.left: parent.left; anchors.right: parent.right
        anchors.leftMargin: 30; anchors.rightMargin: 30
        height: showGames ? 60 : 0
        visible: showGames
        opacity: showGames ? 1 : 0
        color: Theme.viewBackground // Changed from "transparent"
        property color activeAccentColor: Theme.accentColor
        Behavior on height { NumberAnimation { duration: 400; easing.type: Easing.OutQuint } }
        Behavior on opacity { NumberAnimation { duration: 400 } }

        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            width: parent.width; height: 44; radius: Theme.radiusSmall
            color: Theme.controlBackground; border.color: searchInput.focus ? Theme.accentColor : Theme.cardBorder; border.width: Theme.borderThin
            Behavior on border.color { ColorAnimation { duration: 200 } }
            
            RowLayout {
                anchors.fill: parent; anchors.leftMargin: Theme.spaceMedium; anchors.rightMargin: Theme.spaceSmall; spacing: Theme.spaceMedium
                Text { text: "🔍"; color: searchInput.focus ? Theme.accentColor : Theme.textMuted; font.pixelSize: Theme.fontHeader }
                TextField {
                    id: searchInput
                    Layout.fillWidth: true
                    color: Theme.textMain
                    placeholderText: I18n.t.search_placeholder
                    background: Item {} // Remover el subrayado por defecto
                    font.pixelSize: Theme.fontBody; font.letterSpacing: 1
                    onTextEdited: gamesModel.search_games(text, activePlatform)
                }
            }
        }
    }

    // --- GALERÍA DE JUEGOS ---
    GridView {
        id: romGallery
        anchors.top: searchContainer.bottom; anchors.bottom: parent.bottom
        anchors.left: parent.left; anchors.right: parent.right; anchors.margins: 30; anchors.topMargin: Theme.spaceMedium
        
        // Distribución perfecta: Ajusta el ancho de celda para llenar el espacio proporcionalmente
        cellWidth: width / Math.max(1, Math.floor(width / 240))
        cellHeight: cellWidth * 1.5
        clip: true; visible: showGames; opacity: showGames ? 1 : 0
        model: gamesModel
        cacheBuffer: 1000 
        
        delegate: RomCard {
            title: model.title; platform: model.platform
            gameId: model.gameId; isFavorite: model.isFavorite
            cover2d: model.cover2dPath; cover3d: model.cover3dPath
            accentColor: libraryRoot.resolvedActiveAccent
            onClicked: mainController.launch_game_by_id(model.gameId)
            onInfoClicked: window.openGameDetails(model.gameId)
        }
        Behavior on opacity { NumberAnimation { duration: 500 } }
    }

    // --- BOTÓN VOLVER (Reubicado para no estorbar) ---
    EmuFloatingButton {
        icon: "⟲"; accentColor: Theme.accentColor; size: 54; visible: showGames
        anchors.bottom: parent.bottom; anchors.bottomMargin: Theme.spaceExtraLarge
        anchors.right: parent.right; anchors.rightMargin: Theme.spaceExtraLarge
        onClicked: showGames = false
    }
}
