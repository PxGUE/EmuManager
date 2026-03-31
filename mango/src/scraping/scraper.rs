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
    };

    let mut sources: Vec<Box<dyn MetadataSource>> = Vec::new();
    
    // Prioridad 1: Local (Sostenibilidad Local-First)
    sources.push(Box::new(scrapers::local_nfo::LocalNfoSource));

    // Prioridad 2: ScreenScraper (Metadatos completos)
    if !skip_ss {
        sources.push(Box::new(scrapers::screenscraper::ScreenScraperSource));
    }
    
    // Prioridad 3: Libretro (Rescate ante fallos)
    sources.push(Box::new(scrapers::libretro::LibretroSource));

    let mut final_meta = ScrapedMetadata::default();
    let mut metadata_found = false;

    for source in sources {
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
