import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Models 1.0
import EmuManager.Controllers 1.0
import "../components"

Item {
    id: libraryRoot
    objectName: "libraryView"

    // --- MODELOS DE DATOS REALES ---
    GameListModel { id: gamesModel }
    MainController { 
        id: controller 
    }

    // Estados de la vista
    property string selectedConsole: "all"
    property int totalGames: 0
    property bool isEmpty: totalGames === 0
    property bool isScanning: false
    property real scanProgress: 0.0
    property string scanStatusText: "Iniciando escaneo..."

    // Conexión con las señales reales del backend
    Connections {
        target: controller
        function onScanProgressChanged(p) { scanProgress = p }
        function onScanStatusChanged(s) { scanStatusText = s }
    }

    Component.onCompleted: {
        refreshLibrary()
    }

    function refreshLibrary() {
        gamesModel.update_games()
        totalGames = controller.get_games_count()
    }

    // Fondo
    Rectangle { anchors.fill: parent; color: "#050505" }

    // --- 1. CABECERA DE FILTROS ---
    Item {
        id: consoleFilterArea
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        height: 150; clip: true; visible: !isEmpty && !isScanning
        
        ScrollView {
            anchors.fill: parent; ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            Row {
                anchors.verticalCenter: parent.verticalCenter
                leftPadding: 40; rightPadding: 40; spacing: 15
                ConsoleCard { title: "TODO"; iconEmoji: "🎮"; isSelected: selectedConsole === "all"; onClicked: { selectedConsole = "all"; gamesModel.filter_by_platform("all") } }
                ConsoleCard { title: "SNES"; iconEmoji: "🕹️"; isSelected: selectedConsole === "snes"; onClicked: { selectedConsole = "snes"; gamesModel.filter_by_platform("snes") } }
                ConsoleCard { title: "NES"; iconEmoji: "📺"; isSelected: selectedConsole === "nes"; onClicked: { selectedConsole = "nes"; gamesModel.filter_by_platform("nes") } }
                ConsoleCard { title: "PS1"; iconEmoji: "💿"; isSelected: selectedConsole === "ps1"; onClicked: { selectedConsole = "ps1"; gamesModel.filter_by_platform("ps1") } }
                ConsoleCard { title: "GBA"; iconEmoji: "📱"; isSelected: selectedConsole === "gba"; onClicked: { selectedConsole = "gba"; gamesModel.filter_by_platform("gba") } }
            }
        }
    }

    // --- 2. GRID DE JUEGOS ---
    Flickable {
        id: libraryScroll
        anchors.top: consoleFilterArea.bottom; anchors.bottom: parent.bottom; anchors.left: parent.left; anchors.right: parent.right
        anchors.margins: 40; anchors.topMargin: 10
        visible: !isEmpty && !isScanning; contentWidth: width; contentHeight: libraryGrid.height
        clip: true; ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

        GridLayout {
            id: libraryGrid
            width: parent.width; columns: Math.max(1, Math.floor(width / 220)); rowSpacing: 25; columnSpacing: 25
            Repeater {
                model: gamesModel
                delegate: RomCard {
                    title: model.title; platform: model.platform; coverPath: model.coverPath
                    onClicked: { console.log("Seleccionado: " + model.title) }
                }
            }
        }
    }

    // --- 3. ESTADO DE ESCANEO ACTIVO ---
    Item {
        anchors.fill: parent; visible: isScanning
        ColumnLayout {
            anchors.centerIn: parent; spacing: 25; width: 400
            
            Text { 
                text: "ESCANEANDO BIBLIOTECA"; color: "white"; font.pixelSize: 18; font.bold: true; font.letterSpacing: 2
                Layout.alignment: Qt.AlignCenter 
            }
            
            ProgressBar {
                value: scanProgress; Layout.fillWidth: true; Material.accent: "#16a085"
                Behavior on value { NumberAnimation { duration: 200 } }
            }
            
            Text { 
                text: scanStatusText.toUpperCase(); color: "#66ffffff"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1
                Layout.alignment: Qt.AlignCenter; elide: Text.ElideRight; Layout.preferredWidth: 350; horizontalAlignment: Text.AlignHCenter
            }
        }
    }

    // --- 4. ESTADO VACÍO (Splash de bienvenida) ---
    Item {
        anchors.fill: parent; visible: isEmpty && !isScanning
        ColumnLayout {
            anchors.centerIn: parent; spacing: 30
            Rectangle { 
                Layout.preferredWidth: 100; Layout.preferredHeight: 100; radius: 50; color: "#0a0a0c"
                border.color: "#16a085"; border.width: 1; opacity: 0.4
                Text { anchors.centerIn: parent; text: "📂"; font.pixelSize: 40 }
            }
            Column {
                Layout.alignment: Qt.AlignCenter; spacing: 10
                Text { text: "BIBLIOTECA VACÍA"; color: "white"; font.pixelSize: 22; font.bold: true; font.letterSpacing: 2; anchors.horizontalCenter: parent.horizontalCenter }
                Text { text: "No hemos encontrado juegos en tus carpetas configuradas."; color: "#66ffffff"; font.pixelSize: 13; anchors.horizontalCenter: parent.horizontalCenter }
            }
            Button {
                text: "INICIAR ESCANEO"; flat: true; font.bold: true; font.letterSpacing: 1; Material.accent: "#16a085"
                Layout.alignment: Qt.AlignCenter
                onClicked: {
                    isScanning = true
                    // Usamos un pequeño delay opcional para que la UI cambie de estado visual antes de bloquearse
                    startScanTimer.start()
                }
            }
        }
    }

    Timer {
        id: startScanTimer; interval: 100; running: false; repeat: false
        onTriggered: {
            controller.start_full_scan()
            isScanning = false
            refreshLibrary()
        }
    }
}
