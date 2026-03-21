import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: settingRowRoot
    property string icon: ""
    property string title: ""
    property string subtitle: ""
    
    // Captura cualquier widget y lo mete al final de la fila
    default property alias _content: row.data
    
    Layout.fillWidth: true
    implicitHeight: 76

    RowLayout {
        id: row
        anchors.fill: parent
        anchors.leftMargin: 24
        anchors.rightMargin: 24
        spacing: 18

        // 1. Icono (Fijo a la izquierda)
        Rectangle {
            Layout.preferredWidth: 40; Layout.preferredHeight: 40; radius: 10
            color: "#1affffff"
            Layout.alignment: Qt.AlignVCenter
            Icon {
                anchors.centerIn: parent
                name: settingRowRoot.icon
                size: 16
                color: "white"
                opacity: 0.6
                visible: name !== ""
            }
        }

        // 2. Textos (Estrechan el espacio pero alineados a la izquierda)
        ColumnLayout {
            spacing: 0
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            
            Label {
                text: title
                font.pixelSize: 14; font.weight: Font.Medium; color: "white"
                horizontalAlignment: Text.AlignLeft
                Layout.fillWidth: true
            }
            Label {
                text: subtitle
                font.pixelSize: 10; color: "#666677"
                visible: subtitle !== ""
                horizontalAlignment: Text.AlignLeft
                Layout.fillWidth: true
            }
        }

        // 3. Widgets de la derecha aparecerán aquí automáticamente y
        // respetarán el anchors.rightMargin: 24 del layout.
    }
}
