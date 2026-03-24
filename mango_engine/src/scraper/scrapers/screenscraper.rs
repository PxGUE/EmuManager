use pyo3::prelude::*;
use reqwest::Client;
use std::path::Path;
use serde_json::Value;
use crate::scraper::scrapers::{ScrapedMetadata, download_image, extract_single, extract_text, clean_filename_for_search};

pub async fn scrape_game(
    md5: &str,
    crc: &str,
    filename: &str,
    system_id: &str,
    ss_id: &str,
    ss_pass: &str,
    dev_id: &str,
    dev_pass: &str,
    media_dir_base: &str,
    interrupt_flag: &std::sync::atomic::AtomicBool,
) -> Option<ScrapedMetadata> {
    
    let softname = "EmuManagerApp";
    let mut query_params = vec![
        ("devid", dev_id),
        ("devpassword", dev_pass),
        ("softname", softname),
        ("output", "json"),
    ];

    if !ss_id.is_empty() {
        query_params.push(("ssid", ss_id));
        query_params.push(("sspassword", ss_pass));
    }

    let client = Client::builder()
        .user_agent("EmuManager/1.0 (Rust MANGO Engine)")
        .build()
        .ok()?;

    // 1. MD5 Search
    let mut search_params = query_params.clone();
    search_params.push(("crc", crc));
    search_params.push(("md5", md5));
    
    let url_infos = "https://www.screenscraper.fr/api2/jeuInfos.php";
    let mut response_json: Option<Value> = None;

    if let Ok(res) = client.get(url_infos).query(&search_params).send().await {
        if res.status().is_success() {
            if let Ok(json) = res.json::<Value>().await {
                response_json = Some(json);
            }
        }
    }

    // 2. Fuzzy Search Fallback
    if response_json.is_none() {
        let file_stem = Path::new(filename).file_stem().unwrap_or_default().to_string_lossy().to_string();
        let clean_name = clean_filename_for_search(&file_stem);
        
        let mut fallback_params = query_params.clone();
        fallback_params.push(("recherche", &clean_name));
        if !system_id.is_empty() {
            fallback_params.push(("systemeid", system_id));
        }

        let url_search = "https://www.screenscraper.fr/api2/jeuRecherche.php";
        if let Ok(res) = client.get(url_search).query(&fallback_params).send().await {
            if res.status().is_success() {
                if let Ok(json) = res.json::<Value>().await {
                    if let Some(jeux) = json.get("response").and_then(|r| r.get("jeux")).and_then(|j| j.as_array()) {
                        let mut best_sim = 0.0;
                        let mut best_game: Option<serde_json::Value> = None;
                        
                        let mut candidates: Vec<String> = Vec::new();
                        let mut game_map: std::collections::HashMap<String, serde_json::Value> = std::collections::HashMap::new();
                        
                        for jeu_item in jeux {
                            if let Some(api_name) = extract_text(jeu_item, "noms", "nom") {
                                candidates.push(api_name.clone());
                                game_map.insert(api_name, jeu_item.clone());
                            }
                        }

                        if let Some(match_result) = crate::tools::fuzzy::find_best_match(&clean_name, candidates, 0.85) {
                            Python::with_gil(|py| {
                                crate::batch_scraper::log_to_python(py, "info", &format!(
                                    "[SCREEN-SCRAPER] ¡Match encontrado! '{}' (Confianza: {:.2})", 
                                    match_result.name, match_result.similarity
                                ));
                            });

                            if let Some(winner) = game_map.get(&match_result.name) {
                                let wrapped = serde_json::json!({
                                    "response": {
                                        "jeu": winner
                                    }
                                });
                                response_json = Some(wrapped);
                            }
                        } else {
                            Python::with_gil(|py| {
                                crate::batch_scraper::log_to_python(py, "warning", &format!(
                                    "[SCREEN-SCRAPER] Sin coincidencias confiables para: '{}'", 
                                    clean_name
                                ));
                            });
                        }
                    }
                }
            }
        }
    }

    let json = response_json?;
    let jeu = if let Some(j) = json.get("response").and_then(|r| r.get("jeu")) {
        j
    } else {
        return None;
    };

    let mut meta = ScrapedMetadata {
        title: extract_text(jeu, "noms", "nom"),
        developer: extract_single(jeu, "developpeur"),
        publisher: extract_single(jeu, "editeur"),
        release_date: extract_text(jeu, "dates", "date"),
        genre: extract_text(jeu, "genres", "genre"),
        description: extract_text(jeu, "synopsis", "synopsis"),
        cover_2d_path: None,
        cover_3d_path: None,
    };

    // Media Download
    if let Some(medias) = jeu.get("medias").and_then(|m| m.as_array()) {
        let mut url_2d = None;
        let mut url_3d = None;
        
        for media in medias {
            let m_type = media.get("type").and_then(|t| t.as_str()).unwrap_or("");
            let m_url = media.get("url").and_then(|u| u.as_str());
            
            if let Some(url) = m_url {
                if m_type == "box-2D" || m_type == "box-2D-v" {
                    if url_2d.is_none() { url_2d = Some(url); }
                } else if m_type == "box-3D" {
                    url_3d = Some(url);
                }
            }
        }

        let base_ext = Path::new(filename).file_stem().unwrap_or_default().to_string_lossy();

        if let Some(url) = url_3d {
            if let Ok(path) = download_image(&client, url, media_dir_base, "covers/3d", &base_ext).await {
                meta.cover_3d_path = Some(path);
            }
        }

        if let Some(url) = url_2d {
            if let Ok(path) = download_image(&client, url, media_dir_base, "covers/2d", &base_ext).await {
                meta.cover_2d_path = Some(path);
            }
        }
    }

    Some(meta)
}
