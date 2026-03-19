import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * EmulatorTweakPopup.qml
 * Popup modularizado para configurar ajustes específicos de cada emulador.
 */

Popup {
    id: root
    anchors.centerIn: parent
    width: 540
    height: Math.min(700, parent.height * 0.9)
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    // --- PROPIEDADES PÚBLICAS ---
    property string currentEmuId: ""
    property string currentEmuName: ""
    property color accentColor: "#4da6ff"
    
    // El objeto 'bridge' debe ser accesible globalmente o pasado

    background: Rectangle {
        color: "#121520"
        radius: 24
        border.color: "#33ffffff"
        border.width: 1
        
        // Brillo interior sutil
        Rectangle {
            anchors.fill: parent; anchors.margins: 1; radius: 31
            color: "transparent"; border.color: Qt.alpha(root.accentColor, 0.05); border.width: 1
        }
    }

    contentItem: ColumnLayout {
        anchors.fill: parent
        anchors.margins: 35
        spacing: 25

        // Cabecera
        RowLayout {
            spacing: 18
            Rectangle {
                width: 44; height: 44; radius: 22
                color: Qt.alpha(root.accentColor, 0.15)
                Label { anchors.centerIn: parent; text: "⚙️"; font.pixelSize: 20 }
            }
            ColumnLayout {
                spacing: 2
                Label {
                    text: root.currentEmuName.toUpperCase()
                    color: "white"; font.pixelSize: 20; font.weight: Font.Black; font.letterSpacing: 1
                }
                Label {
                    text: "AJUSTES DEL EMULADOR"
                    color: root.accentColor; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2
                }
            }
            Item { Layout.fillWidth: true }
            Button {
                text: "✕"
                onClicked: root.close()
                flat: true
                contentItem: Label { text: parent.text; color: "#66ffffff"; font.pixelSize: 22 }
                background: null
            }
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#1affffff" }

        // Lista de Ajustes
        ListView {
            id: tweakListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 14
            model: (root.visible && bridge) ? bridge.emu.getEmulatorTweaks(root.currentEmuId) : []
            
            ScrollBar.vertical: ScrollBar {
                id: scrollBar
                policy: tweakListView.contentHeight > tweakListView.height ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
            }

            delegate: Rectangle {
                id: tweakItem
                width: tweakListView.width - (scrollBar.visible ? 18 : 0)
                height: isVisible ? 100 : 0
                radius: 20
                color: "#252b3b"
                border.color: highlighted ? root.accentColor : "#33ffffff"
                border.width: highlighted ? 1.5 : 0.5
                visible: isVisible
                clip: true
                
                property bool highlighted: false
                property bool isVisible: {
                    if (modelData.depends_on === undefined) return true;
                    if (modelData.depends_on.fullscreen !== undefined) {
                        var fsValue = true;
                        for (var i=0; i < tweakListView.count; i++) {
                            var item = tweakListView.model[i];
                            if (item.id === "fullscreen") { fsValue = item.value; break; }
                        }
                        return modelData.depends_on.fullscreen === fsValue;
                    }
                    return true;
                }

                Behavior on height { NumberAnimation { duration: 300; easing.type: Easing.OutQuart } }
                Behavior on border.color { ColorAnimation { duration: 200 } }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 25; anchors.rightMargin: 25
                    spacing: 20

                    ColumnLayout {
                        spacing: 4; Layout.fillWidth: true
                        Label {
                            text: (bridge && modelData.label.indexOf("lib_") === 0) ? bridge.translate(modelData.label) : modelData.label
                            font.pixelSize: 17; color: "white"; font.weight: Font.DemiBold
                        }
                        Label {
                            text: modelData.description || "Ajuste dinámico"
                            font.pixelSize: 11; color: "#8899aa"; font.weight: Font.Medium
                        }
                    }

                    // Selectores dinámicos según el tipo de dato
                    Loader {
                        sourceComponent: {
                            if (modelData.type === "bool") return switchComp;
                            if (modelData.type === "list") return comboComp;
                            return null;
                        }
                    }
                }

                // --- COMPONENTES INTERNOS ---
                Component {
                    id: switchComp
                    Switch {
                        checked: modelData.value
                        onToggled: bridge.emu.saveEmulatorTweak(root.currentEmuId, modelData.id, checked)
                        palette.windowText: "white"
                    }
                }

                Component {
                    id: comboComp
                    ComboBox {
                        Layout.preferredWidth: 160
                        model: modelData.options
                        currentIndex: modelData.value_index !== undefined ? modelData.value_index : 0
                        textRole: "label"
                        onActivated: (index) => {
                            bridge.emu.saveEmulatorTweak(root.currentEmuId, modelData.id, model[index].value)
                        }
                        
                        // Estilo similar al resto de la app
                        background: Rectangle {
                            color: "#1a202c"; radius: 10; border.color: "#4a5568"
                        }
                    }
                }
            }
        }
        
        Button {
            id: doneBtn
            Layout.fillWidth: true; Layout.preferredHeight: 56
            text: "LISTO"
            onClicked: root.close()
            background: Rectangle {
                radius: 28; color: doneBtn.hovered ? "#33ffffff" : "#1affffff"
                border.color: "#22ffffff"; border.width: 1
            }
            contentItem: Label { text: parent.text; color: "white"; font.bold: true; font.letterSpacing: 2; horizontalAlignment: Text.AlignHCenter }
        }
    }

    enter: Transition {
        NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 250 }
        NumberAnimation { property: "scale"; from: 0.9; to: 1; duration: 400; easing.type: Easing.OutBack }
    }
    exit: Transition {
        NumberAnimation { property: "opacity"; to: 0; duration: 150 }
        NumberAnimation { property: "scale"; to: 0.9; duration: 150; easing.type: Easing.InBack }
    }
}
