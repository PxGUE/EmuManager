import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: pathSettingRoot
    property string title: ""
    property string subtitle: ""
    property string path: ""
    signal browse()
    
    function tr(key, ...args) {
        if (!bridge) return key
        var _ = bridge.currentLanguage
        if (args.length > 0) return bridge.translateWithArgs(key, args)
        return bridge.translate(key)
    }

    Layout.fillWidth: true
    implicitHeight: 76

    // Fondo con efecto hover
    Rectangle {
        anchors.fill: parent
        anchors.margins: 2
        radius: 12
        color: hoverTracker.hovered ? window.themeCardBg : "transparent"
        Behavior on color { ColorAnimation { duration: 150 } }
        HoverHandler { id: hoverTracker }
    }

    SettingRow {
        id: row
        anchors.fill: parent
        icon: "folder"
        title: pathSettingRoot.title
        subtitle: (pathSettingRoot.subtitle ? pathSettingRoot.subtitle + "\n" : "") + (pathSettingRoot.path ? pathSettingRoot.path : tr("dash_missing"))

        Button {
            id: browseBtn
            text: tr("set_btn_select")
            onClicked: browse()
            Layout.preferredHeight: 30
            
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                propagateComposedEvents: true
                onPressed: (mouse) => { mouse.accepted = false; }
            }
            
            background: Rectangle {
                color: browseBtn.pressed ? window.themeAccent : (browseBtn.hovered ? "#33ffffff" : "#1affffff")
                radius: 6
                border.color: browseBtn.hovered ? window.themeBorder : "transparent"
                border.width: 1
                Behavior on color { ColorAnimation { duration: 150 } }
            }
            contentItem: Label {
                text: browseBtn.text
                color: browseBtn.pressed ? "black" : "white"
                font.pixelSize: 11; font.weight: Font.Medium
                horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                leftPadding: 16; rightPadding: 16
            }
        }
    }
}
