import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: cardRoot
    
    // Propiedades (Renombradas para evitar colisión con built-in 'enabled')
    property string providerId: ""
    property string name: ""
    property string typeDisplay: ""
    property string description: ""
    property bool isActive: true
    property bool isConfigured: true
    
    signal configureClicked()

    implicitHeight: 72
    Layout.fillWidth: true

    readonly property var needsConfig: ["tgdb", "rawg", "screenscraper"]
    property bool hasAConfig: needsConfig.includes(providerId)

    // Fondo con HoverHandler (No bloquea clics)
    Rectangle {
        anchors.fill: parent
        anchors.margins: 2
        radius: 12
        color: hoverTracker.hovered ? window.themeCardBg : "transparent"
        Behavior on color { ColorAnimation { duration: 150 } }
        HoverHandler { id: hoverTracker }
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 20
        spacing: 12

        // 🟢 Columna 1: Status LED (Ancho Fijo para Alineación)
        Item {
            Layout.preferredWidth: 40
            Layout.fillHeight: true
            Rectangle {
                anchors.centerIn: parent
                width: 10; height: 10; radius: 5
                
                // Lógica de colores Solicitada:
                // 🟡 Amarrillo: No configurado
                // 🟢 Verde: Configurado y Activo
                // 4 Rojo: Configurado y Apagado
                color: !isConfigured ? "#f1c40f" : (isActive ? "#2ecc71" : "#e74c3c")
                
                Rectangle {
                    anchors.centerIn: parent
                    width: parent.width + 6; height: parent.height + 6; radius: 8
                    color: parent.color; opacity: 0.2
                }
                Behavior on color { ColorAnimation { duration: 300 } }
            }
        }

        // 🟢 Columna 2: Info (Flexible)
        ColumnLayout {
            spacing: 2
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            
            Label { 
                text: name
                font.pixelSize: 15; font.weight: Font.DemiBold; color: "white" 
                horizontalAlignment: Text.AlignLeft
                Layout.fillWidth: true
                opacity: isActive ? 1.0 : 0.6
                Behavior on opacity { NumberAnimation { duration: 200 } }
            }
            Label {
                text: description
                font.pixelSize: 11; color: "#aaaab0"
                horizontalAlignment: Text.AlignLeft
                Layout.fillWidth: true
                visible: description !== ""
                opacity: isActive ? 0.9 : 0.5
            }
            Label {
                text: typeDisplay.toUpperCase()
                font.pixelSize: 10; color: "#2ecc71"
                font.letterSpacing: 1.2; font.bold: true
                horizontalAlignment: Text.AlignLeft
                Layout.fillWidth: true
                Layout.topMargin: 2
            }
        }

        // 🟢 Columna 3: Acciones (Ancho Fijo para Alineación Vertical Perfecta)
        RowLayout {
            Layout.preferredWidth: 100
            Layout.alignment: Qt.AlignRight
            spacing: 12

            // Botón Gear
            Item {
                width: 32; height: 32
                visible: hasAConfig
                Rectangle {
                    anchors.fill: parent; radius: 16
                    color: gearMouse.containsMouse ? "#20ffffff" : "transparent"
                    Icon {
                        anchors.centerIn: parent
                        name: "settings"
                        size: 16
                        color: gearMouse.containsMouse ? "white" : "#888899"
                        opacity: gearMouse.containsMouse ? 1.0 : 0.6
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                }
                MouseArea {
                    id: gearMouse
                    anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onClicked: cardRoot.configureClicked()
                }
            }

            // Espaciador si no hay gear
            Item { width: 32; height: 32; visible: !hasAConfig }

            // INTERRUPTOR CUSTOM (Mecánica Robusta)
            Rectangle {
                id: toggleBase
                width: 38; height: 21; radius: 10.5
                color: isActive ? window.themeAccent : "#2a2d3e"
                
                Rectangle {
                    id: handle
                    x: isActive ? parent.width - width - 2 : 2
                    anchors.verticalCenter: parent.verticalCenter
                    width: 17; height: 17; radius: 8.5
                    color: "white"
                    Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (bridge) bridge.set.toggleProvider(providerId, !isActive)
                    }
                }
                
                Behavior on color { ColorAnimation { duration: 200 } }
            }
        }
    }
}
