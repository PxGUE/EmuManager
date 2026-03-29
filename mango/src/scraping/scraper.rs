pub mod scrapers;
pub use scrapers::ScrapedMetadata;

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
    interrupt_flag: &std::sync::atomic::AtomicBool,
    skip_ss: bool,
) -> Option<ScrapedMetadata> {
    let mut meta = None;

    // 1. Intentar con ScreenScraper (Metadatos + Portadas) si no está desactivado
    if !skip_ss {
        meta = scrapers::screenscraper::scrape_game(
            md5, crc, filename, system_id, ss_id, ss_pass, dev_id, dev_pass, media_dir_base, interrupt_flag
        ).await;

        if let Some(ref m) = meta {
            if m.cover_2d_path.is_some() || m.cover_3d_path.is_some() {
                return meta;
            }
        }

        // Trazado de Fallback
        pyo3::Python::with_gil(|py| {
            crate::scraping::batch_scraper::log_to_python(py, "debug", &format!(
                "[MANGO] ScreenScraper sin medios. Activando Protocolo de Rescate (Libretro) para: '{}'", 
                filename
            ));
        });
    } else {
        pyo3::Python::with_gil(|py| {
            crate::scraping::batch_scraper::log_to_python(py, "info", &format!(
                "[MANGO] Saltando ScreenScraper (Modo Rescate Activo) para: '{}'", 
                filename
            ));
        });
    }

    // 2. Si ScreenScraper falla o no tiene carátula, Fallback a Libretro Thumbnails
    if let Some(libretro_meta) = scrapers::libretro::scrape_game(filename, platform, media_dir_base, interrupt_flag).await {
        if let Some(mut existing) = meta {
            existing.cover_2d_path = libretro_meta.cover_2d_path;
            return Some(existing);
        }
        return Some(libretro_meta);
    }

    meta
}
