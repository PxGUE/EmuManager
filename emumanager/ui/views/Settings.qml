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
    MainController { 
        id: controller 
        onScanProgressChanged: (p) => { settingsRoot.scanProgressVal = p }
        onScanStatusChanged: (s) => { settingsRoot.scanStatusText = s.toUpperCase() }
        onScanFinished: (n) => { 
            settingsRoot.isScanning = false // RESET INMEDIATO DEL BOTON
            settingsRoot.scanStatusText = "ESCANEO COMPLETADO: " + n + " JUEGOS"
            settingsRoot.scanProgressVal = 1.0
            resetTimer.start()
        }
    }

    Timer {
        id: resetTimer
        interval: 4000
        onTriggered: {
            settingsRoot.scanStatusText = "LISTO"
            settingsRoot.scanProgressVal = 0.0
        }
    }

    property string currentRomsPath: "Cargando..."
    property string currentCoresPath: "Cores..."
    property bool isScanning: false
    property real scanProgressVal: 0.0
    property string scanStatusText: "LISTO"
    property int activeTab: 0

    Component.onCompleted: {
        currentRomsPath = controller.get_roms_path()
        currentCoresPath = controller.get_cores_path()
    }

    // FONDO BASE (Garantiza opacidad inicial)
    Rectangle {
        anchors.fill: parent
        color: "#050505"
        visible: true
    }

    // --- 1. SIDEBAR (Anclado a la izquierda) ---
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

            Text { 
                text: "CONFIGURACIÓN"
                color: "white"; font.pixelSize: 22; font.bold: true; font.letterSpacing: 2
            }

            Item { width: 1; height: 30 } // Espaciador

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

    // --- 2. CONTENIDO (Anclado al resto del espacio) ---
    Item {
        id: contentArea
        anchors.left: sidebarArea.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: 40
        anchors.leftMargin: 20

        // PANELES INDIVIDUALES (Simulación de StackLayout manual para estabilidad)
        
        // --- PANEL: GENERAL ---
        Column {
            anchors.fill: parent; spacing: 25; visible: activeTab === 0
            Text { text: "PREFERENCIAS DE SISTEMA"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            SettingsItem { width: parent.width; title: "Idioma Global"; description: "Interfaz en tu idioma"; controlArea: ComboBox { model: ["Español", "English"]; width: 120 } }
            SettingsItem { width: parent.width; title: "Tema Automático"; description: "Sincronizar luz/oscuridad"; controlArea: Switch { checked: true; Material.accent: "#16a085" } }
        }

        // --- PANEL: BIBLIOTECA ---
        Column {
            anchors.fill: parent; spacing: 25; visible: activeTab === 1
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
                }
            }

            Button {
                width: parent.width; height: 50
                text: settingsRoot.isScanning ? "DETENER ESCANEO" : "SINCRONIZAR BIBLIOTECA"
                enabled: !settingsRoot.isScanning // Por ahora deshabilitar si ya escanea
                Material.background: settingsRoot.isScanning ? "#111" : "#16a085"
                onClicked: { 
                    settingsRoot.isScanning = true
                    settingsRoot.scanStatusText = "INICIANDO..."
                    controller.start_full_scan() 
                }
            }

            Column {
                width: parent.width; spacing: 8
                opacity: (settingsRoot.isScanning || settingsRoot.scanProgressVal > 0) ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: 600 } }
                
                ProgressBar { 
                    width: parent.width; height: 4; value: settingsRoot.scanProgressVal
                    Material.accent: "#16a085" 
                }
                
                Text {
                    width: parent.width; horizontalAlignment: Text.AlignHCenter
                    text: settingsRoot.scanStatusText
                    color: "#66ffffff"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1
                    elide: Text.ElideRight
                }
            }
        }

        // --- PANEL: SERVICIOS ---
        Column {
            anchors.fill: parent; spacing: 25; visible: activeTab === 2
            Text { text: "RECURSOS EXTERNOS"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            Rectangle {
                width: parent.width; height: 180; radius: 16; color: "#0a0a0c"; border.color: "#33ffffff"
                Column {
                    anchors.fill: parent; anchors.margins: 20; spacing: 10
                    Text { text: "SCREEN SCRAPER API"; color: "white"; font.bold: true }
                    TextField { placeholderText: "Usuario"; width: parent.width; onEditingFinished: controller.set_api_credential("screenscraper_user", text) }
                    TextField { placeholderText: "Contraseña"; echoMode: TextInput.Password; width: parent.width; onEditingFinished: controller.set_api_credential("screenscraper_pass", text) }
                }
            }
        }

        // --- PANEL: AVANZADO (M.A.N.G.O Settings) ---
        Column {
            anchors.fill: parent; spacing: 25; visible: activeTab === 3
            Text { text: "MOTOR M.A.N.G.O (RUST CORE)"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            
            Column {
                width: parent.width; spacing: 20
                
                SettingsItem { 
                    width: parent.width; title: "Optimización Multinúcleo"
                    description: "Usa todos los hilos del CPU para el hashing (MD5/CRC32)"
                    controlArea: Switch { checked: true; Material.accent: "#16a085" } 
                }
                
                SettingsItem { 
                    width: parent.width; title: "Verificación de Integridad"
                    description: "Comprobar archivos corruptos durante el escaneo"
                    controlArea: Switch { checked: false; Material.accent: "#16a085" } 
                }

                SettingsItem { 
                    width: parent.width; title: "Modo Ultra-Baja Latencia"
                    description: "Scraping asíncrono optimizado por RUST"
                    controlArea: Switch { checked: true; Material.accent: "#16a085" } 
                }

                Item { width: 1; height: 10 }
                
                Button { 
                    text: "PURGAR CACHÉ DEL MOTOR"
                    flat: true; highlighted: true
                    onClicked: console.log("Purgando caché M.A.N.G.O...")
                }
            }
        }
        // --- PANEL: ACERCA DE (REDESIGN UNIFICADO) ---
        Flickable {
            anchors.fill: parent; visible: activeTab === 4
            contentHeight: aboutColumn.height + 100; clip: true
            ScrollBar.vertical: ScrollBar { }
            
            Column {
                id: aboutColumn; width: parent.width; spacing: 40; anchors.horizontalCenter: parent.horizontalCenter
                
                // 1. HEADER UNIFICADO (El Logo del Ecosistema)
                Column {
                    width: parent.width; spacing: 15
                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter; spacing: 25
                        Image { source: "../assets/logo.svg"; width: 70; height: 70 }
                        Text { text: "🥭"; font.pixelSize: 45; anchors.verticalCenter: parent.verticalCenter; opacity: 0.9 }
                    }
                    Column {
                        width: parent.width; spacing: 5
                        Text { 
                            text: "EMUMANAGER ECOSYSTEM"; color: "white"; font.pixelSize: 22; font.bold: true; font.letterSpacing: 6
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text { 
                            text: "v0.1.0-alpha | Powered by MANGO Native Core"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }

                // 2. DESCRIPCIÓN TÉCNICA (Informativa, no promocional)
                Column {
                    width: parent.width * 0.85; spacing: 10; anchors.horizontalCenter: parent.horizontalCenter
                    Text { 
                        text: "¿QUÉ ES EMUMANAGER?"; color: "#16a085"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2
                        anchors.horizontalCenter: parent.horizontalCenter 
                    }
                    Text { 
                        width: parent.width; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter
                        color: "#ccffffff"; font.pixelSize: 12; lineHeight: 1.4
                        text: "EmuManager es una interfaz de código abierto diseñada para centralizar y organizar bibliotecas locales de videojuegos. El sistema utiliza <b>M.A.N.G.O Engine</b> para realizar tareas pesadas como el cálculo de hashes (MD5/CRC32), la sincronización de archivos y la descarga de metadatos vía API. Todo el proceso está enfocado en la estabilidad del ecosistema local del usuario."
                    }
                }

                // Separador Sutil
                Rectangle { 
                    width: parent.width * 0.6; height: 1; opacity: 0.1
                    anchors.horizontalCenter: parent.horizontalCenter
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "transparent" }
                        GradientStop { position: 0.5; color: "white" }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }

                // 3. COMPROMISO LEGAL Y PRIVACIDAD (Vertical para mejor lectura)
                Column {
                    width: parent.width * 0.8; spacing: 25; anchors.horizontalCenter: parent.horizontalCenter
                    
                    Column {
                        width: parent.width; spacing: 5
                        Text { text: "LOCAL-FIRST PRIVACY"; color: "#16a085"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                        Text { 
                            width: parent.width; wrapMode: Text.WordWrap; color: "#99ffffff"; font.pixelSize: 11; lineHeight: 1.3
                            text: "Tus datos son tuyos. El motor M.A.N.G.O procesa todo localmente. No hay telemetría ni rastreo. La transparencia es nuestro pilar fundamental."
                        }
                    }

                    Column {
                        width: parent.width; spacing: 5
                        Text { text: "SOFTWARE LIBRE"; color: "#16a085"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1 }
                        Text { 
                            width: parent.width; wrapMode: Text.WordWrap; color: "#99ffffff"; font.pixelSize: 11; lineHeight: 1.3
                            text: "Distribuido bajo la Licencia MIT. EmuManager es y será siempre gratuito, abierto a la comunidad para su mejora y auditoría."
                        }
                    }
                }

                Item { width: 1; height: 40 }

                // 4. FOOTER FINAL
                Column {
                    width: parent.width; spacing: 5
                    Text { 
                        text: "© 2026 PAIDEX | EMUMANAGER TEAM"; color: "#44ffffff"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    Text { 
                        text: "Crafted with passion for the Retro Community"; color: "#22ffffff"; font.pixelSize: 9; font.italic: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }
    }
}
