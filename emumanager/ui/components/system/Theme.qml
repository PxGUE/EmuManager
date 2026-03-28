pragma Singleton
import QtQuick

/**
 * Theme.qml
 * MOTOR DE ESTÉTICA "SEMANTIC PORSCHE"
 * Este archivo es la ÚNICA fuente de verdad para el color en EmuManager.
 * Organizado por categorías intuitivas para facilitar la personalización global.
 */
QtObject {
    id: theme

    // ==========================================
    // --- 🏎️ PALETA DE MARCA (REFERENCIA) ---
    // ==========================================
    // No usar estas propiedades directamente en Componentes. Usar los TOKENS de abajo.
    readonly property color _p1: "#025E73" // Deep Teal
    readonly property color _p2: "#011F26" // Darkest Teal
    readonly property color _p3: "#A5A692" // Sage Grey
    readonly property color _p4: "#BFB78F" // Sand Olive
    readonly property color _p5: "#F2A71B" // Porsche Orange

    // ==========================================
    // --- 🧩 1. APP LAYOUT (FONDOS GLOBALES) ---
    // ==========================================
    readonly property color windowBackground: _p2    // Fondo base de la ventana principal.
    readonly property color viewBackground: _p2      // Fondo de las vistas (Dashboard, Library, etc).
    readonly property color sidebarBackground: "#0a0a0f" // Fondo de la barra lateral de navegación.
    readonly property color panelBackground: _p1     // Fondo de paneles sólidos y modales.
    readonly property color surfaceBackground: "#0d0d12" // Fondo para contenedores oscuros secundarios.
    readonly property color divider: "#ffffff1a"    // Líneas divisorias sutiles.

    // ==========================================
    // --- 🎴 2. CARDS & PANELS (TARJETAS) ---
    // ==========================================
    // Afecta a RomCard, ConsoleCard, DashboardStatCard, etc.
    readonly property color cardBackground: "#0d0d12" // Fondo base de todas las tarjetas.
    readonly property color cardBorder: "#ffffff1a"   // Borde sutil por defecto (GlassBorder).
    readonly property color cardHoverBackground: "#16161c" // Fondo cuando el ratón está encima.
    readonly property color cardHoverBorder: _p5      // Borde cuando el ratón está encima (Accent).
    readonly property color cardGlow: _p1            // Color del resplandor/sombra de la tarjeta.
    readonly property real cardOpacity: 0.85          // Opacidad para tarjetas tipo "Glass".
    readonly property real glowOpacity: 0.15          // Opacidad para resplandores ambientales.

    // ==========================================
    // --- ✍️ 3. TYPOGRAPHY (TEXTOS) ---
    // ==========================================
    readonly property color textMain: "#ffffff"       // Títulos y etiquetas de alta importancia.
    readonly property color textDim: _p3              // Párrafos y descripciones secundarias.
    readonly property color textMuted: _p4            // Datos técnicos o texto de menor jerarquía.
    readonly property color textAccent: _p5           // Texto resaltado o con color de marca.

    // ==========================================
    // --- 🔘 4. CONTROLS (BOTONES E INPUTS) ---
    // ==========================================
    readonly property color accentColor: _p5          // Color de interacción principal.
    readonly property color controlBackground: "#16161c" // Fondo de botones y campos de entrada.
    readonly property color controlBorder: "#33ffffff"   // Borde de controles desactivados.
    readonly property color controlHighlight: _p5       // Borde o acento de control enfocado.
    readonly property color danger: "#e74c3c"         // Acciones destructivas (Borrar, Desinstalar).

    // ==========================================
    // --- 🚥 5. STATUS & FEEDBACK ---
    // ==========================================
    readonly property color statusSuccess: "#2ecc71"  // Procesos OK, Online, Instalado.
    readonly property color statusWarning: "#f39c12"  // Escaneando, Scraping, Pendiente.
    readonly property color statusDanger: "#e74c3c"   // Error, Desconectado.
    readonly property color statusInfo: "#3498db"     // Info técnica, Notificaciones.

    // ==========================================
    // --- 📏 6. ESTRUCTURA (RADII & SPACING) ---
    // ==========================================
    // Mantener para "Zero-Hex", pero secundario frente al color.
    readonly property real radiusSmall: 8; readonly property real radiusMedium: 16
    readonly property real radiusLarge: 24; readonly property real radiusExtraLarge: 32
    readonly property real radiusCircle: 999
    readonly property real spaceSmall: 8; readonly property real spaceMedium: 15
    readonly property real spaceLarge: 25; readonly property real spaceExtraLarge: 45
    readonly property real borderThin: 1.0; readonly property real borderThick: 2.2
    readonly property real glowRadius: 20; readonly property int glowSamples: 14

    // ==========================================
    // --- ✒️ 7. TIPOGRAFÍA (FONT SIZES) ---
    // ==========================================
    readonly property real fontMicro: 9; readonly property real fontSmall: 10
    readonly property real fontBody: 13; readonly property real fontHeader: 18
    readonly property real fontTitle: 28; readonly property real fontDisplay: 42

    // --- 🎮 8. EMULATOR ACCENTS (Sync with repositories.json) ---
    // ==========================================
    readonly property color emuRetroArch: "#FF4E11"
    readonly property color emuDolphin: "#3498DB"
    readonly property color emuPPSSPP: "#00E5FF"
    readonly property color emuPCSX2: "#3A7BD5"
    readonly property color emuRPCS3: "#FFFFFF"
    readonly property color emuDuckStation: "#FFD700" // Yellow accent for DuckStation
    
    // Compatibility aliases
    readonly property color accentRetroArch: emuRetroArch
    readonly property color accentDolphin: emuDolphin
    readonly property color accentPlayStation: emuPPSSPP
    readonly property color accentNintendo: "#FF4B2B"
    readonly property color accentSega: "#2C3E50"

    // Mapeo dinámico para plataformas
    readonly property color platSnes: accentNintendo; readonly property color platNes: accentNintendo
    readonly property color platGba: "#9D50BB"; readonly property color platN64: "#3A7BD5"
    readonly property color platPs1: accentPlayStation; readonly property color platPs2: accentPlayStation
    readonly property color platPsp: "#00AAFF"; readonly property color platDs: "#16A085"
    readonly property color platGc: "#8E44AD"; readonly property color platWii: "#FFFFFF"
    readonly property color platMegaDrive: accentSega; readonly property color platDreamcast: "#E67E22"
    readonly property color platGb: "#81822A"; readonly property color platGbc: "#C51C5B"
    readonly property color platUnknown: "#95A5A6"

    /**
     * Mapeo inteligente para obtener el color de una consola por su nombre.
     */
    function colorForPlatform(name) {
        if (!name) return accentColor;
        var p = name.toLowerCase();
        if (p.includes("gba")) return platGba;
        if (p.includes("snes") || p.includes("super nintendo")) return platSnes;
        if (p.includes("n64") || p.includes("nintendo 64")) return platN64;
        if (p.includes("ds")) return platDs;
        if (p.includes("gamecube") || p.includes("gc")) return platGc;
        if (p.includes("wii")) return platWii;
        if (p.includes("ps1") || p.includes("playstation")) return platPs1;
        if (p.includes("ps2")) return platPs2;
        if (p.includes("psp")) return platPsp;
        if (p.includes("mega drive") || p.includes("genesis")) return platMegaDrive;
        if (p.includes("dreamcast")) return platDreamcast;
        if (p.includes("game boy color") || p.includes("gbc")) return platGbc;
        if (p.includes("game boy") || p.includes("gb")) return platGb;
        return accentColor;
    }
}
