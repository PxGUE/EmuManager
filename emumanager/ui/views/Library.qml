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
    property color activeAccentColor: Theme.accentColor
    onActiveAccentColorChanged: if (showGames) window.globalAccentColor = activeAccentColor
    onShowGamesChanged: if (!showGames) window.globalAccentColor = Theme.accentColor

    // --- FONDO DINÁMICO (Optimizado para Rendimiento) ---
    Rectangle {
        anchors.fill: parent
        color: Theme.viewBackground
        z: -1

        Rectangle {
            anchors.fill: parent
            opacity: libraryRoot.showGames ? 0.2 : 0.5
            visible: consoleModel.count > 0
            
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.transparent }
                GradientStop { 
                    id: dynamicGradientStop
                    position: 1.0; 
                    color: Qt.rgba(libraryRoot.activeAccentColor.r, libraryRoot.activeAccentColor.g, libraryRoot.activeAccentColor.b, 0.2)
                }
            }
            Behavior on opacity { NumberAnimation { duration: 500 } }
        }
    }

    function selectConsole(platform, index, colorKey) {
        activePlatform = platform
        activeAccentColor = Theme.resolveColor(colorKey, platform)
        gamesModel.update_games()
        gamesModel.filter_by_platform(platform)
        showGames = true
    }

    function refreshConsoles() {
        // 1. Guardar estado actual antes de limpiar
        var savedPlatform = activePlatform
        
        consoleModel.clear()
        if (!mainController) return;
        var summary = mainController.get_consoles_summary()
        console.log("M.A.N.G.O (UI): Cargando " + summary.length + " sistemas en la biblioteca.")
        
        var newIndex = 0
        for (var i = 0; i < summary.length; i++) {
            consoleModel.append(summary[i])
            // 2. Intentar encontrar la posición que teníamos antes
            if (summary[i].platform === savedPlatform) {
                newIndex = i
            }
        }

        // 3. Restaurar posición y color de forma atómica
        if (consoleModel.count > 0) {
            consoleCarousel.currentIndex = newIndex
            var item = consoleModel.get(newIndex)
            activeAccentColor = Theme.resolveColor(item.accentColor, item.platform)
        }
    }

    // No cargar inmediatamente al completar componente para evitar lag inicial
    // Dejamos que el controlador la cargue cuando la DB esté lista (gamesUpdated)
    Component.onCompleted: {
        // La carga se gestiona a través del Connection.onGamesUpdated
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

        onCurrentIndexChanged: {
            if (consoleModel.count > 0 && currentIndex !== -1) {
                var item = consoleModel.get(currentIndex);
                // El color siempre se actualiza con el carrusel
                libraryRoot.activeAccentColor = Theme.resolveColor(item.accentColor, item.platform)
                
                if (libraryRoot.showGames) {
                    // Solo actualizamos plataforma y filtros si ya entramos
                    libraryRoot.activePlatform = item.platform
                    gamesModel.filter_by_platform(item.platform)
                }
            }
        }

        delegate: Item {
            id: delegateRoot; width: libraryRoot.showGames ? 220 : 660; height: libraryRoot.showGames ? 80 : 400
            
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
            startX: -250; startY: consoleCarousel.height / 2
            PathAttribute { name: "iconScale"; value: 0.55 }
            PathAttribute { name: "iconOpacity"; value: 0.25 }
            PathAttribute { name: "iconZ"; value: -20 }
            PathLine { x: consoleCarousel.width / 2; y: consoleCarousel.height / 2 }
            PathAttribute { name: "iconScale"; value: 1.1 }
            PathAttribute { name: "iconOpacity"; value: 1.0 }
            PathAttribute { name: "iconZ"; value: 100 }
            PathLine { x: consoleCarousel.width + 250; y: consoleCarousel.height / 2 }
            PathAttribute { name: "iconScale"; value: 0.55 }
            PathAttribute { name: "iconOpacity"; value: 0.25 }
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
            color: Theme.controlBackground; border.color: searchInput.focus ? libraryRoot.activeAccentColor : Qt.rgba(libraryRoot.activeAccentColor.r, libraryRoot.activeAccentColor.g, libraryRoot.activeAccentColor.b, 0.3); border.width: Theme.borderThin
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
            accentColor: (activePlatform === "all") ? undefined : libraryRoot.activeAccentColor
            onClicked: mainController.launch_game_by_id(model.gameId)
            onInfoClicked: window.openGameDetails(model.gameId)
        }
        Behavior on opacity { NumberAnimation { duration: 500 } }
    }

    EmuFloatingButton {
        icon: "⟲"; accentColor: libraryRoot.activeAccentColor; size: 54; visible: showGames
        anchors.bottom: parent.bottom; anchors.bottomMargin: Theme.spaceExtraLarge
        anchors.right: parent.right; anchors.rightMargin: Theme.spaceExtraLarge
        onClicked: showGames = false
    }
}
