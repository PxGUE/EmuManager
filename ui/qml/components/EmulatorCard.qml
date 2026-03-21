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
    
    // Diccionario global de actualizaciones detectadas
    property var updateResults: ({})
    
    // Obtenemos info especÃ­fica para el emulador seleccionado actualmente
    property var updateInfo: (currentEmu && updateResults) ? updateResults[currentEmu.id] || null : null
    property bool isUpdateAvailable: updateInfo && updateInfo.update_available && isInstalled

    width: 300
    height: 480
    
    Timer { id: statusTimer; interval: 5000; onTriggered: statusText = "" }

    // --- POPUP DE CONFIGURACIÃ“N (REDISEÃ‘O CON CENTRADO ABSOLUTO) ---
    Popup {
        id: configPopup
        parent: Overlay.overlay
        x: Math.round((parent.width - width) / 2); y: Math.round((parent.height - height) / 2)
        width: 500; height: 440; modal: true; focus: true
        padding: 0
        
        enter: Transition {
            NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 250; easing.type: Easing.OutQuint }
            NumberAnimation { property: "scale"; from: 0.98; to: 1.0; duration: 250; easing.type: Easing.OutBack }
        }

        background: Rectangle { 
            color: "#0a0b12"; radius: 30; border.color: "#25283a"; border.width: 1
            Rectangle {
                anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width; height: 140; radius: 30; opacity: 0.1
                gradient: Gradient {
                    GradientStop { position: 0.0; color: accentColor }
                    GradientStop { position: 1.0; color: "transparent" }
                }
            }
        }

        contentItem: ColumnLayout {
            spacing: 0
            // Forzamos que el ColumnLayout ocupe todo el ancho del Popup
            width: 500 

            // 1. CABECERA (CENTRADO GARANTIZADO)
            Item {
                Layout.fillWidth: true; Layout.preferredHeight: 180
                ColumnLayout {
                    anchors.centerIn: parent; spacing: 15; width: parent.width
                    
                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter; width: 72; height: 72; radius: 24; color: "#161826"
                        border.color: accentColor; border.width: 2
                        Icon { anchors.centerIn: parent; name: "settings"; size: 24; color: accentColor }
                    }
                    
                    ColumnLayout {
                        Layout.fillWidth: true; spacing: 4
                        Label { 
                            text: currentEmu ? currentEmu.name : ""; font.pixelSize: 28; font.bold: true; color: "white"
                            Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter
                        }
                        Label { 
                            text: name.toUpperCase(); font.pixelSize: 11; color: accentColor; font.bold: true; opacity: 0.7; font.letterSpacing: 4
                            Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }

            // 2. INSTRUCCIONES
            Label {
                Layout.fillWidth: true; Layout.leftMargin: 45; Layout.rightMargin: 45; Layout.bottomMargin: 30
                text: tr("dl_manual_step1_info")
                font.pixelSize: 14; color: "#9999aa"; wrapMode: Text.WordWrap; lineHeight: 1.6
                horizontalAlignment: Text.AlignHCenter
            }

            // 3. ACCIONES
            RowLayout {
                Layout.fillWidth: true; Layout.leftMargin: 45; Layout.rightMargin: 45; Layout.bottomMargin: 40; spacing: 15
                
                Button {
                    id: btnWeb
                    Layout.preferredWidth: 64; Layout.preferredHeight: 64
                    onClicked: { bridge.emu.openManualUrl(currentEmu.github); configPopup.close() }
                    background: Rectangle { 
                        color: btnWeb.hovered ? "#1c1e2a" : "transparent"; radius: 20; border.color: btnWeb.hovered ? accentColor : "#25283a"; border.width: 2
                    }
                    contentItem: Icon { name: "globe"; size: 24; anchors.centerIn: parent; color: btnWeb.hovered ? "white" : "#888899" }
                }

                Button {
                    id: btnManual
                    Layout.fillWidth: true; Layout.preferredHeight: 64
                    onClicked: { manualFileDialog.open(); configPopup.close() }
                    background: Rectangle { 
                        radius: 20
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: accentColor }
                            GradientStop { position: 1.0; color: Qt.lighter(accentColor, 1.2) }
                        }
                        scale: btnManual.pressed ? 0.98 : 1.0
                        Behavior on scale { NumberAnimation { duration: 100 } }
                        Rectangle { anchors.fill: parent; radius: 20; color: "white"; opacity: btnManual.hovered ? 0.1 : 0.0 }
                    }
                    contentItem: RowLayout {
                        anchors.centerIn: parent; spacing: 12
                        Icon { name: "folder"; size: 20; color: "white" }
                        Label { text: tr("dl_btn_manual").toUpperCase(); color: "black"; font.bold: true; font.pixelSize: 13; font.letterSpacing: 1 }
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

    // --- TARJETA PRINCIPAL ---
    Rectangle {
        id: container
        anchors.fill: parent; radius: 40; color: window.themeCardBg
        border.color: cardHover.hovered ? accentColor : Qt.rgba(1,1,1,0.08)
        border.width: cardHover.hovered ? 2 : 1; clip: true
        scale: cardHover.hovered ? 1.02 : 1.0
        Behavior on scale { NumberAnimation { duration: 400; easing.type: Easing.OutBack } }

        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true; shadowColor: cardHover.hovered ? accentColor : "black"
            shadowBlur: cardHover.hovered ? 2.5 : 1.0; shadowOpacity: cardHover.hovered ? 0.8 : 0.4
            shadowVerticalOffset: 4
        }
        
        Rectangle {
            anchors.fill: parent; anchors.margins: 1; radius: 39; color: "transparent"
            border.color: Qt.rgba(1,1,1,0.05); border.width: 1
        }

        // Inner Glass glare
        Rectangle {
            anchors.fill: parent
            radius: 40
            gradient: Gradient {
                GradientStop { position: 0.0; color: cardHover.hovered ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.25) : Qt.rgba(1,1,1,0.05) }
                GradientStop { position: 1.0; color: "transparent" }
            }
            Behavior on color { ColorAnimation { duration: 400 } }
        }

        ColumnLayout {
            anchors.fill: parent; anchors.margins: 25; spacing: 0

            // LOGO
            Item {
                Layout.fillWidth: true; Layout.preferredHeight: 140
                Rectangle {
                    anchors.centerIn: parent; width: 100; height: 100; radius: 50; color: Qt.rgba(0,0,0,0.4)
                    border.color: cardHover.hovered ? accentColor : Qt.rgba(1,1,1,0.1); border.width: 2
                    
                    layer.enabled: cardHover.hovered
                    layer.effect: MultiEffect {
                        shadowEnabled: true; shadowColor: accentColor; shadowBlur: 1.2; shadowOpacity: 0.8
                    }
                    
                    Label { anchors.centerIn: parent; text: name !== "" ? name.charAt(0).toUpperCase() : "?"; font.pixelSize: 44; font.bold: true; color: accentColor 
                        layer.enabled: true
                        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: accentColor; shadowBlur: 1.0; shadowOpacity: 0.8 }
                    }
                    
                    // Indicador de ActualizaciÃ³n
                    Rectangle {
                        anchors.top: parent.top; anchors.right: parent.right; width: 24; height: 24; radius: 12
                        color: window.neonYellow; border.color: window.themeBg; border.width: 2
                        visible: updateInfo && updateInfo.update_available
                        
                        layer.enabled: true
                        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: window.neonYellow; shadowBlur: 0.8; shadowOpacity: 1.0 }
                        
                        HoverHandler { id: updateHover }
                        
                        Icon { anchors.centerIn: parent; name: "arrow_up"; color: "black"; size: 14 }
                        ToolTip.visible: updateHover.hovered; ToolTip.text: updateInfo ? tr("maint_update_available", updateInfo.latest_version) : ""
                    }

                    Rectangle {
                        anchors.bottom: parent.bottom; anchors.right: parent.right; width: 28; height: 28; radius: 14
                        color: isInstalled ? window.neonCyan : "transparent"; border.color: isInstalled ? window.themeBg : Qt.rgba(1,1,1,0.2); border.width: 3
                        
                        layer.enabled: isInstalled
                        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: window.neonCyan; shadowBlur: 0.8; shadowOpacity: 0.8 }

                        Icon { 
                            anchors.centerIn: parent
                            name: isInstalled ? "" : "plus"
                            size: 14
                            color: "#666677"
                            visible: !isInstalled
                        }
                        Icon {
                            anchors.centerIn: parent
                            name: "check"
                            size: 14
                            color: "black"
                            visible: isInstalled
                        }
                    }
                }
            }

            Label {
                text: name.toUpperCase(); font.pixelSize: 22; font.bold: true; color: "white"
                Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; font.letterSpacing: 1; elide: Text.ElideRight
            }

            Item { Layout.preferredHeight: 15 }

            // SELECTOR
            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: 52; color: "#161922"; radius: 15; border.color: "#2a2d3a"
                RowLayout {
                    anchors.fill: parent; spacing: 0
                    Button {
                        id: prevBtn; Layout.preferredWidth: 45; Layout.fillHeight: true
                        visible: emulatorsList && emulatorsList.length > 1
                        onClicked: selectedIndex = (selectedIndex - 1 + emulatorsList.length) % emulatorsList.length
                        background: null
                        contentItem: Icon { name: "chevron_left"; size: 16; color: prevBtn.hovered ? accentColor : "#555566"; anchors.centerIn: parent }
                    }
                    Label { 
                        Layout.fillWidth: true; text: currentEmu ? currentEmu.name : ""; font.pixelSize: 12; font.bold: true; color: accentColor; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight 
                    }
                    Button {
                        id: nextBtn; Layout.preferredWidth: 45; Layout.fillHeight: true
                        visible: emulatorsList && emulatorsList.length > 1
                        onClicked: selectedIndex = (selectedIndex + 1) % emulatorsList.length
                        background: null
                        contentItem: Icon { name: "chevron_right"; size: 16; color: nextBtn.hovered ? accentColor : "#555566"; anchors.centerIn: parent }
                    }
                }
            }

            Item { Layout.fillHeight: true }

            // STATUS
            Item {
                Layout.fillWidth: true; Layout.preferredHeight: 70
                ColumnLayout {
                    anchors.fill: parent; visible: isDownloading; spacing: 8
                    Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 6; color: "#1a1c24"; radius: 3; Rectangle { width: parent.width * downloadProgress; height: parent.height; radius: 3; color: accentColor } }
                    Label { text: tr("dl_installing").toUpperCase() + " " + Math.round(downloadProgress * 100) + "%"; font.pixelSize: 10; font.bold: true; color: accentColor; Layout.alignment: Qt.AlignHCenter }
                }
                Label { anchors.fill: parent; visible: statusText !== "" && !isDownloading; text: statusText; font.pixelSize: 11; font.bold: true; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; wrapMode: Text.WordWrap }
            }

            // DOCK
            RowLayout {
                Layout.fillWidth: true; Layout.preferredHeight: 56; spacing: 12
                Button {
                    id: btnFolder; Layout.preferredWidth: 56; Layout.preferredHeight: 56
                    onClicked: bridge.emu.openEmulatorFolder(currentEmu.github); enabled: currentEmu && currentEmu.isInstalled
                    background: Rectangle { radius: 16; color: btnFolder.pressed ? accentColor : (btnFolder.hovered ? "#252836" : "#161922"); border.color: btnFolder.hovered ? accentColor : "#252836"; border.width: 1; opacity: enabled ? 1.0 : 0.2 }
                    contentItem: Icon { name: "folder"; size: 18; color: btnFolder.pressed ? "white" : (btnFolder.hovered ? "white" : "#888899") }
                }

                Button {
                    id: btnAction; Layout.fillWidth: true; Layout.preferredHeight: 56
                    onClicked: { 
                        if (!currentEmu) return; 
                        if (isUpdateAvailable || !isInstalled) {
                            isDownloading = true; 
                            statusText = ""; 
                            bridge.emu.installEmulator(currentEmu.github) 
                        } else { 
                            bridge.emu.uninstallEmulator(currentEmu.github);
                        }
                    }
                    background: Rectangle { 
                        radius: 16; 
                        color: isUpdateAvailable ? (btnAction.pressed ? "#cc8800" : "#ffaa00") : (isInstalled ? "transparent" : (btnAction.pressed ? Qt.darker(accentColor) : accentColor)); 
                        border.color: isUpdateAvailable ? "transparent" : (isInstalled ? (btnAction.hovered ? "#ff4d4d" : "#303440") : "transparent"); 
                        border.width: 1 
                    }
                    contentItem: Label { 
                        text: isUpdateAvailable ? tr("dl_btn_update").toUpperCase() : (isInstalled ? tr("dl_btn_uninstall").toUpperCase() : tr("dl_btn_install").toUpperCase()); 
                        color: isUpdateAvailable ? "black" : (isInstalled ? (btnAction.hovered ? "#ff4d4d" : "#888899") : "#000000"); 
                        font.bold: true; font.pixelSize: 13; font.letterSpacing: 1; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter 
                    }
                }
                Button {
                    id: btnConfig; Layout.preferredWidth: 56; Layout.preferredHeight: 56
                    onClicked: configPopup.open()
                    background: Rectangle { radius: 16; color: btnConfig.hovered ? "#252836" : "#161922"; border.color: btnConfig.hovered ? accentColor : "#252836"; border.width: 1 }
                    contentItem: Icon { name: "settings"; size: 18; color: btnConfig.hovered ? "white" : "#888899" }
                }
            }
        }
    }

    Connections {
        target: bridge
        function onDownloadProgress(id, p) { if (currentEmu && id === currentEmu.id) { downloadProgress = p; isDownloading = true; statusText = "" } }
        function onDownloadFinished(id, success, msg) { if (currentEmu && id === currentEmu.id) { isDownloading = false; downloadProgress = 0; statusText = msg; statusTimer.start() } }
    }
}
