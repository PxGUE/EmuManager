pub mod scrapers;
pub use scrapers::{ScrapedMetadata, ScrapeQuery, MetadataSource};

pub async fn scrape_game(
    md5: &str,
    crc: &str,
    filename: &str,
    platform: &str,
    system_id: &str,
    ss_id: &str,
    ss_pass: &str,
    dev_id: &str,
    dev_pass: &str,
    media_dir_base: &str,
    skip_ss: bool,
    serial: &str,
    gametdb_mode: &str,
) -> Option<ScrapedMetadata> {
    let query = ScrapeQuery {
        md5: md5.to_string(),
        crc: crc.to_string(),
        filename: filename.to_string(),
        platform: platform.to_string(),
        system_id: system_id.to_string(),
        media_dir: media_dir_base.to_string(),
        ss_user: ss_id.to_string(),
        ss_pass: ss_pass.to_string(),
        dev_id: dev_id.to_string(),
        dev_pass: dev_pass.to_string(),
        serial: serial.to_string(),
        gametdb_mode: gametdb_mode.to_string(),
    };

    let mut sources: Vec<Box<dyn MetadataSource>> = Vec::new();
    
    // Prioridad 1: Local (Sostenibilidad Local-First)
    sources.push(Box::new(scrapers::local_nfo::LocalNfoSource));

    // Prioridad 1.5: Wikipedia (Keyless universal metadata)
    sources.push(Box::new(scrapers::wikipedia::WikipediaSource));

    // Prioridad 1.7: GameTDB (Especialista Nintendo/Sony + Serial)
    let plat_low = query.platform.to_lowercase();
    if plat_low == "wii" || plat_low == "gc" || plat_low == "gamecube" || plat_low == "nds" || plat_low == "ds" || plat_low == "3ds" ||
       plat_low == "snes" || plat_low == "nes" || plat_low == "gba" || plat_low == "gb" || plat_low == "gbc" || plat_low == "n64" ||
       plat_low == "ps1" || plat_low == "ps2" {
        sources.push(Box::new(scrapers::gametdb::GameTDBSource));
    }

    // Prioridad 2: ScreenScraper (Metadatos completos)
    if !skip_ss {
        sources.push(Box::new(scrapers::screenscraper::ScreenScraperSource));
    }
    
    // Prioridad 3: Libretro (Rescate ante fallos)
    sources.push(Box::new(scrapers::libretro::LibretroSource));

    let mut final_meta = ScrapedMetadata::default();
    let mut metadata_found = false;

    for source in sources {
        // Abortar si hay señal global de Hard-Stop
        if crate::ABORT_ALL.load(std::sync::atomic::Ordering::SeqCst) {
            return None;
        }

        if let Some(meta) = source.scrape(&query).await {
            // Mezcla inteligente de metadatos (llenar huecos)
            if final_meta.title.is_none() { final_meta.title = meta.title; }
            if final_meta.developer.is_none() { final_meta.developer = meta.developer; }
            if final_meta.publisher.is_none() { final_meta.publisher = meta.publisher; }
            if final_meta.release_date.is_none() { final_meta.release_date = meta.release_date; }
            if final_meta.genre.is_none() { final_meta.genre = meta.genre; }
            if final_meta.description.is_none() { final_meta.description = meta.description; }
            if final_meta.cover_2d_path.is_none() { final_meta.cover_2d_path = meta.cover_2d_path; }
            if final_meta.cover_3d_path.is_none() { final_meta.cover_3d_path = meta.cover_3d_path; }
            
            metadata_found = true;
            
            // Si ya tenemos lo crítico (Título + Portada 2D), podemos considerar éxito
            // No obstante, seguimos iterando si faltan datos como la descripción
            if final_meta.cover_2d_path.is_some() && final_meta.description.is_some() {
                break;
            }
        }
    }

    if metadata_found { Some(final_meta) } else { None }
}
