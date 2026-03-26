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

        // --- PANEL 4: ACERCA DE ---
        Flickable {
            Layout.fillWidth: true; Layout.fillHeight: true
            contentHeight: aboutColumn.height + 100; clip: true
            ScrollBar.vertical: ScrollBar { }
            
            Column {
                id: aboutColumn; width: parent.width; spacing: 30; anchors.horizontalCenter: parent.horizontalCenter
                
                // HEADER SECTION (LOGO + VERSION)
                Column {
                    width: parent.width; spacing: 15
                    Item {
                        width: 120; height: 120; anchors.horizontalCenter: parent.horizontalCenter
                        Rectangle {
                            anchors.fill: parent; radius: 30; color: "#0a0a0c"
                            border.color: "#33ffffff"; border.width: 1
                            Image { 
                                source: "../assets/logo.svg"; anchors.fill: parent; anchors.margins: 25; 
                                fillMode: Image.PreserveAspectFit; smooth: true 
                            }
                            Rectangle {
                                width: 20; height: 20; radius: 10; color: "#16a085"; border.color: "white"
                                anchors.bottom: parent.bottom; anchors.right: parent.right
                                anchors.margins: -5
                                ToolTip.text: (systemInfo.is_engine_ready ? "🥭 " : "❌ ") + I18n.t.engine_online
                                ToolTip.visible: statusMa.containsMouse
                                MouseArea { id: statusMa; anchors.fill: parent; hoverEnabled: true }
                            }
                        }
                    }
                    Text { 
                        text: (systemInfo.app_name || "EMUMANAGER").toUpperCase()
                        color: "white"; font.pixelSize: 22; font.bold: true; font.letterSpacing: 6; 
                        anchors.horizontalCenter: parent.horizontalCenter 
                    }
                    Rectangle {
                        width: 120; height: 24; radius: 12; color: "#1a1a1f"
                        anchors.horizontalCenter: parent.horizontalCenter
                        Text { 
                            anchors.centerIn: parent; text: systemInfo.app_version || "v1.0.0"
                            color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1
                        }
                    }
                }

                // DESCRIPTION
                Text { 
                    width: parent.width * 0.9; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter 
                    color: "#ccffffff"; font.pixelSize: 13; lineHeight: 1.5; anchors.horizontalCenter: parent.horizontalCenter
                    text: I18n.t.about_desc
                }

                // GRID DE ESPECIFICACIONES (Glassmorphism inspired)
                Flow {
                    width: parent.width; spacing: 10; Layout.alignment: Qt.AlignHCenter
                    
                    AboutStatCard { 
                        title: I18n.t.os_spec; value: systemInfo.os || "Buscando..."
                        icon: "💻" 
                    }
                    AboutStatCard { 
                        title: I18n.t.engine_spec; value: systemInfo.mango || "M.A.N.G.O Inactivo"
                        valueColor: "#16a085"; icon: "🥭"
                    }
                    AboutStatCard { 
                        title: I18n.t.ram_spec; value: systemInfo.ram || "Detectando..."
                        icon: "🧠" 
                    }
                    AboutStatCard { 
                        title: I18n.t.cpu_spec; value: systemInfo.cpu || "N/A"
                        icon: "⚡" 
                    }
                    AboutStatCard { 
                        title: I18n.t.python_spec; value: systemInfo.python || "N/A"
                        icon: "🐍" 
                    }
                }

                // BARRAS DE ESTADO RAPIDO
                Column {
                    width: parent.width; spacing: 15
                    Rectangle { 
                        width: parent.width; height: 1; color: "#1a1a1f" 
                    }
                    Row {
                        spacing: 20; anchors.horizontalCenter: parent.horizontalCenter
                        Button { 
                            text: I18n.t.contribute_github; width: 180; height: 40; 
                            flat: true; highlighted: true
                            onClicked: Qt.openUrlExternally("https://github.com/PxGUE/EmuManager") 
                        }
                        Button { 
                            text: I18n.t.official_site; width: 150; height: 40; 
                            flat: true; onClicked: Qt.openUrlExternally("https://emumanager.app") 
                        }
                    }
                    Text { 
                        text: I18n.t.copyright; 
                        color: "#44ffffff"; font.pixelSize: 9; font.bold: true; 
                        anchors.horizontalCenter: parent.horizontalCenter 
                    }
                }
            }
        }
    }
}
