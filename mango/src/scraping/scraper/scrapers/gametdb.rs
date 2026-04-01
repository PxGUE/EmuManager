use crate::scraping::scraper::scrapers::{ScrapedMetadata, ScrapeQuery, MetadataSource, download_image};
use reqwest::Client;
use async_trait::async_trait;
use std::fs;
use std::path::Path;
use pyo3::Python;

pub struct GameTDBSource;

#[async_trait]
impl MetadataSource for GameTDBSource {
    fn name(&self) -> &'static str { "GameTDB" }

    async fn scrape(&self, query: &ScrapeQuery) -> Option<ScrapedMetadata> {
        let platform_tdb = match query.platform.to_lowercase().as_str() {
            "wii" => "wii",
            "gc" | "gamecube" => "gamecube",
            "ds" | "nds" => "ds",
            "3ds" => "3ds",
            "snes" => "snes",
            "nes" => "nes",
            "gba" => "gba",
            "gb" => "gb",
            "gbc" => "gbc",
            "n64" => "n64",
            "ps1" => "ps1",
            "ps2" => "ps2",
            _ => {
                return None;
            },
        };

        Python::with_gil(|py| {
            crate::scraping::batch_scraper::log_to_python(py, "debug", &format!(
                "[GAMETDB] Iniciando búsqueda ({}) para: '{}' (Serial: '{}')", 
                platform_tdb.to_uppercase(), query.filename, query.serial
            ));
        });

        if query.serial.is_empty() {
             Python::with_gil(|py| {
                crate::scraping::batch_scraper::log_to_python(py, "warning", &format!(
                    "[GAMETDB] Saltando '{}'. No se detectó Serial en la ROM, requerido para GameTDB.", 
                    query.filename
                ));
            });
             return None;
        }

        let mut metadata = ScrapedMetadata::default();
        let mut found_in_local = false;

        // 1. MODO LOCAL: Intentar leer desde XML en Cache
        if query.gametdb_mode == "local" {
            let cache_dir = query.media_dir.replace("media", "cache");
            let filename = match platform_tdb {
                "wii" | "gamecube" => "wiitdb.xml",
                "ds" => "dstdb.xml",
                "3ds" => "3dstdb.xml",
                _ => "wiitdb.xml",
            };
            let local_path = Path::new(&cache_dir).join("gametdb").join(&platform_tdb).join(filename);
            
            if local_path.exists() {
                if let Ok(xml_content) = fs::read_to_string(&local_path) {
                    if let Some(meta) = scrape_from_xml(&xml_content, &query.serial) {
                        metadata = meta;
                        found_in_local = true;
                    }
                }
            }
        }

        let client = Client::builder()
            .user_agent("EmuManager/1.0 (Rust MANGO Engine)")
            .build()
            .ok()?;

        // 2. MODO WEB (o Fallback si no se encontró en local)
        if !found_in_local {
            let xml_url = format!("https://www.gametdb.com/{}/{}&xml=1", platform_tdb, query.serial);
            if let Ok(res) = client.get(&xml_url).send().await {
                if let Ok(text) = res.text().await {
                    metadata.title = extract_tag(&text, "title");
                    metadata.developer = extract_tag(&text, "developer");
                    metadata.publisher = extract_tag(&text, "publisher");
                    metadata.release_date = extract_tag(&text, "date");
                    metadata.genre = extract_tag(&text, "genre");
                    metadata.description = extract_tag(&text, "synopsis");
                }
            }
        }

        // 3. DESCARGA DE ARTE (Siempre vía WEB en GameTDB por ahora)
        // Intentamos regiones comunes: US, EN (International), JA
        let regions = vec!["US", "EN", "JA"]; 
        let mut cover_path = None;

        for region in regions {
            let art_url = format!("https://art.gametdb.com/{}/cover/{}/{}.png", platform_tdb, region, query.serial);
            if let Ok(path) = download_image(&client, &art_url, &query.media_dir, "covers/2d", &query.filename).await {
                cover_path = Some(path);
                break;
            }
        }
        metadata.cover_2d_path = cover_path;

        if metadata.title.is_some() || metadata.cover_2d_path.is_some() {
            Python::with_gil(|py| {
                crate::scraping::batch_scraper::log_to_python(py, "info", &format!(
                    "[GAMETDB] Metadatos encontrados para: '{}' (Origen: {})", 
                    query.filename, if found_in_local { "Local XML" } else { "Web API" }
                ));
            });
            Some(metadata)
        } else {
            None
        }
    }
}

/// Extrae metadatos de un bloque de juego dentro del XML maestro de GameTDB.
fn scrape_from_xml(xml: &str, serial: &str) -> Option<ScrapedMetadata> {
    // GameTDB XML usa id="XXXXXX" para identificar juegos en el modo maestro
    let id_pattern = format!("id=\"{}\"", serial);
    let start_pos = xml.find(&id_pattern)?;
    
    // Retroceder al inicio del tag <game ...>
    let block_start = xml[..start_pos].rfind("<game")?;
    
    // Avanzar al final del bloque </game>
    let relative_end = xml[start_pos..].find("</game>")?;
    let block_end = start_pos + relative_end + 7;
    
    let game_xml = &xml[block_start..block_end];
    
    Some(ScrapedMetadata {
        title: extract_tag(game_xml, "title"),
        developer: extract_tag(game_xml, "developer"),
        publisher: extract_tag(game_xml, "publisher"),
        release_date: extract_tag(game_xml, "date"),
        genre: extract_tag(game_xml, "genre"),
        description: extract_tag(game_xml, "synopsis"),
        ..Default::default()
    })
}

/// Extrae el contenido de un tag XML de forma básica.
fn extract_tag(xml: &str, tag: &str) -> Option<String> {
    // Buscar con lenguaje prioritario (EN)
    let pattern_en = format!("<{} lang=\"en\">", tag);
    if let Some(start) = xml.find(&pattern_en) {
        if let Some(end) = xml[start..].find(&format!("</{}>", tag)) {
             return Some(xml[start+pattern_en.len()..start+end].to_string());
        }
    }
    
    // Fallback: Buscar sin atributo de lenguaje
    let pattern_simple = format!("<{}>", tag);
    if let Some(start) = xml.find(&pattern_simple) {
        if let Some(end) = xml[start..].find(&format!("</{}>", tag)) {
             return Some(xml[start+pattern_simple.len()..start+end].to_string());
        }
    }
    
    None
}
