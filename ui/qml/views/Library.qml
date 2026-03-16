import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: mainLibraryContainer
    
    state: "carousel" // carousel or grid
    
    property string currentConsoleId: ""
    property string currentConsoleName: ""
    property var currentGames: []
    property string currentBackground: (carousel.currentItem) ? carousel.currentItem.backgroundSource : ""
    property color currentAccentColor: (carousel.currentItem) ? carousel.currentItem.accentColor : "#4da6ff"
    
    property var selectedGame: null // Para el panel de información
    property bool isEmpty: bridge ? (bridge.scannedConsoles.length === 0) : true

    signal gridEntranceTriggered()

    Component.onCompleted: console.log("[QML] Library view loaded successfully")
    
    Connections {
        target: bridge
        function onStatsUpdated() {
            if (mainLibraryContainer.state === "grid" && mainLibraryContainer.currentConsoleId !== "") {
                mainLibraryContainer.currentGames = bridge.getGamesForConsole(mainLibraryContainer.currentConsoleId)
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
        PropertyAction { target: immersiveBg; property: "source"; value: mainLibraryContainer.currentBackground }
        NumberAnimation { target: immersiveBg; property: "opacity"; to: 0.4; duration: 600; easing.type: Easing.OutQuad }
    }
    
    // --- LÓGICA DE RESPONSIVIDAD PREMIUM ---
    readonly property real responsiveScale: Math.max(1.0, Math.min(width / 1000, height / 650))
    readonly property real cardWidth: 340 * responsiveScale
    readonly property real cardHeight: 480 * responsiveScale
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
            visible: mainLibraryContainer.state === "grid"
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
                Label { text: (bridge && bridge.currentLanguage) ? bridge.translate("lib_empty_title").toUpperCase() : "BIBLIOTECA VACÍA"; font.pixelSize: 26; font.bold: true; color: "white"; Layout.alignment: Qt.AlignHCenter }
                Label { text: (bridge && bridge.currentLanguage) ? bridge.translate("lib_empty_sub") : "Escanea tus carpetas de juegos de cada consola desde los ajustes para ver tus títulos aquí."; font.pixelSize: 14; color: "#666677"; horizontalAlignment: Text.AlignHCenter; Layout.preferredWidth: 340; wrapMode: Text.WordWrap; Layout.alignment: Qt.AlignHCenter }
            }
            Button {
                text: (bridge && bridge.currentLanguage) ? bridge.translate("lib_scan_now") : "ESCANEAR AHORA"
                Layout.alignment: Qt.AlignHCenter
                onClicked: bridge.scanGames()
                background: Rectangle { radius: 20; color: "#4da6ff" }
                contentItem: Label { text: parent.text; color: "white"; font.bold: true; padding: 15; font.pixelSize: 12 }
            }
        }
    }

    // --- CAROUSEL MODE ---
    PathView {
        id: carousel
        z: 10
        anchors.fill: parent
        anchors.topMargin: 40
        visible: !mainLibraryContainer.isEmpty
        opacity: mainLibraryContainer.state === "carousel" ? 1 : 0
        model: (bridge && bridge.scannedConsoles) ? bridge.scannedConsoles : []
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
            width: mainLibraryContainer.cardWidth
            height: mainLibraryContainer.cardHeight
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
                            text: (bridge && bridge.currentLanguage ? bridge.translateWithArg("lib_games_count", modelData.count) : (modelData.count + " TÍTULOS")).toUpperCase()
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
                            text: (bridge && bridge.currentLanguage) ? bridge.translate("lib_btn_explore").toUpperCase() : "EXPLORAR"
                            font.bold: true; color: isCurrent ? "black" : "white"; font.pixelSize: 12 * responsiveScale
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onEntered: delegateRoot.isHovered = true
                    onExited: delegateRoot.isHovered = false
                    onClicked: {
                        dispersionAnim.restart()
                        if (index === carousel.currentIndex) {
                            mainLibraryContainer.currentConsoleId = modelData.id
                            mainLibraryContainer.currentConsoleName = modelData.name
                            mainLibraryContainer.currentGames = bridge.getGamesForConsole(modelData.id)
                            mainLibraryContainer.state = "grid"
                            // Disparamos la señal individual para las tarjetas de roms
                            mainLibraryContainer.gridEntranceTriggered()
                        } else {
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
        opacity: 0
        scale: 1.0
        visible: false
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 30

            // Modern Transparent Header
            RowLayout {
                id: gridHeader
                Layout.fillWidth: true
                Layout.leftMargin: (gamesGrid.width - (Math.floor(gamesGrid.width / gamesGrid.cellWidth) * gamesGrid.cellWidth)) / 2
                Layout.rightMargin: Layout.leftMargin
                spacing: 20
                
                Button {
                    id: btnBackGrid
                    Layout.preferredWidth: 48
                    Layout.preferredHeight: 48
                    onClicked: mainLibraryContainer.state = "carousel"
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
                        text: mainLibraryContainer.currentConsoleName
                        font.pixelSize: 26
                        font.bold: true
                        color: "white"
                    }
                    Label {
                        text: (bridge && bridge.currentLanguage ? bridge.translateWithArg("lib_games_count", mainLibraryContainer.currentGames.length).toUpperCase() : (mainLibraryContainer.currentGames.length + " JUEGOS DISPONIBLES"))
                        font.pixelSize: 10
                        font.bold: true
                        color: currentAccentColor
                        font.letterSpacing: 1
                    }
                }

                Item { Layout.fillWidth: true }

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
                                text: (bridge && bridge.currentLanguage) ? bridge.translate("lib_search") : "Buscar título..."
                                color: "#66ffffff"
                                visible: searchInput.text === ""
                                anchors.fill: parent
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }
            }

            GridView {
                id: gamesGrid
                Layout.fillWidth: true
                Layout.fillHeight: true
                cellWidth: 240
                cellHeight: 380
                model: mainLibraryContainer.currentGames
                property var currentItemData: null
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                
                leftMargin: (width - (Math.floor(width / cellWidth) * cellWidth)) / 2
                rightMargin: leftMargin

                delegate: Item {
                    id: gameCardRoot
                    width: 240
                    height: 380
                    
                    // PROPIEDAD MAESTRA: El único estado de verdad
                    property bool isHovered: masterArea.containsMouse || 
                                             (typeof infoBtnMouse !== "undefined" && infoBtnMouse.containsMouse) || 
                                             (typeof favBtnMouse !== "undefined" && favBtnMouse.containsMouse)

                    // --- ANIMACIÓN DE ENTRADA ---
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
                        target: mainLibraryContainer
                        function onGridEntranceTriggered() {
                            cardBody.opacity = 0
                            cardBody.scale = 0.8
                            staggeredEntry.restart()
                        }
                    }

                    // 1. ÁREA DE INTERACCIÓN MAESTRA (Base estática para clics y hover general)
                    MouseArea {
                        id: masterArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: containsMouse ? Qt.PointingHandCursor : Qt.ArrowCursor
                        onEntered: { gamesGrid.currentItemData = modelData }
                        onClicked: {
                            if (window && window.requestLaunch) 
                                window.requestLaunch(modelData.path, modelData.id_emu, modelData.name)
                        }

                        // 2. CUERPO VISUAL (Solo estética, reacciona al estado isHovered)
                        Rectangle {
                            id: cardBody
                            anchors.fill: parent
                            anchors.margins: 12
                            radius: 28
                            color: "#1a1c26"
                            clip: true
                            scale: isHovered ? 1.05 : 1.0
                            z: isHovered ? 10 : 1
                            Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutBack } }

                            // Borde Glow
                            Rectangle {
                                anchors.fill: parent; radius: 28; color: "transparent"
                                border.color: currentAccentColor
                                border.width: isHovered ? 3 : 1
                                opacity: isHovered ? 1.0 : 0.2
                                Behavior on border.width { NumberAnimation { duration: 200 } }
                            }

                            Image {
                                id: coverImg
                                anchors.fill: parent
                                source: modelData.cover || ""
                                fillMode: Image.PreserveAspectCrop
                                opacity: modelData.cover ? (isHovered ? 1.0 : 0.8) : 0.1
                                scale: isHovered ? 1.1 : 1.0
                                Behavior on scale { NumberAnimation { duration: 1200; easing.type: Easing.OutCubic } }
                            }

                            // Overlay de Información
                            Rectangle {
                                id: infoOverlay
                                anchors.bottom: parent.bottom
                                width: parent.width
                                height: isHovered ? 100 : 70
                                gradient: Gradient {
                                    GradientStop { position: 0.0; color: "transparent" }
                                    GradientStop { position: 0.4; color: Qt.rgba(10/255, 12/255, 20/255, 0.9) }
                                    GradientStop { position: 1.0; color: "#0a0c14" }
                                }
                                Behavior on height { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 16
                                    spacing: 4
                                    Label {
                                        Layout.fillWidth: true
                                        text: modelData.name
                                        color: "white"; font.pixelSize: 14; font.bold: true
                                        elide: Text.ElideRight; maximumLineCount: 2
                                        wrapMode: Text.WordWrap
                                    }
                                    Label { 
                                        text: "🕒 " + modelData.playtime
                                        color: "#b0ffffff"; font.pixelSize: 11
                                        visible: isHovered 
                                    }
                                }
                            }
                        }
                    }

                    // 3. BARRA DE ACCIÓN (Info + Favoritos) - Independiente para evitar z-conflicts
                    Row {
                        id: actionBar
                        anchors.top: parent.top; anchors.right: parent.right
                        anchors.topMargin: 22; anchors.rightMargin: 22
                        spacing: 8
                        z: 20
                        visible: isHovered || modelData.isFavorite

                        // Botón INFO
                        Rectangle {
                            width: 38; height: 38; radius: 19
                            color: infoBtnMouse.containsMouse ? currentAccentColor : "#e00a0c14"
                            border.color: currentAccentColor; border.width: 1
                            visible: isHovered
                            
                            Label {
                                anchors.centerIn: parent
                                text: "ⓘ"
                                font.pixelSize: 20; color: infoBtnMouse.containsMouse ? "black" : "white"
                            }
                            
                            MouseArea {
                                id: infoBtnMouse
                                anchors.fill: parent; hoverEnabled: true
                                onClicked: (mouse) => {
                                    mouse.accepted = true
                                    mainLibraryContainer.selectedGame = modelData
                                    infoPanel.open()
                                }
                            }
                        }

                        // Botón FAVORITO
                        Rectangle {
                            width: 38; height: 38; radius: 19
                            color: favBtnMouse.containsMouse ? "#ff4d4d" : (modelData.isFavorite ? "#33ff4d4d" : "#e00a0c14")
                            border.color: modelData.isFavorite ? "#ff4d4d" : currentAccentColor
                            border.width: 1
                            
                            Label {
                                anchors.centerIn: parent
                                text: modelData.isFavorite ? "❤️" : "🤍"
                                font.pixelSize: 18
                            }
                            
                            MouseArea {
                                id: favBtnMouse
                                anchors.fill: parent; hoverEnabled: true
                                onClicked: (mouse) => {
                                    mouse.accepted = true
                                    modelData.isFavorite = bridge.toggleFavorite(modelData.path)
                                    mainLibraryContainer.currentGames = bridge.getGamesForConsole(mainLibraryContainer.currentConsoleId)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

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
        }
    ]

    transitions: [
        Transition {
            from: "carousel"; to: "grid"
            SequentialAnimation {
                PropertyAction { target: gridContainer; property: "visible"; value: true }
                ParallelAnimation {
                    NumberAnimation { target: carousel; property: "opacity"; duration: 400; easing.type: Easing.OutCubic }
                    NumberAnimation { target: carousel; property: "scale"; duration: 400; easing.type: Easing.InBack }
                    
                    NumberAnimation { target: gridContainer; property: "opacity"; duration: 600; easing.type: Easing.OutCubic }
                    NumberAnimation { target: gridContainer; property: "y"; duration: 600; easing.type: Easing.OutBack }
                    NumberAnimation { target: gridContainer; property: "scale"; duration: 600; easing.type: Easing.OutBack }
                }
                PropertyAction { target: carousel; property: "visible"; value: false }
            }
        },
        Transition {
            from: "grid"; to: "carousel"
            SequentialAnimation {
                PropertyAction { target: carousel; property: "visible"; value: true }
                ParallelAnimation {
                    NumberAnimation { target: gridContainer; property: "opacity"; duration: 350; easing.type: Easing.OutCubic }
                    NumberAnimation { target: gridContainer; property: "scale"; duration: 350; easing.type: Easing.InBack }
                    
                    NumberAnimation { target: carousel; property: "opacity"; duration: 500; easing.type: Easing.OutCubic }
                    NumberAnimation { target: carousel; property: "scale"; duration: 500; easing.type: Easing.OutBack }
                }
                PropertyAction { target: gridContainer; property: "visible"; value: false }
            }
        }
    ]

    // --- PANEL DE DETALLES INMERSIVO ---
    // Overlay oscuro para el fondo (Dimmer)
    Rectangle {
        id: infoDimmer
        anchors.fill: parent
        color: "#aa000000"
        opacity: infoPanel.isOpen ? 1.0 : 0.0
        visible: opacity > 0
        z: 999
        Behavior on opacity { NumberAnimation { duration: 400 } }
        MouseArea {
            anchors.fill: parent
            onClicked: infoPanel.close()
        }
    }

    Rectangle {
        id: infoPanel
        width: Math.min(500, parent.width * 0.8)
        height: parent.height
        x: parent.width // Escondido a la derecha
        color: "#f80a0b12" // Más sólido para legibilidad de texto
        border.color: "#33ffffff"; border.width: 1
        z: 1000

        property bool isOpen: false
        function open() { x = parent.width - width; isOpen = true }
        function close() { x = parent.width; isOpen = false }

        Behavior on x { NumberAnimation { duration: 600; easing.type: Easing.OutQuart } }

        // Blur para fondo
        Rectangle {
            anchors.fill: parent; color: "transparent"; z: -1
            // Aquí iría un FastBlur si estuviéramos usando capas de efectos, 
            // por ahora usamos la opacidad del color base.
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 25

            RowLayout {
                Layout.fillWidth: true
                Label {
                    text: "INFORMACIÓN"
                    font.pixelSize: 12; font.bold: true; color: currentAccentColor
                    font.letterSpacing: 2
                }
                Item { Layout.fillWidth: true }
                
                // Botón Cerrar - Premium Circular
                Rectangle {
                    id: closeCircle
                    width: 36; height: 36; radius: 18
                    color: closeArea.containsMouse ? "#ccff4d4d" : "#22ffffff"
                    border.color: closeArea.containsMouse ? "#ff4d4d" : "#44ffffff"
                    border.width: 1
                    
                    Label {
                        anchors.centerIn: parent
                        text: "✕"; color: "white"; font.pixelSize: 16; font.bold: true
                    }
                    
                    MouseArea {
                        id: closeArea
                        anchors.fill: parent; hoverEnabled: true
                        onClicked: infoPanel.close()
                    }
                    
                    Behavior on color { ColorAnimation { duration: 250 } }
                    Behavior on border.color { ColorAnimation { duration: 250 } }
                    
                    scale: closeArea.pressed ? 0.85 : (closeArea.containsMouse ? 1.1 : 1.0)
                    Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutBack } }
                }
            }

            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: 240
                radius: 20; clip: true
                color: "#11ffffff"
                visible: selectedGame && selectedGame.cover != ""
                
                Image {
                    anchors.fill: parent
                    source: selectedGame ? (selectedGame.cover || "") : ""
                    fillMode: Image.PreserveAspectCrop
                }
                
                Rectangle { 
                    anchors.fill: parent; radius: 20
                    color: "transparent"; border.color: "#33ffffff"; border.width: 1 
                }
            }

            RowLayout {
                Layout.fillWidth: true; spacing: 20
                
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 5
                    Label {
                        text: selectedGame ? selectedGame.title : ""
                        font.pixelSize: 32; font.weight: Font.Black; color: "white"
                        wrapMode: Text.WordWrap; Layout.fillWidth: true
                        font.letterSpacing: -0.5
                    }
                    RowLayout {
                        spacing: 15
                        Label {
                            text: selectedGame ? (selectedGame.developer + " • " + selectedGame.year) : ""
                            font.pixelSize: 15; color: "#aa88ccff"
                        }
                        Rectangle {
                            visible: selectedGame && selectedGame.genre != ""
                            height: 24; width: genreLabel.width + 20; radius: 12
                            color: "#22ffffff"
                            Label {
                                id: genreLabel
                                anchors.centerIn: parent; text: selectedGame ? selectedGame.genre : ""
                                font.pixelSize: 11; font.bold: true; color: currentAccentColor
                            }
                        }
                    }
                }

                // Botón Favorito Sutil (Estilo Tarjeta)
                Rectangle {
                    width: 48; height: 48; radius: 24
                    color: favInfoMouse.containsMouse ? (selectedGame && selectedGame.isFavorite ? "#33ff4d4d" : "#22ffffff") : "transparent"
                    border.color: selectedGame && selectedGame.isFavorite ? "#ff4d4d" : "#33ffffff"
                    border.width: 1
                    Layout.alignment: Qt.AlignTop
                    
                    Label {
                        anchors.centerIn: parent
                        text: selectedGame && selectedGame.isFavorite ? "❤️" : "🤍"
                        font.pixelSize: 22
                    }
                    
                    MouseArea {
                        id: favInfoMouse
                        anchors.fill: parent; hoverEnabled: true
                        onClicked: {
                            if (selectedGame) {
                                // Cambiamos el estado en el backend
                                let newState = bridge.toggleFavorite(selectedGame.path)
                                selectedGame.isFavorite = newState
                                
                                // Forzamos el refresco de los bindings notificando el cambio de selectedGame
                                let temp = selectedGame
                                selectedGame = null
                                selectedGame = temp
                                
                                // Refrescamos también el grid principal
                                mainLibraryContainer.currentGames = bridge.getGamesForConsole(mainLibraryContainer.currentConsoleId)
                            }
                        }
                    }
                    
                    Behavior on color { ColorAnimation { duration: 200 } }
                    scale: favInfoMouse.pressed ? 0.9 : (favInfoMouse.containsMouse ? 1.05 : 1.0)
                    Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutBack } }
                }
            }


            // Descripción
            ScrollView {
                id: descScroll
                Layout.fillWidth: true; Layout.fillHeight: true
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                
                Label {
                    width: descScroll.availableWidth
                    text: selectedGame ? (selectedGame.description || "No hay descripción disponible para este título.") : ""
                    font.pixelSize: 14; color: "#b0ffffff"; wrapMode: Text.WordWrap
                    lineHeight: 1.4
                    bottomPadding: 20
                }
            }

            Button {
                id: launchMainBtn
                Layout.fillWidth: true; Layout.preferredHeight: 50
                onClicked: {
                    if (window && window.requestLaunch && selectedGame) {
                        window.requestLaunch(selectedGame.path, selectedGame.id_emu, selectedGame.title)
                        infoPanel.close()
                    }
                }
                
                background: Rectangle {
                    radius: 25
                    color: launchMainBtn.hovered ? Qt.lighter(currentAccentColor, 1.2) : currentAccentColor
                    
                    // Efecto de brillo/sombra interna
                    Rectangle {
                        anchors.fill: parent; radius: 25; color: "transparent"
                        border.color: "#33ffffff"; border.width: 1
                    }
                    
                    Behavior on color { ColorAnimation { duration: 200 } }
                }
                
                contentItem: Label {
                    text: "LANZAR JUEGO"
                    color: "black"; font.bold: true; font.pixelSize: 14
                    horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                    scale: launchMainBtn.pressed ? 0.95 : 1.0
                    Behavior on scale { NumberAnimation { duration: 100 } }
                }
            }
        }
    }
}
