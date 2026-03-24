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

    MainController { id: controller }
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
        var summary = controller.get_consoles_summary()
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
        target: controller
        function onScanFinished(count) { refreshConsoles() }
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
                title: model.title; iconEmoji: model.iconEmoji; accentColor: model.accentColor
                gameCount: model.gameCount; playTime: model.playTime
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
            startX: -200; startY: consoleCarousel.height / 2
            PathAttribute { name: "iconScale"; value: 0.4 }
            PathAttribute { name: "iconOpacity"; value: 0.0 }
            PathAttribute { name: "iconZ"; value: -20 }
            PathLine { x: consoleCarousel.width / 2; y: consoleCarousel.height / 2 }
            PathAttribute { name: "iconScale"; value: 1.15 }
            PathAttribute { name: "iconOpacity"; value: 1.0 }
            PathAttribute { name: "iconZ"; value: 100 }
            PathLine { x: consoleCarousel.width + 200; y: consoleCarousel.height / 2 }
            PathAttribute { name: "iconScale"; value: 0.4 }
            PathAttribute { name: "iconOpacity"; value: 0.0 }
            PathAttribute { name: "iconZ"; value: -20 }
        }
    }

    // --- GALERÍA DE JUEGOS ---
    GridView {
        id: romGallery
        anchors.top: consoleCarousel.bottom; anchors.bottom: parent.bottom
        anchors.left: parent.left; anchors.right: parent.right; anchors.margins: 40; anchors.topMargin: 20
        cellWidth: 220; cellHeight: 300; clip: true; visible: showGames; opacity: showGames ? 1 : 0
        model: gamesModel
        delegate: RomCard {
            title: model.title; platform: model.platform
            cover2d: model.cover2dPath; cover3d: model.cover3dPath
            onClicked: console.log("Lanzando " + model.title)
        }
        Behavior on opacity { NumberAnimation { duration: 500 } }
    }

    // --- BOTÓN VOLVER ---
    EmuFloatingButton {
        icon: "⟲"; accentColor: "#16a085"; size: 54; visible: showGames
        anchors.bottom: parent.bottom; anchors.bottomMargin: 30; anchors.horizontalCenter: parent.horizontalCenter
        onClicked: showGames = false
    }
}
