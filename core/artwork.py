import os
import json
import asyncio
import aiohttp
import core.scrapers.metadata.screenscraper as screenscraper
from core.scrapers.artwork.libretro import LibretroScraper
from core.scrapers.artwork.steamgriddb import SteamGridDBScraper
from . import metadata
from . import config
from typing import Optional, List, Dict, Any

class ArtworkHub:
    """
    Coordinador central de descargas de arte.
    """
    def __init__(self, session: aiohttp.ClientSession, configs: List[Dict]):
        self.session = session
        self.configs = configs
        
        # Localizamos los scrapers activados
        ss_cfg = next((c for c in configs if c["id"] == "screenscraper"), None)
        lr_cfg = next((c for c in configs if c["id"] == "libretro"), None)
        sg_cfg = next((c for c in configs if c["id"] == "steamgriddb"), None)
        
        # ScreenScraper (Requiere cuenta)
        self.ss = None
        if ss_cfg and ss_cfg.get("enabled"):
            user = ss_cfg.get("user")
            pw = ss_cfg.get("password")
            devid = ss_cfg.get("devid")
            devpass = ss_cfg.get("devpassword")
            if user and pw:
                self.ss = screenscraper.ScreenScraperScraper(user, pw, devid, devpass)

        # Libretro (Fuzzy Match vía CDN)
        self.libretro = LibretroScraper() if lr_cfg and lr_cfg.get("enabled") else None

        # SteamGridDB (Requiere API Key)
        self.sgdb = None
        if sg_cfg and sg_cfg.get("enabled"):
            api_key = sg_cfg.get("api_key")
            if api_key:
                self.sgdb = SteamGridDBScraper(api_key)

    async def download_for_game(self, platform: str, game_name: str, rom_path: str, **kwargs) -> bool:
        """
        Descarga arte para un juego específico usando los scrapers disponibles.
        Implementa recursividad de búsqueda para casos difíciles (hacks o subtítulos).
        """
        emu_id = kwargs.get("emu_id", "unknown")
        caratula_path = obtener_ruta_caratula(rom_path, emu_id, "2d")
        caratula_3d_path = obtener_ruta_caratula(rom_path, emu_id, "3d")
        
        # Estrategia de búsqueda por niveles de profundidad
        search_terms = [game_name]
        words = game_name.split()
        if len(words) > 1:
            search_terms.append(" ".join(words[:-1])) # Quitar última palabra
            if len(words) > 2:
                search_terms.append(" ".join(words[:-2])) # Quitar dos últimas
        
        # Deduplicar términos manteniendo el orden (priorizar el nombre completo)
        final_terms = []
        for term in search_terms:
            if term and term not in final_terms:
                final_terms.append(term)

        for attempt_name in final_terms:
            # --- 1. Intento con ScreenScraper (El más completo) ---
            if self.ss:
                ss_id = kwargs.get("ss_platform_id")
                rom_file = os.path.basename(rom_path)
                res = await self.ss.fetch(self.session, attempt_name, ss_platform_id=ss_id, rom_file=rom_file)
                if res:
                    # Descargar variados (2D, 3D, Background, Logo, Manual)
                    if res.get("boxart_url") and not os.path.exists(caratula_path):
                        await _descargar_archivo(self.session, res["boxart_url"], caratula_path)
                    
                    if res.get("boxart_3d_url") and not os.path.exists(caratula_3d_path):
                        await _descargar_archivo(self.session, res["boxart_3d_url"], caratula_3d_path)

                    if res.get("background_url"):
                        bg_path = obtener_ruta_background(rom_path, emu_id)
                        if not os.path.exists(bg_path):
                            await _descargar_archivo(self.session, res["background_url"], bg_path)
                    
                    if res.get("logo_url"):
                        logo_path = obtener_ruta_logo(rom_path, emu_id)
                        if not os.path.exists(logo_path):
                            await _descargar_archivo(self.session, res["logo_url"], logo_path)
                    
                    if res.get("manual_url"):
                        manual_path = obtener_ruta_manual(rom_path, emu_id)
                        if not os.path.exists(manual_path):
                            await _descargar_archivo(self.session, res["manual_url"], manual_path)

            # --- 2. Intento con Libretro (Boxarts) ---
            if self.libretro and not os.path.exists(caratula_path):
                res = await self.libretro.fetch(self.session, attempt_name, platform=platform)
                if res and res.get("boxart_url"):
                    await _descargar_archivo(self.session, res["boxart_url"], caratula_path)

            # --- 3. Intento con SteamGridDB (Assets Premium) ---
            if self.sgdb and not os.path.exists(caratula_path):
                res = await self.sgdb.fetch(self.session, attempt_name)
                if res:
                    # Descargar Carátula
                    if res.get("boxart_url") and not os.path.exists(caratula_path):
                        await _descargar_archivo(self.session, res["boxart_url"], caratula_path)
                    
                    # Descargar Fondo
                    if res.get("background_url"):
                        bg_path = obtener_ruta_background(rom_path, emu_id)
                        if not os.path.exists(bg_path):
                            await _descargar_archivo(self.session, res["background_url"], bg_path)
                    
                    # Descargar Logo
                    if res.get("logo_url"):
                        logo_path = obtener_ruta_logo(rom_path, emu_id)
                        if not os.path.exists(logo_path):
                            await _descargar_archivo(self.session, res["logo_url"], logo_path)
            
            # Si tras cualquier scraper ya tenemos carátula, salimos de los intentos de nombre
            if os.path.exists(caratula_path):
                return True
                
        return os.path.exists(caratula_path)


# ── UTILIDADES DE RUTAS ──────────────────────────────────────────────

def obtener_ruta_caratula(ruta_rom: str, emu_id: str = "unknown", type: str = "2d") -> str:
    """Retorna la ruta centralizada donde debe guardarse/leerse la carátula de un juego."""
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(config.MEDIA_DIR, "scraped", emu_id, type, f"{game_name}.png")

def obtener_ruta_background(ruta_rom: str, emu_id: str = "unknown") -> str:
    """Retorna la ruta centralizada para el fondo (fanart) de un juego."""
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(config.MEDIA_DIR, "scraped", emu_id, "backgrounds", f"{game_name}.jpg")

def obtener_ruta_logo(ruta_rom: str, emu_id: str = "unknown") -> str:
    """Retorna la ruta centralizada para el logo (marquee) de un juego."""
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(config.MEDIA_DIR, "scraped", emu_id, "logos", f"{game_name}.png")

def obtener_ruta_manual(ruta_rom: str, emu_id: str = "unknown") -> str:
    """Retorna la ruta centralizada para el manual (pdf o png) de un juego."""
    game_name = os.path.splitext(os.path.basename(ruta_rom))[0]
    return os.path.join(config.MEDIA_DIR, "scraped", emu_id, "manuals", f"{game_name}.pdf")

def tiene_caratula(ruta_rom: str, emu_id: str = "unknown") -> bool:
    """Verifica si existe el archivo de carátula para un juego."""
    return os.path.exists(obtener_ruta_caratula(ruta_rom, emu_id))

def obtener_ruta_logo_consola(id_emu: str) -> str:
    """
    Localiza el logo SVG o PNG de una consola en la carpeta de recursos del sistema.
    """
    base_path = os.path.join(config.MEDIA_DIR, "consolas", id_emu)
    for ext in (".svg", ".png"):
        full_path = os.path.abspath(base_path + ext)
        if os.path.exists(full_path):
            return full_path
    return os.path.abspath(base_path + ".png")

def obtener_ruta_fondo_consola(id_o_emu: Any) -> str:
    """
    Obtiene la ruta del fondo decorativo local para una consola.
    """
    bg_id = id_o_emu if isinstance(id_o_emu, str) else id_o_emu.get("console_id", id_o_emu.get("id"))
    bg_dir = os.path.join(config.BASE_DIR, "fondos_consolas")
    return os.path.abspath(os.path.join(bg_dir, f"{bg_id}.jpg"))

async def _descargar_archivo(session: aiohttp.ClientSession, url: str, ruta_destino: str, retries: int = 1) -> bool:
    """
    Función interna para descargar un binario y guardarlo en disco.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(retries + 1):
        try:
            async with session.get(url, headers=headers, timeout=15) as resp:
                if resp.status == 200:
                    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                    with open(ruta_destino, "wb") as f:
                        f.write(await resp.read())
                    return True
        except:
            if attempt < retries:
                await asyncio.sleep(1)
    return False

# Mapeos de Consolas para scrapers externos
EXTENSION_PLATFORM_MAP = {
    ".nes": "Nintendo - Nintendo Entertainment System",
    ".sfc": "Nintendo - Super Nintendo Entertainment System",
    ".smc": "Nintendo - Super Nintendo Entertainment System",
    ".gba": "Nintendo - Game Boy Advance",
    ".gb":  "Nintendo - Game Boy",
    ".gbc": "Nintendo - Game Boy Color",
    ".n64": "Nintendo - Nintendo 64",
    ".z64": "Nintendo - Nintendo 64",
    ".v64": "Nintendo - Nintendo 64",
    ".gen": "Sega - Mega Drive - Genesis",
    ".md":  "Sega - Mega Drive - Genesis",
    ".smd": "Sega - Mega Drive - Genesis",
    ".sms": "Sega - Master System - Mark III",
    ".gg":  "Sega - Game Gear",
    ".pce": "NEC - PC Engine - TurboGrafx 16",
}

def get_platform_for_rom(emu_id: str, ruta_rom: str, default_platform: Optional[str]) -> Optional[str]:
    """
    Resuelve el nombre de plataforma exacto requerido por Libretro basándose en la extensión.
    """
    ext = os.path.splitext(ruta_rom)[1].lower()
    plat = EXTENSION_PLATFORM_MAP.get(ext)
    return plat if plat else default_platform

async def descargar_caratulas_biblioteca(juegos: list, emu_map: dict, **kwargs) -> dict:
    """
    Descarga masiva de arte para la biblioteca del usuario.
    """
    stats = {"ok": 0, "skip": 0, "fail": 0}
    fails_list = []
    configs = metadata.get_providers_config()
    on_progress = kwargs.get("on_progress")
    total = len(juegos)

    async with aiohttp.ClientSession() as session:
        hub = ArtworkHub(session, configs)
        semaphore = asyncio.Semaphore(5)

        async def _worker(idx, juego):
            async with semaphore:
                emu_id = juego.get("id_emu", "")
                ruta = juego.get("ruta", "")
                nombre = juego.get("nombre", "")
                
                # Resolver plataforma técnica
                emu_info = emu_map.get(emu_id, {})
                libretro_p = emu_info.get("libretro_platform", emu_info.get("console", ""))
                plat = get_platform_for_rom(emu_id, ruta, libretro_p)
                ss_id = emu_info.get("screenscraper_id")
                
                if not plat:
                    stats["skip"] += 1
                else:
                    ok = await hub.download_for_game(plat, nombre, ruta, ss_platform_id=ss_id, emu_id=emu_id)
                    if ok: 
                        stats["ok"] += 1
                    else: 
                        stats["fail"] += 1
                        fails_list.append(nombre)
                
                if on_progress:
                    on_progress(idx + 1, total, nombre)

        await asyncio.gather(*[_worker(i, j) for i, j in enumerate(juegos)])

    # Reporte Final
    print("\n" + "="*45)
    print("🎨 RESUMEN DE ARTE Y CARÁTULAS")
    print(f"   ✅ Descargados: {stats['ok']}")
    print(f"   ⏭️ Omitidos:    {stats['skip']}")
    print(f"   ❌ Fallidos:    {stats['fail']}")
    
    if fails_list:
        print("\n--- 🔍 JUEGOS SIN CARÁTULA ENCONTRADA ---")
        for f in sorted(fails_list)[:25]:
            print(f" • {f}")
        if len(fails_list) > 25:
            print(f" ... y {len(fails_list)-25} más.")
    print("="*45 + "\n")

    return stats
