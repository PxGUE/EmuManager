import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: settingsRoot

    property var selectedProvider: null
    
    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        contentHeight: settingsCol.implicitHeight + 100
        clip: true
        ScrollBar.vertical.policy: ScrollBar.AsNeeded

        ColumnLayout {
            id: settingsCol
            width: parent.width - 120
            anchors.horizontalCenter: parent.horizontalCenter
            y: 40
            spacing: 40

            // --- HEADER ---
            ColumnLayout {
                spacing: 4
                Label {
                    text: tr("nav_settings")
                    font.pixelSize: 14
                    color: "#888899"
                    opacity: 0.8
                }
            }

            // --- SECCIÓN: IDIOMA ---
            ColumnLayout {
                spacing: 12
                Layout.fillWidth: true

                RowLayout {
                    spacing: 10
                    Rectangle { width: 3; height: 16; radius: 1.5; color: "#4da6ff" }
                    Label {
                        text: tr("set_lang_lbl").toUpperCase()
                        font.pixelSize: 13; font.bold: true; color: "white"; font.letterSpacing: 1
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    radius: 20
                    color: "#0dffffff"
                    border.color: "#1affffff"; border.width: 1

                    SettingRow {
                        anchors.fill: parent
                        icon: ""
                        title: tr("set_lang_title")
                        subtitle: tr("set_lang_sub")

                        ComboBox {
                            id: langCombo
                            model: ["Español", "English"]
                            currentIndex: (bridge && bridge.currentLanguage === "es") ? 0 : 1
                            onActivated: { if (bridge) bridge.changeLanguage(currentIndex === 0 ? "es" : "en") }
                            Layout.preferredWidth: 180
                            Layout.preferredHeight: 38
                            
                            // Texto del botón principal
                            contentItem: Label {
                                text: langCombo.displayText
                                color: "white"
                                font.pixelSize: 13; font.weight: Font.Medium
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 16
                                rightPadding: 36
                            }

                            // Diseño de cada opción en la lista
                            delegate: ItemDelegate {
                                width: langCombo.width
                                contentItem: Label {
                                    text: modelData
                                    color: highlighted ? "white" : "#9999aa"
                                    font.pixelSize: 13; font.weight: highlighted ? Font.Medium : Font.Normal
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: 16
                                }
                                background: Rectangle {
                                    color: highlighted ? "#2a2d3e" : "transparent"
                                    radius: 8; anchors.fill: parent; anchors.margins: 2
                                }
                                highlighted: langCombo.highlightedIndex === index
                            }

                            // Estilo del menú desplegable (Popup)
                            popup: Popup {
                                y: langCombo.height + 5
                                width: langCombo.width
                                padding: 2
                                contentItem: ListView {
                                    clip: true
                                    implicitHeight: contentHeight
                                    model: langCombo.delegateModel
                                    currentIndex: langCombo.highlightedIndex
                                }
                                background: Rectangle {
                                    color: "#1a1c24"; radius: 12
                                    border.color: "#33ffffff"; border.width: 1
                                }
                            }

                            // Flecha personalizada
                            indicator: Canvas {
                                id: canvas
                                x: langCombo.width - width - 12
                                y: (langCombo.height - height) / 2
                                width: 12; height: 8
                                onPaint: {
                                    var ctx = getContext("2d");
                                    ctx.reset();
                                    ctx.moveTo(0, 0);
                                    ctx.lineTo(width, 0);
                                    ctx.lineTo(width / 2, height);
                                    ctx.closePath();
                                    ctx.fillStyle = langCombo.hovered ? "#4da6ff" : "#666677";
                                    ctx.fill();
                                }
                                Connections {
                                    target: langCombo
                                    function onHoveredChanged() { canvas.requestPaint(); }
                                }
                            }

                            background: Rectangle { 
                                radius: 10; color: "#1a1c24"
                                border.color: langCombo.hovered ? "#4da6ff" : "#33ffffff"
                                border.width: 1 
                                Behavior on border.color { ColorAnimation { duration: 150 } }
                            }
                        }
                    }
                }
            }

            // --- SECCIÓN: RUTAS ---
            ColumnLayout {
                spacing: 12
                Layout.fillWidth: true

                RowLayout {
                    spacing: 10
                    Rectangle { width: 3; height: 16; radius: 1.5; color: "#4da6ff" }
                    Label {
                        text: tr("set_paths_section").toUpperCase()
                        font.pixelSize: 13; font.bold: true; color: "white"; font.letterSpacing: 1
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: pathsCol.implicitHeight
                    radius: 20
                    color: "#0dffffff"
                    border.color: "#1affffff"; border.width: 1

                    ColumnLayout {
                        id: pathsCol
                        width: parent.width
                        spacing: 0

                        PathSetting {
                            title: tr("set_path_apps_title")
                            subtitle: tr("set_path_apps_sub")
                            path: bridge ? bridge.set.installPath : ""
                            onBrowse: bridge.set.browseInstallPath()
                        }
                        
                        Rectangle { Layout.fillWidth: true; Layout.leftMargin: 20; Layout.rightMargin: 20; height: 1; color: "#0fffffff" }

                        PathSetting {
                            title: tr("set_path_roms_title")
                            subtitle: tr("set_path_roms_sub")
                            path: bridge ? bridge.set.romsPath : ""
                            onBrowse: bridge.set.browseRomsPath()
                        }
                    }
                }
            }

            // --- SECCIÓN: INTERFAZ ---
            ColumnLayout {
                spacing: 12
                Layout.fillWidth: true

                RowLayout {
                    spacing: 10
                    Rectangle { width: 3; height: 16; radius: 1.5; color: "#4da6ff" }
                    Label {
                        text: tr("set_interface_section").toUpperCase()
                        font.pixelSize: 13; font.bold: true; color: "white"; font.letterSpacing: 1
                    }
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    radius: 20
                    color: "#0dffffff"
                    border.color: "#1affffff"; border.width: 1

                    SettingRow {
                        anchors.fill: parent
                        icon: "🎮"
                        title: tr("set_collector_title")
                        subtitle: tr("set_collector_sub")

                        Switch {
                            id: collectorSwitch
                            checked: bridge ? bridge.set.collectorMode : false
                            onClicked: {
                                if (bridge) bridge.set.setCollectorMode(checked)
                            }
                            
                            indicator: Rectangle {
                                implicitWidth: 48
                                implicitHeight: 26
                                radius: 13
                                color: collectorSwitch.checked ? "#4da6ff" : "#2a2d3e"
                                border.color: collectorSwitch.checked ? "#4da6ff" : "#33ffffff"

                                Rectangle {
                                    x: collectorSwitch.checked ? parent.width - width - 2 : 2
                                    y: 2
                                    width: 22
                                    height: 22
                                    radius: 11
                                    color: "white"
                                    Behavior on x {
                                        NumberAnimation { duration: 200; easing.type: Easing.OutQuad }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // --- SECCIÓN: DATOS ---
            ColumnLayout {
                spacing: 12
                Layout.fillWidth: true

                RowLayout {
                    spacing: 10
                    Rectangle { width: 3; height: 16; radius: 1.5; color: "#4da6ff" }
                    Label {
                        text: tr("set_data_section").toUpperCase()
                        font.pixelSize: 13; font.bold: true; color: "white"; font.letterSpacing: 1
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: providersCol.implicitHeight
                    radius: 20
                    color: "#0dffffff"
                    border.color: "#1affffff"; border.width: 1

                    ColumnLayout {
                        id: providersCol
                        width: parent.width
                        spacing: 0
                        Repeater {
                            model: bridge ? bridge.set.scraperProviders : []
                            delegate: ColumnLayout {
                                spacing: 0
                                Layout.fillWidth: true
                                ProviderCard {
                                    providerId: modelData.id
                                    name: modelData.name
                                    typeDisplay: modelData.type
                                    isActive: modelData.enabled
                                    isConfigured: modelData.is_configured
                                    onConfigureClicked: {
                                        selectedProvider = modelData
                                        configPopup.open()
                                    }
                                }
                                Rectangle {
                                    visible: index < (bridge.set.scraperProviders.length - 1)
                                    Layout.fillWidth: true; Layout.leftMargin: 20; Layout.rightMargin: 20; height: 1; color: "#0fffffff"
                                }
                            }
                        }
                    }
                }
            }

            // --- ABOUT BUTTON ---
            Button {
                id: aboutBtn
                text: tr("set_btn_about")
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 280
                Layout.preferredHeight: 44
                onClicked: aboutDialog.open()
                
                background: Rectangle {
                    color: "transparent"
                    radius: 12
                    border.color: aboutBtn.hovered ? "#4da6ff" : "#2a2d3a"
                    border.width: 1
                    Behavior on border.color { ColorAnimation { duration: 200 } }
                }
                contentItem: Label {
                    text: aboutBtn.text
                    color: aboutBtn.hovered ? "white" : "#888899"
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }

    // --- POPUPS ---

    // Scraper Config Popup
    Popup {
        id: configPopup
        anchors.centerIn: parent
        width: 400
        height: contentCol.implicitHeight + 60
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        
        property bool apiKeyVisible: false
        property bool passVisible: false

        onOpened: {
            configPopup.apiKeyVisible = false
            configPopup.passVisible = false
            if (selectedProvider && bridge) {
                if (selectedProvider.id === "screenscraper") {
                    userField.text = bridge.set.getSecret(selectedProvider.id, "user")
                    passField.text = bridge.set.getSecret(selectedProvider.id, "password")
                } else {
                    apiKeyField.text = bridge.set.getSecret(selectedProvider.id, "api_key")
                }
            }
        }
        
        background: Rectangle {
            color: "#1a1c24"
            radius: 20
            border.color: "#303440"
            border.width: 1
        }

        ColumnLayout {
            id: contentCol
            anchors.fill: parent
            anchors.margins: 25
            spacing: 20

            Label {
                text: tr("set_dlg_config_title", (selectedProvider ? selectedProvider.name : ""))
                font.pixelSize: 20
                font.bold: true
                color: "white"
            }

            ColumnLayout {
                spacing: 15
                Layout.fillWidth: true

                // API Key Field (for TGDB, RAWG, SteamGridDB)
                ColumnLayout {
                    visible: selectedProvider && ["tgdb", "rawg", "steamgriddb"].includes(selectedProvider.id)
                    Layout.fillWidth: true
                    spacing: 6
                    Label { text: tr("set_lbl_api_key"); color: "#888899"; font.pixelSize: 12 }
                    TextField {
                        id: apiKeyField
                        Layout.fillWidth: true
                        placeholderText: tr("set_api_placeholder")
                        echoMode: configPopup.apiKeyVisible ? TextInput.Normal : TextInput.Password
                        color: "white"
                        rightPadding: 40
                        background: Rectangle { color: "#0f111a"; radius: 8; border.color: parent.activeFocus ? "#4da6ff" : "#252830" }

                        Label {
                            anchors.right: parent.right
                            anchors.rightMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            text: configPopup.apiKeyVisible ? "H" : "A"
                            font.pixelSize: 14
                            opacity: 0.7
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: configPopup.apiKeyVisible = !configPopup.apiKeyVisible
                            }
                        }
                    }
                }

                // ScreenScraper Specific Fields
                ColumnLayout {
                    visible: selectedProvider && selectedProvider.id === "screenscraper"
                    Layout.fillWidth: true
                    spacing: 15
                    
                    ColumnLayout {
                        spacing: 6
                        Layout.fillWidth: true
                        Label { text: tr("set_lbl_user"); color: "#888899"; font.pixelSize: 12 }
                        TextField {
                            id: userField
                            Layout.fillWidth: true
                            color: "white"
                            background: Rectangle { color: "#0f111a"; radius: 8; border.color: parent.activeFocus ? "#4da6ff" : "#252830" }
                        }
                    }
                    
                    ColumnLayout {
                        spacing: 6
                        Layout.fillWidth: true
                        Label { text: tr("set_lbl_pass"); color: "#888899"; font.pixelSize: 12 }
                        TextField {
                            id: passField
                            Layout.fillWidth: true
                            echoMode: configPopup.passVisible ? TextInput.Normal : TextInput.Password
                            color: "white"
                            rightPadding: 40
                            background: Rectangle { color: "#0f111a"; radius: 8; border.color: parent.activeFocus ? "#4da6ff" : "#252830" }

                            Label {
                                anchors.right: parent.right
                                anchors.rightMargin: 12
                                anchors.verticalCenter: parent.verticalCenter
                                text: configPopup.passVisible ? "H" : "A"
                                font.pixelSize: 14
                                opacity: 0.7
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: configPopup.passVisible = !configPopup.passVisible
                                }
                            }
                        }
                    }
                }
            }

            RowLayout {
                spacing: 12
                Layout.topMargin: 10
                
                Button {
                    text: tr("set_btn_clear")
                    Layout.fillWidth: true
                    onClicked: {
                        if (bridge) bridge.set.clearSecrets(selectedProvider.id)
                        apiKeyField.text = ""
                        userField.text = ""
                        passField.text = ""
                        configPopup.close()
                    }
                    background: Rectangle { color: "#252830"; radius: 10 }
                    contentItem: Label { text: parent.text; color: "#ff4d4d"; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                }

                Button {
                    text: tr("set_btn_save")
                    Layout.fillWidth: true
                    onClicked: {
                        if (bridge) {
                            if (selectedProvider.id === "screenscraper") {
                                bridge.set.saveSecret(selectedProvider.id, "user", userField.text)
                                bridge.set.saveSecret(selectedProvider.id, "password", passField.text)
                            } else {
                                bridge.set.saveSecret(selectedProvider.id, "api_key", apiKeyField.text)
                            }
                        }
                        configPopup.close()
                    }
                    background: Rectangle { color: "#4da6ff"; radius: 10 }
                    contentItem: Label { text: parent.text; color: "black"; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                }
            }
        }
    }

    // --- ABOUT DIALOG ULTIMATE PRESTIGE ---
    Dialog {
        id: aboutDialog
        parent: Overlay.overlay
        anchors.centerIn: parent
        width: 420
        height: 750
        modal: true
        padding: 0
        
        background: Item {
            Rectangle {
                id: dialogBg
                anchors.fill: parent
                color: "#161821"
                radius: 40
                border.color: "#303440"
                border.width: 1
            }

            Rectangle {
                anchors.fill: parent
                radius: 40
                opacity: 0.12
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#4da6ff" }
                    GradientStop { position: 0.5; color: "transparent" }
                    GradientStop { position: 1.0; color: "#7c6ff7" }
                }
            }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 0

            // 1. Logo
            Item {
                Layout.preferredWidth: 80
                Layout.preferredHeight: 80
                Layout.alignment: Qt.AlignHCenter
                Layout.topMargin: 10

                Rectangle {
                    anchors.fill: parent
                    radius: 20
                    color: "#1c1e29"
                    border.color: "#2a2d3a"
                    
                    Image {
                        anchors.fill: parent
                        anchors.margins: 18
                        source: bridge ? bridge.logoPath : ""
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                    }
                }
                
                Rectangle {
                    anchors.centerIn: parent
                    width: 50; height: 50
                    radius: 25
                    color: "#4da6ff"
                    opacity: 0.1
                    z: -1
                }
            }
            
            Item { Layout.preferredHeight: 25 }

            // 2. Título y Versión
            ColumnLayout {
                spacing: 6
                Layout.alignment: Qt.AlignHCenter
                Label {
                    text: bridge ? bridge.appName : "EmuManager"
                    font.pixelSize: 32
                    font.weight: Font.Black
                    font.letterSpacing: -0.5
                    color: "white"
                    Layout.alignment: Qt.AlignHCenter
                    horizontalAlignment: Text.AlignHCenter
                }
                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    width: 40; height: 2; radius: 1; color: "#4da6ff"
                }
                Label {
                    text: tr("app_version", (bridge ? bridge.appVersion : "1.0")).toUpperCase()
                    font.pixelSize: 10
                    font.bold: true
                    font.letterSpacing: 2
                    color: "#666677"
                    Layout.topMargin: 4
                    Layout.alignment: Qt.AlignHCenter
                    horizontalAlignment: Text.AlignHCenter
                }
            }

            Item { Layout.preferredHeight: 30 }

            // 3. Descripción principal
            Label {
                text: tr("set_about_desc")
                wrapMode: Text.WordWrap
                color: "#9da3b4"
                font.pixelSize: 14
                lineHeight: 1.6
                horizontalAlignment: Text.AlignHCenter
                Layout.alignment: Qt.AlignHCenter
                Layout.fillWidth: true
            }

            Item { Layout.preferredHeight: 35 }

            // 4. Secciones de Información
            ColumnLayout {
                spacing: 14
                Layout.fillWidth: true

                // Licencia
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: licCol.implicitHeight + 24
                    radius: 18
                    color: "#0f111a"
                    border.color: "#1d1f2b"
                    
                    ColumnLayout {
                        id: licCol
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 4
                        Label {
                            text: tr("set_about_license_title").toUpperCase()
                            font.pixelSize: 10; font.bold: true; color: "#4da6ff"
                            Layout.alignment: Qt.AlignHCenter
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Label {
                            text: tr("set_about_license")
                            font.pixelSize: 11; color: "#c0c0c0"; wrapMode: Text.WordWrap
                            textFormat: Text.RichText
                            horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true
                            lineHeight: 1.2
                        }
                    }
                }

                // Privacidad
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: privCol.implicitHeight + 24
                    radius: 18
                    color: "#0f111a"
                    border.color: "#1d1f2b"
                    
                    ColumnLayout {
                        id: privCol
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 4
                        Label {
                            text: tr("set_about_privacy_title").toUpperCase()
                            font.pixelSize: 10; font.bold: true; color: "#4da6ff"
                            Layout.alignment: Qt.AlignHCenter
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Label {
                            text: tr("set_about_privacy_desc")
                            font.pixelSize: 11; color: "#c0c0c0"; wrapMode: Text.WordWrap
                            textFormat: Text.RichText
                            horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true
                            lineHeight: 1.2
                        }
                    }
                }
            }

            Item { Layout.fillHeight: true }

            // 5. Copyright y Botón de cierre
            ColumnLayout {
                spacing: 20
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                Layout.bottomMargin: 10
                
                Label {
                    text: tr("set_about_copy")
                    font.pixelSize: 10
                    color: "#444455"
                    Layout.alignment: Qt.AlignHCenter
                    horizontalAlignment: Text.AlignHCenter
                }
                
                Button {
                    id: closeAboutBtn
                    text: tr("set_btn_close").toUpperCase()
                    Layout.preferredWidth: 160
                    Layout.preferredHeight: 46
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: aboutDialog.close()
                    
                    background: Rectangle {
                        color: closeAboutBtn.pressed ? "white" : (closeAboutBtn.hovered ? "#4da6ff" : "transparent")
                        radius: 23
                        border.color: closeAboutBtn.hovered ? "transparent" : "#2a2d3a"
                        border.width: 1
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                    
                    contentItem: Label {
                        text: closeAboutBtn.text
                        color: closeAboutBtn.hovered ? "black" : "white"
                        font.bold: true
                        font.pixelSize: 11
                        font.letterSpacing: 2
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }
    }
}
