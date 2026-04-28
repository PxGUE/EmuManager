import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../system"

ColumnLayout {
    id: root
    property string label: ""
    property string text: ""
    signal textUpdated(string value)
    
    spacing: 6
    
    Text { 
        text: root.label.toUpperCase()
        color: root.activeFocus ? Theme.accentColor : Theme.textMuted
        font.pixelSize: 10
        font.bold: true 
        font.letterSpacing: 1.5
        
        Behavior on color { ColorAnimation { duration: 200 } }
    }
    
    TextField {
        id: inputField
        Layout.fillWidth: true
        text: root.text
        color: Theme.textMain
        font.pixelSize: 14
        font.bold: false
        leftPadding: 15
        rightPadding: 15
        topPadding: 12
        bottomPadding: 12
        
        background: Rectangle { 
            color: inputField.activeFocus ? Theme.cardHoverBackground : Theme.controlBackground
            radius: Theme.radiusSmall
            border.color: inputField.activeFocus ? Theme.accentColor : Theme.cardBorder
            border.width: 1.5
            
            Behavior on color { ColorAnimation { duration: 200 } }
            Behavior on border.color { ColorAnimation { duration: 200 } }
            
            // Subtle glow on focus
            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: "transparent"
                border.color: Theme.accentColor
                border.width: 2
                opacity: inputField.activeFocus ? 0.3 : 0
                scale: inputField.activeFocus ? 1.02 : 1.0
                
                Behavior on opacity { NumberAnimation { duration: 300 } }
                Behavior on scale { NumberAnimation { duration: 300; easing.type: Easing.OutBack } }
            }
        }
        
        onTextChanged: root.textUpdated(text)
    }
}

