import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: dashboardView
    objectName: "dashboardView"

    ColumnLayout {
        anchors.centerIn: parent
        
        Text {
            text: "Welcome to EmuManager"
            font.pixelSize: 28
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }
        
        Text {
            text: "Your Local-First Game Library."
            font.pixelSize: 18
            color: "gray"
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
