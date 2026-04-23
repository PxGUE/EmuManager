import QtQuick
import "../system"

/**
 * ChameleonEffect.qml
 * Componente reactivo que centraliza la estética adaptativa en la UI.
 */
QtObject {
    id: chameleonEffect

    // Color actual (conectado al controlador de Python)
    readonly property color adaptiveColor: chameleonController ? chameleonController.currentColor : Theme.accentColor
    readonly property bool isDefault: adaptiveColor == "#025E73" || adaptiveColor == Theme.accentColor
    
    // Versiones derivadas para efectos de UI
    readonly property color lightAccent: Qt.lighter(adaptiveColor, 1.2)
    readonly property color darkAccent: Qt.darker(adaptiveColor, 1.5)
    readonly property color glassAccent: Qt.rgba(adaptiveColor.r, adaptiveColor.g, adaptiveColor.b, 0.2)

    // Función para adaptar a una nueva carátula
    function adaptTo(imagePath) {
        if (chameleonController) {
            chameleonController.adapt_to_image(imagePath)
        }
    }

    // Función para resetear a los valores del tema
    function reset() {
        if (chameleonController) {
            chameleonController.reset_to_default()
        }
    }
}
