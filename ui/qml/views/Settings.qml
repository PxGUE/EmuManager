import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../components"

Item {
    id: settingsRoot

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 30
            Layout.margins: 40

            Label {
                text: bridge.translate("set_title")
                font.pixelSize: 32
                font.bold: true
                color: "white"
            }

            // LANGUAGE
            Rectangle {
                Layout.fillWidth: true
                height: 80
                radius: 16
                color: "#16181f"
                border.color: "#252830"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 20

                    ColumnLayout {
                        spacing: 2
                        Label {
                            text: bridge.translate("set_lang_lbl")
                            font.pixelSize: 14
                            font.bold: true
                            color: "white"
                        }
                        Label {
                            text: "Select application language"
                            font.pixelSize: 11
                            color: "#666677"
                        }
                    }

                    Item { Layout.fillWidth: true }

                    ComboBox {
                        model: ["Español", "English"]
                        currentIndex: bridge.currentLanguage === "es" ? 0 : 1
                        onActivated: {
                            bridge.changeLanguage(currentIndex === 0 ? "es" : "en")
                        }
                        Layout.preferredWidth: 150
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: "#252830" }

            // PATHS
            ColumnLayout {
                spacing: 16
                Layout.fillWidth: true

                PathSetting {
                    title: bridge.translate("set_emus_title")
                    subtitle: bridge.translate("set_emus_sub")
                    path: bridge.installPath
                    onBrowse: bridge.browseInstallPath()
                }

                PathSetting {
                    title: bridge.translate("set_roms_title")
                    subtitle: bridge.translate("set_roms_sub")
                    path: bridge.romsPath
                    onBrowse: bridge.browseRomsPath()
                }
            }

            Label {
                text: bridge.translate("set_auto_save")
                font.pixelSize: 11
                color: "#666677"
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: "#252830" }

            // SCRAPERS
            ColumnLayout {
                spacing: 12
                Layout.fillWidth: true

                Label {
                    text: bridge.translate("set_scrapers_title")
                    font.pixelSize: 14
                    font.bold: true
                    color: "#4da6ff"
                    font.letterSpacing: 2
                    Layout.bottomMargin: 4
                }
                Label {
                    text: bridge.translate("set_scrapers_sub")
                    font.pixelSize: 12
                    color: "#888899"
                    Layout.bottomMargin: 12
                }

                Repeater {
                    model: bridge.scraperProviders
                    delegate: ProviderCard {
                        providerId: modelData.id
                        name: modelData.name
                        type: modelData.type
                        enabled: modelData.enabled
                    }
                }
            }

            Item { Layout.fillHeight: true }

            Button {
                text: bridge.translate("set_btn_about")
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 240
                onClicked: aboutDialog.open()
            }
        }
    }

    // Modal placeholders (About Dialog simplified)
    Dialog {
        id: aboutDialog
        title: bridge.translate("set_about_title")
        anchors.centerIn: parent
        width: 400
        modal: true
        standardButtons: Dialog.Close

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            Label { text: "EmuManager"; font.pixelSize: 24; font.bold: true; Layout.alignment: Qt.AlignHCenter }
            Label { text: "v" + bridge.appVersion; color: "#888"; Layout.alignment: Qt.AlignHCenter }
            Label { text: bridge.translate("set_about_desc"); wrapMode: Text.WordWrap; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
        }
    }
}
