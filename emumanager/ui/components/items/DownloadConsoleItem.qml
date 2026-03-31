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
    readonly property color resolvedAccent: Theme.resolveColor(accent)
    property string downloadUrl: ""
    property string executable: ""
    property bool isInstalled: false
    property bool hasUpdate: false
    
    // Propiedades de Estado (Vinculadas al Controller)
    property real progress: 0.0
    property string statusText: ""
    property bool activeOrchestration: {
        if (progress > 0 && progress < 1.0) return true;
        var activeKeys = ["emu_status_connecting", "emu_status_downloading", "emu_status_extracting", "emu_status_configuring", "emu_status_uninstalling"];
        return activeKeys.indexOf(statusText) !== -1;
    }
    
    signal configClicked()

    radius: Theme.radiusMedium
    color: Theme.cardBackground
    border.color: (activeOrchestration || isInstalled) ? resolvedAccent : Theme.controlBackground
    border.width: activeOrchestration ? Theme.borderThick : Theme.borderThin
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
                opacity: isInstalled || activeOrchestration ? 1.0 : 0.3
            }
            
            layer.enabled: isInstalled || activeOrchestration
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
                color: activeOrchestration ? Theme.accentColor + "22" : (isInstalled ? Theme.panelBackground : Theme.cardBorder)
                Text {
                    id: badgeText; anchors.centerIn: parent
                    text: activeOrchestration ? (I18n.tp(root.statusText) || I18n.t.status_processing) : I18n.tp(root.statusText)
                    color: activeOrchestration ? Theme.accentColor : (isInstalled ? Theme.textMain : Theme.textMuted)
                    font.pixelSize: Theme.fontMicro; font.bold: true; font.letterSpacing: 1
                }
            }
        }

        // 3. Panel de Acciones (Derecha)
        ColumnLayout {
            Layout.preferredWidth: 160; spacing: 10
            
            // Barra de Progreso Minimalista con Texto de Estado
            ColumnLayout {
                Layout.fillWidth: true; spacing: 8
                visible: activeOrchestration
                
                Text {
                    text: I18n.tp(root.statusText).toUpperCase()
                    color: Theme.textAccent; font.pixelSize: Theme.fontMicro; font.bold: true; font.letterSpacing: 1.5
                    opacity: 0.9
                }
                
                // Barra de Progreso Cálida (Warm/Glass)
                Rectangle {
                    id: progressBarBg
                    Layout.fillWidth: true; height: 8; radius: 4; color: Theme.transparent; clip: true
                    
                    // Capa de fondo traslúcida con pulsación sutil
                    Rectangle {
                        anchors.fill: parent; radius: 4; color: Theme.white
                        opacity: activeOrchestration ? (progress > 0 ? 0.15 : 0.1) : 0.08
                        
                        SequentialAnimation on opacity {
                            running: activeOrchestration && progress == 0
                            loops: Animation.Infinite
                            NumberAnimation { from: 0.15; to: 0.05; duration: 1000 }
                            NumberAnimation { from: 0.05; to: 0.15; duration: 1000 }
                        }
                    }
                    
                    // Barra Propiamente Dicha (Progreso)
                    Rectangle {
                        id: progressBarFill
                        width: Math.max(progressBarBg.width * progress, activeOrchestration ? 24 : 0)
                        height: parent.height; color: resolvedAccent; radius: 4
                        Behavior on width { NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
                    }
                }
            }

            Button {
                id: mainActionBtn
                Layout.fillWidth: true; Layout.preferredHeight: 38
                flat: true; enabled: !activeOrchestration
                
                // Lógica de 4 Estados
                property string btnText: {
                    if (activeOrchestration) return I18n.t.status_processing
                    if (!isInstalled) return I18n.t.btn_install
                    if (hasUpdate) return I18n.t.btn_update
                    return I18n.t.btn_uninstall
                }
                
                property color btnColor: {
                    if (activeOrchestration) return Theme.textMuted
                    if (!isInstalled) return Theme.accentColor
                    if (hasUpdate) return Theme.accentColor
                    return Theme.danger
                }

                contentItem: Text {
                    text: mainActionBtn.btnText
                    color: Theme.textMain; font.pixelSize: Theme.fontBody; font.bold: true
                    horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                    opacity: mainActionBtn.enabled ? 1.0 : 0.5
                }

                background: Rectangle {
                    color: (mainActionBtn.hovered && mainActionBtn.enabled) ? mainActionBtn.btnColor + "33" : Theme.transparent
                    border.color: mainActionBtn.enabled ? mainActionBtn.btnColor : Theme.controlBorder
                    border.width: Theme.borderThin; radius: Theme.radiusSmall
                }

                onClicked: {
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
