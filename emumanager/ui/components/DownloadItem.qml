import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects

Rectangle {
    id: downloadItem
    
    property int itemIndex: -1
    property string itemName: ""
    property string itemType: "" // CORE, EMULATOR, ASSET, MEDIA
    property string platform: ""
    property real progressValue: 0.0
    property string totalSize: ""
    property string statusText: ""
    property string downloadSpeed: ""
    property color accentColor: "#16a085"
    property string eta: "Calculando..."
    property string lastLog: ""
    property bool isPaused: statusText === "Pausado"

    signal pauseRequested(int index)
    signal resumeRequested(int index)
    signal cancelRequested(int index)
    signal openFolderRequested(int index)

    height: 110
    radius: 20
    color: "#0a0a0c"
    border.color: progressValue > 0 && progressValue < 1 ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.2) : "#1a1a1f"
    border.width: 1
    clip: true

    // --- EFECTO GLASSMORPHISM DE FONDO ---
    Rectangle {
        anchors.fill: parent
        color: progressValue >= 1.0 ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.03) : "transparent"
        Behavior on color { ColorAnimation { duration: 500 } }
    }

    // --- CONTENIDO PRINCIPAL ---
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 18

            // 1. Icono de Estado con Brillo
            Rectangle {
                width: 50; height: 50; radius: 14
                color: "#16161a"
                border.color: "#25252b"; border.width: 1
                
                Text {
                    anchors.centerIn: parent
                    text: {
                        if (itemType === "CORE") return "🧩"
                        if (itemType === "EMULATOR") return "🖥️"
                        if (itemType === "MEDIA") return "🖼️"
                        return "📦"
                    }
                    font.pixelSize: 24
                    opacity: progressValue >= 1.0 ? 1.0 : 0.7
                }

                Rectangle {
                    anchors.fill: parent; radius: 14; opacity: 0.1
                    color: isPaused ? "#f1c40f" : accentColor
                    visible: progressValue > 0 && progressValue < 1.0
                }
            }

            // 2. Info de Tarea
            ColumnLayout {
                Layout.fillWidth: true; spacing: 2
                
                RowLayout {
                    spacing: 10
                    Text {
                        text: itemName.toUpperCase()
                        color: "white"; font.pixelSize: 14; font.bold: true; font.letterSpacing: 1
                    }
                    Rectangle {
                        width: 40; height: 16; radius: 4; color: "#1a1a1f"
                        Text { anchors.centerIn: parent; text: platform; color: accentColor; font.pixelSize: 8; font.bold: true }
                        visible: platform !== "" && platform !== "ALL"
                    }
                }
                
                RowLayout {
                    spacing: 8
                    Text {
                        text: isPaused ? "PAUSADO" : (progressValue >= 1.0 ? "✓ COMPLETADO" : (statusText + " • " + downloadSpeed))
                        color: isPaused ? "#f1c40f" : (progressValue >= 1.0 ? "#16a085" : "#66ffffff")
                        font.pixelSize: 10; font.bold: true
                    }
                    Text {
                        text: "ETA: " + eta
                        color: "#33ffffff"; font.pixelSize: 9; visible: progressValue > 0 && progressValue < 1.0 && !isPaused
                    }
                }
            }

            // 3. CONTROLES DE INTERACCIÓN REAL
            RowLayout {
                spacing: 2
                
                // Botón Acción Primaria (Pausa/Resumen)
                Button {
                    visible: progressValue < 1.0
                    flat: true; Layout.preferredWidth: 36; Layout.preferredHeight: 36
                    contentItem: Text { 
                        text: isPaused ? "▶" : "⏸"; color: isPaused ? "#16a085" : "white"
                        font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                        opacity: 0.8
                    }
                    onClicked: {
                        if (isPaused) resumeRequested(itemIndex)
                        else pauseRequested(itemIndex)
                    }
                }

                // Botón Cancelar
                Button {
                    visible: progressValue < 1.0
                    flat: true; Layout.preferredWidth: 36; Layout.preferredHeight: 36
                    contentItem: Text { 
                        text: "✕"; color: "#e74c3c"
                        font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                        opacity: 0.5
                    }
                    onClicked: cancelRequested(itemIndex)
                }

                // Botón Carpeta (Solo al completar)
                Button {
                    visible: progressValue >= 1.0
                    flat: true; Layout.preferredWidth: 100; Layout.preferredHeight: 36
                    contentItem: RowLayout {
                        spacing: 8; anchors.centerIn: parent
                        Text { text: "📁"; font.pixelSize: 12 }
                        Text { text: "VER CARPETA"; color: "white"; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1; opacity: 0.6 }
                    }
                    onClicked: openFolderRequested(itemIndex)
                }
            }
        }

        // 4. BARRA DE PROGRESO "NEON"
        ColumnLayout {
            Layout.fillWidth: true; spacing: 6
            
            Rectangle {
                Layout.fillWidth: true; height: 4; radius: 2; color: "#1a1a1f"
                
                Rectangle {
                    id: progressFill
                    width: parent.width * progressValue; height: parent.height; radius: 2
                    color: isPaused ? "#f1c40f" : accentColor
                    
                    Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }

                    layer.enabled: true
                    layer.effect: DropShadow {
                        transparentBorder: true
                        color: isPaused ? "#f1c40f" : accentColor; samples: 20; radius: 8
                    }
                }
            }

            Text {
                text: isPaused ? "ENGINE: Motor en espera por el usuario." : (lastLog !== "" ? ("ENGINE: " + lastLog) : (itemType + " " + totalSize + " REGISTERED"))
                color: isPaused ? "#44f1c40f" : "#22ffffff"; font.pixelSize: 9; font.family: "Consolas"
                Layout.fillWidth: true; elide: Text.ElideRight
            }
        }
    }
}
