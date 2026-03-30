import QtQuick
import ".."
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
    property var accent: Theme.accentColor
    readonly property color resolvedAccent: (typeof accent === "string" && Theme[accent] !== undefined) ? Theme[accent] : accent
    property string downloadUrl: ""
    property string executable: ""
    property bool isInstalled: false
    property bool hasUpdate: false
    
    // Propiedades de Estado (Vinculadas al Controller)
    property real progress: 0.0
    property string statusText: ""
    property bool isInstalling: progress > 0 && progress < 1.0
    
    signal configClicked()

    radius: Theme.radiusMedium
    color: Theme.cardBackground
    border.color: (isInstalling || isInstalled) ? resolvedAccent : Theme.controlBackground
    border.width: isInstalling ? Theme.borderThick : Theme.borderThin
    clip: true

    // Glossy Overlay sutil
    Rectangle {
        anchors.fill: parent
        opacity: 0.03
        gradient: Gradient {
            GradientStop { position: 0.0; color: Theme.textMain }
            GradientStop { position: 1.0; color: Theme.transparent }
        }
    }

    RowLayout {
        anchors.fill: parent; anchors.margins: Theme.spaceMedium; spacing: Theme.spaceMedium

        // 1. Icono con estilo neón expandido
        Rectangle {
            Layout.preferredWidth: 80; Layout.preferredHeight: 80; radius: Theme.radiusMedium
            color: Theme.controlBackground
            border.color: isInstalled ? resolvedAccent : Theme.cardBorder
            border.width: Theme.borderThin
            
            Text {
                anchors.centerIn: parent
                text: root.icon; font.pixelSize: Theme.fontDisplay
                opacity: isInstalled || isInstalling ? 1.0 : 0.3
            }
            
            layer.enabled: isInstalled || isInstalling
            layer.effect: DropShadow {
                transparentBorder: true
                color: Qt.rgba(resolvedAccent.r, resolvedAccent.g, resolvedAccent.b, 0.4)
                samples: Theme.glowSamples; radius: Theme.radiusSmall
            }
        }

        // 2. Información del Emulador
        ColumnLayout {
            Layout.fillWidth: true; spacing: 4
            RowLayout {
                spacing: 10
                Text {
                    text: root.name; color: Theme.textMain; font.pixelSize: Theme.fontHeader; font.bold: true
                }
                Text {
                    text: (I18n.t[root.consoleName] || root.consoleName).toUpperCase()
                    color: Theme.textAccent; font.pixelSize: Theme.fontMicro; font.bold: true; font.letterSpacing: 1.5; opacity: 0.8
                }
            }
            Text {
                text: I18n.t[root.description] || root.description
                color: Theme.textDim; font.pixelSize: Theme.fontBody; Layout.fillWidth: true; wrapMode: Text.WordWrap; maximumLineCount: 2
                elide: Text.ElideRight
            }
            
            // Badge de estado
            Rectangle {
                Layout.topMargin: 5
                implicitWidth: badgeText.width + 16; implicitHeight: 20; radius: Theme.radiusSmall
                color: isInstalling ? Theme.accentColor + "20" : (isInstalled ? Theme.panelBackground : Theme.cardBorder)
                Text {
                    id: badgeText; anchors.centerIn: parent
                    text: isInstalling ? (I18n.tp(root.statusText) || I18n.t.status_processing) : I18n.tp(root.statusText)
                    color: isInstalling ? Theme.accentColor : (isInstalled ? Theme.textMain : Theme.textMuted)
                    font.pixelSize: Theme.fontMicro; font.bold: true; font.letterSpacing: 1
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
                    color: resolvedAccent; font.pixelSize: Theme.fontSmall; font.bold: true; font.letterSpacing: 2
                }
                
                Rectangle {
                    Layout.fillWidth: true; height: 3; radius: 1.5; color: Theme.divider
                    Rectangle {
                        width: parent.width * progress; height: parent.height; color: resolvedAccent; radius: 1.5
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
                    if (isInstalling) return Theme.textMuted
                    if (!isInstalled) return Theme.accentColor
                    if (hasUpdate) return Theme.accentColor
                    return Theme.danger // Preserve red for uninstall
                }

                contentItem: Text {
                    text: mainActionBtn.btnText
                    color: Theme.textMain; font.pixelSize: Theme.fontBody; font.bold: true
                    horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    color: (mainActionBtn.hovered && mainActionBtn.enabled) ? mainActionBtn.btnColor + "22" : Theme.transparent
                    border.color: mainActionBtn.enabled ? mainActionBtn.btnColor : Theme.controlBorder
                    border.width: Theme.borderThin; radius: Theme.radiusSmall
                    opacity: mainActionBtn.enabled ? 1.0 : 0.3
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
            contentItem: Text { text: "⚙️"; font.pixelSize: Theme.fontHeader; horizontalAlignment: Text.AlignHCenter }
            onClicked: root.configClicked()
        }
    }
}
