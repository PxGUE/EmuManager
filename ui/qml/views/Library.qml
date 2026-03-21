import QtQuick
import QtQuick.Layouts
import QtQuick.Effects
import QtQuick.Controls
import QtQuick.Shapes
import "../components"

/**
 * Library.qml — Vista principal de la biblioteca de juegos.
 */
Item {
    id: libraryRoot
    
    state: "carousel"

    states: [
        State { 
            name: "carousel"
            PropertyChanges { 
                target: carousel
                visible: true
                opacity: 1
                scale: 1.0 
            }
            PropertyChanges { 
                target: gridContainer
                visible: false
                opacity: 0
                y: 40
                scale: 0.95 
            }
        },
        State {
            name: "grid"
            PropertyChanges { 
                target: carousel
                visible: false
                opacity: 0
                scale: 0.9 
            }
            PropertyChanges { 
                target: gridContainer
                visible: true
                opacity: 1
                y: 0
                scale: 1.0 
            }
        },
        State {
            name: "collector" 
            PropertyChanges { 
                target: carousel
                visible: false
                opacity: 0
                scale: 0.8 
            }
            PropertyChanges { 
                target: gridContainer
                visible: false
                opacity: 0
                y: 40
                scale: 0.95 
            }
            PropertyChanges { 
                target: collectorContainer
                visible: true
                opacity: 1
                y: 0
                scale: 1.0 
            }
            PropertyChanges { 
                target: backgroundBlur
                opacity: 0.8 
            }
        }
    ]

    transitions: [
        Transition {
            from: "carousel"
            to: "grid"
            SequentialAnimation {
                PropertyAction { 
                    target: gridContainer
                    property: "visible"
                    value: true 
                }
                ParallelAnimation {
                    NumberAnimation { 
                        target: carousel
                        property: "opacity"
                        duration: 450
                        easing.type: Easing.OutCubic 
                    }
                    NumberAnimation { 
                        target: carousel
                        property: "scale"
                        duration: 450
                        easing.type: Easing.InBack 
                    }
                    NumberAnimation { 
                        target: gridContainer
                        property: "opacity"
                        duration: 600
                        easing.type: Easing.OutCubic 
                    }
                    NumberAnimation { 
                        target: gridContainer
                        property: "y"
                        duration: 600
                        easing.type: Easing.OutBack 
                    }
                    NumberAnimation { 
                        target: gridContainer
                        property: "scale"
                        duration: 600
                        easing.type: Easing.OutBack 
                    }
                }
                PropertyAction { 
                    target: carousel
                    property: "visible"
                    value: false 
                }
            }
        },
        Transition {
             from: "*"
             to: "carousel"
             SequentialAnimation {
                 PropertyAction { 
                     target: carousel
                     property: "visible"
                     value: true 
                 }
                 ParallelAnimation {
                     NumberAnimation { 
                         target: gridContainer
                         property: "opacity"
                         duration: 350
                         easing.type: Easing.OutCubic 
                     }
                     NumberAnimation { 
                         target: collectorContainer
                         property: "opacity"
                         duration: 350
                         easing.type: Easing.OutCubic 
                     }
                     NumberAnimation { 
                         target: carousel
                         property: "opacity"
                         duration: 500
                         easing.type: Easing.OutCubic 
                     }
                     NumberAnimation { 
                         target: carousel
                         property: "scale"
                         duration: 550
                         easing.type: Easing.OutBack 
                     }
                 }
                 PropertyAction { 
                     target: gridContainer
                     property: "visible"
                     value: false 
                 }
                 PropertyAction { 
                     target: collectorContainer
                     property: "visible"
                     value: false 
                 }
             }
         },
         Transition {
             from: "carousel"
             to: "collector"
             SequentialAnimation {
                 PropertyAction { 
                     target: collectorContainer
                     property: "visible"
                     value: true 
                 }
                 ParallelAnimation {
                     NumberAnimation { 
                         target: carousel
                         property: "opacity"
                         duration: 400
                         easing.type: Easing.OutCubic 
                     }
                     NumberAnimation { 
                         target: carousel
                         property: "scale"
                         duration: 400
                         easing.type: Easing.InBack 
                     }
                     NumberAnimation { 
                         target: collectorContainer
                         property: "opacity"
                         duration: 650
                         easing.type: Easing.OutCubic 
                     }
                     NumberAnimation { 
                         target: collectorContainer
                         property: "y"
                         duration: 650
                         easing.type: Easing.OutBack 
                     }
                     NumberAnimation { 
                         target: collectorContainer
                         property: "scale"
                         duration: 650
                         easing.type: Easing.OutBack 
                     }
                 }
                 PropertyAction { 
                     target: carousel
                     property: "visible"
                     value: false 
                 }
             }
         }
    ]

    property string currentConsoleId: ""
    property string currentConsoleName: ""
    property string currentEmuName: ""
    property var currentGames: []
    property color currentPlatformColor: window.themeAccent
    
    property string searchText: searchInput.text
    property bool onlyFavorites: false
    property bool needsHardRefresh: false
    property var favMap: ({})
    property int favoritesTrigger: 0
    
    property var filteredGames: {
        let _f = favMap; 
        if (!currentGames) return []
        let search = (libraryRoot.searchText || "").toLowerCase()
        return currentGames.filter(game => {
            let titleStr = (game.title || game.name || "").toLowerCase()
            let matchSearch = search === "" || titleStr.includes(search)
            let isFav = (favMap[game.path] !== undefined) ? favMap[game.path] : game.isFavorite
            let matchFav = !libraryRoot.onlyFavorites || isFav
            return matchSearch && matchFav
        })
    }

    property string currentBackground: {
        if (libraryRoot.state === "collector" && libraryRoot.selectedGame) {
            return libraryRoot.selectedGame.background || ""
        }
        if (libraryRoot.state === "grid" && libraryRoot.selectedGame) {
            return libraryRoot.selectedGame.background || (carousel.currentItem ? carousel.currentItem.backgroundSource || "" : "")
        }
        if (libraryRoot.state === "carousel" || libraryRoot.state === "grid") {
            return (carousel.currentItem) ? carousel.currentItem.backgroundSource || "" : ""
        }
        return ""
    }

    property color currentAccentColor: {
        if (libraryRoot.state === "collector" && libraryRoot.selectedGame) return libraryRoot.selectedGame.accentColor || libraryRoot.currentPlatformColor
        if (libraryRoot.state === "grid" && libraryRoot.selectedGame) return libraryRoot.selectedGame.accentColor || libraryRoot.currentPlatformColor
        return (carousel.currentItem) ? carousel.currentItem.accentColor || "#4da6ff" : window.themeAccent
    }
    
    property var selectedGame: null
    property bool isEmpty: bridge ? (bridge.lib.scannedConsoles.length === 0) : true

    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    signal gridEntranceTriggered()
    
    onStateChanged: {
        if (state === "carousel") {
            selectedGame = null
            immersiveBg.source = ""
            immersiveBg.opacity = 0
        }
        if (state === "collector" && !selectedGame && currentGames.length > 0) {
            selectedGame = currentGames[0]
        }
    }

    Connections {
        target: bridge
        function onStatsUpdated() {
            let consoles = bridge.lib.scannedConsoles
            libraryRoot.isEmpty = (consoles.length === 0)
            carousel.model = consoles
            if (libraryRoot.state === "grid" && libraryRoot.currentConsoleId !== "") {
                if (libraryRoot.needsHardRefresh) {
                    let games = bridge.lib.getGamesForConsole(libraryRoot.currentConsoleId)
                    libraryRoot.currentGames = games
                    libraryRoot.needsHardRefresh = false
                }
            }
        }
    }

    onCurrentBackgroundChanged: {
        bgFadeAnim.stop()
        bgFadeAnim.start()
    }
    
    SequentialAnimation {
        id: bgFadeAnim
        NumberAnimation { 
            target: immersiveBg
            property: "opacity"
            to: 0
            duration: 250 
        }
        PropertyAction { 
            target: immersiveBg
            property: "source"
            value: libraryRoot.currentBackground 
        }
        NumberAnimation { 
            target: immersiveBg
            property: "opacity"
            to: (libraryRoot.currentBackground !== "" ? 0.4 : 0)
            duration: 600
            easing.type: Easing.OutQuad 
        }
    }

    readonly property real responsiveScale: Math.max(1.0, Math.min(width / 1100, height / 750))
    readonly property real cardWidth: 380 * responsiveScale
    readonly property real cardHeight: 540 * responsiveScale

    readonly property real gridCellWidth: 240
    readonly property real gridHorizontalPadding: {
        let available = gridContainer.width
        return Math.max(0, (available - (Math.floor(available / gridCellWidth) * gridCellWidth)) / 2)
    }

    Rectangle {
        anchors.fill: parent
        color: "#0a0b12"
        z: 0

        Rectangle {
            id: backgroundBlur
            anchors.fill: parent
            opacity: 0.45
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { 
                    position: 0.0
                    color: Qt.alpha(currentAccentColor, 0.5) 
                }
                GradientStop { 
                    position: 0.8
                    color: "transparent" 
                }
            }
            Behavior on color { 
                ColorAnimation { duration: 800 } 
            }
            z: 1
        }

        Image {
            id: immersiveBg
            anchors.fill: parent
            source: ""
            fillMode: Image.PreserveAspectCrop
            opacity: 0.0
            visible: opacity > 0
            z: 2
        }

        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { 
                    position: 0.5
                    color: "transparent" 
                }
                GradientStop { 
                    position: 1.0
                    color: "#000000" 
                }
            }
            opacity: 0.6
        }

        Rectangle {
            anchors.fill: parent
            visible: libraryRoot.state === "grid"
            color: "#ee000000"
        }
    }

    Rectangle {
        id: emptyState
        anchors.centerIn: parent
        implicitWidth: 380
        implicitHeight: 540
        radius: 40
        color: "#11131a"
        border.color: "#252835"
        border.width: 1
        visible: isEmpty
        opacity: visible ? 1.0 : 0.0
        Behavior on opacity { 
            NumberAnimation { duration: 400 } 
        }

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 30
            Icon {
                name: "library"
                size: 80
                color: "#252835"
                Layout.alignment: Qt.AlignHCenter
            }
            ColumnLayout {
                spacing: 8
                Layout.alignment: Qt.AlignHCenter
                Label { 
                    text: tr("lib_empty_title").toUpperCase()
                    font.pixelSize: 26
                    font.bold: true
                    color: "white"
                    Layout.alignment: Qt.AlignHCenter 
                }
                Label { 
                    text: tr("lib_empty_sub")
                    font.pixelSize: 14
                    color: "#666677"
                    horizontalAlignment: Text.AlignHCenter
                    Layout.preferredWidth: 340
                    wrapMode: Text.WordWrap
                    Layout.alignment: Qt.AlignHCenter 
                }
            }
        }
    }

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
            PathAttribute { name: "itemScale"; value: 1.25 }
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
                radius: 45 * responsiveScale
                color: "#13151d"
                border.color: isCurrent ? accentColor : "#2a2d3a"
                border.width: isCurrent ? 3 : 1
                
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
                        NumberAnimation { 
                            target: clickRipple
                            property: "opacity"
                            from: 0.8
                            to: 0
                            duration: 600
                            easing.type: Easing.OutCubic 
                        }
                        NumberAnimation { 
                            target: clickRipple
                            property: "scale"
                            from: 1.0
                            to: 1.4
                            duration: 600
                            easing.type: Easing.OutCubic 
                        }
                    }
                }
                transform: Rotation { 
                    origin.x: 170
                    origin.y: 230
                    axis { x: 0; y: 1; z: 0 }
                    angle: PathView.itemRotation || 0 
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 40
                    spacing: 0
                    Item {
                        Layout.alignment: Qt.AlignHCenter
                        width: 160 * responsiveScale
                        height: 160 * responsiveScale
                        Rectangle {
                            id: aura
                            anchors.centerIn: parent
                            width: 140 * responsiveScale
                            height: 140 * responsiveScale
                            radius: (width / 2)
                            color: "transparent"
                            border.color: accentColor
                            border.width: 5
                            opacity: 0
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
                            width: 140
                            height: 140
                            radius: 70
                            color: "#0a0b12"
                            border.color: Qt.alpha(accentColor, 0.5)
                            border.width: 2
                            Icon { 
                                anchors.centerIn: parent
                                name: "library"
                                size: 64
                                color: isCurrent ? accentColor : "#33ffffff"
                                scale: isCurrent ? 1.1 : 1.0
                                Behavior on scale { 
                                    NumberAnimation { duration: 400 } 
                                } 
                            }
                        }
                    }
                    Item { Layout.fillHeight: true }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4 * responsiveScale
                        Label { 
                            text: modelData.name.toUpperCase()
                            font.pixelSize: 28 * responsiveScale
                            font.bold: true
                            color: "white"
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            font.letterSpacing: 1.5
                            opacity: isCurrent ? 1.0 : 0.6 
                        }
                        Label { 
                            text: modelData.emu_name
                            font.pixelSize: 14 * responsiveScale
                            font.weight: Font.Medium
                            color: accentColor
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            opacity: isCurrent ? 0.8 : 0.4 
                        }
                        Label { 
                            text: tr("lib_games_count", modelData.count).toUpperCase()
                            font.pixelSize: 11 * responsiveScale
                            font.bold: true
                            color: "#888899"
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            opacity: isCurrent ? 0.8 : 0.3 
                        }
                    }
                    Item { Layout.fillHeight: true }
                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter
                        width: 180 * responsiveScale
                        height: 54 * responsiveScale
                        radius: height / 2
                        color: isCurrent ? accentColor : "#1affffff"
                        opacity: isCurrent ? 1.0 : 0.2
                        border.color: isCurrent ? "white" : "transparent"
                        border.width: isCurrent ? 1 : 0
                        Label { 
                            anchors.centerIn: parent
                            text: tr("lib_btn_explore").toUpperCase()
                            font.bold: true
                            color: isCurrent ? "black" : "white"
                            font.pixelSize: 12 * responsiveScale 
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
                                    libraryRoot.currentPlatformColor = modelData.color
                                    libraryRoot.currentGames = bridge.lib.getGamesForConsole(modelData.id)
                                    if (bridge && bridge.set.collectorMode && libraryRoot.currentGames.length > 0) {
                                        libraryRoot.selectedGame = libraryRoot.currentGames[0]
                                    }
                                    libraryRoot.state = (bridge && bridge.set.collectorMode) ? "collector" : "grid"
                                    libraryRoot.gridEntranceTriggered()
                                } else {
                                    carousel.currentIndex = index
                                }
                            }
                        }
                    }
                }
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
                    onClicked: (mouse) => { 
                        libraryRoot.selectedGame = null
                        libraryRoot.state = "carousel" 
                    }
                    background: Rectangle { 
                        radius: 24
                        color: btnBackGrid.hovered ? "#33ffffff" : "#11ffffff"
                        border.color: "#22ffffff"
                        border.width: 1 
                    }
                    contentItem: Icon { 
                        name: "back"
                        color: "white"
                        size: 24
                    }
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
                    Button {
                        id: btnFavFilter
                        Layout.preferredWidth: 44
                        Layout.preferredHeight: 44
                        onClicked: (mouse) => {
                            libraryRoot.onlyFavorites = !libraryRoot.onlyFavorites
                        }
                        background: Rectangle { 
                            radius: 22
                            color: btnFavFilter.hovered ? "#22ffffff" : (libraryRoot.onlyFavorites ? "#33ffff00" : "#12ffffff")
                            border.color: libraryRoot.onlyFavorites ? "#ffff00" : "transparent"
                            border.width: 1 
                        }
                        contentItem: Icon { 
                            name: libraryRoot.onlyFavorites ? "favorite_filled" : "favorite"
                            color: libraryRoot.onlyFavorites ? "#ffff00" : "white"
                            size: 20
                            opacity: libraryRoot.onlyFavorites ? 1.0 : 0.4
                        }
                    }
                    Button {
                        id: btnRefresh
                        Layout.preferredWidth: 44
                        Layout.preferredHeight: 44
                        onClicked: (mouse) => { 
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
                        contentItem: Icon { 
                            name: "refresh"
                            color: "white"
                            size: 22

                            RotationAnimation on rotation { 
                                running: btnRefresh.pressed
                                from: 0
                                to: 360
                                duration: 500
                                loops: Animation.Infinite 
                            } 
                        }
                    }
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
                        contentItem: Icon { 
                            anchors.centerIn: parent
                            name: "settings"
                            size: 18
                            color: "white"
                            opacity: btnSettings.hovered ? 1.0 : 0.6
                            Behavior on opacity { 
                                NumberAnimation { duration: 200 } 
                            } 
                        }
                    }
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
                            Label { 
                                text: ""
                                opacity: 0.6
                                font.pixelSize: 14 
                            }
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
                clip: true
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                leftMargin: libraryRoot.gridHorizontalPadding
                rightMargin: libraryRoot.gridHorizontalPadding
                delegate: Item {
                    id: gameCardRoot
                    width: 240
                    height: 380
                    property bool isHovered: (mainCardArea.containsMouse) || (infoBtnArea && infoBtnArea.containsMouse) || (favBtnArea && favBtnArea.containsMouse)
                    SequentialAnimation { 
                        id: staggeredEntry
                        running: false
                        PauseAnimation { duration: Math.min(index * 20, 300) }
                        ParallelAnimation { 
                            NumberAnimation { target: cardBody; property: "opacity"; to: 1.0; duration: 500 }
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
                    MouseArea { 
                        id: mainCardArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onEntered: {
                            if (gamesGrid) {
                                libraryRoot.selectedGame = modelData
                            }
                        }
                        onClicked: (mouse) => { 
                            if (window && window.requestLaunch) {
                                window.requestLaunch(modelData.path, modelData.id_emu, modelData.name)
                            }
                        } 
                    }
                    Rectangle {
                        id: cardBody
                        anchors.fill: parent
                        anchors.margins: 12
                        radius: 28
                        color: window.themeCardBg
                        clip: true
                        scale: isHovered ? 1.05 : 1.0
                        z: isHovered ? 10 : 1
                        Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutBack } }
                        
                        // Glassmorphism border panel
                        Rectangle { 
                            anchors.fill: parent
                            radius: 28
                            color: "transparent"
                            border.color: isHovered ? (modelData.accentColor || themeAccent) : window.themeBorder
                            border.width: isHovered ? 2 : 1
                            opacity: isHovered ? 1.0 : 0.6
                            Behavior on border.width { 
                                NumberAnimation { duration: 200 } 
                            } 
                        }
                        Image { 
                            id: coverImg
                            anchors.fill: parent
                            anchors.margins: 4
                            source: modelData.cover || ""
                            fillMode: Image.PreserveAspectCrop
                            opacity: modelData.cover ? (isHovered ? 1.0 : 0.8) : 0.1
                            scale: isHovered ? 1.1 : 1.0
                            Behavior on scale { 
                                NumberAnimation { duration: 1200; easing.type: Easing.OutCubic } 
                            } 
                        }
                        Rectangle { 
                            id: infoOverlay
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: isHovered ? 110 : 70
                            gradient: Gradient { 
                                GradientStop { position: 0.0; color: "transparent" }
                                GradientStop { position: 0.4; color: Qt.rgba(10/255, 12/255, 20/255, 0.9) }
                                GradientStop { position: 1.0; color: "#0a0c14" } 
                            }
                            Behavior on height { NumberAnimation { duration: 300 } }
                            ColumnLayout { 
                                anchors.fill: parent
                                anchors.margins: 16
                                Layout.topMargin: 20
                                spacing: 4
                                Label { 
                                    Layout.fillWidth: true
                                    text: modelData.name
                                    color: "white"
                                    font.pixelSize: 14
                                    font.bold: true
                                    elide: Text.ElideRight
                                    maximumLineCount: 2
                                    wrapMode: Text.WordWrap 
                                }
                                Label { 
                                    text: "R " + modelData.playtime
                                    color: "#b0ffffff"
                                    font.pixelSize: 11
                                    visible: isHovered 
                                }
                            }
                        }
                    }
                    Row {
                        id: actionBar
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.topMargin: 22
                        anchors.rightMargin: 22
                        spacing: 8
                        z: 100
                        visible: isHovered || modelData.isFavorite
                        Rectangle {
                            width: 38
                            height: 38
                            radius: 19
                            color: infoBtnArea.containsMouse ? (modelData.accentColor || libraryRoot.currentPlatformColor) : "#e00a0c14"
                            border.color: modelData.accentColor || libraryRoot.currentPlatformColor
                            border.width: 1
                            visible: isHovered
                            Icon { 
                                anchors.centerIn: parent
                                name: "info"
                                size: 18
                                color: infoBtnArea.containsMouse ? "black" : "white" 
                            }
                            MouseArea { 
                                id: infoBtnArea
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: (mouse) => { 
                                    mouse.accepted = true
                                    libraryRoot.selectedGame = modelData
                                    infoPanel.open() 
                                } 
                            }
                        }
                        Rectangle {
                            width: 38
                            height: 38
                            radius: 19
                            color: favBtnArea.containsMouse ? "#ff4d4d" : (modelData.isFavorite ? "#33ff4d4d" : "#e00a0c14")
                            border.color: modelData.isFavorite ? "#ff4d4d" : (modelData.accentColor || libraryRoot.currentPlatformColor)
                            border.width: 1
                            Icon { 
                                anchors.centerIn: parent
                                name: modelData.isFavorite ? "favorite_filled" : "favorite"
                                size: 18
                                color: modelData.isFavorite ? "#ff4d4d" : (favBtnArea.containsMouse ? "white" : "#ccffffff")
                            }
                            MouseArea { 
                                id: favBtnArea
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: (mouse) => { 
                                    mouse.accepted = true
                                    let newVal = bridge.lib.toggleFavorite(modelData.path)
                                    modelData.isFavorite = newVal
                                    if (libraryRoot.onlyFavorites) {
                                        libraryRoot.needsHardRefresh = true
                                    }
                                } 
                            }
                        }
                    }
                }
            }
        }
    }

    Item {
        id: collectorContainer
        anchors.fill: parent
        opacity: libraryRoot.state === "collector" ? 1 : 0
        visible: opacity > 0
        Behavior on opacity { 
            NumberAnimation { duration: 600 } 
        }
        Rectangle { 
            anchors.fill: parent
            color: "#080a0f" 
        }
        Rectangle { 
            id: galleryAura
            anchors.centerIn: parent
            width: parent.width * 1.5
            height: parent.height * 1.2
            radius: width / 2
            color: "transparent"
            border.color: currentAccentColor
            border.width: 0
            opacity: 0.15
            z: 1
            layer.enabled: true
            layer.effect: MultiEffect { 
                shadowEnabled: true
                shadowBlur: 1.0
                shadowColor: currentAccentColor 
            } 
        }
        Item {
            id: galleryZone
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: parent.height * 0.6
            z: 100 
            PathView {
                id: galleryView
                anchors.fill: parent
                model: libraryRoot.currentGames || []
                pathItemCount: 11
                preferredHighlightBegin: 0.5
                preferredHighlightEnd: 0.5
                highlightRangeMode: PathView.StrictlyEnforceRange
                snapMode: PathView.SnapToItem
                clip: false
                onCurrentIndexChanged: { 
                    if (currentItem) {
                        libraryRoot.selectedGame = currentItem.gameData
                    }
                }
                path: Path {
                    startX: -galleryView.width * 0.2
                    startY: galleryView.height * 0.55
                    PathAttribute { name: "itemScale"; value: 0.6 }
                    PathAttribute { name: "itemOpacity"; value: 0.2 }
                    PathAttribute { name: "itemRotation"; value: 35 }
                    PathAttribute { name: "itemZ"; value: 1 }
                    PathLine { 
                        x: galleryView.width * 0.15
                        y: galleryView.height * 0.55 
                    }
                    PathPercent { value: 0.2 }
                    PathAttribute { name: "itemScale"; value: 0.9 }
                    PathAttribute { name: "itemOpacity"; value: 0.6 }
                    PathAttribute { name: "itemRotation"; value: 15 }
                    PathAttribute { name: "itemZ"; value: 10 }
                    PathLine { 
                        x: galleryView.width * 0.5
                        y: galleryView.height * 0.55 
                    }
                    PathPercent { value: 0.5 }
                    PathAttribute { name: "itemScale"; value: 1.45 }
                    PathAttribute { name: "itemOpacity"; value: 1.0 }
                    PathAttribute { name: "itemRotation"; value: 0 }
                    PathAttribute { name: "itemZ"; value: 1000 }
                    PathLine { 
                        x: galleryView.width * 0.85
                        y: galleryView.height * 0.55 
                    }
                    PathPercent { value: 0.8 }
                    PathAttribute { name: "itemScale"; value: 0.9 }
                    PathAttribute { name: "itemOpacity"; value: 0.6 }
                    PathAttribute { name: "itemRotation"; value: -15 }
                    PathAttribute { name: "itemZ"; value: 10 }
                    PathLine { 
                        x: galleryView.width * 1.2
                        y: galleryView.height * 0.55 
                    }
                    PathPercent { value: 1.0 }
                    PathAttribute { name: "itemScale"; value: 0.6 }
                    PathAttribute { name: "itemOpacity"; value: 0.2 }
                    PathAttribute { name: "itemRotation"; value: -35 }
                    PathAttribute { name: "itemZ"; value: 1 }
                }
                delegate: Item {
                    id: galleryDelegate
                    width: galleryView.width * 0.35
                    height: galleryView.height
                    opacity: galleryDelegate.PathView.itemOpacity || 1.0
                    z: galleryDelegate.PathView.itemZ || 1
                    property var gameData: modelData
                    GameBox3D { 
                        id: case3d
                        anchors.centerIn: parent
                        source: modelData.cover_3d || modelData.cover || ""
                        accentColor: libraryRoot.currentPlatformColor
                        showShadow: false
                        showGlow: galleryView.currentIndex === index
                        height: galleryView.height * 0.6
                        width: height * 0.72
                        scale: galleryDelegate.PathView.itemScale || 1.0
                        property real pathRotation: galleryDelegate.PathView.itemRotation || 0 
                    }
                }
            }
        }
        Item {
            id: infoZone
            anchors.top: galleryZone.bottom
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            z: 10
            anchors.bottomMargin: 45 * responsiveScale 
            ColumnLayout {
                anchors.centerIn: parent
                width: parent.width * 0.85
                spacing: 22 * responsiveScale 
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 6 * responsiveScale
                    Label { 
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        text: (libraryRoot.selectedGame && libraryRoot.selectedGame.name ? libraryRoot.selectedGame.name : "").toUpperCase()
                        font.pixelSize: Math.max(18, 28 * responsiveScale)
                        font.weight: Font.Black
                        color: "white"
                        font.letterSpacing: 2
                        elide: Text.ElideRight
                        maximumLineCount: 1 
                    }
                    Label { 
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        text: libraryRoot.selectedGame ? (libraryRoot.selectedGame.developer + "  |  " + libraryRoot.selectedGame.year).toUpperCase() : ""
                        font.pixelSize: 11 * responsiveScale
                        font.bold: true
                        color: currentAccentColor
                        opacity: 0.7
                        font.letterSpacing: 3 
                    }
                }
                ScrollView { 
                    Layout.fillWidth: true
                    Layout.preferredHeight: 90 * responsiveScale
                    Layout.leftMargin: parent.width * 0.05
                    Layout.rightMargin: parent.width * 0.05
                    clip: true
                    contentWidth: availableWidth
                    ScrollBar.vertical.policy: ScrollBar.AsNeeded
                    TextArea { 
                        width: parent.width
                        text: (libraryRoot.selectedGame ? libraryRoot.selectedGame.description || "" : "")
                        color: "#b0ffffff"
                        font.pixelSize: 13 * responsiveScale
                        wrapMode: Text.WordWrap
                        horizontalAlignment: Text.AlignHCenter
                        background: null
                        readOnly: true
                        padding: 0
                        selectByMouse: true 
                    }
                }
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 25 * responsiveScale
                    Button { 
                        id: playBtn
                        Layout.preferredWidth: 260 * responsiveScale
                        Layout.preferredHeight: 52 * responsiveScale
                        onClicked: {
                            if (libraryRoot.selectedGame) {
                                window.requestLaunch(libraryRoot.selectedGame.path, libraryRoot.selectedGame.id_emu, libraryRoot.selectedGame.name)
                            }
                        }
                        background: Rectangle { 
                            radius: height / 2
                            color: currentAccentColor
                            layer.enabled: true
                            layer.effect: MultiEffect { 
                                shadowEnabled: true
                                shadowColor: currentAccentColor
                                shadowBlur: 0.6 
                            } 
                        }
                        contentItem: Label { 
                            text: libraryRoot.tr("lib_btn_launch").toUpperCase()
                            color: "black"
                            font.bold: true
                            font.pixelSize: 15 * responsiveScale
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter 
                        } 
                    }
                    Button { 
                        Layout.preferredWidth: 52 * responsiveScale
                        Layout.preferredHeight: 52 * responsiveScale
                        onClicked: { 
                            libraryRoot.selectedGame = null
                            libraryRoot.state = "carousel" 
                        }
                        background: Rectangle { 
                            radius: height / 2
                            color: "#1affffff"
                            border.color: "#30ffffff"
                            border.width: 1 
                        }
                        contentItem: Label { 
                            text: " "
                            color: "white"
                            font.pixelSize: 18 * responsiveScale
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter 
                        } 
                    }
                }
            }
        }
    }

    Popup {
        id: tweakPopup
        anchors.centerIn: parent
        width: 520
        height: Math.min(680, parent.height * 0.85)
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        property string currentEmuId: ""
        property string currentEmuName: ""
        property color accentColor: window.themeAccent
        
        background: Rectangle { 
            color: "#161923"
            radius: 30
            border.color: "#33ffffff"
            border.width: 1
            Rectangle { 
                anchors.fill: parent
                anchors.margins: 1
                radius: 29
                color: "transparent"
                border.color: Qt.alpha(tweakPopup.accentColor, 0.1)
                border.width: 1 
            } 
        }
        
        contentItem: ColumnLayout { 
            id: tweakContent
            anchors.fill: parent
            anchors.margins: 30
            spacing: 25
            RowLayout { 
                spacing: 15
                Rectangle { 
                    width: 40
                    height: 40
                    radius: 20
                    color: Qt.alpha(tweakPopup.accentColor, 0.2)
                    Label { 
                        anchors.centerIn: parent
                        text: "⚙️"
                        font.pixelSize: 18 
                    } 
                }
                ColumnLayout { 
                    spacing: 0
                    Label { 
                        text: tweakPopup.currentEmuName.toUpperCase()
                        color: "white"
                        font.pixelSize: 18
                        font.weight: Font.Black
                        font.letterSpacing: 1 
                    }
                    Label { 
                        text: tr("lib_emu_settings").toUpperCase()
                        color: tweakPopup.accentColor
                        font.pixelSize: 10
                        font.bold: true
                        font.letterSpacing: 2 
                    }
                }
                Item { Layout.fillWidth: true }
                Button { 
                    text: " "
                    onClicked: tweakPopup.close()
                    flat: true
                    contentItem: Label { 
                        text: parent.text
                        color: "#66ffffff"
                        font.pixelSize: 20 
                    }
                    background: null 
                }
            }
            Rectangle { 
                Layout.fillWidth: true
                height: 1
                color: "#1affffff" 
            }
            ListView { 
                id: tweakListView
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: 12
                model: (tweakPopup.visible && bridge) ? bridge.emu.getEmulatorTweaks(tweakPopup.currentEmuId) : []
                ScrollBar.vertical: ScrollBar { 
                    id: scrollBar
                    policy: tweakListView.contentHeight > tweakListView.height ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff 
                }
                delegate: Rectangle { 
                    id: tweakItem
                    width: tweakListView.width - (scrollBar.visible ? 15 : 0)
                    height: shouldShow ? 90 : 0
                    radius: 18
                    color: "#1a202c"
                    border.color: "#2d3748"
                    border.width: 1
                    visible: height > 0
                    clip: true
                    Behavior on height { NumberAnimation { duration: 250 } }
                    property bool shouldShow: { 
                        if (modelData.depends_on === undefined) return true; 
                        if (modelData.depends_on.fullscreen !== undefined) { 
                            var fsValue = true; 
                            for (var i = 0; i < tweakListView.count; i++) { 
                                var item = tweakListView.model[i]; 
                                if (item.id === "fullscreen") { 
                                    fsValue = item.value; 
                                    break; 
                                } 
                            } 
                            return modelData.depends_on.fullscreen === fsValue; 
                        } 
                        return true; 
                    }
                    RowLayout { 
                        anchors.fill: parent
                        anchors.leftMargin: 25
                        anchors.rightMargin: 25
                        spacing: 20
                        ColumnLayout { 
                            spacing: 4
                            Layout.fillWidth: true
                            Label { 
                                text: (bridge && modelData.label.indexOf("lib_") === 0) ? bridge.translate(modelData.label) : modelData.label
                                font.pixelSize: 16
                                color: "white"
                                font.weight: Font.DemiBold
                                elide: Text.ElideRight
                                Layout.fillWidth: true 
                            }
                            Label { 
                                text: (bridge && bridge.currentLanguage) ? (modelData.type === "bool" ? bridge.translate("lib_tweak_on_start") : bridge.translate("lib_tweak_config")) : "Ajuste"
                                font.pixelSize: 11
                                color: "#718096"
                                font.bold: true
                                font.letterSpacing: 1.0 
                            }
                        }
                        Switch { 
                            visible: modelData.type === "bool"
                            checked: modelData.value
                            onToggled: { 
                                if (bridge) { 
                                    bridge.emu.saveEmulatorTweak(tweakPopup.currentEmuId, modelData.id, checked)
                                    tweakListView.model = bridge.emu.getEmulatorTweaks(tweakPopup.currentEmuId) 
                                } 
                            }
                            indicator: Rectangle { 
                                implicitWidth: 46
                                implicitHeight: 24
                                radius: 12
                                color: parent.checked ? Qt.alpha(tweakPopup.accentColor, 0.2) : "#2d3748"
                                border.color: parent.checked ? tweakPopup.accentColor : "#4a5568"
                                border.width: 1
                                Rectangle { 
                                    x: parent.parent.checked ? parent.width - width - 3 : 3
                                    y: 3
                                    width: 18
                                    height: 18
                                    radius: 9
                                    color: parent.parent.checked ? tweakPopup.accentColor : "#718096"
                                    Behavior on x { NumberAnimation { duration: 150 } } 
                                } 
                            } 
                        }
                        ComboBox { 
                            id: tweakCombo
                            visible: modelData.type === "list"
                            model: modelData.type === "list" ? modelData.options : []
                            currentIndex: modelData.type === "list" && modelData.options ? modelData.options.indexOf(modelData.value) : -1
                            Layout.preferredWidth: 160
                            Layout.preferredHeight: 38
                            onActivated: { 
                                if (bridge) { 
                                    bridge.emu.saveEmulatorTweak(tweakPopup.currentEmuId, modelData.id, modelData.options[currentIndex])
                                    tweakListView.model = bridge.emu.getEmulatorTweaks(tweakPopup.currentEmuId) 
                                } 
                            }
                            contentItem: Label { 
                                text: tweakCombo.displayText
                                color: "white"
                                font.pixelSize: 13
                                font.weight: Font.Medium
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 16
                                rightPadding: 36 
                            }
                            delegate: ItemDelegate { 
                                width: tweakCombo.width
                                contentItem: Label { 
                                    text: modelData
                                    color: highlighted ? "white" : "#9999aa"
                                    font.pixelSize: 13
                                    font.weight: highlighted ? Font.Medium : Font.Normal
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: 16 
                                }
                                background: Rectangle { 
                                    color: highlighted ? "#2d3748" : "transparent"
                                    radius: 8
                                    anchors.fill: parent
                                    anchors.margins: 2 
                                }
                                highlighted: tweakCombo.highlightedIndex === index 
                            }
                            popup: Popup { 
                                y: tweakCombo.height + 5
                                width: tweakCombo.width
                                padding: 2
                                contentItem: ListView { 
                                    clip: true
                                    implicitHeight: Math.min(contentHeight, 200)
                                    model: tweakCombo.delegateModel
                                    currentIndex: tweakCombo.highlightedIndex 
                                }
                                background: Rectangle { 
                                    color: "#1a1c24"
                                    radius: 12
                                    border.color: "#33ffffff"
                                    border.width: 1 
                                } 
                            }
                            background: Rectangle { 
                                color: "#2d3748"
                                radius: 10
                                border.color: tweakCombo.hovered ? tweakPopup.accentColor : "#4a5568"
                                border.width: 1
                                Behavior on border.color { 
                                    ColorAnimation { duration: 150 } 
                                } 
                            }
                            indicator: Canvas { 
                                id: comboCanvas
                                x: tweakCombo.width - width - 15
                                y: (tweakCombo.height - height) / 2
                                width: 10
                                height: 6
                                onPaint: { 
                                    var ctx = getContext("2d")
                                    ctx.reset()
                                    ctx.moveTo(0, 0)
                                    ctx.lineTo(width, 0)
                                    ctx.lineTo(width / 2, height)
                                    ctx.closePath()
                                    ctx.fillStyle = tweakCombo.hovered ? tweakPopup.accentColor : "#718096"
                                    ctx.fill() 
                                }
                                Connections { 
                                    target: tweakCombo
                                    function onHoveredChanged() { 
                                        comboCanvas.requestPaint() 
                                    } 
                                } 
                            } 
                        }
                    }
                }
                footer: Item { 
                    width: tweakListView.width
                    height: 10
                    visible: tweakListView.count > 0 
                }
                Label { 
                    anchors.centerIn: parent
                    visible: tweakListView.count === 0
                    text: tr("lib_no_tweaks")
                    font.pixelSize: 13
                    color: "#44ffffff"
                    font.italic: true 
                }
            }
            Button { 
                id: closeTweakBtn
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                text: tr("lib_tweak_done").toUpperCase()
                onClicked: tweakPopup.close()
                hoverEnabled: true
                background: Rectangle { 
                    radius: 25
                    color: closeTweakBtn.pressed ? "#1a202c" : (closeTweakBtn.hovered ? "#2d3748" : "#2a2f45")
                    border.color: closeTweakBtn.hovered ? "#4a5568" : "transparent"
                    border.width: 1 
                }
                contentItem: Label { 
                    text: parent.text
                    color: "white"
                    font.bold: true
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.letterSpacing: 1 
                } 
            }
        }
        enter: Transition { 
            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 200 }
            NumberAnimation { property: "scale"; from: 0.9; to: 1; duration: 300; easing.type: Easing.OutBack } 
        }
        exit: Transition { 
            NumberAnimation { property: "opacity"; to: 0; duration: 150 }
            NumberAnimation { property: "scale"; to: 0.9; duration: 150; easing.type: Easing.InBack } 
        }
    }

    MetadataEditor { 
        id: metaEditor
        onMetadataSaved: { 
            libraryRoot.needsHardRefresh = true
            if (libraryRoot.selectedGame) { 
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
                let newVal = bridge.lib.toggleFavorite(libraryRoot.selectedGame.path)
                libraryRoot.selectedGame.isFavorite = newVal
                let temp = favMap
                temp[libraryRoot.selectedGame.path] = newVal
                libraryRoot.favMap = Object.assign({}, temp) 
            } 
        }
    }
}
