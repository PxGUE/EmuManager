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
    }
    
    property QtObject controller: mainController

    property string currentRomsPath: "Cargando..."
    property string currentCoresPath: "Cores..."
    property string currentRunnerPath: "Runner..."
    property int gamesCount: 0
    property int activeTab: 0
 
    function updateGamesCount() {
        gamesCount = controller.get_games_count()
    }

    Component.onCompleted: {
        if (controller) {
            currentRomsPath = controller.get_roms_path()
            currentCoresPath = controller.get_cores_path()
            currentRunnerPath = controller.get_runner_path()
            updateGamesCount()
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
            Text { text: "CONFIGURACIÓN"; color: "white"; font.pixelSize: 22; font.bold: true; font.letterSpacing: 2 }
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
                            text: model.title.toUpperCase(); color: "white"
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
        ListElement { title: "General"; iconEmoji: "⚙️" }
        ListElement { title: "Biblioteca"; iconEmoji: "📚" }
        ListElement { title: "Servicios"; iconEmoji: "🌐" }
        ListElement { title: "Avanzado"; iconEmoji: "🥭" }
        ListElement { title: "Acerca de"; iconEmoji: "ℹ️" }
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
            Text { text: "PREFERENCIAS DE SISTEMA"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            SettingsItem { width: parent.width; title: "Idioma Global"; description: "Interfaz en tu idioma"; controlArea: ComboBox { model: ["Español", "English"]; width: 120 } }
            SettingsItem { width: parent.width; title: "Tema Automático"; description: "Sincronizar luz/oscuridad"; controlArea: Switch { checked: true; Material.accent: "#16a085" } }
            Item { Layout.fillHeight: true }
        }

        // --- PANEL 1: BIBLIOTECA ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 25
            Text { text: "RUTAS Y ESCANEO"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            Rectangle {
                width: parent.width; height: 180; radius: 16; color: "#0a0a0c"; border.color: "#33ffffff"; border.width: 1
                Column {
                    anchors.fill: parent; anchors.margins: 20; spacing: 15
                    Row {
                        width: parent.width; spacing: 10
                        Text { text: "ROMS:"; color: "white"; font.bold: true; width: 60; anchors.verticalCenter: parent.verticalCenter }
                        Text { text: currentRomsPath; color: "#16a085"; font.pixelSize: 11; width: parent.width - 160; wrapMode: Text.WrapAnywhere; anchors.verticalCenter: parent.verticalCenter }
                        Button { text: "CAMBIAR"; flat: true; highlighted: true; onClicked: currentRomsPath = controller.select_roms_directory() }
                    }
                    Rectangle { width: parent.width; height: 1; color: "#1a1a1f" }
                    Row {
                        width: parent.width; spacing: 10
                        Text { text: "CORES:"; color: "white"; font.bold: true; width: 60; anchors.verticalCenter: parent.verticalCenter }
                        Text { text: currentCoresPath; color: "#16a085"; font.pixelSize: 11; width: parent.width - 160; wrapMode: Text.WrapAnywhere; anchors.verticalCenter: parent.verticalCenter }
                        Button { text: "CAMBIAR"; flat: true; highlighted: true; onClicked: currentCoresPath = controller.select_cores_directory() }
                    }
                    Rectangle { width: parent.width; height: 1; color: "#1a1a1f" }
                    Row {
                        width: parent.width; spacing: 10
                        Text { text: "RUNNER:"; color: "white"; font.bold: true; width: 60; anchors.verticalCenter: parent.verticalCenter }
                        Text { text: currentRunnerPath; color: "#16a085"; font.pixelSize: 11; width: parent.width - 160; wrapMode: Text.WrapAnywhere; anchors.verticalCenter: parent.verticalCenter }
                        Button { text: "CAMBIAR"; flat: true; highlighted: true; onClicked: currentRunnerPath = controller.select_runner_executable() }
                    }
                }
            }
            Text { text: "INFO DE COLECCIÓN"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2; topPadding: 15 }
            Text { 
                text: "Tienes " + gamesCount + " juegos registrados."; 
                color: "#66ffffff"; font.pixelSize: 11 
            }
            Text { 
                text: "Para actualizar tu biblioteca o descargar medios, dirígete a la sección de DESCARGAS."; 
                color: "#33ffffff"; font.pixelSize: 10; font.italic: true; width: parent.width; wrapMode: Text.WordWrap
            }
            Item { Layout.fillHeight: true }
        }

        // --- PANEL 2: SERVICIOS ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 25
            Text { text: "RECURSOS EXTERNOS"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            Rectangle {
                width: parent.width; height: 260; radius: 16; color: "#0a0a0c"; border.color: "#33ffffff"
                Column {
                    anchors.fill: parent; anchors.margins: 20; spacing: 15
                    Text { text: "SCREEN SCRAPER API"; color: "white"; font.bold: true }
                    Text { 
                        text: "Introduce tus credenciales de ScreenScraper.fr para descargar portadas y metadatos automáticamente."; 
                        color: "#66ffffff"; font.pixelSize: 11; width: parent.width - 40; wrapMode: Text.WordWrap 
                    }
                    TextField { 
                        id: userField; placeholderText: "Usuario"; width: parent.width; 
                        text: controller ? controller.get_api_credential("screenscraper_user") : ""
                        onEditingFinished: if(controller) controller.set_api_credential("screenscraper_user", text) 
                    }
                    TextField { 
                        id: passField; placeholderText: "Contraseña"; echoMode: TextInput.Password; width: parent.width; 
                        text: controller ? controller.get_api_credential("screenscraper_pass") : ""
                        onEditingFinished: if(controller) controller.set_api_credential("screenscraper_pass", text) 
                    }
                }
            }
            Text { 
                text: "Configuración de API guardada. El motor M.A.N.G.O usará estas credenciales al iniciar una sincronización desde la sección de DESCARGAS."; 
                color: "#33ffffff"; font.pixelSize: 10; font.italic: true; width: parent.width; wrapMode: Text.WordWrap
            }
            Item { Layout.fillHeight: true }
        }

        // --- PANEL 3: AVANZADO ---
        Column {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 25
            Text { text: "MOTOR M.A.N.G.O (RUST CORE)"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            Column {
                width: parent.width; spacing: 20
                SettingsItem { width: parent.width; title: "Optimización Multinúcleo"; description: "Usa todos los hilos del CPU para el hashing"; controlArea: Switch { checked: true; Material.accent: "#16a085" } }
                SettingsItem { width: parent.width; title: "Verificación de Integridad"; description: "Comprobar archivos corruptos durante el escaneo"; controlArea: Switch { checked: false; Material.accent: "#16a085" } }
                SettingsItem { width: parent.width; title: "Modo Ultra-Baja Latencia"; description: "Scraping asíncrono optimizado por RUST"; controlArea: Switch { checked: true; Material.accent: "#16a085" } }
                Item { width: 1; height: 10 }
                Button { text: "PURGAR CACHÉ DEL MOTOR"; flat: true; highlighted: true; onClicked: console.log("Purgando caché M.A.N.G.O...") }
            }
            Item { Layout.fillHeight: true }
        }

        // --- PANEL 4: ACERCA DE ---
        Flickable {
            Layout.fillWidth: true; Layout.fillHeight: true
            contentHeight: aboutColumn.height + 100; clip: true
            ScrollBar.vertical: ScrollBar { }
            Column {
                id: aboutColumn; width: parent.width; spacing: 40; anchors.horizontalCenter: parent.horizontalCenter
                Column {
                    width: parent.width; spacing: 15
                    Row { 
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 25
                        Image { source: "../assets/logo.svg"; width: 70; height: 70 }
                        Text { text: "🥭"; font.pixelSize: 45; anchors.verticalCenter: parent.verticalCenter; opacity: 0.9 } 
                    }
                    Text { text: "EMUMANAGER ECOSYSTEM"; color: "white"; font.pixelSize: 22; font.bold: true; font.letterSpacing: 6; anchors.horizontalCenter: parent.horizontalCenter }
                }
                Text { 
                    width: parent.width * 0.85; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; color: "#ccffffff"; font.pixelSize: 12; lineHeight: 1.4; anchors.horizontalCenter: parent.horizontalCenter
                    text: "EmuManager es una interfaz de código abierto diseñada para centralizar y organizar bibliotecas locales de videojuegos. El sistema utiliza <b>M.A.N.G.O Engine</b> para realizar tareas pesadas..."
                }
                Column {
                    width: parent.width * 0.8; spacing: 25; anchors.horizontalCenter: parent.horizontalCenter
                    Column { 
                        width: parent.width
                        spacing: 5
                        Text { text: "LOCAL-FIRST PRIVACY"; color: "#16a085"; font.pixelSize: 9; font.bold: true }
                        Text { width: parent.width; wrapMode: Text.WordWrap; color: "#99ffffff"; font.pixelSize: 11; text: "Tus datos son tuyos. El motor M.A.N.G.O procesa todo localmente." } 
                    }
                    Column { 
                        width: parent.width
                        spacing: 5
                        Text { text: "SOFTWARE LIBRE"; color: "#16a085"; font.pixelSize: 9; font.bold: true } 
                        Text { width: parent.width; wrapMode: Text.WordWrap; color: "#99ffffff"; font.pixelSize: 11; text: "Distribuido bajo la Licencia MIT. EmuManager es y será siempre gratuito." } 
                    }
                }
                Column {
                    width: parent.width; spacing: 5; Text { text: "© 2026 PAIDEX | EMUMANAGER TEAM"; color: "#44ffffff"; font.pixelSize: 10; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter }
                }
            }
        }
    }
}
