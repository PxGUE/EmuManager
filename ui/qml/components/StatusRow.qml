import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects

RowLayout {
    id: root
    property string title: "Status"
    property string path: "None"
    property bool exists: false

    spacing: 15

    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    // Status icon pill
    Rectangle {
        width: 44; height: 44; radius: 14
        color: root.exists
            ? Qt.rgba(0.20, 0.83, 0.60, 0.12)
            : (root.path ? Qt.rgba(0.98, 0.75, 0.14, 0.12) : Qt.rgba(0.97, 0.44, 0.44, 0.12))
        border.color: root.exists
            ? Qt.rgba(0.20, 0.83, 0.60, 0.35)
            : (root.path ? Qt.rgba(0.98, 0.75, 0.14, 0.35) : Qt.rgba(0.97, 0.44, 0.44, 0.35))
        border.width: 1

        layer.enabled: root.exists
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: "#34d399"
            shadowBlur: 1.0
            shadowOpacity: 0.6
        }

        Icon {
            anchors.centerIn: parent
            name: root.exists ? "check" : (root.path ? "warning" : "close")
            size: 18
            color: root.exists ? "#34d399" : (root.path ? "#fbbf24" : "#f87171")
        }
    }

    ColumnLayout {
        spacing: 2
        Label {
            text: root.title.toUpperCase()
            font.pixelSize: 10; font.bold: true
            color: "#6e7282"; font.letterSpacing: 1.5
        }
        Label {
            text: root.path ? root.path.split(/[\/\\]/).pop() : tr("dash_missing")
            font.pixelSize: 15; font.weight: Font.DemiBold
            color: root.exists ? "#f0e8ff" : "#b0b0c0"
            Layout.maximumWidth: 300; elide: Text.ElideRight
        }
    }

    Item { Layout.fillWidth: true }
}
