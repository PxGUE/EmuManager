import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: dialogRoot
    
    property string title: "ADVERTENCIA"
    property string message: ""
    property string confirmText: "SÍ, CONTINUAR"
    property string cancelText: "CANCELAR"
    property bool isInfoOnly: false
    property color accentColor: "#4da6ff"

    signal confirmed()
    signal cancelled()

    anchors.centerIn: parent
    width: 440
    height: contentColumn.implicitHeight + 80
    modal: true
    focus: true
    closePolicy: Popup.NoAutoClose

    Overlay.modal: Rectangle {
        color: "#aa000000"
        Behavior on opacity { NumberAnimation { duration: 300 } }
    }

    background: Rectangle {
        color: "#161923"
        radius: 24
        border.color: "#33ffffff"
        border.width: 1

        // Sutil brillo interior
        Rectangle {
            anchors.fill: parent; anchors.margins: 1; radius: 23
            color: "transparent"
            border.color: Qt.alpha(accentColor, 0.1)
            border.width: 1
        }
    }

    contentItem: ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: 30
        spacing: 20

        RowLayout {
            spacing: 12
            Rectangle {
                width: 32; height: 32; radius: 16
                color: Qt.alpha(accentColor, 0.2)
                Label {
                    anchors.centerIn: parent
                    text: isInfoOnly ? "ℹ️" : "⚠️"
                    font.pixelSize: 14
                }
            }
            Label {
                text: dialogRoot.title
                color: accentColor
                font.pixelSize: 12; font.bold: true; font.letterSpacing: 2
            }
        }

        Label {
            Layout.fillWidth: true
            text: dialogRoot.message
            color: "white"
            font.pixelSize: 16; font.weight: Font.Medium
            wrapMode: Text.WordWrap
            lineHeight: 1.2
        }

        Item { Layout.preferredHeight: 10 }

        RowLayout {
            Layout.fillWidth: true
            spacing: 15

            Button {
                id: cancelBtn
                visible: !isInfoOnly
                Layout.fillWidth: true
                Layout.preferredHeight: 44
                text: dialogRoot.cancelText
                hoverEnabled: true
                onClicked: {
                    dialogRoot.close()
                    dialogRoot.cancelled()
                }
                background: Rectangle {
                    radius: 12
                    color: cancelBtn.hovered ? "#1affffff" : "transparent"
                    border.color: cancelBtn.hovered ? accentColor : "#33ffffff"
                    border.width: 1
                    Behavior on color { ColorAnimation { duration: 150 } }
                    Behavior on border.color { ColorAnimation { duration: 150 } }
                }
                contentItem: Label {
                    text: parent.text; color: cancelBtn.hovered ? "white" : "#888899"
                    font.bold: true; font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    Behavior on color { ColorAnimation { duration: 150 } }
                }
            }

            Button {
                id: confirmBtn
                Layout.fillWidth: true
                Layout.preferredHeight: 44
                text: isInfoOnly ? "ACEPTAR" : dialogRoot.confirmText
                hoverEnabled: true
                onClicked: {
                    dialogRoot.close()
                    dialogRoot.confirmed()
                }
                background: Rectangle {
                    radius: 12
                    color: confirmBtn.hovered ? Qt.lighter(isInfoOnly ? "#2a2f45" : accentColor, 1.1) : (isInfoOnly ? "#2a2f45" : accentColor)
                    
                    scale: confirmBtn.pressed ? 0.95 : (confirmBtn.hovered ? 1.02 : 1.0)
                    Behavior on scale { NumberAnimation { duration: 100 } }
                    Behavior on color { ColorAnimation { duration: 150 } }
                }
                contentItem: Label {
                    text: parent.text; color: isInfoOnly ? "white" : "black"
                    font.bold: true; font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }

    enter: Transition {
        NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 250 }
        NumberAnimation { property: "scale"; from: 0.9; to: 1.0; duration: 350; easing.type: Easing.OutBack }
    }
    exit: Transition {
        NumberAnimation { property: "opacity"; to: 0.0; duration: 200 }
        NumberAnimation { property: "scale"; to: 0.9; duration: 200; easing.type: Easing.InBack }
    }
}
