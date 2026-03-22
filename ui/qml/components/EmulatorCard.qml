import QtQuick
import QtQuick.Effects
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Dialogs

Item {
    id: cardRoot

    property string name: ""
    property string emulatorsJson: "[]"
    property color accentColor: window.themeAccent
    property bool isInstalled: false

    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    property var emulatorsList: {
        try { return JSON.parse(emulatorsJson) }
        catch(e) { return [] }
    }

    property int selectedIndex: 0
    property var currentEmu: emulatorsList && emulatorsList.length > 0 ? emulatorsList[selectedIndex] : null

    property real downloadProgress: 0
    property bool isDownloading: false
    property string statusText: ""

    property var updateResults: ({})
    property var updateInfo: (currentEmu && updateResults) ? updateResults[currentEmu.id] || null : null
    property bool isUpdateAvailable: updateInfo && updateInfo.update_available && isInstalled

    width: 300
    height: 490

    Timer { id: statusTimer; interval: 5000; onTriggered: statusText = "" }

    // ── Config Popup ──
    Popup {
        id: configPopup
        parent: Overlay.overlay
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        width: 510; height: 460; modal: true; focus: true
        padding: 0

        enter: Transition {
            NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 280; easing.type: Easing.OutQuint }
            NumberAnimation { property: "scale"; from: 0.95; to: 1.0; duration: 320; easing.type: Easing.OutBack }
        }
        exit: Transition {
            NumberAnimation { property: "opacity"; from: 1.0; to: 0.0; duration: 200 }
            NumberAnimation { property: "scale"; from: 1.0; to: 0.95; duration: 200 }
        }

        background: Item {
            Rectangle {
                anchors.fill: parent
                anchors.margins: -5
                radius: 36
                color: "transparent"
                border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.15)
                border.width: 1
                opacity: 0.7
            }
            Rectangle {
                anchors.fill: parent
                radius: 32
                color: Qt.rgba(0.04, 0.02, 0.1, 0.97)
                border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.45)
                border.width: 1
                layer.enabled: true
                layer.effect: MultiEffect {
                    shadowEnabled: true; shadowColor: accentColor
                    shadowBlur: 2.0; shadowOpacity: 0.4; shadowVerticalOffset: 10
                }
                // Radial top glow
                Rectangle {
                    anchors.top: parent.top
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: parent.width; height: 160; radius: parent.radius
                    opacity: 0.13
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: accentColor }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }
                // Inner sheen
                Rectangle {
                    anchors.fill: parent; anchors.margins: 1; radius: 31
                    color: "transparent"; border.color: Qt.rgba(1,1,1,0.05); border.width: 1
                }
            }
        }

        contentItem: ColumnLayout {
            spacing: 0
            width: 510

            // Header
            Item {
                Layout.fillWidth: true; Layout.preferredHeight: 190
                ColumnLayout {
                    anchors.centerIn: parent; spacing: 14; width: parent.width

                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter; width: 76; height: 76; radius: 26
                        color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.15)
                        border.color: accentColor; border.width: 1.5
                        layer.enabled: true
                        layer.effect: MultiEffect {
                            shadowEnabled: true; shadowColor: accentColor
                            shadowBlur: 1.2; shadowOpacity: 0.6
                        }
                        Icon { anchors.centerIn: parent; name: "settings"; size: 26; color: accentColor }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true; spacing: 4
                        Label {
                            text: currentEmu ? currentEmu.name : ""
                            font.pixelSize: 28; font.bold: true; color: "#f0e8ff"
                            Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter
                        }
                        Label {
                            text: name.toUpperCase()
                            font.pixelSize: 10; color: accentColor; font.bold: true
                            opacity: 0.7; font.letterSpacing: 4
                            Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }

            Label {
                Layout.fillWidth: true; Layout.leftMargin: 48; Layout.rightMargin: 48; Layout.bottomMargin: 28
                text: tr("dl_manual_step1_info")
                font.pixelSize: 14; color: "#8888aa"; wrapMode: Text.WordWrap
                lineHeight: 1.6; horizontalAlignment: Text.AlignHCenter
            }

            RowLayout {
                Layout.fillWidth: true; Layout.leftMargin: 48; Layout.rightMargin: 48
                Layout.bottomMargin: 44; spacing: 14

                Button {
                    id: btnWeb
                    Layout.preferredWidth: 66; Layout.preferredHeight: 66
                    onClicked: { bridge.emu.openManualUrl(currentEmu.github); configPopup.close() }
                    background: Rectangle {
                        radius: 20
                        color: btnWeb.hovered
                            ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.15)
                            : Qt.rgba(1,1,1,0.04)
                        border.color: btnWeb.hovered ? accentColor : "#25283a"
                        border.width: 1
                        Behavior on color { ColorAnimation { duration: 150 } }
                        Behavior on border.color { ColorAnimation { duration: 150 } }
                    }
                    contentItem: Icon { name: "globe"; size: 24; anchors.centerIn: parent; color: btnWeb.hovered ? accentColor : "#666677" }
                }

                Button {
                    id: btnManual
                    Layout.fillWidth: true; Layout.preferredHeight: 66
                    onClicked: { manualFileDialog.open(); configPopup.close() }
                    background: Rectangle {
                        radius: 20
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: accentColor }
                            GradientStop { position: 1.0; color: window.neonMagenta }
                        }
                        scale: btnManual.pressed ? 0.97 : 1.0
                        Behavior on scale { NumberAnimation { duration: 100 } }
                        layer.enabled: btnManual.hovered
                        layer.effect: MultiEffect {
                            shadowEnabled: true; shadowColor: accentColor
                            shadowBlur: 1.0; shadowOpacity: 0.6
                        }
                        Rectangle { anchors.fill: parent; radius: 20; color: "white"; opacity: btnManual.hovered ? 0.08 : 0 }
                    }
                    contentItem: RowLayout {
                        anchors.centerIn: parent; spacing: 12
                        Icon { name: "folder"; size: 20; color: "#0a0520" }
                        Label { text: tr("dl_btn_manual").toUpperCase(); color: "#0a0520"; font.bold: true; font.pixelSize: 13; font.letterSpacing: 0.5 }
                    }
                }
            }
        }
    }

    FileDialog {
        id: manualFileDialog
        title: tr("dl_manual_dlg_title")
        onAccepted: {
            if (!currentEmu) return
            isDownloading = true
            statusText = tr("dl_manual_prep")
            bridge.emu.manualInstall(currentEmu.github, selectedFile.toString().replace("file://", ""))
        }
    }

    HoverHandler { id: cardHover }

    // ── Main Card ──
    Rectangle {
        id: container
        anchors.fill: parent
        radius: 44
        color: Qt.rgba(0.08, 0.05, 0.18, 0.78)
        border.color: cardHover.hovered
            ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.85)
            : Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.22)
        border.width: cardHover.hovered ? 1.5 : 1
        clip: true
        scale: cardHover.hovered ? 1.025 : 1.0
        Behavior on scale { NumberAnimation { duration: 400; easing.type: Easing.OutBack } }
        Behavior on border.color { ColorAnimation { duration: 300 } }

        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: cardHover.hovered ? accentColor : "#220022"
            shadowBlur: cardHover.hovered ? 2.5 : 1.0
            shadowOpacity: cardHover.hovered ? 0.7 : 0.3
            shadowVerticalOffset: 6
        }

        // Inner glass sheen
        Rectangle {
            anchors.fill: parent; anchors.margins: 1; radius: 43
            color: "transparent"; border.color: Qt.rgba(1,1,1,0.05); border.width: 1
        }

        // Hover top glow
        Rectangle {
            anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
            height: 120; radius: 44
            opacity: cardHover.hovered ? 0.22 : 0.06
            Behavior on opacity { NumberAnimation { duration: 350 } }
            gradient: Gradient {
                GradientStop { position: 0.0; color: accentColor }
                GradientStop { position: 1.0; color: "transparent" }
            }
        }

        ColumnLayout {
            anchors.fill: parent; anchors.margins: 26; spacing: 0

            // LOGO
            Item {
                Layout.fillWidth: true; Layout.preferredHeight: 150

                // Animated ring
                Rectangle {
                    anchors.centerIn: parent
                    width: 116; height: 116; radius: 58
                    color: "transparent"
                    border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.25)
                    border.width: 1
                    visible: cardHover.hovered
                    SequentialAnimation on scale {
                        running: cardHover.hovered; loops: Animation.Infinite
                        NumberAnimation { from: 1.0; to: 1.1; duration: 1500; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.1; to: 1.0; duration: 1500; easing.type: Easing.InOutSine }
                    }
                }

                Rectangle {
                    anchors.centerIn: parent
                    width: 100; height: 100; radius: 50
                    color: Qt.rgba(0,0,0,0.45)
                    border.color: cardHover.hovered ? accentColor : Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.2)
                    border.width: cardHover.hovered ? 2 : 1
                    Behavior on border.color { ColorAnimation { duration: 300 } }

                    layer.enabled: cardHover.hovered
                    layer.effect: MultiEffect {
                        shadowEnabled: true; shadowColor: accentColor; shadowBlur: 1.5; shadowOpacity: 0.8
                    }

                    Label {
                        anchors.centerIn: parent
                        text: name !== "" ? name.charAt(0).toUpperCase() : "?"
                        font.pixelSize: 44; font.bold: true; color: accentColor
                        layer.enabled: true
                        layer.effect: MultiEffect {
                            shadowEnabled: true; shadowColor: accentColor; shadowBlur: 1.2; shadowOpacity: 0.9
                        }
                    }

                    // Update indicator
                    Rectangle {
                        anchors.top: parent.top; anchors.right: parent.right
                        width: 24; height: 24; radius: 12
                        color: window.neonGold; border.color: "#060711"; border.width: 2
                        visible: updateInfo && updateInfo.update_available
                        layer.enabled: true
                        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: window.neonGold; shadowBlur: 0.8; shadowOpacity: 1.0 }
                        HoverHandler { id: updateHover }
                        Icon { anchors.centerIn: parent; name: "arrow_up"; color: "#0a0520"; size: 13 }
                        ToolTip.visible: updateHover.hovered
                        ToolTip.text: updateInfo ? tr("maint_update_available", updateInfo.latest_version) : ""
                    }

                    // Installed badge
                    Rectangle {
                        anchors.bottom: parent.bottom; anchors.right: parent.right
                        width: 28; height: 28; radius: 14
                        color: isInstalled ? window.neonGreen : Qt.rgba(1,1,1,0.06)
                        border.color: isInstalled ? "#060711" : Qt.rgba(1,1,1,0.15); border.width: 3
                        layer.enabled: isInstalled
                        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: window.neonGreen; shadowBlur: 0.8; shadowOpacity: 0.8 }
                        Icon { anchors.centerIn: parent; name: isInstalled ? "check" : "plus"; size: 14; color: isInstalled ? "#060711" : "#666677"; visible: true }
                    }
                }
            }

            Label {
                text: name.toUpperCase()
                font.pixelSize: 20; font.weight: Font.Black; color: "#f0e8ff"
                Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter
                font.letterSpacing: 1.5; elide: Text.ElideRight
                layer.enabled: cardHover.hovered
                layer.effect: MultiEffect {
                    shadowEnabled: true; shadowColor: accentColor; shadowBlur: 0.6; shadowOpacity: 0.5
                }
            }

            Item { Layout.preferredHeight: 18 }

            // Selector
            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: 52
                color: Qt.rgba(0,0,0,0.35); radius: 16
                border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.2); border.width: 1
                RowLayout {
                    anchors.fill: parent; spacing: 0
                    Button {
                        id: prevBtn; Layout.preferredWidth: 46; Layout.fillHeight: true
                        visible: emulatorsList && emulatorsList.length > 1
                        onClicked: selectedIndex = (selectedIndex - 1 + emulatorsList.length) % emulatorsList.length
                        background: null
                        contentItem: Icon { name: "chevron_left"; size: 16; color: prevBtn.hovered ? accentColor : "#555566"; anchors.centerIn: parent }
                    }
                    Label {
                        Layout.fillWidth: true
                        text: currentEmu ? currentEmu.name : ""
                        font.pixelSize: 12; font.bold: true; color: accentColor
                        horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight
                    }
                    Button {
                        id: nextBtn; Layout.preferredWidth: 46; Layout.fillHeight: true
                        visible: emulatorsList && emulatorsList.length > 1
                        onClicked: selectedIndex = (selectedIndex + 1) % emulatorsList.length
                        background: null
                        contentItem: Icon { name: "chevron_right"; size: 16; color: nextBtn.hovered ? accentColor : "#555566"; anchors.centerIn: parent }
                    }
                }
            }

            Item { Layout.fillHeight: true }

            // Status
            Item {
                Layout.fillWidth: true; Layout.preferredHeight: 68
                ColumnLayout {
                    anchors.fill: parent; visible: isDownloading; spacing: 8
                    Item {
                        Layout.fillWidth: true; Layout.preferredHeight: 6
                        Rectangle { anchors.fill: parent; radius: 3; color: Qt.rgba(1,1,1,0.06) }
                        Rectangle {
                            width: parent.width * downloadProgress; height: parent.height; radius: 3
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0.0; color: accentColor }
                                GradientStop { position: 1.0; color: window.neonMagenta }
                            }
                            layer.enabled: true
                            layer.effect: MultiEffect { shadowEnabled: true; shadowColor: accentColor; shadowBlur: 0.8; shadowOpacity: 0.7 }
                        }
                    }
                    Label {
                        text: tr("dl_installing").toUpperCase() + " " + Math.round(downloadProgress * 100) + "%"
                        font.pixelSize: 10; font.bold: true; color: accentColor; font.letterSpacing: 1
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
                Label {
                    anchors.fill: parent; visible: statusText !== "" && !isDownloading; text: statusText
                    font.pixelSize: 11; font.bold: true; color: "#c0c0d0"
                    horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; wrapMode: Text.WordWrap
                }
            }

            // Action Dock
            RowLayout {
                Layout.fillWidth: true; Layout.preferredHeight: 58; spacing: 10

                Button {
                    id: btnFolder; Layout.preferredWidth: 58; Layout.preferredHeight: 58
                    onClicked: bridge.emu.openEmulatorFolder(currentEmu.github)
                    enabled: currentEmu && currentEmu.isInstalled
                    background: Rectangle {
                        radius: 18
                        color: btnFolder.pressed ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.3)
                             : (btnFolder.hovered ? Qt.rgba(1,1,1,0.07) : Qt.rgba(1,1,1,0.03))
                        border.color: btnFolder.hovered ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.5) : "#252836"
                        border.width: 1
                        opacity: enabled ? 1.0 : 0.2
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                    contentItem: Icon {
                        name: "folder"; size: 18
                        color: btnFolder.hovered ? accentColor : "#666677"
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                }

                Button {
                    id: btnAction; Layout.fillWidth: true; Layout.preferredHeight: 58
                    onClicked: {
                        if (!currentEmu) return
                        if (isUpdateAvailable || !isInstalled) {
                            isDownloading = true; statusText = ""
                            bridge.emu.installEmulator(currentEmu.github)
                        } else {
                            bridge.emu.uninstallEmulator(currentEmu.github)
                        }
                    }
                    background: Rectangle {
                        radius: 18
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop {
                                position: 0.0
                                color: isUpdateAvailable ? window.neonGold
                                     : (isInstalled ? Qt.rgba(0.97, 0.44, 0.44, btnAction.hovered ? 0.25 : 0.0)
                                     : accentColor)
                            }
                            GradientStop {
                                position: 1.0
                                color: isUpdateAvailable ? Qt.lighter(window.neonGold, 1.2)
                                     : (isInstalled ? Qt.rgba(0.97, 0.44, 0.44, btnAction.hovered ? 0.15 : 0.0)
                                     : window.neonMagenta)
                            }
                        }
                        border.color: isInstalled && !isUpdateAvailable
                            ? (btnAction.hovered ? "#f87171" : "#2a2a3a")
                            : "transparent"
                        border.width: 1
                        scale: btnAction.pressed ? 0.96 : 1.0
                        Behavior on scale { NumberAnimation { duration: 100 } }
                        layer.enabled: !isInstalled || isUpdateAvailable
                        layer.effect: MultiEffect {
                            shadowEnabled: true; shadowColor: accentColor; shadowBlur: 0.8; shadowOpacity: 0.5
                        }
                    }
                    contentItem: Label {
                        text: isUpdateAvailable ? tr("dl_btn_update").toUpperCase()
                            : (isInstalled ? tr("dl_btn_uninstall").toUpperCase() : tr("dl_btn_install").toUpperCase())
                        color: isUpdateAvailable ? "#0a0520"
                             : (isInstalled ? (btnAction.hovered ? "#f87171" : "#777788") : "#0a0520")
                        font.bold: true; font.pixelSize: 13; font.letterSpacing: 0.5
                        horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                }

                Button {
                    id: btnConfig; Layout.preferredWidth: 58; Layout.preferredHeight: 58
                    onClicked: configPopup.open()
                    background: Rectangle {
                        radius: 18
                        color: btnConfig.hovered ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.15) : Qt.rgba(1,1,1,0.03)
                        border.color: btnConfig.hovered ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.5) : "#252836"
                        border.width: 1
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                    contentItem: Icon {
                        name: "settings"; size: 18
                        color: btnConfig.hovered ? accentColor : "#666677"
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                }
            }
        }
    }

    Connections {
        target: bridge
        function onDownloadProgress(id, p) {
            if (currentEmu && id === currentEmu.id) { downloadProgress = p; isDownloading = true; statusText = "" }
        }
        function onDownloadFinished(id, success, msg) {
            if (currentEmu && id === currentEmu.id) { isDownloading = false; downloadProgress = 0; statusText = msg; statusTimer.start() }
        }
    }
}
