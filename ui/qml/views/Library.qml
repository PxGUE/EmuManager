import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: libraryRoot
    
    state: "carousel" // carousel or grid
    
    property string currentConsoleId: ""
    property string currentConsoleName: ""
    property var currentGames: []
    property color currentAccentColor: (carousel.currentItem && carousel.currentItem.delegateRoot) ? carousel.currentItem.delegateRoot.accentColor : "#4da6ff"
    
    property bool isEmpty: bridge ? (bridge.scannedConsoles.length === 0) : true
    
    // --- LÓGICA DE RESPONSIVIDAD PREMIUM ---
    readonly property real responsiveScale: Math.max(1.0, Math.min(width / 1000, height / 650))
    readonly property real cardWidth: 340 * responsiveScale
    readonly property real cardHeight: 480 * responsiveScale

    // --- FONDO ATMOSFÉRICO ---
    Rectangle {
        anchors.fill: parent
        color: "#07080c"
        z: -2
        
        Rectangle {
            id: backgroundBlur
            anchors.centerIn: parent
            width: parent.width * 1.5
            height: parent.height * 1.5
            radius: width / 2
            opacity: 0.12
            gradient: Gradient {
                GradientStop { position: 0.0; color: currentAccentColor }
                GradientStop { position: 0.5; color: "transparent" }
            }
            Behavior on color { ColorAnimation { duration: 1000; easing.type: Easing.OutCubic } }
        }

        // Fondo Dinámico para la Galería
        Image {
            id: immersiveBg
            anchors.fill: parent
            source: (libraryRoot.state === "grid" && gamesGrid.currentItemData) ? "file:///" + gamesGrid.currentItemData.cover : ""
            fillMode: Image.PreserveAspectCrop
            opacity: (libraryRoot.state === "grid" && source != "") ? 0.2 : 0.0
            Behavior on opacity { NumberAnimation { duration: 800 } }
        }
        
        Rectangle {
            anchors.fill: parent
            visible: libraryRoot.state === "grid"
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(7/255, 8/255, 12/255, 0.7) }
                GradientStop { position: 1.0; color: "#07080c" }
            }
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
        anchors.fill: parent
        anchors.topMargin: 40
        visible: !libraryRoot.isEmpty
        opacity: libraryRoot.state === "carousel" ? 1 : 0
        model: bridge ? bridge.scannedConsoles : []
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
            
            property real floatOffset: 0
            SequentialAnimation on floatOffset {
                running: delegateRoot.isCurrent
                loops: Animation.Infinite
                NumberAnimation { from: 0; to: -30; duration: 2000; easing.type: Easing.InOutQuad }
                NumberAnimation { from: -30; to: 0; duration: 2000; easing.type: Easing.InOutQuad }
            }

            // --- REFLEJO / SOMBRA DINÁMICA PREMIUM ---
            Item {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 10 * responsiveScale
                width: 300 * responsiveScale; height: 60 * responsiveScale
                visible: isCurrent || opacity > 0.1

                // Capa 1: Brillo Nuclear (Intenso y definido)
                Rectangle {
                    anchors.centerIn: parent
                    width: parent.width * 0.8; height: parent.height * 0.4
                    radius: width / 2
                    opacity: isCurrent ? (0.6 + (floatOffset / 100)) : 0.1
                    scale: isCurrent ? (1.0 + (floatOffset / 150)) : 1.0
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "transparent" }
                        GradientStop { position: 0.5; color: Qt.alpha(accentColor, 0.8) }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }

                // Capa 2: Difusión Suave (Atmosférica)
                Rectangle {
                    anchors.centerIn: parent
                    width: parent.width; height: parent.height
                    radius: width / 2
                    opacity: isCurrent ? (0.3 + (floatOffset / 200)) : 0.05
                    scale: isCurrent ? (1.2 + (floatOffset / 100)) : 1.0
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "transparent" }
                        GradientStop { position: 0.5; color: accentColor }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }
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
                    onClicked: {
                        if (index === carousel.currentIndex) {
                            libraryRoot.currentConsoleId = modelData.id
                            libraryRoot.currentConsoleName = modelData.name
                            libraryRoot.currentGames = bridge.getGamesForConsole(modelData.id)
                            libraryRoot.state = "grid"
                        } else {
                            carousel.currentIndex = index
                        }
                    }
                }
            }
        }
    }

    // --- MODERN IMMERSIVE GRID ---
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
                        text: (bridge && bridge.currentLanguage ? bridge.translateWithArg("lib_games_count", libraryRoot.currentGames.length).toUpperCase() : (libraryRoot.currentGames.length + " JUEGOS DISPONIBLES"))
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
                model: libraryRoot.currentGames
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                
                leftMargin: (width - (Math.floor(width / cellWidth) * cellWidth)) / 2
                rightMargin: leftMargin

                property var currentItemData: null

                add: Transition {
                    NumberAnimation { property: "opacity"; from: 0; to: 1.0; duration: 400 }
                    NumberAnimation { property: "scale"; from: 0.8; to: 1.0; duration: 500; easing.type: Easing.OutBack }
                }

                delegate: Item {
                    id: gameCardRoot
                    width: 240
                    height: 380
                    property bool isHovered: false
                    
                    Rectangle {
                        id: cardBody
                        anchors.fill: parent
                        anchors.margins: 15
                        radius: 32
                        color: "#1a1c26"
                        clip: true
                        scale: isHovered ? 1.08 : 1.0
                        z: isHovered ? 10 : 1
                        Behavior on scale { NumberAnimation { duration: 400; easing.type: Easing.OutBack } }

                        Rectangle {
                            anchors.fill: parent
                            radius: 32
                            color: "transparent"
                            border.color: currentAccentColor
                            border.width: isHovered ? 3 : 1
                            opacity: isHovered ? 1.0 : 0.2
                            Behavior on border.width { NumberAnimation { duration: 200 } }
                            Behavior on opacity { NumberAnimation { duration: 300 } }
                        }

                        Image {
                            id: coverImg
                            anchors.fill: parent
                            source: modelData.cover ? "file:///" + modelData.cover : ""
                            fillMode: Image.PreserveAspectCrop
                            opacity: modelData.cover ? (isHovered ? 1.0 : 0.8) : 0.1
                            scale: isHovered ? 1.15 : 1.0
                            Behavior on scale { NumberAnimation { duration: 1200; easing.type: Easing.OutCubic } }
                            Behavior on opacity { NumberAnimation { duration: 400 } }
                        }

                        Rectangle {
                            id: infoOverlay
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: isHovered ? 110 : 65
                            gradient: Gradient {
                                GradientStop { position: 0.0; color: "transparent" }
                                GradientStop { position: 0.4; color: Qt.rgba(7/255, 8/255, 12/255, 0.8) }
                                GradientStop { position: 1.0; color: "#07080c" }
                            }
                            Behavior on height { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 6
                                Item { Layout.fillHeight: true }
                                Label {
                                    text: modelData.name
                                    color: "white"; font.pixelSize: 14; font.bold: true
                                    Layout.fillWidth: true; elide: Text.ElideRight; maximumLineCount: 2
                                    wrapMode: Text.WordWrap; font.letterSpacing: 0.5
                                }
                                RowLayout {
                                    Layout.fillWidth: true
                                    visible: isHovered || modelData.isFavorite
                                    spacing: 10
                                    Label { text: "🕒 " + modelData.playtime; color: "#b0ffffff"; font.pixelSize: 11; visible: isHovered }
                                    Item { Layout.fillWidth: true }
                                    Item {
                                        width: 28; height: 28
                                        Label {
                                            anchors.centerIn: parent
                                            text: modelData.isFavorite ? "❤️" : "🤍"
                                            font.pixelSize: 16
                                            scale: favMouse.pressed ? 0.8 : (isHovered ? 1.1 : 1.0)
                                            opacity: (isHovered || modelData.isFavorite) ? 1.0 : 0.0
                                            Behavior on scale { NumberAnimation { duration: 100 } }
                                            Behavior on opacity { NumberAnimation { duration: 200 } }
                                        }
                                        MouseArea {
                                            id: favMouse
                                            anchors.fill: parent
                                            onClicked: {
                                                modelData.isFavorite = bridge.toggleFavorite(modelData.path)
                                                libraryRoot.currentGames = bridge.getGamesForConsole(currentConsoleId)
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        Rectangle {
                            anchors.top: parent.top; anchors.right: parent.right; anchors.margins: 15
                            width: 38; height: 38; radius: 19
                            color: "#dd07080c"; border.color: currentAccentColor; border.width: 1
                            visible: modelData.isFavorite
                            Label {
                                anchors.centerIn: parent; text: "⭐"; font.pixelSize: 16
                                SequentialAnimation on opacity {
                                    loops: Animation.Infinite
                                    NumberAnimation { from: 0.6; to: 1.0; duration: 1500; easing.type: Easing.InOutQuad }
                                    NumberAnimation { from: 1.0; to: 0.6; duration: 1500; easing.type: Easing.InOutQuad }
                                }
                            }
                        }

                        MouseArea {
                            anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                            onEntered: { gameCardRoot.isHovered = true; gamesGrid.currentItemData = modelData }
                            onExited: { gameCardRoot.isHovered = false }
                            onClicked: { if (bridge) bridge.launchGame(modelData.path, modelData.id_emu) }
                        }
                    }
                }
            }
        }
    }

    states: [
        State {
            name: "carousel"
            PropertyChanges { target: carousel; visible: !isEmpty; opacity: 1; scale: 1.0 }
            PropertyChanges { target: gridContainer; visible: false; opacity: 0; y: 100 }
        },
        State {
            name: "grid"
            PropertyChanges { target: carousel; visible: false; opacity: 0; scale: 1.2 }
            PropertyChanges { target: gridContainer; visible: !isEmpty; opacity: 1; y: 0 }
        }
    ]

    transitions: [
        Transition {
            from: "carousel"; to: "grid"
            SequentialAnimation {
                PropertyAction { target: gridContainer; property: "visible"; value: true }
                ParallelAnimation {
                    NumberAnimation { target: carousel; properties: "opacity,scale"; duration: 450; easing.type: Easing.InBack }
                    NumberAnimation { target: gridContainer; properties: "opacity,y"; duration: 550; easing.type: Easing.OutCubic }
                }
                PropertyAction { target: carousel; property: "visible"; value: false }
            }
        },
        Transition {
            from: "grid"; to: "carousel"
            SequentialAnimation {
                PropertyAction { target: carousel; property: "visible"; value: true }
                ParallelAnimation {
                    NumberAnimation { target: gridContainer; properties: "opacity,y"; duration: 450; easing.type: Easing.InCubic }
                    NumberAnimation { target: carousel; properties: "opacity,scale"; duration: 550; easing.type: Easing.OutBack }
                }
                PropertyAction { target: gridContainer; property: "visible"; value: false }
            }
        }
    ]
}
