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
    
    // --- NUEVA IDENTIDAD: KINETIC NEBULA ---
    readonly property color _n1: "#00f2ff" // Electric Cyan (Nebula Accent)
    readonly property color _n2: "#050508" // Void Black (Maximum Contrast)
    readonly property color _n3: "#0a1015" // Deep Pod (Background for HUD stats)
    readonly property color _n4: "#ffffff1a" // Glass Border (Low Opacity)
    readonly property color _n5: "#33ffffff" // Glass Alpha (Medium Opacity)
    readonly property color _n6: "#000000"   // Pure Black
    readonly property color _n7: "#15ffffff" // Very Light White
    readonly property color _n8: "#25ffffff" // Light White
    
    // --- 🌏 UNIVERSAL TOKENS ---
    readonly property color transparent: "transparent"
    readonly property color white: "#ffffff"
    readonly property color black: "#000000"

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
    readonly property color accentElectric: _n1       // Acento Nebula (Reactor, HUD).
    readonly property color backgroundDeep: _n2       // Fondo ultra oscuro.
    readonly property color backgroundPod: _n3        // Fondo de pods estadísticos.
    
    // --- GLASSMORPHISM & OVERLAYS ---
    readonly property color glassPlain: _n6           // Negro puro para modales.
    readonly property color glassLight: _n7           // Blanco ultra-sutil (Overlays).
    readonly property color glassStrong: _n8          // Blanco sutil (Bordes Glass).
    
    readonly property color controlBackground: "#16161c" // Fondo de botones y campos de entrada.
    readonly property color controlBorder: "#33ffffff"   // Borde de controles desactivados.
    readonly property color controlHighlight: _p5       // Borde o acento de control enfocado.
    readonly property color danger: "#e74c3c"         // Acciones destructivas (Borrar, Desinstalar).
    
    // --- 🌙 OVERLAYS & HUD ---
    readonly property color overlayBackground: "#0a0a0f" // Fondo de overlays oscuros.
    readonly property color backgroundVoid: "#050508"    // Fondo negro HUD (Maximum black).

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

    // --- 🎮 8. EMULATOR ACCENTS (Mapeo Estático Robusto) ---
    // ==========================================
    readonly property color platSnes: "#FF4B2B"
    readonly property color platNes: "#FF4B2B"
    readonly property color platGba: "#9B59B6"
    readonly property color platN64: "#3498DB"
    readonly property color platPs1: "#00E5FF"
    readonly property color platPs2: "#00E5FF"
    readonly property color platPsp: "#00AAFF"
    readonly property color platDs: "#16A085"
    readonly property color platGc: "#8E44AD"
    readonly property color platWii: "#FFFFFF"
    readonly property color platMegaDrive: "#2C3E50"
    readonly property color platDreamcast: "#E67E22"
    readonly property color platGb: "#81822A"
    readonly property color platGbc: "#C51C5B"
    readonly property color platUnknown: "#95A5A6"

    readonly property color emuRetroArch: "#3498DB"
    readonly property color emuDolphin: "#00E5FF"
    readonly property color emuPPSSPP: "#00AAFF"
    readonly property color emuPCSX2: "#3498DB"
    readonly property color emuRPCS3: "#E74C3C"
    readonly property color emuDuckStation: "#F1C40F"

    /**
     * Motor de resolución de color infalible (Static Map para evitar errores de ámbito JS)
     * No recursivo para evitar StackOverflow.
     */
    function colorForPlatform(name) { return resolveColor("", name); }

    function resolveColor(c, platform) {
        // 1. Manejo de tipos ya resueltos (objetos de color o strings hex)
        if (typeof c === "object") return c;
        if (typeof c === "string" && (c.startsWith("#") || c.startsWith("rgba"))) return c;

        // 2. Mapeo estático de claves
        var map = {
            "platSnes": theme.platSnes,
            "platNes": theme.platNes,
            "platGba": theme.platGba,
            "platN64": theme.platN64,
            "platPs1": theme.platPs1,
            "platPs2": theme.platPs2,
            "platPsp": theme.platPsp,
            "platDs": theme.platDs,
            "platGc": theme.platGc,
            "platWii": theme.platWii,
            "platMegaDrive": theme.platMegaDrive,
            "platDreamcast": theme.platDreamcast,
            "platGb": theme.platGb,
            "platGbc": theme.platGbc,
            "accentColor": theme.accentColor,
            "emuRetroArch": theme.emuRetroArch,
            "emuDolphin": theme.emuDolphin,
            "emuPPSSPP": theme.emuPPSSPP,
            "emuPCSX2": theme.emuPCSX2,
            "emuRPCS3": theme.emuRPCS3,
            "emuDuckStation": theme.emuDuckStation
        };

        // Si la clave 'c' existe en el mapa, devolverla
        if (c && map[c] !== undefined) return map[c];

        // 3. Si no hay clave o no se encontró, buscar por nombre de plataforma (usando c o platform)
        var p = (c && c !== "") ? c.toLowerCase() : (platform ? platform.toLowerCase() : "");
        
        if (p.includes("snes")) return theme.platSnes;
        if (p.includes("nes")) return theme.platNes;
        if (p.includes("gba") || p.includes("advance")) return theme.platGba;
        if (p.includes("n64")) return theme.platN64;
        if (p.includes("ps1") || p.includes("playstation")) return theme.platPs1;
        if (p.includes("ps2")) return theme.platPs2;
        if (p.includes("psp")) return theme.platPsp;
        if (p.includes("ds")) return theme.platDs;
        if (p.includes("gc") || p.includes("cube")) return theme.platGc;
        if (p.includes("wii")) return theme.platWii;
        
        return theme.accentColor;
    }
}
