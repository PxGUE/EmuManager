import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import EmuManager.Controllers 1.0
import "../components"

Item {
    id: settingsRoot
    objectName: "settingsView"

    // --- MOTOR DEL CONTROLADOR ---
    MainController { id: controller }

    // Propiedades de Estado para Rutas (Actualización en Tiempo Real)
    property string currentRomsPath: "Cargando..."
    property string currentCoresPath: "Cargando..."

    Component.onCompleted: {
        currentRomsPath = controller.get_roms_path()
        currentCoresPath = controller.get_cores_path()
    }

    // Fondo base
    Rectangle {
        anchors.fill: parent
        color: "#050505"
    }

    // --- SCROLL PRINCIPAL ---
    ScrollView {
        id: mainScroll
        anchors.fill: parent
        anchors.leftMargin: 40; anchors.rightMargin: 40; anchors.topMargin: 40
        clip: true; ScrollBar.vertical.policy: ScrollBar.AsNeeded

        Column {
            width: mainScroll.width - 20; spacing: 50

            // 1. BANNER DE TÍTULO
            Column {
                width: parent.width; spacing: 10
                Text { text: "CONFIGURACIÓN"; color: "white"; font.pixelSize: 32; font.bold: true; font.letterSpacing: 2 }
                Text { text: "Personaliza tu motor de emulación y servicios externos."; color: "#55ffffff"; font.pixelSize: 14; font.bold: true }
            }

            // 2. SECCIÓN: RUTAS (TARJETA VERDE)
            Rectangle {
                width: parent.width; height: contentPaths.implicitHeight + 40
                radius: 15; color: "#0a0a0c"; border.color: "#16a085"; border.width: 1; opacity: 0.95
                
                ColumnLayout {
                    id: contentPaths
                    anchors.fill: parent; anchors.margins: 25; spacing: 5
                    Text { text: "BIBLIOTECAS Y RUTAS"; color: "#16a085"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2; Layout.bottomMargin: 15 }
                    
                    SettingsItem { 
                        Layout.fillWidth: true; accentColor: "#16a085"; iconEmoji: "📂"; showArrow: true 
                        title: "Ruta de ROMs"
                        description: "Actual: " + currentRomsPath
                        
                        MouseArea {
                            anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                            onClicked: currentRomsPath = controller.select_roms_directory()
                        }
                    }

                    SettingsItem { 
                        Layout.fillWidth: true; accentColor: "#16a085"; iconEmoji: "🧩"; showArrow: true 
                        title: "Núcleos Libretro"
                        description: "Actual: " + currentCoresPath

                        MouseArea {
                            anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                            onClicked: currentCoresPath = controller.select_cores_directory()
                        }
                    }
                }
            }

            // 3. SECCIÓN: SERVICIOS (TARJETA MORADA)
            Rectangle {
                width: parent.width; height: contentAPIs.implicitHeight + 40
                radius: 15; color: "#0a0a0c"; border.color: "#4f319b"; border.width: 1; opacity: 0.95
                
                ColumnLayout {
                    id: contentAPIs
                    anchors.fill: parent; anchors.margins: 25; spacing: 5
                    Text { text: "SERVICIOS EXTERNOS"; color: "#4f319b"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2; Layout.bottomMargin: 15 }
                    SettingsItem { Layout.fillWidth: true; accentColor: "#4f319b"; iconEmoji: "🖼️"; title: "ScreenScraper"; description: "Metadata y arte para tu colección." }
                    SettingsItem { Layout.fillWidth: true; accentColor: "#4f319b"; iconEmoji: "🏆"; title: "RetroAchievements"; description: "Activa los logros mundiales para juegos retro." }
                }
            }

            // 4. SECCIÓN: INTERFAZ (TARJETA AZUL)
            Rectangle {
                width: parent.width; height: contentUI.implicitHeight + 40
                radius: 15; color: "#0a0a0c"; border.color: "#2980b9"; border.width: 1; opacity: 0.95
                
                ColumnLayout {
                    id: contentUI
                    anchors.fill: parent; anchors.margins: 25; spacing: 5
                    Text { text: "APARIENCIA Y LENGUAJE"; color: "#2980b9"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2; Layout.bottomMargin: 15 }
                    SettingsItem { 
                        Layout.fillWidth: true; accentColor: "#2980b9"; iconEmoji: "🌎"; title: "Idioma del Sistema"; description: "Cambia el idioma global de EmuManager."
                        controlArea: ComboBox {
                            currentIndex: 0; model: ["Español", "English"]
                        }
                    }
                    SettingsItem { Layout.fillWidth: true; accentColor: "#2980b9"; iconEmoji: "🎨"; title: "Color de Acento"; description: "Personaliza el tono visual." }
                }
            }

            // 5. SECCIÓN: SISTEMA (TARJETA NARANJA)
            Rectangle {
                width: parent.width; height: contentSys.implicitHeight + 40
                radius: 15; color: "#0a0a0c"; border.color: "#e67e22"; border.width: 1; opacity: 0.95
                
                ColumnLayout {
                    id: contentSys
                    anchors.fill: parent; anchors.margins: 25; spacing: 5
                    Text { text: "SISTEMA"; color: "#e67e22"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2; Layout.bottomMargin: 15 }
                    SettingsItem { 
                        Layout.fillWidth: true; accentColor: "#e67e22"; iconEmoji: "⚡"; title: "Descargas Automáticas"; description: "Gestión autónoma de recursos."
                        controlArea: Switch { checked: true; Material.accent: "#e67e22" }
                    }
                }
            }
            Item { height: 60; width: 1 } 
        }
    }
}
