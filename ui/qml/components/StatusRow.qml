import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

RowLayout {
    id: root
    property string title: "Status"
    property string path: "None"
    property bool exists: false

    spacing: 15

    Rectangle {
        width: 38; height: 38; radius: 12
        color: root.exists ? "#154d3d" : (root.path ? "#4d3d15" : "#4d1515")
        opacity: 0.8
        
        Label {
            anchors.centerIn: parent
            text: root.exists ? "✓" : (root.path ? "!" : "✕")
            font.pixelSize: 18; font.bold: true
            color: root.exists ? "#4dc6a6" : (root.path ? "#f0a040" : "#e05050")
        }
    }

    ColumnLayout {
        spacing: 0
        Label {
            text: root.title.toUpperCase()
            font.pixelSize: 10; font.bold: true; color: "#555566"; font.letterSpacing: 1
        }
        Label {
            text: root.path ? root.path.split(/[\\/]/).pop() : (bridge ? bridge.translate("dash_missing") : "Missing")
            font.pixelSize: 14; font.weight: Font.Medium; color: "#e0e0e0"
            Layout.maximumWidth: 280; elide: Text.ElideRight
        }
    }
    
    Item { Layout.fillWidth: true }
}
