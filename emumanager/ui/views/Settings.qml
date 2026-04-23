import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0
import "../components"
import "../components/cards"

Item {
    id: settingsRoot
    objectName: "settingsView"

    // --- LOGICA DE CONTROLADOR ---
    Connections { 
        target: mainController
        function onGamesUpdated() { updateGamesCount() }
        function onLanguage_changed(lang) {
            systemInfo = controller.get_system_info()
        }
    }
    
    property QtObject controller: mainController

    property string currentRomsPath: I18n.t.loading_dots
    property string currentEmulatorsPath: I18n.t.emulators_dots
    property int gamesCount: 0
    property int activeTab: 0
    property var systemInfo: ({})
 
    function updateGamesCount() {
        gamesCount = controller.get_games_count()
    }

    Component.onCompleted: {
        if (controller) {
            currentRomsPath = controller.get_roms_path()
            currentEmulatorsPath = controller.get_emulators_path()
            updateGamesCount()
            systemInfo = controller.get_system_info()
        }
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.viewBackground
        visible: true
    }

    Item {
        id: sidebarArea
        width: 250
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: Theme.spaceExtraLarge

        Column {
            anchors.fill: parent
            spacing: Theme.spaceSmall
            Text { text: I18n.t.settings_title; color: Theme.textMain; font.pixelSize: Theme.fontHeader; font.bold: true; font.letterSpacing: 2 }
            Item { width: 1; height: 30 }
            Repeater {
                model: navModel
                delegate: Rectangle {
                    width: 220; height: 48; radius: Theme.radiusSmall
                    color: activeTab === index ? Theme.controlBackground : Theme.transparent
                    border.color: activeTab === index ? Theme.accentColor : Theme.transparent
                    border.width: activeTab === index ? 1 : 0
                    Row {
                        anchors.fill: parent; anchors.margins: 12; spacing: 15
                        Text { text: model.iconEmoji; font.pixelSize: Theme.fontHeader; opacity: activeTab === index ? 1.0 : 0.4 }
                        Text { 
                            text: (I18n.t[model.key] || "").toUpperCase()
                            color: Theme.textMain
                            font.pixelSize: Theme.fontSmall; font.bold: activeTab === index; font.letterSpacing: 1
                            opacity: activeTab === index ? 1.0 : 0.4 
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                    MouseArea { anchors.fill: parent; onClicked: activeTab = index; cursorShape: Qt.PointingHandCursor }
                }
            }
        }
    }

    ListModel {
        id: navModel
        ListElement { key: "tab_general"; iconEmoji: "⚙️" }
        ListElement { key: "tab_library"; iconEmoji: "📚" }
        ListElement { key: "tab_services"; iconEmoji: "🌐" }
        ListElement { key: "tab_input"; iconEmoji: "🎮" }
        ListElement { key: "tab_about"; iconEmoji: "ℹ️" }
    }

    StackLayout {
        id: contentArea
        anchors.left: sidebarArea.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: Theme.spaceExtraLarge; anchors.leftMargin: Theme.spaceLarge
        currentIndex: activeTab

        // --- PANEL 0: GENERAL ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: Theme.spaceLarge
            Text { text: I18n.t.system_preferences; color: Theme.accentColor; font.pixelSize: Theme.fontSmall; font.bold: true; font.letterSpacing: 2 }
            SettingsItem { 
                width: parent.width; title: I18n.t.global_language; description: I18n.t.global_language_desc
                controlArea: ComboBox { 
                    model: ["Español", "English"]; width: 120;
                    currentIndex: I18n.language === "es" ? 0 : 1
                    onActivated: (index) => {
                        var lang = (index === 0) ? "es" : "en"
                        if (controller) controller.set_language(lang)
                    }
                } 
            }

            Item { Layout.fillHeight: true }
        }

        // --- PANEL 1: BIBLIOTECA ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: Theme.spaceLarge
            Text { text: I18n.t.paths_scanning; color: Theme.accentColor; font.pixelSize: Theme.fontSmall; font.bold: true; font.letterSpacing: 2 }
            Rectangle {
                width: parent.width; height: 180; radius: Theme.radiusMedium; color: Theme.cardBackground; border.color: Theme.cardBorder; border.width: Theme.borderThin
                Column {
                    anchors.fill: parent; anchors.margins: 20; spacing: 15
                    GridLayout {
                        width: parent.width; columns: 3; columnSpacing: 15; rowSpacing: 15
                        
                        // ROW 1: ROMS
                        Text { 
                            text: I18n.t.roms_path + ":"
                            color: Theme.textMain; font.bold: true; font.pixelSize: Theme.fontSmall
                            Layout.alignment: Qt.AlignVCenter
                        }
                        Text { 
                            text: currentRomsPath; color: Theme.accentColor; font.pixelSize: Theme.fontBody
                            Layout.fillWidth: true; elide: Text.ElideRight; maximumLineCount: 1
                            Layout.alignment: Qt.AlignVCenter
                        }
                        Button { 
                            text: I18n.t.change_btn; flat: true; highlighted: true
                            onClicked: currentRomsPath = controller.select_roms_directory() 
                        }

                        // DIVIDER (Spans 3 columns)
                        Rectangle { Layout.columnSpan: 3; Layout.fillWidth: true; height: 1; color: Theme.divider; opacity: 0.3 }

                        // ROW 2: EMULATORS
                        Text { 
                            text: I18n.t.emus_path + ":"
                            color: Theme.textMain; font.bold: true; font.pixelSize: Theme.fontSmall
                            Layout.alignment: Qt.AlignVCenter
                        }
                        Text { 
                            text: currentEmulatorsPath; color: Theme.accentColor; font.pixelSize: Theme.fontBody
                            Layout.fillWidth: true; elide: Text.ElideRight; maximumLineCount: 1
                            Layout.alignment: Qt.AlignVCenter
                        }
                        Button { 
                            text: I18n.t.change_btn; flat: true; highlighted: true
                            onClicked: currentEmulatorsPath = controller.select_cores_directory() 
                        }
                    }
                }
            }
            Text { text: I18n.t.collection_info; color: Theme.accentColor; font.pixelSize: Theme.fontSmall; font.bold: true; font.letterSpacing: 2; topPadding: 15 }
            Text { 
                text: (I18n.t.games_registered || "").arg(gamesCount); 
                color: Theme.textMuted; font.pixelSize: Theme.fontBody 
            }
            Text { 
                text: I18n.t.section_downloads_ref; 
                color: Theme.textMuted; opacity: 0.3; font.pixelSize: Theme.fontSmall; font.italic: true; width: parent.width; wrapMode: Text.WordWrap
            }
            Item { Layout.fillHeight: true }
        }

        // --- PANEL 2: SERVICIOS ---
        ScrollView {
            id: servicesScroll
            Layout.fillWidth: true; Layout.fillHeight: true; clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded
            contentWidth: availableWidth

            Column {
                width: servicesScroll.availableWidth - 20
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: Theme.spaceLarge
                topPadding: 10; bottomPadding: 20
                
                Text { text: I18n.t.external_resources; color: Theme.accentColor; font.pixelSize: Theme.fontSmall; font.bold: true; font.letterSpacing: 2 }
                
                // --- ScreenScraper Section ---
                CollapsibleSection {
                    title: I18n.t.api_screenscraper
                    description: I18n.t.api_desc
                    iconEmoji: "🖼️"
                    expanded: false
                    sectionContent: Column {
                        width: parent.width; spacing: 15
                        TextField { 
                            id: userField; placeholderText: I18n.t.username_placeholder; width: parent.width; 
                            text: controller ? controller.get_api_credential("screenscraper_user") : ""
                            onEditingFinished: if(controller) controller.set_api_credential("screenscraper_user", text) 
                        }
                        TextField { 
                            id: passField; placeholderText: I18n.t.password_placeholder; 
                            echoMode: showPassword ? TextInput.Normal : TextInput.Password; 
                            width: parent.width; 
                            rightPadding: 40
                            text: controller ? controller.get_api_credential("screenscraper_pass") : ""
                            onEditingFinished: if(controller) controller.set_api_credential("screenscraper_pass", text) 
                            
                            property bool showPassword: false

                            Text {
                                text: parent.showPassword ? "👁️" : "🤫"
                                anchors.right: parent.right
                                anchors.rightMargin: 12
                                anchors.verticalCenter: parent.verticalCenter
                                opacity: parent.activeFocus ? 0.9 : 0.4
                                font.pixelSize: 14
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: parent.parent.showPassword = !parent.parent.showPassword
                                }
                                Behavior on opacity { NumberAnimation { duration: 200 } }
                            }
                        }
                    }
                }

                // --- GameTDB Section ---
                CollapsibleSection {
                    title: I18n.t.api_gametdb
                    description: I18n.t.api_gametdb_desc
                    iconEmoji: "🎲"
                    expanded: false
                    sectionContent: Column {
                        width: parent.width; spacing: 15
                        RowLayout {
                            width: parent.width
                            Text { text: I18n.t.gametdb_method; color: Theme.textMain; Layout.fillWidth: true }
                            ComboBox {
                                model: ["Web (Online)", "Local (Offline)"]
                                currentIndex: (controller && controller.get_api_credential("gametdb_mode") === "local") ? 1 : 0
                                onActivated: (index) => {
                                    if(controller) controller.set_api_credential("gametdb_mode", index === 0 ? "web" : "local")
                                }
                            }
                        }
                    }
                }

                // --- Discord Presence ---
                CollapsibleSection {
                    title: I18n.t.discord_presence
                    description: I18n.t.discord_presence_desc
                    iconEmoji: "🎮"
                    expanded: false
                    sectionContent: RowLayout {
                        width: parent.width; spacing: 15
                        Text { text: I18n.t.discord_presence; color: Theme.textMain; font.bold: true; Layout.fillWidth: true }
                        Switch {
                            checked: controller ? controller.get_api_credential("discord_rpc") === "true" : true
                            onToggled: {
                                if(controller) controller.set_api_credential("discord_rpc", checked ? "true" : "false")
                            }
                        }
                    }
                }

                Text { 
                    text: I18n.t.api_saved; 
                    color: Theme.textMuted; opacity: 0.5; font.pixelSize: Theme.fontSmall; font.italic: true; width: parent.width; wrapMode: Text.WordWrap
                }
                Item { Layout.preferredHeight: 50; width: 1 } // Bottom padding
            }
        }

        // --- PANEL 3: MANDO E INPUT ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: Theme.spaceLarge
            Text { text: I18n.t.tab_input_settings.toUpperCase(); color: Theme.accentColor; font.pixelSize: Theme.fontSmall; font.bold: true; font.letterSpacing: 2 }
            
            // 1. LISTA DE DISPOSITIVOS
            Rectangle {
                width: parent.width; height: 120; radius: Theme.radiusMedium
                color: Theme.cardBackground; border.color: Theme.cardBorder; border.width: Theme.borderThin
                
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 20; spacing: 10
                    Text { text: I18n.t.detected_devices; color: Theme.textMuted; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                    
                    RowLayout {
                        Layout.fillWidth: true; spacing: 15
                        Rectangle {
                            width: 48; height: 48; radius: 12; color: Theme.controlBackground
                            Text { text: "🎮"; anchors.centerIn: parent; font.pixelSize: 24; opacity: gamepadController.get_devices().length > 0 ? 1.0 : 0.2 }
                        }
                        
                        ColumnLayout {
                            spacing: 2
                            Text { 
                                text: gamepadController.get_devices().length > 0 ? gamepadController.get_devices()[0] : I18n.t.no_devices_detected
                                color: Theme.textMain; font.pixelSize: 16; font.bold: true 
                            }
                            Text { 
                                text: gamepadController.get_devices().length > 0 ? "ESTADO: ACTIVO" : "ESTADO: ESPERANDO HARDWARE"
                                color: gamepadController.get_devices().length > 0 ? Theme.statusSuccess : Theme.textMuted
                                font.pixelSize: 10; font.bold: true; font.letterSpacing: 1
                            }
                        }
                    }
                }
            }

            // 2. CONFIGURACIÓN TÉCNICA
            SettingsItem {
                width: parent.width
                title: I18n.t.deadzone_label
                description: "Ajusta el área muerta de los sticks analógicos para corregir el drift."
                controlArea: RowLayout {
                    spacing: 15
                    Slider {
                        id: deadzoneSlider
                        from: 0.1; to: 0.9; value: gamepadController.get_deadzone()
                        Layout.preferredWidth: 200
                        onMoved: {
                            gamepadController.set_deadzone(value)
                        }
                    }
                    Text { text: Math.round(deadzoneSlider.value * 100) + "%"; color: Theme.accentColor; font.bold: true; font.pixelSize: 14 }
                }
            }

            // 3. MONITOR DE INPUTS (PREMIUM UI)
            Text { text: I18n.t.input_monitoring; color: Theme.accentColor; font.pixelSize: Theme.fontSmall; font.bold: true; font.letterSpacing: 2; topPadding: 15 }
            
            Rectangle {
                width: parent.width; height: 100; radius: Theme.radiusMedium
                color: Theme.panelBackground; opacity: 0.5; border.color: Theme.cardBorder; border.width: 1
                
                RowLayout {
                    anchors.centerIn: parent; spacing: 20
                    property string lastKey: ""
                    
                    Connections {
                        target: gamepadController
                        function onButtonPressed(key) {
                            parent.lastKey = key
                            keyAnim.restart()
                        }
                    }

                    Rectangle {
                        width: 60; height: 60; radius: 30; color: Theme.accentColor; opacity: 0.1
                        Text { 
                            id: keyDisplay; anchors.centerIn: parent; text: parent.parent.lastKey || "--"
                            color: Theme.accentColor; font.pixelSize: 24; font.bold: true 
                        }
                        
                        NumberAnimation { id: keyAnim; target: keyDisplay; property: "scale"; from: 1.5; to: 1.0; duration: 200; easing.type: Easing.OutBack }
                    }
                    
                    Text { 
                        text: I18n.t.gamepad_test_hint; 
                        color: Theme.textMuted; font.pixelSize: 12; font.italic: true 
                    }
                }
            }

            Item { Layout.fillHeight: true }
        }



        // --- PANEL 4: ACERCA DE (RADICAL MINIMALIST IDENTITY) ---
        Item {
            Layout.fillWidth: true; Layout.fillHeight: true
            
            ColumnLayout {
                id: aboutContent
                width: parent.width - 100; anchors.centerIn: parent
                spacing: 50
                
                // --- 1. THE KINETIC CORE ---
                ColumnLayout {
                    Layout.alignment: Qt.AlignHCenter; spacing: 20
                    
                    Item {
                        Layout.alignment: Qt.AlignHCenter; width: 120; height: 120
                        Rectangle { anchors.centerIn: parent; width: 100; height: 100; radius: 50; color: Theme.transparent; border.color: Theme.accentElectric; border.width: 1.5; opacity: 0.2 }
                        Rectangle {
                            anchors.centerIn: parent; width: 110; height: 110; radius: 18
                            color: Theme.transparent; border.color: Theme.accentElectric; border.width: 1.5; opacity: 0.1
                            RotationAnimation on rotation { from: 0; to: 360; duration: 15000; loops: Animation.Infinite }
                        }
                        Image { 
                            source: "../assets/logo.svg"; anchors.fill: parent; anchors.margins: 25; 
                            fillMode: Image.PreserveAspectFit; smooth: true
                        }
                    }
                    
                    ColumnLayout {
                        spacing: 4; Layout.alignment: Qt.AlignHCenter
                        Text { 
                            text: I18n.t.app_name; color: Theme.textMain; font.pixelSize: 48; font.weight: Font.Black; font.letterSpacing: -2 
                        }
                        Text { 
                            Layout.alignment: Qt.AlignHCenter
                            text: mainController ? I18n.tp("app_version_label|" + mainController.appVersion) : ""
                            color: Theme.accentElectric; font.pixelSize: 14; font.bold: true; font.letterSpacing: 6; opacity: 0.8
                        }
                    }
                }

                // --- 2. PROFESSIONAL STATEMENT ---
                Text { 
                    Layout.fillWidth: true; Layout.preferredWidth: 500; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap; lineHeight: 1.6
                    color: Theme.textMain; opacity: 0.7; font.pixelSize: 16; font.letterSpacing: 0.2
                    text: I18n.t.about_statement
                }

                // --- 3. DYNAMIC LINKS ---
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter; spacing: 30
                    
                    // GitHub Link
                    Rectangle {
                        width: 160; height: 40; radius: 20; color: Theme.transparent; border.color: Qt.alpha(Theme.accentElectric, 0.3); border.width: 1
                        Text { anchors.centerIn: parent; text: I18n.t.btn_source_code; color: Theme.accentElectric; font.pixelSize: 9; font.bold: true; font.letterSpacing: 2 }
                        MouseArea { anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onEntered: parent.opacity = 1.0; onExited: parent.opacity = 0.6; onClicked: Qt.openUrlExternally("https://github.com/PxGUE/EmuManager") }
                    }

                    // Engine Link
                    Rectangle {
                        width: 160; height: 40; radius: 20; color: Theme.transparent; border.color: Qt.alpha(Theme.accentElectric, 0.3); border.width: 1
                        Text { anchors.centerIn: parent; text: I18n.t.btn_mango_core; color: Theme.accentElectric; font.pixelSize: 9; font.bold: true; font.letterSpacing: 2 }
                        MouseArea { anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onEntered: parent.opacity = 1.0; onExited: parent.opacity = 0.6; onClicked: Qt.openUrlExternally("https://github.com/PxGUE/mango") }
                    }
                }

                // --- 4. ENGINE FOOTER ---
                Text { 
                    Layout.alignment: Qt.AlignHCenter; text: mainController ? I18n.t.powered_by.arg(mainController.mangoVersion) : ""; 
                    color: Theme.textMuted; opacity: 0.3; font.pixelSize: 9; font.bold: true; font.letterSpacing: 3 
                }
            }
        }
    }
}
