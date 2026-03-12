import asyncio
import aiohttp
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from core.artwork import descargar_caratulas_biblioteca
from core.metadata import descargar_metadata_biblioteca

async def main():
    # Clear previous test data
    if os.path.exists("data/metadata.json"):
        os.remove("data/metadata.json")

    juegos = [
        {"id_emu": "mgba", "ruta": "roms/Pokemon Ruby.gba", "nombre": "Pokemon Ruby Version"},
        {"id_emu": "mgba", "ruta": "roms/Pokemon Sapphire.gba", "nombre": "Pokemon Sapphire Version"},
        {"id_emu": "mgba", "ruta": "roms/Pokemon Liquid Crystal.gba", "nombre": "Pokemon Liquid Crystal"},
        {"id_emu": "mgba", "ruta": "roms/Pokemon AshGray.gba", "nombre": "Pokemon AshGray"},
    ]
    
    emu_map = {"mgba": "Nintendo - Game Boy Advance"}

    # Test Metadata Scrape
    print("\n--- TEST METADATA HUB V3 (CONCURRENT) ---")
    def on_progress(idx, tot, nombre):
        print(f"  [{idx}/{tot}] Scrapeando: {nombre}")

    stats_meta = await descargar_metadata_biblioteca(juegos, emu_map, on_progress=on_progress)
    print(f"\nStats Metadata: {stats_meta}")

    # Test Artwork Scrape
    print("\n--- TEST ARTWORK HUB V3 (CONCURRENT) ---")
    stats_art = await descargar_caratulas_biblioteca(juegos, emu_map, on_progress=on_progress)
    print(f"\nStats Artwork: {stats_art}")

if __name__ == "__main__":
    if not os.path.exists("roms"): os.makedirs("roms")
    for f in ["roms/Pokemon Ruby.gba", "roms/Pokemon Sapphire.gba", "roms/Pokemon Liquid Crystal.gba", "roms/Pokemon AshGray.gba"]:
        with open(f, 'a'): os.utime(f, None)
            
    asyncio.run(main())
