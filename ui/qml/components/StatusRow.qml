import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

RowLayout {
    id: root
    property string title: "Status"
    property string path: "None"
    property bool exists: false

    spacing: 12

    Label {
        text: root.exists ? "✅" : (root.path ? "⚠️" : "❌")
        font.pixelSize: 16
        Layout.preferredWidth: 26
    }

    ColumnLayout {
        spacing: 2
        Label {
            text: root.title
            font.pixelSize: 12
            font.bold: true
            color: "#c0c0c0"
        }
        Label {
            text: root.path ? root.path.split(/[\\/]/).pop() : bridge.translate("dash_missing")
            font.pixelSize: 11
            color: root.exists ? "#4dc6a6" : (root.path ? "#f0a040" : "#e05050")
            Layout.maximumWidth: 220
            elide: Text.ElideRight
        }
    }
    Item { Layout.fillWidth: true }
}
