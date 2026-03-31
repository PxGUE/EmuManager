use serde::{Deserialize, Serialize};
use reqwest::Client;
use std::path::Path;
use std::fs;
use std::io::Write;
use serde_json::Value;

pub mod screenscraper;
pub mod libretro;
pub mod local_nfo;

use async_trait::async_trait;

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ScrapedMetadata {
    pub title: Option<String>,
    pub developer: Option<String>,
    pub publisher: Option<String>,
    pub release_date: Option<String>,
    pub genre: Option<String>,
    pub description: Option<String>,
    pub cover_2d_path: Option<String>,
    pub cover_3d_path: Option<String>,
}

#[derive(Clone)]
pub struct ScrapeQuery {
    pub md5: String,
    pub crc: String,
    pub filename: String,
    pub platform: String,
    pub system_id: String,
    pub media_dir: String,
    pub ss_user: String,
    pub ss_pass: String,
    pub dev_id: String,
    pub dev_pass: String,
}

#[async_trait]
pub trait MetadataSource: Send + Sync {
    fn name(&self) -> &'static str;
    async fn scrape(&self, query: &ScrapeQuery) -> Option<ScrapedMetadata>;
}

pub fn extract_single(jeu: &Value, key: &str) -> Option<String> {
    jeu.get(key).and_then(|v| v.get("text")).and_then(|t| t.as_str()).map(|s| s.to_string())
}

pub fn extract_text(jeu: &Value, array_key: &str, text_key: &str) -> Option<String> {
    if let Some(arr) = jeu.get(array_key).and_then(|v| v.as_array()) {
        for entry in arr {
            if let Some(t) = entry.get("text").or_else(|| entry.get("nom")).or_else(|| entry.get(text_key)) {
                if let Some(s) = t.as_str() {
                    if !s.is_empty() { return Some(s.to_string()); }
                }
            }
        }
    }
    None
}

pub fn clean_filename_for_search(file_stem: &str) -> String {
    let mut clean = file_stem.to_string();
    if let Some(idx) = clean.find('(') { clean.truncate(idx); }
    if let Some(idx) = clean.find('[') { clean.truncate(idx); }
    clean.trim().to_string()
}

pub async fn download_image(client: &Client, url: &str, base_dir: &str, sub_dir: &str, file_stem: &str) -> Result<String, ()> {
    let target_dir = Path::new(base_dir).join(sub_dir);
    if !target_dir.exists() { let _ = fs::create_dir_all(&target_dir); }
    let ext = if url.to_lowercase().ends_with(".jpg") || url.to_lowercase().ends_with(".jpeg") { "jpg" } else { "png" };
    let target_file = target_dir.join(format!("{}.{}", file_stem, ext));
    if target_file.exists() { return Ok(target_file.to_string_lossy().to_string()); }
    if let Ok(response) = client.get(url).send().await {
        if response.status().is_success() {
            if let Ok(bytes) = response.bytes().await {
                if let Ok(mut file) = fs::File::create(&target_file) {
                    if file.write_all(&bytes).is_ok() { return Ok(target_file.to_string_lossy().to_string()); }
                }
            }
        }
    }
    Err(())
}
