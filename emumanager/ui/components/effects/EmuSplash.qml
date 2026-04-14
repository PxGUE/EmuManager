import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import ".."

Rectangle {
    id: splashRoot
    anchors.fill: parent
    color: Theme.backgroundVoid // Deep void for premium contrast
    z: 100
    
    // --- ESTADOS Y CONTROL ---
    property bool isLoaded: false
    property string statusText: I18n.t.initializing
    property real progress: 0.0
    property bool introPhase: false
    readonly property bool isActuallyDone: isLoaded && introTimer.finished
    
    onProgressChanged: {
        if (progress >= 1.0 && !introPhase) {
            introPhase = true
            introTimer.start()
        }
    }

    visible: opacity > 0
    opacity: isActuallyDone ? 0 : 1
    Behavior on opacity { NumberAnimation { duration: 1200; easing.type: Easing.InOutCubic } }

    // --- 1. BACKGROUND ENGINE (KINETIC NEBULA) ---
    Item {
        id: nebulaContainer
        anchors.fill: parent
        opacity: introPhase ? 0.3 : 1.0
        Behavior on opacity { NumberAnimation { duration: 2000 } }

        // Glow A (Cyan)
        Rectangle {
            width: parent.width * 1.5; height: width; radius: width/2
            x: -width * 0.4; y: -height * 0.3
            opacity: 0.12
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.accentElectric }
                GradientStop { position: 1.0; color: "transparent" }
            }
            NumberAnimation on rotation { from: 0; to: 360; duration: 60000; loops: Animation.Infinite }
        }

        // Glow B (Porsche Orange / Accent)
        Rectangle {
            width: parent.width * 1.2; height: width; radius: width/2
            x: parent.width - width * 0.6; y: parent.height - height * 0.4
            opacity: 0.08
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.accentColor }
                GradientStop { position: 1.0; color: "transparent" }
            }
            NumberAnimation on rotation { from: 360; to: 0; duration: 80000; loops: Animation.Infinite }
        }
    }



    // --- 3. MAIN CONTENT ---
    ColumnLayout {
        id: contentLayout
        anchors.centerIn: parent
        spacing: 60
        
        // --- LOGO BLOCK ---
        Item {
            Layout.preferredWidth: 120; Layout.preferredHeight: 120
            Layout.alignment: Qt.AlignCenter
            
            // Background Glow (Manual simulation because MultiEffect failed)
            Rectangle {
                anchors.centerIn: parent
                width: 160; height: 160; radius: 80
                opacity: (1.0 - logoImg.opacity) * 0.15 + (logoImg.scale - 1.0) * 0.5
                visible: !introPhase
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Theme.accentElectric }
                    GradientStop { position: 1.0; color: "transparent" }
                }
            }

            // Halo orbital
            Rectangle {
                anchors.centerIn: parent
                width: 110; height: 110; radius: 55
                color: "transparent"
                border.color: Theme.accentElectric
                border.width: 1
                opacity: introPhase ? 0 : 0.2
                scale: introPhase ? 1.5 : 1.0
                Behavior on opacity { NumberAnimation { duration: 1000 } }
                Behavior on scale { NumberAnimation { duration: 1500; easing.type: Easing.OutQuint } }
                
                RotationAnimation on rotation { from: 0; to: 360; duration: 10000; loops: Animation.Infinite }
            }

            Image {
                id: logoImg
                source: "../../assets/logo.svg"
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                smooth: true; antialiasing: true
                
                opacity: introPhase ? 0.0 : 1.0
                scale: introPhase ? 1.2 : 1.0
                
                Behavior on opacity { NumberAnimation { duration: 800 } }
                Behavior on scale { NumberAnimation { duration: 1200; easing.type: Easing.InBack } }

                // Breath animation
                SequentialAnimation on scale {
                    running: !introPhase; loops: Animation.Infinite
                    NumberAnimation { from: 1.0; to: 1.05; duration: 3000; easing.type: Easing.InOutQuad }
                    NumberAnimation { from: 1.05; to: 1.0; duration: 3000; easing.type: Easing.InOutQuad }
                }
            }
        }

        // --- PROGRESS & STATUS ---
        Column {
            Layout.alignment: Qt.AlignCenter; spacing: 20; width: 300
            opacity: introPhase ? 0 : 1
            visible: opacity > 0
            Behavior on opacity { NumberAnimation { duration: 500 } }

            // High-Tech Loading Bar
            Rectangle {
                width: parent.width; height: 4; radius: 2; color: Qt.rgba(1,1,1,0.1)
                clip: true
                
                // Final gradient line
                Rectangle {
                    id: progressBar
                    width: Math.max(10, parent.width * progress)
                    height: parent.height; radius: 2
                    
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: Theme.accentColor }
                        GradientStop { position: 1.0; color: Theme.accentElectric }
                    }
                    
                    Behavior on width { NumberAnimation { duration: 800; easing.type: Easing.OutQuint } }
                    
                    // Light travel pulse
                    Rectangle {
                        width: 40; height: parent.height
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 0.5; color: "#ffffff" }
                            GradientStop { position: 1.0; color: "transparent" }
                        }
                        opacity: 0.5
                        SequentialAnimation on x {
                            loops: Animation.Infinite; running: !introPhase
                            NumberAnimation { from: -40; to: progressBar.width + 100; duration: 1500; easing.type: Easing.InOutSine }
                        }
                    }
                }
            }

            Text {
                width: parent.width; horizontalAlignment: Text.AlignHCenter
                text: statusText.toUpperCase()
                color: Theme.textMuted
                font.pixelSize: 9; font.bold: true; font.letterSpacing: 4
                opacity: 0.8
            }
        }

        // --- CINEMATIC WELCOME TEXT (Appears after load) ---
        Item {
            Layout.preferredWidth: 400; Layout.preferredHeight: 50
            Layout.alignment: Qt.AlignCenter
            visible: introPhase
            
            Text {
                id: welcomeTxt
                anchors.centerIn: parent
                text: "SYSTEM READY"
                color: Theme.textMain
                font.pixelSize: 20; font.bold: true; font.letterSpacing: 18
                opacity: introPhase ? 1 : 0
                scale: introPhase ? 1 : 0.9
                
                Behavior on opacity { NumberAnimation { duration: 1500; easing.type: Easing.OutQuad } }
                Behavior on scale { NumberAnimation { duration: 2500; easing.type: Easing.OutCubic } }
                
                // Letter spacing animation
                NumberAnimation on font.letterSpacing {
                    running: introPhase; from: 40; to: 18; duration: 2000; easing.type: Easing.OutQuint
                }
            }
            
            // Pulse behind text
            Rectangle {
                anchors.centerIn: parent; width: welcomeTxt.width * 1.2; height: 1
                opacity: introPhase ? 0.3 : 0
                color: Theme.accentElectric
                Behavior on opacity { NumberAnimation { duration: 2000 } }
            }
        }
    }

    // Timer to control the splash duration after load
    Timer {
        id: introTimer
        property bool finished: false
        interval: 1200 
        repeat: false
        onTriggered: finished = true
    }
}
