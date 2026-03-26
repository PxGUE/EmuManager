import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects

Rectangle {
    id: root
    
    // Propiedades de Datos
    property string emuId: ""
    property string name: ""
    property string consoleName: ""
    property string description: ""
    property string icon: "📦"
    property color accent: "#16a085"
    property string downloadUrl: ""
    property string executable: ""
    property bool isInstalled: false
    property bool hasUpdate: false
    
    // Propiedades de Estado (Vinculadas al Controller)
    property real progress: 0.0
    property string statusText: ""
    property bool isInstalling: progress > 0 && progress < 1.0
    
    signal configClicked()

    radius: 20
    color: "#0d0d12"
    border.color: isInstalling ? accent : (isInstalled ? Qt.rgba(accent.r, accent.g, accent.b, 0.3) : "#1a1a1f")
    border.width: isInstalling ? 2 : 1
    clip: true

    // Glossy Overlay sutil
    Rectangle {
        anchors.fill: parent
        opacity: 0.03
        gradient: Gradient {
            GradientStop { position: 0.0; color: "white" }
            GradientStop { position: 1.0; color: "transparent" }
        }
    }

    RowLayout {
        anchors.fill: parent; anchors.margins: 20; spacing: 20

        // 1. Icono con estilo neón expandido
        Rectangle {
            Layout.preferredWidth: 80; Layout.preferredHeight: 80; radius: 18
            color: "#16161c"
            border.color: isInstalled ? accent : "#25252b"
            border.width: 1
            
            Text {
                anchors.centerIn: parent
                text: root.icon; font.pixelSize: 38
                opacity: isInstalled || isInstalling ? 1.0 : 0.3
            }
            
            layer.enabled: isInstalled || isInstalling
            layer.effect: DropShadow {
                transparentBorder: true
                color: Qt.rgba(accent.r, accent.g, accent.b, 0.4)
                samples: 20; radius: 10
            }
        }

        // 2. Información del Emulador
        ColumnLayout {
            Layout.fillWidth: true; spacing: 4
            RowLayout {
                spacing: 10
                Text {
                    text: root.name; color: "white"; font.pixelSize: 18; font.bold: true
                }
                Text {
                    text: (I18n.t[root.consoleName] || root.consoleName).toUpperCase()
                    color: accent; font.pixelSize: 9; font.bold: true; font.letterSpacing: 1.5; opacity: 0.8
                }
            }
            Text {
                text: I18n.t[root.description] || root.description
                color: "#66ffffff"; font.pixelSize: 11; Layout.fillWidth: true; wrapMode: Text.WordWrap; maximumLineCount: 2
                elide: Text.ElideRight
            }
            
            // Badge de estado
            Rectangle {
                Layout.topMargin: 5
                implicitWidth: badgeText.width + 16; implicitHeight: 20; radius: 10
                color: isInstalling ? "#20f1c40f" : (isInstalled ? "#202ecc71" : "#10ffffff")
                Text {
                    id: badgeText; anchors.centerIn: parent
                    text: isInstalling ? (I18n.tp(root.statusText) || I18n.t.status_processing) : I18n.tp(root.statusText)
                    color: isInstalling ? "#f1c40f" : (isInstalled ? "#2ecc71" : "#66ffffff")
                    font.pixelSize: 8; font.bold: true; font.letterSpacing: 1
                }
            }
        }

        // 3. Panel de Acciones (Derecha)
        ColumnLayout {
            Layout.preferredWidth: 150; spacing: 8
            
            // Barra de Progreso Minimalista con Texto de Estado
            ColumnLayout {
                Layout.fillWidth: true; spacing: 4
                visible: isInstalling
                
                Text {
                    text: I18n.tp(root.statusText)
                    color: accent; font.pixelSize: 9; font.bold: true; font.letterSpacing: 2
                }
                
                Rectangle {
                    Layout.fillWidth: true; height: 3; radius: 1.5; color: "#1a1a1f"
                    Rectangle {
                        width: parent.width * progress; height: parent.height; color: accent; radius: 1.5
                        Behavior on width { NumberAnimation { duration: 300 } }
                    }
                }
            }

            Button {
                id: mainActionBtn
                Layout.fillWidth: true; Layout.preferredHeight: 36
                flat: true
                
                // Lógica de 4 Estados
                property string btnText: {
                    if (isInstalling) return I18n.t.status_processing
                    if (!isInstalled) return I18n.t.btn_install
                    if (hasUpdate) return I18n.t.btn_update
                    return I18n.t.btn_uninstall
                }
                
                property color btnColor: {
                    if (isInstalling) return "#66ffffff"
                    if (!isInstalled) return "#16a085"
                    if (hasUpdate) return "#f39c12"
                    return "#e74c3c" // Rojo para Desinstalar
                }

                contentItem: Text {
                    text: mainActionBtn.btnText
                    color: "white"; font.pixelSize: 11; font.bold: true
                    horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    color: mainActionBtn.hovered ? mainActionBtn.btnColor + "22" : "transparent"
                    border.color: mainActionBtn.btnColor
                    border.width: 1; radius: 10
                }

                onClicked: {
                    if (isInstalling) return
                    
                    if (!isInstalled) {
                        mainController.install_emulator(root.emuId, root.downloadUrl, root.executable)
                    } else if (hasUpdate) {
                        mainController.update_emulator(root.emuId, root.downloadUrl, root.executable)
                    } else {
                        mainController.uninstall_emulator(root.emuId)
                    }
                }
            }
        }
    }

    // BOTONES DE CONFIGURACIÓN RÁPIDA (ESQUINA)
    RowLayout {
        anchors.top: parent.top; anchors.right: parent.right; anchors.margins: 15; spacing: 8
        Button {
            width: 30; height: 30; flat: true
            contentItem: Text { text: "⚙️"; font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter }
            onClicked: root.configClicked()
        }
    }
}
