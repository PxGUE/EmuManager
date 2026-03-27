import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material
import "../system"

GlassPanel {
    id: root
    radius: 28
    borderColor: Theme.divider

    property var sysInfo: ({})
    property bool isBusy: false

    ColumnLayout {
        anchors.fill: parent; anchors.margins: 25; spacing: 15
        
        // --- CABECERA ---
        RowLayout {
            Layout.fillWidth: true; spacing: 10
            Rectangle { 
                width: 8; height: 8; radius: 4; color: isBusy ? Theme.statusWarning : Theme.statusSuccess
                Behavior on color { ColorAnimation { duration: 300 } }
                SequentialAnimation on opacity { 
                    loops: Animation.Infinite
                    NumberAnimation { from: 1; to: 0.4; duration: 800 }
                    NumberAnimation { from: 0.4; to: 1; duration: 800 } 
                }
            }
            Text { text: I18n.t.mango_monitor; color: Theme.textMain; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
        }

        // --- SPECS ---
        ColumnLayout {
            Layout.fillWidth: true; spacing: 10
            
            // CPU
            RowLayout {
                Text { text: "CPU"; color: Theme.textMuted; font.pixelSize: 9; font.bold: true }
                Item { Layout.fillWidth: true }
                Text { text: (sysInfo.cpu_threads || "0") + " " + I18n.t.tech_threads; color: Theme.textMain; font.pixelSize: 10; font.bold: true }
            }
            
            // RAM
            RowLayout {
                Text { text: "RAM"; color: Theme.textMuted; font.pixelSize: 9; font.bold: true }
                Item { Layout.fillWidth: true }
                Text { text: sysInfo.ram || "N/A"; color: Theme.textMain; font.pixelSize: 10; font.bold: true }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Theme.divider }

            // ENGINE VERSION
            RowLayout {
                Text { text: I18n.t.engine_spec; color: Theme.textMuted; font.pixelSize: 9; font.bold: true }
                Item { Layout.fillWidth: true }
                Text { text: sysInfo.mango_version || "v0.9.5"; color: Theme.accentColor; font.pixelSize: 10; font.bold: true }
            }

            // OS
            Text { 
                text: sysInfo.os || "N/A"
                color: Theme.textMuted; opacity: 0.6; font.pixelSize: 8; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight
            }
        }

        Item { Layout.fillHeight: true }

        // --- BIG STATUS ---
        GlassPanel {
            Layout.fillWidth: true; height: 44; radius: 12; backgroundColor: Theme.viewBackground; borderColor: Theme.cardBorder
            RowLayout {
                anchors.centerIn: parent
                Text { text: isBusy ? "⚡" : "🟢"; font.pixelSize: 12 }
                Text { text: isBusy ? I18n.t.processing_caps : I18n.t.ready_caps; color: isBusy ? Theme.statusWarning : Theme.statusSuccess; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2 }
            }
        }
    }
}
