import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0
import "../components"

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

    property string currentRomsPath: "Cargando..."
    property string currentEmulatorsPath: "Emuladores..."
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
        color: "#050505"
        visible: true
    }

    Item {
        id: sidebarArea
        width: 250
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: 40

        Column {
            anchors.fill: parent
            spacing: 10
            Text { text: I18n.t.settings_title; color: "white"; font.pixelSize: 22; font.bold: true; font.letterSpacing: 2 }
            Item { width: 1; height: 30 }
            Repeater {
                model: navModel
                delegate: Rectangle {
                    width: 220; height: 48; radius: 10
                    color: activeTab === index ? "#1a1a1f" : "transparent"
                    border.color: activeTab === index ? "#16a085" : "transparent"
                    border.width: activeTab === index ? 1 : 0
                    Row {
                        anchors.fill: parent; anchors.margins: 12; spacing: 15
                        Text { text: model.iconEmoji; font.pixelSize: 16; opacity: activeTab === index ? 1.0 : 0.4 }
                        Text { 
                            text: (I18n.t[model.key] || "").toUpperCase()
                            color: "white"
                            font.pixelSize: 10; font.bold: activeTab === index; font.letterSpacing: 1
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
        ListElement { key: "tab_advanced"; iconEmoji: "🥭" }
        ListElement { key: "tab_about"; iconEmoji: "ℹ️" }
    }

    StackLayout {
        id: contentArea
        anchors.left: sidebarArea.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: 40; anchors.leftMargin: 20
        currentIndex: activeTab

        // --- PANEL 0: GENERAL ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 25
            Text { text: I18n.t.system_preferences; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
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
            SettingsItem { width: parent.width; title: I18n.t.auto_theme; description: I18n.t.auto_theme_desc; controlArea: Switch { checked: true; Material.accent: "#16a085" } }
            Item { Layout.fillHeight: true }
        }

        // --- PANEL 1: BIBLIOTECA ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 25
            Text { text: I18n.t.paths_scanning; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            Rectangle {
                width: parent.width; height: 180; radius: 16; color: "#0a0a0c"; border.color: "#33ffffff"; border.width: 1
                Column {
                    anchors.fill: parent; anchors.margins: 20; spacing: 15
                    Row {
                        width: parent.width; spacing: 10
                        Text { text: I18n.t.roms_path + ":"; color: "white"; font.bold: true; width: 100; font.pixelSize: 9; anchors.verticalCenter: parent.verticalCenter }
                        Text { text: currentRomsPath; color: "#16a085"; font.pixelSize: 11; width: parent.width - 200; wrapMode: Text.WrapAnywhere; anchors.verticalCenter: parent.verticalCenter }
                        Button { text: I18n.t.change_btn; flat: true; highlighted: true; onClicked: currentRomsPath = controller.select_roms_directory() }
                    }
                    Rectangle { width: parent.width; height: 1; color: "#1a1a1f" }
                    Row {
                        width: parent.width; spacing: 10
                        Text { text: I18n.t.emus_path + ":"; color: "white"; font.bold: true; width: 100; font.pixelSize: 9; anchors.verticalCenter: parent.verticalCenter }
                        Text { text: currentEmulatorsPath; color: "#16a085"; font.pixelSize: 11; width: parent.width - 200; wrapMode: Text.WrapAnywhere; anchors.verticalCenter: parent.verticalCenter }
                        Button { text: I18n.t.change_btn; flat: true; highlighted: true; onClicked: currentEmulatorsPath = controller.select_cores_directory() }
                    }
                }
            }
            Text { text: I18n.t.collection_info; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2; topPadding: 15 }
            Text { 
                text: (I18n.t.games_registered || "").arg(gamesCount); 
                color: "#66ffffff"; font.pixelSize: 11 
            }
            Text { 
                text: I18n.t.section_downloads_ref; 
                color: "#33ffffff"; font.pixelSize: 10; font.italic: true; width: parent.width; wrapMode: Text.WordWrap
            }
            Item { Layout.fillHeight: true }
        }

        // --- PANEL 2: SERVICIOS ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 25
            Text { text: I18n.t.external_resources; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            Rectangle {
                width: parent.width; height: 260; radius: 16; color: "#0a0a0c"; border.color: "#33ffffff"
                Column {
                    anchors.fill: parent; anchors.margins: 20; spacing: 15
                    Text { text: I18n.t.api_screenscraper; color: "white"; font.bold: true }
                    Text { 
                        text: I18n.t.api_desc; 
                        color: "#66ffffff"; font.pixelSize: 11; width: parent.width - 40; wrapMode: Text.WordWrap 
                    }
                    TextField { 
                        id: userField; placeholderText: I18n.t.username_placeholder; width: parent.width; 
                        text: controller ? controller.get_api_credential("screenscraper_user") : ""
                        onEditingFinished: if(controller) controller.set_api_credential("screenscraper_user", text) 
                    }
                    TextField { 
                        id: passField; placeholderText: I18n.t.password_placeholder; echoMode: TextInput.Password; width: parent.width; 
                        text: controller ? controller.get_api_credential("screenscraper_pass") : ""
                        onEditingFinished: if(controller) controller.set_api_credential("screenscraper_pass", text) 
                    }
                }
            }
            Text { 
                text: I18n.t.api_saved; 
                color: "#33ffffff"; font.pixelSize: 10; font.italic: true; width: parent.width; wrapMode: Text.WordWrap
            }
            Item { Layout.fillHeight: true }
        }

        // --- PANEL 3: AVANZADO ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 25
            Text { text: I18n.t.mango_engine; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            Column {
                width: parent.width; spacing: 20
                SettingsItem { width: parent.width; title: I18n.t.opt_multicore; description: I18n.t.opt_multicore_desc; controlArea: Switch { checked: true; Material.accent: "#16a085" } }
                SettingsItem { width: parent.width; title: I18n.t.opt_integrity; description: I18n.t.opt_integrity_desc; controlArea: Switch { checked: false; Material.accent: "#16a085" } }
                SettingsItem { width: parent.width; title: I18n.t.opt_low_latency; description: I18n.t.opt_low_latency_desc; controlArea: Switch { checked: true; Material.accent: "#16a085" } }
                Item { width: 1; height: 10 }
                Button { text: I18n.t.purge_cache; flat: true; highlighted: true; onClicked: console.log("Purgando caché M.A.N.G.O...") }
            }
            Item { Layout.fillHeight: true }
        }

        // --- PANEL 4: ACERCA DE (DESIGN REFEDINED - MINIMALIST PREMIUM) ---
        Flickable {
            Layout.fillWidth: true; Layout.fillHeight: true
            contentHeight: aboutContent.height + 60; clip: true
            ScrollBar.vertical: ScrollBar { }
            
            ColumnLayout {
                id: aboutContent
                width: parent.width - 80; anchors.horizontalCenter: parent.horizontalCenter
                spacing: 30
                
                Item { Layout.preferredHeight: 40 }

                // LOGO & TITLE
                ColumnLayout {
                    Layout.alignment: Qt.AlignHCenter; spacing: 10
                    
                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter; width: 100; height: 100; radius: 25; color: "#0a0a0c"; border.color: "#1a1a1f"
                        Image { 
                            source: "../assets/logo.svg"; anchors.fill: parent; anchors.margins: 20; 
                            fillMode: Image.PreserveAspectFit; smooth: true; opacity: 0.9
                        }
                    }
                    
                    Text { 
                        Layout.alignment: Qt.AlignHCenter
                        text: "EmuManager"
                        color: "white"; font.pixelSize: 32; font.bold: true; font.letterSpacing: -1
                    }
                    
                    Text { 
                        Layout.alignment: Qt.AlignHCenter
                        text: "v0.1.3 - alpha"; color: "#66ffffff"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2
                    }
                }

                // POWERED BY TAGLINE
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter; spacing: 12
                    Rectangle { Layout.preferredWidth: 40; Layout.preferredHeight: 1; color: "#1a1a1f" }
                    Text { 
                        text: "POWERED BY M.A.N.G.O v0.2.5"; color: "#16a085"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 3 
                    }
                    Rectangle { Layout.preferredWidth: 40; Layout.preferredHeight: 1; color: "#1a1a1f" }
                }

                // OVERVIEW DESCRIPTION
                Text { 
                    Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap; lineHeight: 1.6
                    color: "#ccffffff"; font.pixelSize: 14
                    text: I18n.t.about_desc
                }

                // STATUS PILLS (FOSS & PRIVACY)
                Row {
                    Layout.alignment: Qt.AlignHCenter; spacing: 15
                    
                    Rectangle {
                        height: 32; width: 140; radius: 16; color: "#0a0a0c"; border.color: "#16a085"; border.width: 1; opacity: 0.8
                        Row { anchors.centerIn: parent; spacing: 8
                            Text { text: "🔓"; font.pixelSize: 12 }
                            Text { text: I18n.t.pill_free_open; color: "white"; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1 }
                        }
                    }
                    Rectangle {
                        height: 32; width: 140; radius: 16; color: "#0a0a0c"; border.color: "#3a7bd5"; border.width: 1; opacity: 0.8
                        Row { anchors.centerIn: parent; spacing: 8
                            Text { text: "🛡️"; font.pixelSize: 12 }
                            Text { text: I18n.t.pill_local_privacy; color: "white"; font.pixelSize: 8; font.bold: true; font.letterSpacing: 1 }
                        }
                    }
                }

                Item { Layout.preferredHeight: 20 }

                // TECHNICAL SPECS GRID
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 15
                    Text { 
                        text: I18n.t.tech_system_specs; color: "#66ffffff"; font.pixelSize: 8; font.bold: true; font.letterSpacing: 2
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    GridLayout {
                        columns: 3; columnSpacing: 15; rowSpacing: 15; Layout.alignment: Qt.AlignHCenter
                        
                        AboutStatCard { 
                            title: I18n.t.os_spec; value: systemInfo.os || "Buscando..."; icon: "💻" 
                            width: 180; height: 65; border.color: "#1a1a1f"
                        }
                        AboutStatCard { 
                            title: I18n.t.cpu_spec; value: (systemInfo.cpu_threads || "?") + " " + I18n.t.tech_threads; icon: "📟" 
                            width: 180; height: 65; border.color: "#1a1a1f"
                        }
                        AboutStatCard { 
                            title: I18n.t.ram_spec; value: systemInfo.ram || "Detectando..."; icon: "🧠" 
                            width: 180; height: 65; border.color: "#1a1a1f"
                        }
                        AboutStatCard { 
                            title: I18n.t.python_spec; value: "v" + systemInfo.python; icon: "🐍" 
                            width: 180; height: 65; border.color: "#1a1a1f"
                        }
                        AboutStatCard { 
                            title: I18n.t.engine_spec; value: systemInfo.is_engine_ready ? I18n.t.tech_engine_ready : I18n.t.tech_inactive; 
                            valueColor: systemInfo.is_engine_ready ? "#16a085" : "#e74c3c"; icon: "🥭"
                            width: 180; height: 65; border.color: "#1a1a1f"
                        }
                    }
                }

                Item { Layout.preferredHeight: 20 }
                
                Text { 
                    Layout.alignment: Qt.AlignHCenter; text: I18n.t.copyright; color: "#22ffffff"; font.pixelSize: 9; font.bold: true 
                }
            }
        }
    }
}
