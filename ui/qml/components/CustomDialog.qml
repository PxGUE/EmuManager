import QtQuick
import QtQuick.Effects
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: dialogRoot

    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    property string title: tr("dlg_warn_title")
    property string message: ""
    property string confirmText: tr("lib_yes_change")
    property string cancelText: tr("dl_btn_cancel")
    property bool isInfoOnly: false
    property color accentColor: "#c084fc"

    signal confirmed()
    signal cancelled()

    anchors.centerIn: parent
    width: 460
    height: contentColumn.implicitHeight + 90
    modal: true
    focus: true
    closePolicy: Popup.NoAutoClose

    Overlay.modal: Rectangle {
        color: "#cc000010"
        Behavior on opacity { NumberAnimation { duration: 300 } }
    }

    background: Item {
        // Outer glow
        Rectangle {
            anchors.fill: parent
            anchors.margins: -6
            radius: 32
            color: "transparent"
            border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.2)
            border.width: 1
            opacity: 0.6
        }
        // Main card
        Rectangle {
            anchors.fill: parent
            radius: 28
            color: Qt.rgba(0.05, 0.03, 0.12, 0.97)
            border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.4)
            border.width: 1

            layer.enabled: true
            layer.effect: MultiEffect {
                shadowEnabled: true; shadowColor: accentColor
                shadowBlur: 1.5; shadowOpacity: 0.3; shadowVerticalOffset: 8
            }

            // Radial top glow
            Rectangle {
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width * 0.7; height: 140
                radius: parent.radius
                opacity: 0.12
                gradient: Gradient {
                    GradientStop { position: 0.0; color: accentColor }
                    GradientStop { position: 1.0; color: "transparent" }
                }
            }

            // Inner glass sheen
            Rectangle {
                anchors.fill: parent
                anchors.margins: 1
                radius: 27; color: "transparent"
                border.color: Qt.rgba(1,1,1,0.06); border.width: 1
            }
        }
    }

    contentItem: ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: 32
        spacing: 22

        // Header
        RowLayout {
            spacing: 14
            Rectangle {
                width: 36; height: 36; radius: 12
                color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.18)
                border.color: Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.4)
                border.width: 1
                layer.enabled: true
                layer.effect: MultiEffect {
                    shadowEnabled: true; shadowColor: accentColor
                    shadowBlur: 1.0; shadowOpacity: 0.5
                }
                Icon {
                    anchors.centerIn: parent
                    name: isInfoOnly ? "info" : "warning"
                    size: 16
                    color: accentColor
                }
            }
            Label {
                text: dialogRoot.title
                color: accentColor
                font.pixelSize: 11; font.bold: true; font.letterSpacing: 2.5
            }
        }

        Label {
            Layout.fillWidth: true
            text: dialogRoot.message
            color: "#e8e0f5"
            font.pixelSize: 16; font.weight: Font.Medium
            wrapMode: Text.WordWrap
            lineHeight: 1.25
        }

        Item { Layout.preferredHeight: 4 }

        RowLayout {
            Layout.fillWidth: true
            spacing: 14

            Button {
                id: cancelBtn
                visible: !isInfoOnly
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                text: dialogRoot.cancelText
                hoverEnabled: true
                onClicked: { dialogRoot.close(); dialogRoot.cancelled() }
                background: Rectangle {
                    radius: 14
                    color: cancelBtn.hovered ? Qt.rgba(1,1,1,0.08) : Qt.rgba(1,1,1,0.04)
                    border.color: cancelBtn.hovered
                        ? Qt.rgba(accentColor.r, accentColor.g, accentColor.b, 0.5)
                        : Qt.rgba(1,1,1,0.14)
                    border.width: 1
                    Behavior on color { ColorAnimation { duration: 150 } }
                    Behavior on border.color { ColorAnimation { duration: 150 } }
                    scale: cancelBtn.pressed ? 0.97 : 1.0
                    Behavior on scale { NumberAnimation { duration: 100 } }
                }
                contentItem: Label {
                    text: parent.text
                    color: cancelBtn.hovered ? "#f0e8ff" : "#8080a0"
                    font.bold: true; font.pixelSize: 13
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    Behavior on color { ColorAnimation { duration: 150 } }
                }
            }

            Button {
                id: confirmBtn
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                text: isInfoOnly ? tr("dlg_btn_ok") : dialogRoot.confirmText
                hoverEnabled: true
                onClicked: { dialogRoot.close(); dialogRoot.confirmed() }
                background: Rectangle {
                    radius: 14
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: isInfoOnly ? "#2a1a4a" : Qt.rgba(accentColor.r, accentColor.g, accentColor.b, confirmBtn.hovered ? 1.0 : 0.9) }
                        GradientStop { position: 1.0; color: isInfoOnly ? "#1a1030" : Qt.rgba(window.neonMagenta.r, window.neonMagenta.g, window.neonMagenta.b, confirmBtn.hovered ? 0.8 : 0.7) }
                    }
                    scale: confirmBtn.pressed ? 0.96 : (confirmBtn.hovered ? 1.02 : 1.0)
                    Behavior on scale { NumberAnimation { duration: 120 } }
                    layer.enabled: confirmBtn.hovered
                    layer.effect: MultiEffect {
                        shadowEnabled: true; shadowColor: accentColor
                        shadowBlur: 1.0; shadowOpacity: 0.5
                    }
                }
                contentItem: Label {
                    text: parent.text
                    color: isInfoOnly ? "#d0c8f0" : "#0a0520"
                    font.bold: true; font.pixelSize: 13; font.letterSpacing: 0.5
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }

    enter: Transition {
        NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 280 }
        NumberAnimation { property: "scale"; from: 0.88; to: 1.0; duration: 380; easing.type: Easing.OutBack }
    }
    exit: Transition {
        NumberAnimation { property: "opacity"; to: 0.0; duration: 200 }
        NumberAnimation { property: "scale"; to: 0.92; duration: 200; easing.type: Easing.InBack }
    }
}
