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
        width: 42; height: 42; radius: 12
        color: root.exists ? Qt.alpha("#4dc6a6", 0.1) : (root.path ? Qt.alpha("#f0a040", 0.1) : Qt.alpha("#e05050", 0.1))
        border.color: root.exists ? Qt.alpha("#4dc6a6", 0.2) : (root.path ? Qt.alpha("#f0a040", 0.2) : Qt.alpha("#e05050", 0.2))
        border.width: 1
        
        Label {
            anchors.centerIn: parent
            text: root.exists ? "✓" : (root.path ? "!" : "✕")
            font.pixelSize: 18; font.bold: true
            color: root.exists ? "#4dc6a6" : (root.path ? "#f0a040" : "#e05050")
        }
    }

    ColumnLayout {
        spacing: 2
        Label {
            text: root.title.toUpperCase()
            font.pixelSize: 10; font.bold: true; color: "#6e7282"; font.letterSpacing: 1.5
        }
        Label {
            text: root.path ? root.path.split(/[\\/]/).pop() : (bridge ? bridge.translate("dash_missing") : "Missing")
            font.pixelSize: 15; font.weight: Font.DemiBold; color: "#ffffff"
            Layout.maximumWidth: 300; elide: Text.ElideRight
        }
    }
    
    Item { Layout.fillWidth: true }
}
