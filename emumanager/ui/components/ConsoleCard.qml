import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Rectangle {
    id: consoleCard
    
    // Propiedades de la Tarjeta
    property string title: "" // Título para la vista de biblioteca
    property string consoleName: title // Alias para compatibilidad
    property string emulatorName: ""
    property string gameCount: "0"
    property string playTime: "0h"
    property string iconEmoji: "🎮"
    property color accentColor: "#16a085"
    property bool isSelected: false
    property bool isFocused: isSelected || mouseArea.containsMouse
    property bool minimalMode: true // Por defecto para el carrusel superior
    property bool hasCore: true // Indica si el emulador/core está instalado

    width: minimalMode ? 240 : 380
    height: minimalMode ? 80 : 480
    radius: minimalMode ? 16 : 32
    
    Behavior on width { NumberAnimation { duration: 500; easing.type: Easing.OutQuint } }
    Behavior on height { NumberAnimation { duration: 500; easing.type: Easing.OutQuint } }
    Behavior on radius { NumberAnimation { duration: 500 } }

    // Fondo Glassmorphism (Atenuado si no hay core)
    color: isSelected ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.2) : "#121216"
    opacity: hasCore ? 0.95 : 0.4
    Behavior on opacity { NumberAnimation { duration: 400 } }
    
    border.color: isFocused ? accentColor : "#25252b"
    border.width: isFocused ? 2 : 1
    clip: true
    
    // Efecto de Brillo Interior (Glow)
    Rectangle {
        anchors.fill: parent; radius: parent.radius
        color: "transparent"
        border.color: "white"
        border.width: 1
        opacity: isFocused ? 0.15 : 0.05
    }

    signal clicked()

    Behavior on color { ColorAnimation { duration: 300 } }
    Behavior on border.color { ColorAnimation { duration: 300 } }
    Behavior on scale { NumberAnimation { duration: 400; easing.type: Easing.OutBack } }

    // --- GRADIENTE DE FONDO SUTIL ---
    Rectangle {
        anchors.fill: parent; radius: parent.radius; opacity: 0.3
        gradient: Gradient {
            GradientStop { position: 0.0; color: isSelected ? accentColor : "transparent" }
            GradientStop { position: 1.0; color: "transparent" }
        }
    }

    // --- DISEÑO MINIMALISTA (CARRUSEL SUPERIOR / BIBLIOTECA) ---
    Item {
        anchors.fill: parent
        opacity: minimalMode ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 400 } }
        visible: opacity > 0

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 2
            
            Text {
                text: iconEmoji
                font.pixelSize: 32
                Layout.alignment: Qt.AlignHCenter
                opacity: isFocused ? 1.0 : 0.6
                Behavior on opacity { NumberAnimation { duration: 300 } }
            }
            
            Text {
                text: title.toUpperCase()
                color: isSelected ? "white" : "#88ffffff"
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 2
                Layout.alignment: Qt.AlignHCenter
            }

            Text {
                text: "SIN NÚCLEO"
                visible: !hasCore
                color: "#ff416c"
                font.pixelSize: 8
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }

    // --- DISEÑO PREMIUM (DASHBOARD / NAV 3D) ---
    Item {
        anchors.fill: parent; anchors.margins: 25
        opacity: !minimalMode ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 400 } }
        visible: opacity > 0

        ColumnLayout {
            anchors.fill: parent; spacing: 10
            
            // 1. Icono Gigante
            Text {
                text: iconEmoji
                font.pixelSize: 100
                Layout.alignment: Qt.AlignCenter
                opacity: isFocused ? 1.0 : 0.5
                Behavior on opacity { NumberAnimation { duration: 400 } }
            }
            
            // 2. Nombre de Consola
            Text {
                text: title.toUpperCase()
                color: "white"; font.pixelSize: 28; font.bold: true
                font.letterSpacing: 3; Layout.alignment: Qt.AlignHCenter
            }

            // 3. Nombre del Emulador o Aviso de Falta de Core
            Text {
                text: !hasCore ? "NÚCLEO NO INSTALADO" : (emulatorName ? emulatorName.toUpperCase() : "RETROARCH / LIBRETRO")
                color: !hasCore ? "#ff416c" : accentColor
                font.pixelSize: 11; font.bold: true
                font.letterSpacing: 2; Layout.alignment: Qt.AlignHCenter
                opacity: 0.8
            }
            
            Rectangle { 
                Layout.preferredWidth: 40; Layout.preferredHeight: 2; radius: 1; color: "#33ffffff"
                Layout.alignment: Qt.AlignHCenter; Layout.topMargin: 5; Layout.bottomMargin: 5
            }
            
            // 4. Tiempo Jugado
            RowLayout {
                Layout.alignment: Qt.AlignHCenter; spacing: 8
                Text { text: "⏱️"; font.pixelSize: 12; opacity: 0.6 }
                Text { text: playTime; color: "white"; font.pixelSize: 14; font.bold: true }
            }

            // 5. Total de Juegos
            RowLayout {
                Layout.alignment: Qt.AlignHCenter; spacing: 8
                Text { text: "📚"; font.pixelSize: 12; opacity: 0.6 }
                Text { text: gameCount + " JUEGOS"; color: "white"; font.pixelSize: 14; font.bold: true }
            }

            // 6. Botón de Acción / Aviso
            Button {
                text: "DESCARGAR NÚCLEO"
                visible: !hasCore
                Layout.alignment: Qt.AlignCenter
                Material.background: "#ff416c"
                font.bold: true
                onClicked: console.log("Ir a descargas para esta consola")
            }

            Item { Layout.fillHeight: true }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: consoleCard.clicked()
    }
}
