import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects
import QtQuick.Shapes

/**
 * GameInfoPanel.qml — Slide-in panel with glass/neon redesign.
 * All signals and logic unchanged.
 */
Item {
    id: root

    property var gameData: null
    property color accentColor: window.themeAccent
    property bool isOpen: false

    property bool localFavorite: gameData ? gameData.isFavorite : false
    onGameDataChanged: { if(gameData) localFavorite = gameData.isFavorite }

    signal launchClicked(string path, string emuId, string gameName)
    signal editClicked()
    signal favoriteClicked()
    signal closed()

    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    function open() { isOpen = true }
    function close() { isOpen = false; closed() }

    anchors.fill: parent
    z: 3000
    visible: opacity > 0
    opacity: isOpen ? 1.0 : 0.0
    Behavior on opacity { NumberAnimation { duration: 320 } }

    // 1. DIMMER with subtle grid
    Rectangle {
        anchors.fill: parent
        color: "#e0000010"

        Canvas {
            anchors.fill: parent; opacity: 0.1
            onPaint: {
                var ctx = getContext("2d")
                ctx.strokeStyle = window.neonViolet
                ctx.lineWidth = 0.5
                for (var x = 0; x <= width; x += 60) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,height); ctx.stroke() }
                for (var y = 0; y <= height; y += 60) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(width,y); ctx.stroke() }
            }
        }
        MouseArea { anchors.fill: parent; onClicked: root.close() }
    }

    // 2. PANEL
    Item {
        id: panelContainer
        width: 500
        height: parent.height * 0.92
        anchors.verticalCenter: parent.verticalCenter
        x: root.isOpen ? parent.width - width - 30 : parent.width + 120
        Behavior on x { NumberAnimation { duration: 480; easing.type: Easing.OutCubic } }

        // Outer glow frame
        Rectangle {
            anchors.fill: parent
            anchors.margins: -1
            radius: 2
            color: "transparent"
            border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.3)
            border.width: 1
        }

        // Background
        Rectangle {
            anchors.fill: parent
            color: Qt.rgba(0.04, 0.02, 0.1, 0.97)
            radius: 0
            layer.enabled: true
            layer.effect: MultiEffect {
                shadowEnabled: true; shadowBlur: 1.5; shadowColor: accentColor
                shadowOpacity: 0.25; shadowHorizontalOffset: -8
            }

            // Left violet accent border
            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top; anchors.bottom: parent.bottom
                width: 2
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "transparent" }
                    GradientStop { position: 0.3; color: accentColor }
                    GradientStop { position: 0.7; color: window.neonMagenta }
                    GradientStop { position: 1.0; color: "transparent" }
                }
                opacity: 0.8
            }
        }

        ColumnLayout {
            anchors.fill: parent
            spacing: 0
            clip: true

            // A. BANNER
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 270
                clip: true

                Image {
                    id: bannerImg
                    anchors.fill: parent; anchors.margins: 0
                    source: root.gameData ? (root.gameData.background || root.gameData.cover || "") : ""
                    fillMode: Image.PreserveAspectCrop
                }

                // Banner gradient overlay
                Rectangle {
                    anchors.fill: parent
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: Qt.rgba(0.04, 0.02, 0.1, 0.3) }
                        GradientStop { position: 0.55; color: "transparent" }
                        GradientStop { position: 1.0; color: Qt.rgba(0.04, 0.02, 0.1, 1.0) }
                    }
                }

                // Top accent line
                Rectangle {
                    anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
                    height: 2
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: accentColor }
                        GradientStop { position: 0.6; color: window.neonMagenta }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                    opacity: 0.7
                }

                // Close button
                Button {
                    anchors.top: parent.top; anchors.right: parent.right
                    anchors.margins: 16; width: 36; height: 36
                    onClicked: root.close()
                    background: Rectangle {
                        radius: 18
                        color: parent.hovered ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.25) : Qt.rgba(0,0,0,0.5)
                        border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, parent.hovered ? 0.6 : 0.2)
                        border.width: 1
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                    contentItem: Icon { name: "close"; color: "white"; size: 15; opacity: 0.9 }
                }
            }

            // B. INFO AREA
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.leftMargin: 36
                Layout.rightMargin: 36
                Layout.topMargin: 0
                spacing: 18

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Label {
                        Layout.fillWidth: true
                        text: root.gameData ? root.gameData.name : ""
                        color: "#f0e8ff"
                        font.pixelSize: 30
                        font.weight: Font.Black
                        font.italic: true
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        layer.enabled: true
                        layer.effect: MultiEffect {
                            shadowEnabled: true; shadowColor: accentColor
                            shadowBlur: 0.5; shadowOpacity: 0.4
                        }
                    }

                    Row {
                        spacing: 8
                        // Favorite button
                        Button {
                            id: subFavBtn; width: 38; height: 38
                            onClicked: { root.favoriteClicked(); root.localFavorite = !root.localFavorite }
                            background: Rectangle {
                                radius: 12
                                color: subFavBtn.hovered
                                    ? Qt.rgba(root.accentColor.r, root.accentColor.g, root.accentColor.b, 0.2)
                                    : Qt.rgba(1,1,1,0.05)
                                border.color: root.localFavorite
                                    ? Qt.rgba(root.accentColor.r, root.accentColor.g, root.accentColor.b, 0.7)
                                    : Qt.rgba(1,1,1,0.15)
                                border.width: 1
                                Behavior on color { ColorAnimation { duration: 150 } }
                            }
                            contentItem: Icon {
                                name: root.localFavorite ? "favorite_filled" : "favorite"
                                color: root.localFavorite ? root.accentColor : "#aaaacc"
                                size: 18; opacity: root.localFavorite ? 1.0 : 0.6
                            }
                        }
                        // Edit button
                        Button {
                            id: subEditBtn; width: 38; height: 38
                            onClicked: root.editClicked()
                            background: Rectangle {
                                radius: 12
                                color: subEditBtn.hovered ? Qt.rgba(1,1,1,0.08) : Qt.rgba(1,1,1,0.04)
                                border.color: Qt.rgba(1,1,1,0.15); border.width: 1
                                Behavior on color { ColorAnimation { duration: 150 } }
                            }
                            contentItem: Icon { name: "edit"; color: "#aaaacc"; size: 16; opacity: 0.75 }
                        }
                    }
                }

                // Meta row
                RowLayout {
                    Layout.fillWidth: true; spacing: 18
                    Column {
                        spacing: 2
                        Label { text: tr("lib_developer"); color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.55); font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                        Label { text: root.gameData ? (root.gameData.developer || "Unknown") : ""; color: "#c0b0e0"; font.pixelSize: 13; font.weight: Font.DemiBold }
                    }
                    Rectangle { width: 1; height: 24; color: Qt.rgba(1,1,1,0.1) }
                    Column {
                        spacing: 2
                        Label { text: tr("lib_played"); color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.55); font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                        Label { text: root.gameData ? root.gameData.playtime : "0m"; color: "#c0b0e0"; font.pixelSize: 13; font.weight: Font.DemiBold }
                    }
                }

                // Description
                ScrollView {
                    Layout.fillWidth: true; Layout.fillHeight: true
                    clip: true
                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded; width: 2 }
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                    Label {
                        width: panelContainer.width - 72
                        text: root.gameData ? (root.gameData.description || tr("lib_no_info")) : ""
                        color: Qt.rgba(1,1,1,0.6)
                        font.pixelSize: 14; wrapMode: Text.WordWrap; lineHeight: 1.75
                        horizontalAlignment: Text.AlignJustify
                    }
                }

                // PLAY BUTTON
                Button {
                    id: megaPlayBtn
                    Layout.fillWidth: true
                    Layout.preferredHeight: 62
                    Layout.bottomMargin: 14
                    onClicked: {
                        if (root.gameData) {
                            root.launchClicked(root.gameData.path, root.gameData.id_emu, root.gameData.name)
                            root.close()
                        }
                    }
                    background: Rectangle {
                        radius: 18
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: megaPlayBtn.hovered ? accentColor : Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.0) }
                            GradientStop { position: 1.0; color: megaPlayBtn.hovered ? window.neonMagenta : Qt.rgba(window.neonMagenta.r, window.neonMagenta.g, window.neonMagenta.b, 0.0) }
                        }
                        border.color: megaPlayBtn.hovered
                            ? "transparent"
                            : Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.45)
                        border.width: 1.5
                        Behavior on gradient { }
                        scale: megaPlayBtn.pressed ? 0.97 : 1.0
                        Behavior on scale { NumberAnimation { duration: 100 } }
                        layer.enabled: megaPlayBtn.hovered
                        layer.effect: MultiEffect {
                            shadowEnabled: true; shadowBlur: 1.2; shadowColor: accentColor; shadowOpacity: 0.6
                        }
                    }
                    contentItem: RowLayout {
                        spacing: 12
                        Layout.alignment: Qt.AlignHCenter
                        Item { Layout.fillWidth: true }
                        Icon {
                            name: "play"; size: 20
                            color: megaPlayBtn.hovered ? "#0a0520" : "#d0c0f0"
                            Behavior on color { ColorAnimation { duration: 200 } }
                        }
                        Label {
                            text: tr("lib_btn_launch").toUpperCase()
                            color: megaPlayBtn.hovered ? "#0a0520" : "#d0c0f0"
                            font.pixelSize: 16; font.weight: Font.Bold; font.letterSpacing: 2
                            Behavior on color { ColorAnimation { duration: 200 } }
                        }
                        Item { Layout.fillWidth: true }
                    }
                }
            }
        }
    }
}
