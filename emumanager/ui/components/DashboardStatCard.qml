import QtQuick
import QtQuick.Controls 
import QtQuick.Layouts

Rectangle {
    id: root
    height: 160
    radius: 24
    color: "#0a0a0c"
    border.color: "#1a1a1f"
    clip: true

    property string label: "STAT"
    property string value: "0"
    property string subLabel: "Description"
    property string icon: "📦"
    property color accentColor: "#16a085"

    Rectangle {
        anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.rightMargin: -30; anchors.bottomMargin: -30
        width: 120; height: 120; radius: 60; color: root.accentColor; opacity: 0.05
    }

    ColumnLayout {
        anchors.fill: parent; anchors.margins: 25; spacing: 5
        
        RowLayout {
            Text { text: root.label; color: root.accentColor; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            Item { Layout.fillWidth: true }
            Text { text: root.icon; font.pixelSize: 22; opacity: 0.4 }
        }
        
        Text { text: root.subLabel; color: "#44ffffff"; font.pixelSize: 11; font.bold: true }
        
        Text { 
            text: root.value.toString(); color: "white"; font.pixelSize: 32; font.bold: true 
            elide: Text.ElideRight; Layout.fillWidth: true
        }
        
        Item { Layout.fillHeight: true }
        
        Rectangle { width: 40; height: 2; radius: 1; color: root.accentColor }
    }

    MouseArea {
        anchors.fill: parent; hoverEnabled: true
        onEntered: { root.border.color = root.accentColor; root.scale = 1.02 }
        onExited: { root.border.color = "#1a1a1f"; root.scale = 1.0 }
    }

    Behavior on border.color { ColorAnimation { duration: 250 } }
    Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutQuint } }
}
