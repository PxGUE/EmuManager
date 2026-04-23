import QtQuick
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import "../system"

Item {
    id: smartImageRoot
    
    property string source: ""
    property int fillMode: Image.PreserveAspectFit
    property int radius: 0
    property bool asynchronous: true
    
    Rectangle {
        id: placeholder
        anchors.fill: parent; radius: smartImageRoot.radius
        color: Theme.controlBackground
        visible: mainImage.status !== Image.Ready
        
        Text {
            anchors.centerIn: parent
            text: "🖼️"; font.pixelSize: 24; opacity: 0.2
        }
        
        // Animación de pulso para el placeholder
        SequentialAnimation on opacity {
            loops: Animation.Infinite
            NumberAnimation { from: 0.3; to: 0.6; duration: 1000; easing.type: Easing.InOutQuad }
            NumberAnimation { from: 0.6; to: 0.3; duration: 1000; easing.type: Easing.InOutQuad }
        }
    }

    Image {
        id: mainImage
        anchors.fill: parent
        source: (smartImageRoot.source && smartImageRoot.source !== "undefined") ? (smartImageRoot.source.startsWith("file://") ? smartImageRoot.source : "file:///" + smartImageRoot.source) : ""
        fillMode: smartImageRoot.fillMode
        asynchronous: smartImageRoot.asynchronous
        opacity: status === Image.Ready ? 1 : 0
        visible: status === Image.Ready
        
        Behavior on opacity { NumberAnimation { duration: 400; easing.type: Easing.OutQuad } }
    }
    
    // Máscara para el radio si es necesario
    layer.enabled: smartImageRoot.radius > 0
    layer.effect: OpacityMask {
        maskSource: Rectangle {
            width: smartImageRoot.width; height: smartImageRoot.height
            radius: smartImageRoot.radius
        }
    }
}
