import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects
import QtQuick.Shapes
import "../components"

/**
 * Library.qml — Vista principal de la biblioteca de juegos.
 * 
 * Presenta dos modos principales:
 * 1. "carousel": Selección de consolas de forma inmersiva y 3D.
 * 2. "grid": Exploración de juegos de una consola seleccionada con filtros y búsqueda.
 * 
 * Gestiona el filtrado dinámico de juegos, el estado de carga y la visualización de
 * detalles del juego en un panel lateral expansible.
 */
Item {
    id: libraryRoot
    
    state: "carousel" // Estados posibles: "carousel", "grid" o "collector"

    states: [
        State { 
            name: "carousel"
            PropertyChanges { target: carousel; visible: true; opacity: 1; scale: 1.0 }
            PropertyChanges { target: gridContainer; visible: false; opacity: 0; y: 40; scale: 0.95 }
        },
        State {
            name: "grid"
            PropertyChanges { target: carousel; visible: false; opacity: 0; scale: 0.9 }
            PropertyChanges { target: gridContainer; visible: true; opacity: 1; y: 0; scale: 1.0 }
        },
        State {
            name: "collector" 
            PropertyChanges { target: carousel; visible: false; opacity: 0; scale: 0.8 }
            PropertyChanges { target: collectorContainer; visible: true; opacity: 1; y: 0; scale: 1.0 }
        }
    ]

    transitions: [
        Transition {
            from: "carousel"; to: "grid"
            SequentialAnimation {
                PropertyAction { target: gridContainer; property: "visible"; value: true }
                ParallelAnimation {
                    NumberAnimation { target: carousel; property: "opacity"; duration: 450; easing.type: Easing.OutCubic }
                    NumberAnimation { target: carousel; property: "scale"; duration: 450; easing.type: Easing.InBack }
                    NumberAnimation { target: gridContainer; property: "opacity"; duration: 600; easing.type: Easing.OutCubic }
                    NumberAnimation { target: gridContainer; property: "y"; duration: 600; easing.type: Easing.OutBack }
                    NumberAnimation { target: gridContainer; property: "scale"; duration: 600; easing.type: Easing.OutBack }
                }
                PropertyAction { target: carousel; property: "visible"; value: false }
            }
        },
        Transition {
            from: "*"; to: "carousel"
            SequentialAnimation {
                PropertyAction { target: carousel; property: "visible"; value: true }
                ParallelAnimation {
                    NumberAnimation { target: gridContainer; property: "opacity"; duration: 350; easing.type: Easing.OutCubic }
                    NumberAnimation { target: collectorContainer; property: "opacity"; duration: 350; easing.type: Easing.OutCubic }
                    NumberAnimation { target: carousel; property: "opacity"; duration: 500; easing.type: Easing.OutCubic }
                    NumberAnimation { target: carousel; property: "scale"; duration: 550; easing.type: Easing.OutBack }
                }
                PropertyAction { target: gridContainer; property: "visible"; value: false }
                PropertyAction { target: collectorContainer; property: "visible"; value: false }
            }
        },
        Transition {
            from: "carousel"; to: "collector"
            SequentialAnimation {
                PropertyAction { target: collectorContainer; property: "visible"; value: true }
                ParallelAnimation {
                    NumberAnimation { target: carousel; property: "opacity"; duration: 400; easing.type: Easing.OutCubic }
                    NumberAnimation { target: carousel; property: "scale"; duration: 400; easing.type: Easing.InBack }
                    NumberAnimation { target: collectorContainer; property: "opacity"; duration: 650; easing.type: Easing.OutCubic }
                    NumberAnimation { target: collectorContainer; property: "y"; duration: 650; easing.type: Easing.OutBack }
                    NumberAnimation { target: collectorContainer; property: "scale"; duration: 650; easing.type: Easing.OutBack }
                }
                PropertyAction { target: carousel; property: "visible"; value: false }
            }
        }
    ]

    
    // Propiedades de estado de la consola seleccionada
    property string currentConsoleId: ""
    property string currentConsoleName: ""
    property string currentEmuName: ""
    property var currentGames: []
    
    // Propiedades de búsqueda y filtrado
    property string searchText: searchInput.text
    property bool onlyFavorites: false
    property bool needsHardRefresh: false
    
    /**
     * Motor de filtrado reactivo.
     * Se actualiza automáticamente cuando cambia searchText o onlyFavorites.
     */
    property var filteredGames: {
        if (!currentGames) return []
        let search = (libraryRoot.searchText || "").toLowerCase()
        return currentGames.filter(game => {
            let titleStr = (game.title || game.name || "").toLowerCase()
            let matchSearch = search === "" || titleStr.includes(search)
            let matchFav = !libraryRoot.onlyFavorites || game.isFavorite
            return matchSearch && matchFav
        })
    }
    property string currentBackground: (libraryRoot.state === "collector" && collectorView.currentItem) ? collectorView.currentItem.itemBackground : ((carousel.currentItem) ? carousel.currentItem.backgroundSource : "")
    property color currentAccentColor: (carousel.currentItem) ? carousel.currentItem.accentColor : "#4da6ff"
    
    property var selectedGame: null // Para el panel de información
    property bool isEmpty: bridge ? (bridge.lib.scannedConsoles.length === 0) : true

    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    signal gridEntranceTriggered()

    Connections {
        target: bridge
        function onStatsUpdated() {
            // Actualizar datos del carrusel
            let consoles = bridge.lib.scannedConsoles
            libraryRoot.isEmpty = (consoles.length === 0)
            carousel.model = consoles
            
            // Solo forzar actualización del modelo si se ha marcado explícitamente (ej: tras un escaneo)
            // O si no estamos en modo grid todavía (primera carga)
            if (libraryRoot.state === "grid" && libraryRoot.currentConsoleId !== "") {
                if (libraryRoot.needsHardRefresh) {
                    let games = bridge.lib.getGamesForConsole(libraryRoot.currentConsoleId)
                    libraryRoot.currentGames = games
                    libraryRoot.needsHardRefresh = false
                }
            }
        }
    }

    // --- ANIMACIONES DE FONDO (FADE) ---
    onCurrentBackgroundChanged: {
        bgFadeAnim.stop()
        bgFadeAnim.start()
    }

    SequentialAnimation {
        id: bgFadeAnim
        NumberAnimation { target: immersiveBg; property: "opacity"; to: 0; duration: 250 }
        PropertyAction { target: immersiveBg; property: "source"; value: libraryRoot.currentBackground }
        NumberAnimation { target: immersiveBg; property: "opacity"; to: 0.4; duration: 600; easing.type: Easing.OutQuad }
    }
    
    // --- LÓGICA DE RESPONSIVIDAD PREMIUM ---
    readonly property real responsiveScale: Math.max(1.0, Math.min(width / 1000, height / 650))
    readonly property real cardWidth: 340 * responsiveScale
    readonly property real cardHeight: 480 * responsiveScale

    // --- LÓGICA DE CENTRADO DE GRID ---
    readonly property real gridCellWidth: 240
    readonly property real gridHorizontalPadding: {
        let available = gridContainer.width
        return Math.max(0, (available - (Math.floor(available / gridCellWidth) * gridCellWidth)) / 2)
    }
    Rectangle {
        anchors.fill: parent
        color: "#0a0b12"
        
        // Glow ambiental (Aurora) - Unificado y más visible
        Rectangle {
            id: backgroundBlur
            anchors.fill: parent
            opacity: 0.4
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: Qt.alpha(currentAccentColor, 0.5) }
                GradientStop { position: 0.8; color: "transparent" }
            }
            Behavior on color { ColorAnimation { duration: 800 } }
        }

        // Fondo de Consola (Simplificado para evitar parpadeos o fallos)
        Image {
            id: immersiveBg
            anchors.fill: parent
            source: "" // Manual control via animation
            fillMode: Image.PreserveAspectCrop
            opacity: 0.0
            visible: opacity > 0
        }

        
        // Viñeta para legibilidad
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.5; color: "transparent" }
                GradientStop { position: 1.0; color: "#000000" }
            }
            opacity: 0.6
        }

        // Overlay Grid
        Rectangle {
            anchors.fill: parent
            visible: libraryRoot.state === "grid"
            color: "#ee000000"
        }
    }

    // --- EMPTY STATE ---
    Rectangle {
        id: emptyState
        anchors.centerIn: parent
        width: 480
        height: 360
        radius: 40
        color: "#11131a"
        border.color: "#252835"
        border.width: 1
        visible: isEmpty
        opacity: visible ? 1.0 : 0.0
        Behavior on opacity { NumberAnimation { duration: 400 } }

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 30
            Label { text: "📚"; font.pixelSize: 84; Layout.alignment: Qt.AlignHCenter }
            ColumnLayout {
                spacing: 8
                Layout.alignment: Qt.AlignHCenter
                Label { text: tr("lib_empty_title").toUpperCase(); font.pixelSize: 26; font.bold: true; color: "white"; Layout.alignment: Qt.AlignHCenter }
                Label { text: tr("lib_empty_sub"); font.pixelSize: 14; color: "#666677"; horizontalAlignment: Text.AlignHCenter; Layout.preferredWidth: 340; wrapMode: Text.WordWrap; Layout.alignment: Qt.AlignHCenter }
            }

        }
    }

    // --- CAROUSEL MODE ---
    PathView {
        id: carousel
        z: 10
        anchors.fill: parent
        anchors.topMargin: 40
        visible: !libraryRoot.isEmpty
        opacity: libraryRoot.state === "carousel" ? 1 : 0
        model: (bridge && bridge.lib.scannedConsoles) ? bridge.lib.scannedConsoles : []
        pathItemCount: 5
        preferredHighlightBegin: 0.5
        preferredHighlightEnd: 0.5
        highlightRangeMode: PathView.StrictlyEnforceRange
        dragMargin: width / 2
        flickDeceleration: 1500
        clip: true

        path: Path {
            startX: -carousel.width * 0.3
            startY: carousel.height * 0.5
            PathAttribute { name: "itemZ"; value: 0 }
            PathAttribute { name: "itemScale"; value: 0.2 }
            PathAttribute { name: "itemRotation"; value: 75 }
            PathAttribute { name: "itemOpacity"; value: 0.0 }
            
            PathLine { x: carousel.width * 0.1; y: carousel.height * 0.5 }
            PathAttribute { name: "itemZ"; value: 10 }
            PathAttribute { name: "itemScale"; value: 0.6 }
            PathAttribute { name: "itemRotation"; value: 50 }
            PathAttribute { name: "itemOpacity"; value: 0.5 }
            
            PathLine { x: carousel.width * 0.5; y: carousel.height * 0.5 }
            PathAttribute { name: "itemZ"; value: 100 }
            PathAttribute { name: "itemScale"; value: 1.15 }
            PathAttribute { name: "itemRotation"; value: 0 }
            PathAttribute { name: "itemOpacity"; value: 1.0 }
            
            PathLine { x: carousel.width * 0.9; y: carousel.height * 0.5 }
            PathAttribute { name: "itemZ"; value: 10 }
            PathAttribute { name: "itemScale"; value: 0.6 }
            PathAttribute { name: "itemRotation"; value: -50 }
            PathAttribute { name: "itemOpacity"; value: 0.5 }
            
            PathLine { x: carousel.width + (carousel.width * 0.3); y: carousel.height * 0.5 }
            PathAttribute { name: "itemZ"; value: 0 }
            PathAttribute { name: "itemScale"; value: 0.2 }
            PathAttribute { name: "itemRotation"; value: -75 }
            PathAttribute { name: "itemOpacity"; value: 0.0 }
        }

        delegate: Item {
            id: delegateRoot
            width: libraryRoot.cardWidth
            height: libraryRoot.cardHeight
            z: PathView.itemZ || 0
            scale: PathView.itemScale || 1.0
            opacity: PathView.itemOpacity || 0.0
            
            readonly property bool isCurrent: PathView.isCurrentItem
            readonly property color accentColor: modelData.color
            readonly property string backgroundSource: modelData.background || ""
            property bool isHovered: false
            
            property real floatOffset: 0
            SequentialAnimation on floatOffset {
                running: delegateRoot.isCurrent
                loops: Animation.Infinite
                NumberAnimation { from: 0; to: -30; duration: 2000; easing.type: Easing.InOutQuad }
                NumberAnimation { from: -30; to: 0; duration: 2000; easing.type: Easing.InOutQuad }
            }


            Rectangle {
                id: containerRect
                width: parent.width
                height: parent.height - (40 * responsiveScale)
                anchors.centerIn: parent
                anchors.verticalCenterOffset: isCurrent ? floatOffset : 0
                radius: 45 * responsiveScale
                color: "#13151d"
                border.color: isCurrent ? accentColor : "#2a2d3a"
                border.width: isCurrent ? 3 : 1
                

                // Efecto de Aura Pulsante al Clic (Dispersión)
                Rectangle {
                    id: clickRipple
                    anchors.centerIn: parent
                    width: parent.width
                    height: parent.height
                    radius: parent.radius
                    color: "transparent"
                    border.color: accentColor
                    border.width: 10 * responsiveScale
                    opacity: 0
                    z: -1
                    
                    ParallelAnimation {
                        id: dispersionAnim
                        NumberAnimation { target: clickRipple; property: "opacity"; from: 0.8; to: 0; duration: 600; easing.type: Easing.OutCubic }
                        NumberAnimation { target: clickRipple; property: "scale"; from: 1.0; to: 1.4; duration: 600; easing.type: Easing.OutCubic }
                        NumberAnimation { target: clickRipple; property: "border.width"; from: 15; to: 0; duration: 600 }
                    }
                }
                transform: Rotation {
                    origin.x: 170; origin.y: 230
                    axis { x: 0; y: 1; z: 0 }
                    angle: PathView.itemRotation || 0
                }


                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 40
                    spacing: 0
                    
                    Item {
                        Layout.alignment: Qt.AlignHCenter
                        width: 160 * responsiveScale; height: 160 * responsiveScale
                        
                        Rectangle {
                            id: aura
                            anchors.centerIn: parent
                            width: 140 * responsiveScale; height: 140 * responsiveScale; radius: (width / 2)
                            color: "transparent"
                            border.color: accentColor
                            border.width: 5
                            opacity: 0
                            scale: 1.0
                            visible: isCurrent
                            
                            SequentialAnimation on opacity {
                                running: aura.visible
                                loops: Animation.Infinite
                                NumberAnimation { from: 0.7; to: 0; duration: 1500; easing.type: Easing.OutQuad }
                                PauseAnimation { duration: 500 }
                            }
                            SequentialAnimation on scale {
                                running: aura.visible
                                loops: Animation.Infinite
                                NumberAnimation { from: 1.0; to: 1.6; duration: 1500; easing.type: Easing.OutQuad }
                                PauseAnimation { duration: 500 }
                            }
                        }
                        Rectangle {
                            anchors.centerIn: parent
                            width: 140; height: 140; radius: 70
                            color: "#0a0b12"
                            border.color: Qt.alpha(accentColor, 0.5)
                            border.width: 2
                            
                            Label { 
                                anchors.centerIn: parent
                                text: "🎮"
                                font.pixelSize: 64
                                scale: isCurrent ? 1.1 : 1.0
                                Behavior on scale { NumberAnimation { duration: 400 } }
                            }
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                    
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4 * responsiveScale
                        
                        // Título: Nombre de la Consola
                        Label {
                            text: modelData.name.toUpperCase()
                            font.pixelSize: 28 * responsiveScale; font.bold: true; color: "white"
                            Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter
                            font.letterSpacing: 1.5; opacity: isCurrent ? 1.0 : 0.6
                        }
                        
                        // Subtítulo: Nombre del Emulador
                        Label {
                            text: modelData.emu_name
                            font.pixelSize: 14 * responsiveScale; font.weight: Font.Medium; color: accentColor
                            Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter
                            opacity: isCurrent ? 0.8 : 0.4
                        }

                        // Contador de Títulos
                        Label {
                            text: tr("lib_games_count", modelData.count).toUpperCase()
                            font.pixelSize: 11 * responsiveScale; font.bold: true; color: "#888899"
                            Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter
                            opacity: isCurrent ? 0.8 : 0.3
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                    
                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter
                        width: 180 * responsiveScale; height: 54 * responsiveScale; radius: height / 2
                        color: isCurrent ? accentColor : "#1affffff"
                        opacity: isCurrent ? 1.0 : 0.2
                        border.color: isCurrent ? "white" : "transparent"
                        border.width: isCurrent ? 1 : 0
                        Label {
                            anchors.centerIn: parent
                            text: tr("lib_btn_explore").toUpperCase()
                            font.bold: true; color: isCurrent ? "black" : "white"; font.pixelSize: 12 * responsiveScale
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                dispersionAnim.restart()
                                if (index === carousel.currentIndex) {
                                    libraryRoot.currentConsoleId = modelData.id
                                    libraryRoot.currentConsoleName = modelData.name
                                    libraryRoot.currentEmuName = modelData.emu_name
                                    libraryRoot.currentGames = bridge.lib.getGamesForConsole(modelData.id)
                                    libraryRoot.state = (bridge && bridge.set.collectorMode) ? "collector" : "grid"
                                    libraryRoot.gridEntranceTriggered()
                                } else {
                                    carousel.currentIndex = index
                                }
                            }
                        }
                    }
                }

                // Eliminamos el MouseArea general para que no interfiera con los botones internos
                // Si el usuario hace clic fuera de los botones pero en la tarjeta, solo hace scroll.
                MouseArea {
                    anchors.fill: parent
                    z: -1
                    onClicked: {
                        if (index !== carousel.currentIndex) {
                            carousel.currentIndex = index
                        }
                    }
                }
            }
        }
    }

    Item {
        id: gridContainer
        anchors.fill: parent
        anchors.margins: 40
        opacity: 0
        scale: 1.0
        visible: false
        
        ColumnLayout {
            anchors.fill: parent
            spacing: 30

            // Modern Transparent Header
            RowLayout {
                id: gridHeader
                Layout.fillWidth: true
                Layout.leftMargin: libraryRoot.gridHorizontalPadding
                Layout.rightMargin: libraryRoot.gridHorizontalPadding
                spacing: 20
                
                Button {
                    id: btnBackGrid
                    Layout.preferredWidth: 48
                    Layout.preferredHeight: 48
                    onClicked: libraryRoot.state = "carousel"
                    background: Rectangle {
                        radius: 24
                        color: btnBackGrid.hovered ? "#33ffffff" : "#11ffffff"
                        border.color: "#22ffffff"
                        border.width: 1
                    }
                    contentItem: Label { text: "←"; color: "white"; font.pixelSize: 20; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }

                ColumnLayout {
                    spacing: 0
                    Label {
                        text: libraryRoot.currentConsoleName
                        font.pixelSize: 26
                        font.bold: true
                        color: "white"
                    }
                    Label {
                        text: tr("lib_games_count", libraryRoot.filteredGames.length).toUpperCase()
                        font.pixelSize: 10
                        font.bold: true
                        color: currentAccentColor
                        font.letterSpacing: 1
                    }
                }

                Item { Layout.fillWidth: true }

                RowLayout {
                    spacing: 12
                    
                    // Botón Favoritos Toggle
                    Button {
                        id: btnFavFilter
                        Layout.preferredWidth: 44
                        Layout.preferredHeight: 44
                        onClicked: libraryRoot.onlyFavorites = !libraryRoot.onlyFavorites
                        background: Rectangle {
                            radius: 22
                            color: btnFavFilter.hovered ? "#22ffffff" : (libraryRoot.onlyFavorites ? "#33ffff00" : "#12ffffff")
                            border.color: libraryRoot.onlyFavorites ? "#ffff00" : "transparent"
                            border.width: 1
                        }
                        contentItem: Label {
                            text: "⭐"
                            opacity: libraryRoot.onlyFavorites ? 1.0 : 0.4
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 18
                        }
                    }

                // Refresh Button
                Button {
                    id: btnRefresh
                    Layout.preferredWidth: 44
                    Layout.preferredHeight: 44
                    onClicked: {
                        searchInput.text = ""
                        libraryRoot.needsHardRefresh = true
                        bridge.lib.scanGames(false, false, libraryRoot.currentConsoleId)
                    }
                    background: Rectangle {
                        radius: 22
                        color: btnRefresh.hovered ? "#22ffffff" : "#12ffffff"
                        border.color: "#1affffff"
                        border.width: 1
                    }
                    contentItem: Label {
                        text: "↻"
                        font.pixelSize: 22
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        opacity: btnRefresh.hovered ? 1.0 : 0.6
                        Behavior on opacity { NumberAnimation { duration: 200 } }
                        
                        RotationAnimation on rotation {
                            running: btnRefresh.pressed
                            from: 0; to: 360; duration: 500; loops: Animation.Infinite
                        }
                    }
                    
                    ToolTip.visible: hovered
                    ToolTip.text: tr("lib_refresh")
                    ToolTip.delay: 500
                    
                    Behavior on scale { NumberAnimation { duration: 100 } }
                    scale: pressed ? 0.9 : 1.0
                }

                // Emulator Tweaks Button
                Button {
                    id: btnSettings
                    Layout.preferredWidth: 44
                    Layout.preferredHeight: 44
                    onClicked: {
                        tweakPopup.currentEmuId = libraryRoot.currentConsoleId
                        tweakPopup.currentEmuName = libraryRoot.currentEmuName
                        tweakPopup.accentColor = libraryRoot.currentAccentColor
                        tweakPopup.open()
                    }
                    background: Rectangle {
                        radius: 22
                        color: btnSettings.hovered ? "#22ffffff" : "#12ffffff"
                        border.color: "#1affffff"
                        border.width: 1
                    }
                    contentItem: Label {
                        text: "⚙️"
                        font.pixelSize: 18
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        opacity: btnSettings.hovered ? 1.0 : 0.6
                        Behavior on opacity { NumberAnimation { duration: 200 } }
                    }
                    
                    ToolTip.visible: hovered
                    ToolTip.text: tr("lib_emu_settings")
                    ToolTip.delay: 500
                    
                    Behavior on scale { NumberAnimation { duration: 100 } }
                    scale: pressed ? 0.9 : 1.0
                }

                // Search Bar
                Rectangle {
                    Layout.preferredWidth: 300
                    Layout.preferredHeight: 44
                    radius: 22
                    color: "#18ffffff"
                    border.color: "#1affffff"
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 15
                        spacing: 10
                        Label { text: "🔍"; opacity: 0.6; font.pixelSize: 14 }
                        TextInput {
                            id: searchInput
                            Layout.fillWidth: true
                            color: "white"
                            font.pixelSize: 14
                            verticalAlignment: TextInput.AlignVCenter
                            Label {
                                text: tr("lib_search")
                                color: "#66ffffff"
                                visible: searchInput.text === ""
                                anchors.fill: parent
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }
            }
        }

        GridView {
            id: gamesGrid
            Layout.fillWidth: true
            Layout.fillHeight: true
            cellWidth: libraryRoot.gridCellWidth
            cellHeight: 380
            model: libraryRoot.filteredGames
            property var currentItemData: null
            clip: true
            
            ScrollBar.vertical: ScrollBar { 
                policy: ScrollBar.AsNeeded
            }
            
            leftMargin: libraryRoot.gridHorizontalPadding
            rightMargin: libraryRoot.gridHorizontalPadding

            delegate: Item {
                id: gameCardRoot
                width: 240
                height: 380
                
                property bool isHovered: cardHover.hovered || 
                                         (typeof infoBtnMouse !== "undefined" && infoBtnMouse.containsMouse) || 
                                         (typeof favBtnMouse !== "undefined" && favBtnMouse.containsMouse)

                SequentialAnimation {
                    id: staggeredEntry
                    running: false
                    PauseAnimation { duration: Math.min(index * 20, 300) }
                    ParallelAnimation {
                        NumberAnimation { target: cardBody; property: "opacity"; to: 1.0; duration: 500; easing.type: Easing.OutCubic }
                        NumberAnimation { target: cardBody; property: "scale"; to: 1.0; duration: 600; easing.type: Easing.OutBack }
                    }
                }

                Connections {
                    target: libraryRoot
                    function onGridEntranceTriggered() {
                        cardBody.opacity = 0
                        cardBody.scale = 0.8
                        staggeredEntry.restart()
                    }
                }

                HoverHandler {
                    id: cardHover
                    cursorShape: Qt.PointingHandCursor
                    onHoveredChanged: if (hovered) gamesGrid.currentItemData = modelData
                }

                Rectangle {
                    id: cardBody
                    anchors.fill: parent
                    anchors.margins: 12
                    radius: 0; clip: true; layer.enabled: true
                    color: "#0d0f1a"
                    scale: isHovered ? 1.05 : 1.0
                    z: isHovered ? 10 : 1
                    Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutBack } }

                    Image {
                        id: coverImg
                        anchors.fill: parent; anchors.margins: 4
                        source: modelData.cover || ""
                        fillMode: Image.PreserveAspectCrop
                        opacity: modelData.cover ? (isHovered ? 1.0 : 0.8) : 0.1
                        scale: isHovered ? 1.1 : 1.0
                        Behavior on scale { NumberAnimation { duration: 1200; easing.type: Easing.OutCubic } }

                        TapHandler {
                            onTapped: {
                                if (window && window.requestLaunch) 
                                    window.requestLaunch(modelData.path, modelData.id_emu, modelData.name)
                            }
                        }
                    }

                    Rectangle {
                        id: infoOverlay
                        anchors.bottom: parent.bottom; width: parent.width
                        height: isHovered ? 110 : 70
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 0.4; color: Qt.rgba(10/255, 12/255, 20/255, 0.9) }
                            GradientStop { position: 1.0; color: "#0a0c14" }
                        }
                        Behavior on height { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }

                        ColumnLayout {
                            anchors.fill: parent; anchors.margins: 16; Layout.topMargin: 20
                            spacing: 4
                            Label {
                                Layout.fillWidth: true; text: modelData.name
                                color: "white"; font.pixelSize: 14; font.bold: true
                                elide: Text.ElideRight; maximumLineCount: 2; wrapMode: Text.WordWrap
                            }
                            Label { 
                                text: "🕒 " + modelData.playtime
                                color: "#b0ffffff"; font.pixelSize: 11; visible: isHovered 
                            }
                        }
                    }

                    Rectangle {
                        id: neonBorder
                        anchors.fill: parent; radius: 0; color: "transparent"
                        border.color: currentAccentColor; border.width: isHovered ? 3 : 1
                        opacity: isHovered ? 1.0 : 0.4
                        Behavior on border.width { NumberAnimation { duration: 250 } }
                        
                        layer.enabled: isHovered
                        layer.effect: MultiEffect {
                            shadowEnabled: true; shadowBlur: 1.0; shadowColor: currentAccentColor
                            shadowHorizontalOffset: 0; shadowVerticalOffset: 0
                        }
                    }
                }

                Row {
                    id: actionBar
                    anchors.top: parent.top; anchors.right: parent.right
                    anchors.topMargin: 22; anchors.rightMargin: 22
                    spacing: 8; z: 20
                    visible: isHovered || modelData.isFavorite

                    Rectangle {
                        width: 38; height: 38; radius: 19
                        color: infoBtnMouse.containsMouse ? currentAccentColor : "#e00a0c14"
                        border.color: currentAccentColor; border.width: 1
                        visible: isHovered
                        Label { anchors.centerIn: parent; text: "ⓘ"; font.pixelSize: 20; color: infoBtnMouse.containsMouse ? "black" : "white" }
                        MouseArea {
                            id: infoBtnMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                            onClicked: { libraryRoot.selectedGame = modelData; infoPanel.open() }
                        }
                    }

                    Rectangle {
                        width: 38; height: 38; radius: 19
                        color: favBtnMouse.containsMouse ? "#ff4d4d" : (modelData.isFavorite ? "#33ff4d4d" : "#e00a0c14")
                        border.color: modelData.isFavorite ? "#ff4d4d" : currentAccentColor
                        border.width: 1
                        Label { anchors.centerIn: parent; text: modelData.isFavorite ? "❤️" : "🤍"; font.pixelSize: 18 }
                        MouseArea {
                            id: favBtnMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                let newVal = bridge.lib.toggleFavorite(modelData.path)
                                modelData.isFavorite = newVal
                                if (libraryRoot.onlyFavorites) libraryRoot.needsHardRefresh = true
                            }
                        }
                    }
                    }
                }
            }
        }
    }


    // --- MODO COLECCIONISTA: CAROUSEL DE JUEGOS ---
    Item {
        id: collectorContainer
        anchors.fill: parent
        opacity: 0
        visible: false
        scale: 0.9
        y: 50

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 20

            // Header simplificado para modo coleccionista
            RowLayout {
                Layout.fillWidth: true
                spacing: 20
                
                Button {
                    id: btnBackCollector
                    Layout.preferredWidth: 48; Layout.preferredHeight: 48
                    onClicked: libraryRoot.state = "carousel"
                    background: Rectangle {
                        radius: 24
                        color: btnBackCollector.hovered ? "#33ffffff" : "#11ffffff"
                        border.color: "#22ffffff"; border.width: 1
                    }
                    contentItem: Label { text: "←"; color: "white"; font.pixelSize: 20; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }

                ColumnLayout {
                    spacing: 0
                    Label {
                        text: libraryRoot.currentConsoleName.toUpperCase()
                        font.pixelSize: 24; font.bold: true; color: "white"; font.letterSpacing: 2
                    }
                    Label {
                        text: tr("lib_games_count", libraryRoot.filteredGames.length).toUpperCase()
                        font.pixelSize: 10; font.bold: true; color: currentAccentColor; font.letterSpacing: 1
                    }
                }
                Item { Layout.fillWidth: true }
            }

            PathView {
                id: collectorView
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: libraryRoot.filteredGames
                pathItemCount: 3
                preferredHighlightBegin: 0.5
                preferredHighlightEnd: 0.5
                highlightRangeMode: PathView.StrictlyEnforceRange
                snapMode: PathView.SnapToItem
                clip: true

                path: Path {
                    startX: -collectorView.width * 0.5
                    startY: collectorView.height / 2
                    PathLine { x: collectorView.width * 0.5; y: collectorView.height / 2 }
                    PathLine { x: collectorView.width * 1.5; y: collectorView.height / 2 }
                }

                    delegate: Item {
                        id: collectorDelegate
                        width: collectorView.width * 0.8
                        height: collectorView.height * 0.85
                        z: PathView.isCurrentItem ? 10 : 1
                        opacity: PathView.isCurrentItem ? 1.0 : 0.4
                        scale: PathView.isCurrentItem ? 1.0 : 0.85
                        
                        property string itemBackground: modelData.background || ""

                        Behavior on opacity { NumberAnimation { duration: 300 } }
                        Behavior on scale { NumberAnimation { duration: 400; easing.type: Easing.OutBack } }

                        Rectangle {
                            anchors.fill: parent
                            radius: 0 // Identidad Hard-Edge
                            color: "#cc0a0b12"
                            border.color: collectorDelegate.PathView.isCurrentItem ? currentAccentColor : "#22ffffff"
                            border.width: collectorDelegate.PathView.isCurrentItem ? 2 : 1
                            
                            // SISTEMA DE DOS COLUMNAS (REPARADO: 35% / 65%)
                            Item {
                                anchors.fill: parent

                                // COLUMNA IZQUIERDA: Información (35%)
                                Item {
                                    id: leftInfoCol
                                    anchors.left: parent.left
                                    width: parent.width * 0.35
                                    anchors.top: parent.top
                                    anchors.bottom: parent.bottom
                                    
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 40
                                        spacing: 20

                                        ColumnLayout {
                                            spacing: 5
                                            Label {
                                                id: mainTitle
                                                text: modelData.title
                                                font.pixelSize: 28; font.weight: Font.Black; color: "white"
                                                wrapMode: Text.WordWrap; Layout.fillWidth: true; font.letterSpacing: -0.5
                                            }
                                            Label {
                                                text: (modelData.developer || "N/A") + " • " + (modelData.year || "N/A")
                                                font.pixelSize: 13; color: currentAccentColor; font.weight: Font.Medium
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true; height: 1; color: "#1affffff"
                                        }

                                        // DESCRIPCIÓN CON SCROLL ESTRICTAMENTE VERTICAL
                                        ScrollView {
                                            id: descScroll
                                            Layout.fillWidth: true; Layout.fillHeight: true
                                            clip: true
                                            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                                            ScrollBar.vertical.policy: ScrollBar.AsNeeded
                                            
                                            Label {
                                                width: descScroll.availableWidth - 10 
                                                text: modelData.description || tr("lib_no_desc")
                                                font.pixelSize: 14; color: "#b0ffffff"; wrapMode: Text.WordWrap
                                                lineHeight: 1.5; horizontalAlignment: Text.AlignJustify
                                            }
                                        }

                                        Button {
                                            id: playBtnCollector
                                            Layout.fillWidth: true; Layout.preferredHeight: 54
                                            onClicked: {
                                                if (window && window.requestLaunch) {
                                                    window.requestLaunch(modelData.path, modelData.id_emu, modelData.title)
                                                }
                                            }
                                            background: Rectangle {
                                                radius: 0
                                                color: playBtnCollector.hovered ? currentAccentColor : "transparent"
                                                border.color: currentAccentColor; border.width: 1
                                            }
                                            contentItem: Label {
                                                text: "L A U N C H"
                                                color: playBtnCollector.hovered ? "black" : "white"
                                                font.bold: true; font.pixelSize: 13; font.letterSpacing: 2
                                                horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                                            }
                                        }
                                    }
                                }

                                // DIVISOR TÉCNICO
                                Rectangle {
                                    anchors.left: leftInfoCol.right
                                    anchors.top: parent.top; anchors.bottom: parent.bottom
                                    width: 1; color: "#1affffff"
                                }

                                // COLUMNA DERECHA: 3D SHOWCASE STAGE (65%)
                                Item {
                                    id: rightStageCol
                                    anchors.left: leftInfoCol.right
                                    anchors.right: parent.right
                                    anchors.top: parent.top
                                    anchors.bottom: parent.bottom
                                    clip: true // Protegemos el área de carátula

                                    Rectangle {
                                        anchors.fill: parent
                                        color: "#0a0b12" // Un poco más oscuro para resaltar el arte

                                        // REJILLA DIGITAL MÁS VISIBLE
                                        Canvas {
                                            anchors.fill: parent; opacity: 0.22 // Opacidad mejorada
                                            onPaint: {
                                                var ctx = getContext("2d"); ctx.strokeStyle = currentAccentColor; ctx.lineWidth = 0.5;
                                                for (var x = 0; x <= width; x += 40) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke(); }
                                                for (var y = 0; y <= height; y += 40) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke(); }
                                            }
                                        }

                                        // RESPLANDOR AMBIENTAL
                                        Rectangle {
                                            anchors.centerIn: parent
                                            width: parent.width * 0.7; height: width
                                            radius: width / 2; color: currentAccentColor; opacity: 0.12
                                            scale: 1.4; z: -1
                                            layer.enabled: true
                                            layer.effect: MultiEffect { blurEnabled: true; blur: 1.0 }
                                        }

                                        // SUELO REFLECTANTE CON MEJOR GRADIENTE
                                        Rectangle {
                                            anchors.bottom: parent.bottom; width: parent.width; height: 140
                                            gradient: Gradient {
                                                GradientStop { position: 0.0; color: "transparent" }
                                                GradientStop { position: 1.0; color: Qt.rgba(currentAccentColor.r, currentAccentColor.g, currentAccentColor.b, 0.25) }
                                            }
                                        }

                                        // IMAGEN HERO 3D (Escalado corregido)
                                        Image {
                                            id: coverImageHero
                                            anchors.centerIn: parent
                                            width: parent.width * 0.82
                                            height: parent.height * 0.82
                                            source: modelData.cover_3d || modelData.cover
                                            fillMode: Image.PreserveAspectFit
                                            smooth: true; asynchronous: true
                                            
                                            SequentialAnimation on anchors.verticalCenterOffset {
                                                loops: Animation.Infinite
                                                NumberAnimation { from: -10; to: 10; duration: 3000; easing.type: Easing.InOutQuad }
                                                NumberAnimation { from: 10; to: -10; duration: 3000; easing.type: Easing.InOutQuad }
                                            }
                                            
                                            // Sombras Cyberpunk
                                            layer.enabled: true
                                            layer.effect: MultiEffect {
                                                shadowEnabled: true; shadowBlur: 0.6; shadowColor: "#33000000"
                                                shadowVerticalOffset: 20
                                            }
                                        }

                                        // BADGE FAVORITO MODERNO
                                        Rectangle {
                                            anchors.top: parent.top; anchors.right: parent.right
                                            width: 52; height: 52
                                            color: modelData.isFavorite ? currentAccentColor : "#1affffff"
                                            visible: modelData.isFavorite
                                            Label {
                                                anchors.centerIn: parent
                                                text: "⭐"; font.pixelSize: 22
                                                color: "black"
                                            }
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        if (!collectorDelegate.PathView.isCurrentItem) {
                                            collectorView.currentIndex = index
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }



    // --- PANEL DE DETALLES NEON HUB (Rediseño Cyberpunk) ---
    GameInfoPanel {
        id: infoPanel
        gameData: libraryRoot.selectedGame
        accentColor: libraryRoot.currentAccentColor
        
        onLaunchClicked: (path, emuId, gameName) => {
            if (window && window.requestLaunch) {
                window.requestLaunch(path, emuId, gameName)
            }
        }
        
        onEditClicked: {
            metaEditor.gameData = libraryRoot.selectedGame
            metaEditor.open()
        }
        
        onFavoriteClicked: {
            if (libraryRoot.selectedGame) {
                libraryRoot.selectedGame.isFavorite = bridge.lib.toggleFavorite(libraryRoot.selectedGame.path)
            }
        }
    }

    // --- POPUP DE AJUSTES DEL EMULADOR (COMPONENTE MODULAR) ---
    EmulatorTweakPopup {
        id: tweakPopup
    }

    // Diálogo de Edición de Metadatos
    MetadataEditor {
        id: metaEditor
        onMetadataSaved: {
            // El guardado de metadatos sí requiere un refresco completo
            libraryRoot.needsHardRefresh = true
            
            // Solo nos aseguramos de que selectedGame se mantenga al día si está abierto
            if (libraryRoot.selectedGame) {
                // Forzamos que el Connection central trabaje si el backend ya emitió la señal
                let games = bridge.lib.getGamesForConsole(libraryRoot.currentConsoleId)
                libraryRoot.currentGames = games
                libraryRoot.needsHardRefresh = false
                
                for (let g of libraryRoot.currentGames) {
                    if (g.path === libraryRoot.selectedGame.path) {
                        libraryRoot.selectedGame = g
                        break
                    }
                }
            }
        }
    }
}

