import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../system"

ColumnLayout {
    id: root
    property string label: ""
    property string text: ""
    signal textUpdated(string value)
    
    spacing: 5
    
    Text { 
        text: root.label
        color: Theme.textMuted
        font.pixelSize: 10
        font.bold: true 
    }
    
    TextField {
        Layout.fillWidth: true
        text: root.text
        color: Theme.textMain
        font.pixelSize: 14
        font.bold: true
        
        background: Rectangle { 
            color: Theme.controlBackground; radius: 8; 
            border.color: parent.focus ? Theme.accentColor : Theme.cardBorder
            border.width: parent.focus ? 2 : 1
        }
        
        onTextChanged: root.textUpdated(text)
    }
}
