import QtQuick
import QtQuick.Effects
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: cardRoot
    property string icon: "library"
    property var value: 0
    property string textValue: ""
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
    
    // AnimaciÃ³n de conteo
    NumberAnimation {
        id: counterAnim
        target: cardRoot
        property: "displayValue"
        from: 0
        to: cardRoot.value
        duration: 1200
        easing.type: Easing.OutExpo
    }

    // Reiniciar animaciÃ³n cuando la tarjeta se hace visible (al cambiar de pestaÃ±a)
    onVisibleChanged: {
        if (visible) {
            displayValue = 0
            counterAnim.restart()
        }
    }

    // Reiniciar si el valor cambia mientras es visible
    onValueChanged: {
        if (visible && typeof value === "number") counterAnim.restart()
        else if (typeof value === "number") displayValue = value
    }

    Rectangle {
        id: cardBody
        anchors.fill: parent
        radius: 20
        color: window.themeCardBg
        border.color: Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.4)
        border.width: 1
        
        // Efecto de brillo interior (Glassmorphism intenso)
        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 19
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.1) }
                GradientStop { position: 0.4; color: "transparent" }
                GradientStop { position: 1.0; color: Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.1) }
            }
        }
        
        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: cardRoot.accentColor
            shadowBlur: 1.0
            shadowOpacity: 0.3
            shadowVerticalOffset: 2
        }

        RowLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 15

            Rectangle {
                width: 48
                height: 48
                radius: 16
                color: Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.15)
                Layout.alignment: Qt.AlignVCenter
                border.color: Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.4)
                border.width: 1
                
                layer.enabled: true
                layer.effect: MultiEffect {
                    shadowEnabled: true
                    shadowColor: cardRoot.accentColor
                    shadowBlur: 1.0
                    shadowOpacity: 0.5
                }
                
                Icon {
                    anchors.centerIn: parent
                    name: cardRoot.icon
                    size: 24
                    color: "white" // In neon design, icon is usually white over colored background
                    
                    layer.enabled: true
                    layer.effect: MultiEffect {
                        shadowEnabled: true
                        shadowColor: "white"
                        shadowBlur: 1.0
                        shadowOpacity: 0.8
                    }
                }
            }

            ColumnLayout {
                spacing: 0
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter

                Label {
                    text: textValue !== "" ? textValue : cardRoot.displayValue
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
