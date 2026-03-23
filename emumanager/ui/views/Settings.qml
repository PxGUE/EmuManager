import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: settingsView
    objectName: "settingsView"

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 15
        width: 320

        Text {
            text: "ScreenScraper Credentials"
            font.pixelSize: 18
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
            Layout.bottomMargin: 10
        }

        TextField {
            id: ssUsername
            placeholderText: "Username"
            Layout.fillWidth: true
        }

        TextField {
            id: ssPassword
            placeholderText: "Password"
            echoMode: TextInput.Password
            Layout.fillWidth: true
        }

        Button {
            text: "Save Securely"
            Layout.alignment: Qt.AlignRight
            highlighted: true
            onClicked: {
                if(ssUsername.text !== "" && ssPassword.text !== "") {
                    // LLamamos al método expuesto en MainController bajo @Slot
                    // mainCtrl está expuesto desde el main.qml de forma global accesible.
                    mainCtrl.saveScreenScraperCredentials(ssUsername.text, ssPassword.text)
                    
                    // Limpia el campo por seguridad luego de enviar el evento
                    ssPassword.text = "" 
                    ssUsername.placeholderText = "Saved!"
                }
            }
        }
    }
}
