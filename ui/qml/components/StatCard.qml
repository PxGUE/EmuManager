import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: cardRoot
    property string icon: "🎯"
    property int value: 0
    property string label: "Stat"
    property color accentColor: "#4da6ff"

    property int displayValue: 0

    implicitWidth: 220
    implicitHeight: 110
    
    Layout.fillWidth: true
    Layout.preferredWidth: 240
    Layout.minimumWidth: 180
    Layout.maximumWidth: 400
    Layout.preferredHeight: 110
    
    // Animación de conteo
    NumberAnimation {
        id: counterAnim
        target: cardRoot
        property: "displayValue"
        from: 0
        to: cardRoot.value
        duration: 1200
        easing.type: Easing.OutExpo
    }

    // Reiniciar animación cuando la tarjeta se hace visible (al cambiar de pestaña)
    onVisibleChanged: {
        if (visible) {
            displayValue = 0
            counterAnim.restart()
        }
    }

    // Reiniciar si el valor cambia mientras es visible
    onValueChanged: {
        if (visible) counterAnim.restart()
        else displayValue = value
    }

    Rectangle {
        id: cardBody
        anchors.fill: parent
        radius: 20
        color: "#141621"
        border.color: "#252835"
        border.width: 1
        
        // Gradiente sutil constante para profundidad
        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 19
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#08ffffff" }
                GradientStop { position: 1.0; color: "transparent" }
            }
        }

        RowLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 15

            Rectangle {
                width: 48
                height: 48
                radius: 14
                color: Qt.alpha(cardRoot.accentColor, 0.12)
                Layout.alignment: Qt.AlignVCenter
                
                Label {
                    anchors.centerIn: parent
                    text: cardRoot.icon
                    font.pixelSize: 24
                }
            }

            ColumnLayout {
                spacing: 0
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter

                Label {
                    text: cardRoot.displayValue
                    font.pixelSize: 28
                    font.weight: Font.Black
                    color: "white"
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                Label {
                    text: cardRoot.label.toUpperCase()
                    font.pixelSize: 11
                    font.bold: true
                    color: "#a0a0b0"
                    font.letterSpacing: 0.5
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    maximumLineCount: 2
                    lineHeight: 0.9
                }
            }
        }
    }
}
