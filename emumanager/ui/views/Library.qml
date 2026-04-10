import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects
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
    property string backgroundCover: ""
    onActiveAccentColorChanged: if (showGames) window.globalAccentColor = activeAccentColor
    onShowGamesChanged: if (!showGames) window.globalAccentColor = Theme.accentColor

    // --- CINEMATIC PORTAL BACKGROUND ---
    Rectangle {
        anchors.fill: parent
        color: Theme.viewBackground
        z: -1

        // 1. Cover Art Layer (Ultra-difusa, ambiental)
        Image {
            id: bgCoverImage
            anchors.fill: parent
            source: libraryRoot.backgroundCover ? "file:///" + libraryRoot.backgroundCover : ""
            fillMode: Image.PreserveAspectCrop
            asynchronous: true
            opacity: (status === Image.Ready && libraryRoot.backgroundCover !== "") ? 0.18 : 0
            visible: libraryRoot.backgroundCover !== ""

            layer.enabled: visible && opacity > 0
            layer.effect: FastBlur { radius: 64 }

            Behavior on opacity { NumberAnimation { duration: 1200; easing.type: Easing.InOutQuad } }
        }

        // 2. Accent Atmosphere (Gradiente lateral — nebula del accent color)
        Rectangle {
            anchors.fill: parent
            opacity: libraryRoot.showGames ? 0.12 : 0.25
            visible: consoleModel.count > 0
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: Qt.rgba(libraryRoot.activeAccentColor.r, libraryRoot.activeAccentColor.g, libraryRoot.activeAccentColor.b, 0.35) }
                GradientStop { position: 0.55; color: Theme.transparent }
            }
            Behavior on opacity { NumberAnimation { duration: 600 } }
        }

        // 3. Accent Bottom Glow (Nebula inferior)
        Rectangle {
            anchors.fill: parent
            opacity: libraryRoot.showGames ? 0.08 : 0.15
            visible: consoleModel.count > 0
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.transparent }
                GradientStop { position: 0.7; color: Theme.transparent }
                GradientStop { position: 1.0; color: Qt.rgba(libraryRoot.activeAccentColor.r, libraryRoot.activeAccentColor.g, libraryRoot.activeAccentColor.b, 0.4) }
            }
            Behavior on opacity { NumberAnimation { duration: 600 } }
        }

        // 4. Vignette (Top + Bottom fade to base) — cinematic framing
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(Theme.viewBackground.r, Theme.viewBackground.g, Theme.viewBackground.b, 0.8) }
                GradientStop { position: 0.2; color: Theme.transparent }
                GradientStop { position: 0.8; color: Theme.transparent }
                GradientStop { position: 1.0; color: Qt.rgba(Theme.viewBackground.r, Theme.viewBackground.g, Theme.viewBackground.b, 0.9) }
            }
        }

        // 5. Horizon Line (Accent energy line en la base)
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width; height: 2
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: Theme.transparent }
                GradientStop { position: 0.3; color: Qt.rgba(libraryRoot.activeAccentColor.r, libraryRoot.activeAccentColor.g, libraryRoot.activeAccentColor.b, 0.5) }
                GradientStop { position: 0.5; color: libraryRoot.activeAccentColor }
                GradientStop { position: 0.7; color: Qt.rgba(libraryRoot.activeAccentColor.r, libraryRoot.activeAccentColor.g, libraryRoot.activeAccentColor.b, 0.5) }
                GradientStop { position: 1.0; color: Theme.transparent }
            }
            opacity: libraryRoot.showGames ? 0.3 : 0.6
            Behavior on opacity { NumberAnimation { duration: 400 } }
        }
    }

    function selectConsole(platform, index, colorKey) {
        activePlatform = platform
        activeAccentColor = Theme.resolveColor(colorKey, platform)
        gamesModel.filter_by_platform(platform)
        showGames = true
    }

    function refreshConsoles() {
        // 1. Guardar estado actual antes de limpiar
        var savedPlatform = activePlatform
        
        consoleModel.clear()
        if (!mainController) return;
        var summary = mainController.get_consoles_summary()
        if (!summary) return;
        
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
            // Cinematic Portal: carátula de fondo al refrescar
            if (mainController) {
                backgroundCover = mainController.get_random_cover_for_platform(item.platform)
            }
        }
    }

    // La carga se gestiona exclusivamente por señales (onGamesUpdated) 
    // garantizando un flujo de datos reactivo y limpio.
    Component.onCompleted: { }

    Connections {
        target: mainController
        function onScanFinished(count) { refreshConsoles() }
        function onLanguage_changed() { refreshConsoles() } // Corregido para coincidir con la señal de Python
        function onGamesUpdated() { 
            refreshConsoles() 
            if (libraryRoot.showGames) gamesModel.filter_by_platform(libraryRoot.activePlatform)
        }
        function onFavoriteToggled(game_id, is_favorite) {
            gamesModel.set_favorite_locally(game_id, is_favorite)
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
                
                // Cinematic Portal: actualizar fondo con carátula aleatoria
                if (mainController) {
                    libraryRoot.backgroundCover = mainController.get_random_cover_for_platform(item.platform)
                }
                
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

    // --- CABECERA DE BÚSQUEDA Y ACCIONES (Rediseño Centrado) ---
    Item {
        id: searchContainer
        anchors.top: consoleCarousel.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: showGames ? 70 : 0
        visible: showGames
        opacity: showGames ? 1 : 0
        Behavior on height { NumberAnimation { duration: 400; easing.type: Easing.OutQuint } }
        Behavior on opacity { NumberAnimation { duration: 400 } }

        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            height: parent.height
            spacing: 25

            // 1. BOTÓN REGRESAR
            Rectangle {
                width: 44; height: 44; radius: 12
                color: backMA.hovered ? Qt.alpha(libraryRoot.activeAccentColor, 0.2) : Theme.controlBackground
                border.color: Qt.alpha(libraryRoot.activeAccentColor, 0.3); border.width: 1
                Text { text: "◀"; color: Theme.textMain; anchors.centerIn: parent; font.pixelSize: 14; opacity: 0.8 }
                MouseArea { id: backMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: showGames = false }
            }

            // 2. BARRA DE BÚSQUEDA (Centrada y proporcianal)
            Rectangle {
                width: 500; height: 44; radius: 12
                color: Theme.controlBackground
                border.color: searchInput.focus ? libraryRoot.activeAccentColor : Qt.alpha(libraryRoot.activeAccentColor, 0.2)
                border.width: 1
                
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 15; anchors.rightMargin: 10; spacing: 12
                    Text { 
                        text: "🔍"
                        font.pixelSize: 16
                        color: searchInput.focus ? libraryRoot.activeAccentColor : Theme.textMuted
                    }
                    TextField {
                        id: searchInput
                        Layout.fillWidth: true
                        color: Theme.textMain
                        placeholderText: I18n.t.search_placeholder
                        background: Item {}
                        font.pixelSize: 14
                        onTextEdited: gamesModel.search_games(text, activePlatform)
                    }
                    Text { 
                        text: "✕"
                        color: Theme.textMuted
                        font.bold: true
                        visible: searchInput.text !== ""
                        opacity: clearMA.hovered ? 1.0 : 0.5
                        MouseArea { 
                            id: clearMA
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                searchInput.text = ""
                                gamesModel.search_games("", activePlatform)
                            }
                        }
                    }
                }
            }

            // 3. FILTRO DE FAVORITOS
            Rectangle {
                width: 44; height: 44; radius: 12
                color: (gamesModel && gamesModel.showFavoritesOnly) ? libraryRoot.activeAccentColor : (favFilterMA.hovered ? Qt.alpha(libraryRoot.activeAccentColor, 0.2) : Theme.controlBackground)
                border.color: (gamesModel && gamesModel.showFavoritesOnly) ? Theme.transparent : Qt.alpha(libraryRoot.activeAccentColor, 0.3)
                border.width: 1
                Text { text: "❤️"; anchors.centerIn: parent; font.pixelSize: 16; opacity: (gamesModel && gamesModel.showFavoritesOnly) ? 1.0 : 0.6 }
                MouseArea { 
                    id: favFilterMA; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor 
                    onClicked: if (gamesModel) gamesModel.showFavoritesOnly = !gamesModel.showFavoritesOnly
                }
            }
        }
    }

    // --- GALERÍA DE JUEGOS ---
    GridView {
        id: romGallery
        anchors.top: searchContainer.bottom; anchors.bottom: parent.bottom
        anchors.left: parent.left; anchors.right: parent.right
        anchors.leftMargin: 60; anchors.rightMargin: 60; anchors.topMargin: 20
        
        cellWidth: Math.floor(width / Math.max(1, Math.floor(width / 220)))
        cellHeight: 340
        clip: true; visible: showGames; opacity: showGames ? 1 : 0
        model: gamesModel
        cacheBuffer: 1000 
        
        delegate: Item {
            width: romGallery.cellWidth; height: romGallery.cellHeight
            RomCard {
                anchors.centerIn: parent
                title: model.title; platform: model.platform
                gameId: model.gameId; isFavorite: model.isFavorite
                cover2d: model.cover2dPath; cover3d: model.cover3dPath
                accentColor: (activePlatform === "all") ? undefined : libraryRoot.activeAccentColor
                onClicked: mainController.launch_game_by_id(model.gameId)
                onInfoClicked: window.openGameDetails(model.gameId)
            }
        }
        Behavior on opacity { NumberAnimation { duration: 500 } }
    }
}
