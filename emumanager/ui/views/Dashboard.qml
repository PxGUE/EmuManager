import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0
import "../components"

Item {
    id: dashboardRoot
    objectName: "dashboardView"

    MainController { id: controller }
    
    // Propiedades de Estado Real
    property int totalGames: controller.get_games_count()
    property bool hasData: totalGames > 0

    anchors.fill: parent

    // Fondo Profundo
    Rectangle { anchors.fill: parent; color: "#050505" }

    // --- 1. BIENVENIDA ESPECTACULAR (Si la app está vacía) ---
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 40
        visible: !hasData
        
        // El nuevo logo en grande con pulso
        Image {
            source: "../assets/logo.svg"
            Layout.preferredWidth: 280; Layout.preferredHeight: 280
            Layout.alignment: Qt.AlignCenter
            opacity: 0.8
            
            SequentialAnimation on scale {
                loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: 1.03; duration: 3000; easing.type: Easing.InOutQuad }
                NumberAnimation { from: 1.03; to: 1.0; duration: 3000; easing.type: Easing.InOutQuad }
            }
        }

        Column {
            Layout.alignment: Qt.AlignCenter; spacing: 10
            Text {
                text: "EMUMANAGER"
                color: "white"; font.pixelSize: 48; font.bold: true
                font.letterSpacing: 12; anchors.horizontalCenter: parent.horizontalCenter
            }
            Text {
                text: "TU PRÓXIMA AVENTURA COMIENZA AQUÍ"
                color: "#44ffffff"; font.pixelSize: 12; font.bold: true
                font.letterSpacing: 4; anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        Button {
            text: "CONFIGURAR BIBLIOTECA"
            Layout.alignment: Qt.AlignCenter
            font.bold: true; font.letterSpacing: 1
            Material.background: "#16a085"
            onClicked: {
                // Aquí podríamos navegar a Settings o abrir el selector de carpeta
                console.log("Iniciando configuración desde Dashboard")
            }
        }
    }

    // --- 2. CONTENIDO REAL (Si ya hay juegos) ---
    Flickable {
        anchors.fill: parent; visible: hasData
        contentWidth: width; contentHeight: dashboardLayout.height
        clip: true; ScrollBar.vertical: ScrollBar {}

        ColumnLayout {
            id: dashboardLayout
            width: parent.width; anchors.margins: 40
            spacing: 35
            
            // Header con Stats
            RowLayout {
                Layout.fillWidth: true; spacing: 20
                Column {
                    Layout.fillWidth: true; spacing: 5
                    Text { text: "BIENVENIDO DE NUEVO"; color: "#66ffffff"; font.pixelSize: 12; font.bold: true; font.letterSpacing: 2 }
                    Text { text: "Resumen de tu Colección"; color: "white"; font.pixelSize: 28; font.bold: true }
                }
                
                // Card de Stats Rápido
                Rectangle {
                    width: 180; height: 80; radius: 16; color: "#0a0a0c"; border.color: "#16a085"; border.width: 1
                    Column {
                        anchors.centerIn: parent; spacing: 2
                        Text { text: totalGames.toString(); color: "white"; font.pixelSize: 24; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter }
                        Text { text: "JUEGOS TOTALES"; color: "#66ffffff"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1; anchors.horizontalCenter: parent.horizontalCenter }
                    }
                }
            }

            // Aquí irán los widgets de descubrimiento y últimas partidas
            Text { text: "DESCUBRIENDO..."; color: "#22ffffff"; font.pixelSize: 12; font.bold: true; Layout.topMargin: 50 }
        }
    }

    // Auto-update al entrar en la vista
    Component.onCompleted: {
        totalGames = controller.get_games_count()
    }
}
