import QtQuick
import ".."
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material

Button {
    id: control
    property color accentColor: Material.accent
    property string label: "BOTÓN"
    property real letterSpacing: 1.5
    property int fontSize: 13
    
    Layout.preferredWidth: 200
    Layout.preferredHeight: 48
    
    contentItem: Text {
        text: control.label.toUpperCase()
        color: Theme.textMain // This is already the new semantic token
        font.bold: true
        font.pixelSize: control.fontSize
        font.letterSpacing: control.letterSpacing
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    
    background: Rectangle {
        radius: height / 2
        color: control.highlighted ? control.accentColor : "transparent"
        border.color: control.accentColor
        border.width: 1.5
        
        // Efecto visual al presionar
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: "white"
            opacity: control.pressed ? 0.1 : 0
        }
    }
}
