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
    property color accentColor: "#c084fc"

    property int displayValue: 0

    implicitWidth: 220
    implicitHeight: 120

    Layout.fillWidth: true
    Layout.preferredWidth: 240
    Layout.minimumWidth: 180
    Layout.maximumWidth: 400
    Layout.preferredHeight: 120

    // Count-up animation
    NumberAnimation {
        id: counterAnim
        target: cardRoot
        property: "displayValue"
        from: 0
        to: cardRoot.value
        duration: 1200
        easing.type: Easing.OutExpo
    }
    onVisibleChanged: {
        if (visible) { displayValue = 0; counterAnim.restart() }
    }
    onValueChanged: {
        if (visible && typeof value === "number") counterAnim.restart()
        else if (typeof value === "number") displayValue = value
    }

    // Outer glow on hover
    HoverHandler { id: cardHover }

    Rectangle {
        id: cardBody
        anchors.fill: parent
        radius: 22
        clip: true
        // Deep glass background
        color: Qt.rgba(0.09, 0.06, 0.18, 0.75)

        // Violet-tinted glass border
        border.color: cardHover.hovered
            ? Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.75)
            : Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.3)
        border.width: cardHover.hovered ? 1.5 : 1
        Behavior on border.color { ColorAnimation { duration: 250 } }

        // Left accent bar (replaces broken top bar)
        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.topMargin: 18
            anchors.bottomMargin: 18
            anchors.leftMargin: 0
            width: 3
            radius: 2
            gradient: Gradient {
                GradientStop { position: 0.0; color: cardRoot.accentColor }
                GradientStop { position: 1.0; color: "transparent" }
            }
            z: 2
        }

        // Inner glass highlight
        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 21
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.06) }
                GradientStop { position: 0.35; color: "transparent" }
                GradientStop { position: 1.0; color: Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.07) }
            }
        }

        scale: cardHover.hovered ? 1.02 : 1.0
        Behavior on scale { NumberAnimation { duration: 350; easing.type: Easing.OutBack } }

        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: cardRoot.accentColor
            shadowBlur: cardHover.hovered ? 1.5 : 0.8
            shadowOpacity: cardHover.hovered ? 0.55 : 0.2
            shadowVerticalOffset: 4
        }

        RowLayout {
            anchors.fill: parent
            anchors.margins: 20
            anchors.leftMargin: 22
            spacing: 18

            // Icon box
            Rectangle {
                width: 52
                height: 52
                radius: 18
                color: Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.15)
                Layout.alignment: Qt.AlignVCenter
                border.color: Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.4)
                border.width: 1

                layer.enabled: true
                layer.effect: MultiEffect {
                    shadowEnabled: true
                    shadowColor: cardRoot.accentColor
                    shadowBlur: 1.2
                    shadowOpacity: 0.6
                }

                Icon {
                    anchors.centerIn: parent
                    name: cardRoot.icon
                    size: 26
                    color: cardRoot.accentColor
                    glow: true
                    glowOpacity: 0.8
                }
            }

            ColumnLayout {
                spacing: 1
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter

                Label {
                    text: textValue !== "" ? textValue : cardRoot.displayValue
                    font.pixelSize: 30
                    font.weight: Font.Black
                    color: "white"
                    font.letterSpacing: -0.5
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                Label {
                    text: cardRoot.label.toUpperCase()
                    font.pixelSize: 10
                    font.bold: true
                    color: Qt.rgba(cardRoot.accentColor.r, cardRoot.accentColor.g, cardRoot.accentColor.b, 0.7)
                    font.letterSpacing: 0.8
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    maximumLineCount: 2
                    lineHeight: 0.9
                }
            }
        }
    }
}
