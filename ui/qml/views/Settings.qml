import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: settingsRoot

    property var selectedProvider: null

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true
        ScrollBar.vertical.policy: ScrollBar.AsNeeded

        ColumnLayout {
            width: parent.width - 120 // Increasing margins to 60px each side
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.topMargin: 40
            anchors.bottomMargin: 60
            spacing: 40

            // --- HEADER ---
            ColumnLayout {
                spacing: 4
                Label {
                    text: (bridge && bridge.currentLanguage) ? bridge.translate("set_title") : "Settings"
                    font.pixelSize: 32
                    font.bold: true
                    color: "white"
                }
                Label {
                    text: (bridge && bridge.currentLanguage) ? bridge.translate("nav_settings") : "Personalize your experience"
                    font.pixelSize: 14
                    color: "#888899"
                    opacity: 0.8
                }
            }

            // --- SECCIÓN: IDIOMA ---
            ColumnLayout {
                spacing: 16
                Layout.fillWidth: true

                RowLayout {
                    spacing: 10
                    Rectangle { width: 4; height: 18; radius: 2; color: "#4da6ff" }
                    Label {
                        text: bridge ? bridge.translate("set_lang_lbl").toUpperCase() : "IDIOMA"
                        font.pixelSize: 14
                        font.bold: true
                        color: "white"
                        font.letterSpacing: 1
                    }
                }

                ComboBox {
                    id: langCombo
                    model: ["Español", "English"]
                    currentIndex: (bridge && bridge.currentLanguage === "es") ? 0 : 1
                    onActivated: {
                        if (bridge) bridge.changeLanguage(currentIndex === 0 ? "es" : "en")
                    }
                    Layout.preferredWidth: 220
                    Layout.leftMargin: 14

                    delegate: ItemDelegate {
                        width: langCombo.width
                        padding: 12
                        
                        contentItem: RowLayout {
                            spacing: 12
                            Label {
                                text: index === 0 ? "🇪🇸" : "🇺🇸"
                                font.pixelSize: 16
                            }
                            Label {
                                text: modelData
                                color: highlighted ? "white" : "#888899"
                                font.bold: highlighted
                                font.pixelSize: 14
                                Layout.fillWidth: true
                            }
                            Label {
                                text: "✓"
                                color: "#4da6ff"
                                font.bold: true
                                visible: langCombo.currentIndex === index
                            }
                        }
                        
                        background: Rectangle {
                            color: highlighted ? "#252b3d" : "transparent"
                            radius: 8
                        }
                    }

                    indicator: Label {
                        x: langCombo.width - width - 15
                        y: (langCombo.height - height) / 2
                        text: "⌄"
                        font.pixelSize: 18
                        color: "#4da6ff"
                        rotation: langCombo.opened ? 180 : 0
                        Behavior on rotation { NumberAnimation { duration: 200 } }
                    }
                    leftPadding: 16
                    rightPadding: 40

                    contentItem: RowLayout {
                        spacing: 12
                        
                        Label {
                            text: "🌐" // Globe icon
                            font.pixelSize: 16
                        }
                        
                        Label {
                            text: langCombo.displayText
                            font.pixelSize: 14
                            font.bold: true
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    background: Rectangle {
                        implicitWidth: 220
                        implicitHeight: 45
                        radius: 12
                        color: "#1a1c24"
                        border.color: langCombo.activeFocus || langCombo.opened ? "#4da6ff" : "#252830"
                        border.width: 1
                        
                        Rectangle {
                            anchors.fill: parent
                            radius: 12
                            visible: langCombo.hovered
                            color: "#ffffff"
                            opacity: 0.03
                        }
                    }

                    popup: Popup {
                        y: langCombo.height + 5
                        width: langCombo.width
                        implicitHeight: contentItem.implicitHeight + 20
                        padding: 10

                        contentItem: ListView {
                            clip: true
                            implicitHeight: contentHeight
                            model: langCombo.popup.visible ? langCombo.delegateModel : null
                            currentIndex: langCombo.highlightedIndex
                            ScrollIndicator.vertical: ScrollIndicator { }
                        }

                        background: Rectangle {
                            color: "#16181f"
                            radius: 12
                            border.color: "#303440"
                            border.width: 1
                        }
                    }
                }
            }

            // --- SECCIÓN: RUTAS DE EMULADORES ---
            ColumnLayout {
                spacing: 16
                Layout.fillWidth: true

                RowLayout {
                    spacing: 10
                    Rectangle { width: 4; height: 18; radius: 2; color: "#4da6ff" }
                    Label {
                        text: bridge ? bridge.translate("set_paths_section").toUpperCase() : "RUTAS DE EMULADORES"
                        font.pixelSize: 14
                        font.bold: true
                        color: "white"
                        font.letterSpacing: 1
                    }
                }

                ColumnLayout {
                    spacing: 12
                    Layout.fillWidth: true

                    PathSetting {
                        title: (bridge && bridge.currentLanguage) ? bridge.translate("set_emus_title") : "Ruta de Aplicaciones"
                        subtitle: (bridge && bridge.currentLanguage) ? bridge.translate("set_emus_sub") : "Donde se instalan los ejecutables"
                        path: bridge ? bridge.installPath : ""
                        onBrowse: bridge.browseInstallPath()
                    }

                    PathSetting {
                        title: (bridge && bridge.currentLanguage) ? bridge.translate("set_roms_title") : "Ruta de Juegos (ROMs)"
                        subtitle: (bridge && bridge.currentLanguage) ? bridge.translate("set_roms_sub") : "Donde guardas tus bibliotecas"
                        path: bridge ? bridge.romsPath : ""
                        onBrowse: bridge.browseRomsPath()
                    }
                }
            }

            // --- SECCIÓN: CONFIGURACIÓN DE DATOS ---
            ColumnLayout {
                spacing: 16
                Layout.fillWidth: true

                RowLayout {
                    spacing: 10
                    Rectangle { width: 4; height: 18; radius: 2; color: "#4da6ff" }
                    Label {
                        text: bridge ? bridge.translate("set_data_section").toUpperCase() : "CONFIGURACIÓN DE LOS DATOS"
                        font.pixelSize: 14
                        font.bold: true
                        color: "white"
                        font.letterSpacing: 1
                    }
                }
                
                Label {
                    text: bridge ? bridge.translate("set_scrapers_sub") : "Fuentes de información y arte"
                    font.pixelSize: 12
                    color: "#888899"
                    Layout.leftMargin: 14
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0
                    Repeater {
                        model: bridge ? bridge.scraperProviders : []
                        delegate: ProviderCard {
                            Layout.fillWidth: true
                            providerId: modelData.id
                            name: modelData.name
                            type: modelData.type
                            enabled: modelData.enabled
                            onConfigureClicked: {
                                selectedProvider = modelData
                                configPopup.open()
                            }
                        }
                    }
                }
            }

            // --- ABOUT BUTTON ---
            Item { Layout.preferredHeight: 20 }
            
            Button {
                id: aboutBtn
                text: (bridge && bridge.currentLanguage) ? bridge.translate("set_btn_about") : "About EmuManager"
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
            
            Item { Layout.preferredHeight: 40 }
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
                text: (selectedProvider && bridge) ? bridge.translateWithArg("set_dlg_config_title", selectedProvider.name) : ""
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
                    Label { text: bridge ? bridge.translate("set_lbl_api_key") : "API Key"; color: "#888899"; font.pixelSize: 12 }
                    TextField {
                        id: apiKeyField
                        Layout.fillWidth: true
                        placeholderText: "Introducir API Key..."
                        echoMode: TextInput.PasswordEchoOnEdit
                        color: "white"
                        background: Rectangle { color: "#0f111a"; radius: 8; border.color: parent.activeFocus ? "#4da6ff" : "#252830" }
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
                        Label { text: bridge ? bridge.translate("set_lbl_user") : "User"; color: "#888899"; font.pixelSize: 12 }
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
                        Label { text: bridge ? bridge.translate("set_lbl_pass") : "Password"; color: "#888899"; font.pixelSize: 12 }
                        TextField {
                            id: passField
                            Layout.fillWidth: true
                            echoMode: TextInput.Password
                            color: "white"
                            background: Rectangle { color: "#0f111a"; radius: 8; border.color: parent.activeFocus ? "#4da6ff" : "#252830" }
                        }
                    }
                }
            }

            RowLayout {
                spacing: 12
                Layout.topMargin: 10
                
                Button {
                    text: bridge ? bridge.translate("set_btn_clear") : "Clear"
                    Layout.fillWidth: true
                    onClicked: {
                        if (bridge) bridge.clearSecrets(selectedProvider.id)
                        apiKeyField.text = ""
                        userField.text = ""
                        passField.text = ""
                        configPopup.close()
                    }
                    background: Rectangle { color: "#252830"; radius: 10 }
                    contentItem: Label { text: parent.text; color: "#ff4d4d"; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                }

                Button {
                    text: bridge ? bridge.translate("set_btn_save") : "Save"
                    Layout.fillWidth: true
                    onClicked: {
                        if (bridge) {
                            if (selectedProvider.id === "screenscraper") {
                                bridge.saveSecret(selectedProvider.id, "user", userField.text)
                                bridge.saveSecret(selectedProvider.id, "password", passField.text)
                            } else {
                                bridge.saveSecret(selectedProvider.id, "api_key", apiKeyField.text)
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
                    text: "EmuManager"
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
                    text: (bridge && bridge.currentLanguage) ? bridge.translateWithArg("app_version", bridge.appVersion).toUpperCase() : "V1.0"
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
                text: (bridge && bridge.currentLanguage) ? bridge.translate("set_about_desc") : "A premium retro gaming experience managed with elegance."
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
                            text: bridge ? bridge.translate("set_about_license_title").toUpperCase() : "LICENSE"
                            font.pixelSize: 10; font.bold: true; color: "#4da6ff"
                            Layout.alignment: Qt.AlignHCenter
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Label {
                            text: bridge ? bridge.translate("set_about_license") : "Open Source under GNU GPL v3"
                            font.pixelSize: 11; color: "#c0c0c0"; wrapMode: Text.WordWrap
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
                            text: bridge ? bridge.translate("set_about_privacy_title").toUpperCase() : "PRIVACY"
                            font.pixelSize: 10; font.bold: true; color: "#4da6ff"
                            Layout.alignment: Qt.AlignHCenter
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Label {
                            text: bridge ? bridge.translate("set_about_privacy_desc") : "Your data stays on your machine."
                            font.pixelSize: 11; color: "#c0c0c0"; wrapMode: Text.WordWrap
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
                    text: bridge ? bridge.translate("set_about_copy") : "© 2024 ChrisPC"
                    font.pixelSize: 10
                    color: "#444455"
                    Layout.alignment: Qt.AlignHCenter
                    horizontalAlignment: Text.AlignHCenter
                }
                
                Button {
                    id: closeAboutBtn
                    text: (bridge && bridge.currentLanguage) ? bridge.translate("set_btn_close").toUpperCase() : "CLOSE"
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
