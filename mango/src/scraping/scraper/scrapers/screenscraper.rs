use pyo3::prelude::*;
use reqwest::Client;
use std::path::Path;
use serde_json::Value;
use crate::scraping::scraper::scrapers::{ScrapedMetadata, ScrapeQuery, MetadataSource, download_image, extract_single, extract_text, clean_filename_for_search};
use async_trait::async_trait;

pub struct ScreenScraperSource;

#[async_trait]
impl MetadataSource for ScreenScraperSource {
    fn name(&self) -> &'static str { "ScreenScraper" }

    async fn scrape(&self, query: &ScrapeQuery) -> Option<ScrapedMetadata> {
        if query.ss_user.is_empty() || query.ss_pass.is_empty() {
            return None;
        }

        let softname = "EmuManagerApp";
        let mut query_params = vec![
            ("devid", query.dev_id.as_str()),
            ("devpassword", query.dev_pass.as_str()),
            ("softname", softname),
            ("output", "json"),
        ];

        query_params.push(("ssid", query.ss_user.as_str()));
        query_params.push(("sspassword", query.ss_pass.as_str()));

        let client = Client::builder()
            .user_agent("EmuManager/1.0 (Rust MANGO Engine)")
            .build()
            .ok()?;

        // 1. MD5 Search
        let mut search_params = query_params.clone();
        search_params.push(("crc", query.crc.as_str()));
        search_params.push(("md5", query.md5.as_str()));
        
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
            let file_stem = Path::new(&query.filename).file_stem().unwrap_or_default().to_string_lossy().to_string();
            let clean_name = clean_filename_for_search(&file_stem);
            
            let mut fallback_params = query_params.clone();
            fallback_params.push(("recherche", &clean_name));
            if !query.system_id.is_empty() {
                fallback_params.push(("systemeid", query.system_id.as_str()));
            }

            let url_search = "https://www.screenscraper.fr/api2/jeuRecherche.php";
            if let Ok(res) = client.get(url_search).query(&fallback_params).send().await {
                if res.status().is_success() {
                    if let Ok(json) = res.json::<Value>().await {
                        if let Some(jeux) = json.get("response").and_then(|r| r.get("jeux")).and_then(|j| j.as_array()) {
                            if let Some(winner) = crate::tools::searcher::find_best_match_with_platform(&clean_name, jeux, &query.system_id) {
                                Python::with_gil(|py| {
                                    crate::scraping::batch_scraper::log_to_python(py, "info", &format!(
                                        "[SCREEN-SCRAPER] Match verificado por plataforma para: '{}'", 
                                        clean_name
                                    ));
                                });

                                let wrapped = serde_json::json!({
                                    "response": {
                                        "jeu": winner
                                    }
                                });
                                response_json = Some(wrapped);
                            }
                        }
                    }
                }
            }
        }

        let json = response_json?;
        let jeu = json.get("response").and_then(|r| r.get("jeu"))?;

        let mut meta = ScrapedMetadata {
            title: extract_text(jeu, "noms", "nom"),
            developer: extract_single(jeu, "developpeur"),
            publisher: extract_single(jeu, "editeur"),
            release_date: extract_text(jeu, "dates", "date"),
            genre: extract_text(jeu, "genres", "genre"),
            description: extract_text(jeu, "synopsis", "synopsis"),
            ..ScrapedMetadata::default()
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

            let base_ext = Path::new(&query.filename).file_stem().unwrap_or_default().to_string_lossy();

            if let Some(url) = url_3d {
                if let Ok(path) = download_image(&client, url, &query.media_dir, "covers/3d", &base_ext).await {
                    meta.cover_3d_path = Some(path);
                }
            }

            if let Some(url) = url_2d {
                if let Ok(path) = download_image(&client, url, &query.media_dir, "covers/2d", &base_ext).await {
                    meta.cover_2d_path = Some(path);
                }
            }
        }

        Some(meta)
    }
}
