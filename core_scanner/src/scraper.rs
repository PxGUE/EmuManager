use serde::{Deserialize, Serialize};
use reqwest::blocking::Client;
use std::path::Path;
use std::fs;
use std::io::Write;
use serde_json::Value;
use pyo3::prelude::*;

#[derive(Debug, Serialize, Deserialize)]
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

pub fn scrape_game(
    md5: &str,
    crc: &str,
    filename: &str,
    system_id: &str, // ScreenScraper system ID (e.g. 12 for GBA)
    ss_id: &str,
    ss_pass: &str,
    media_dir_base: &str, // e.g., "C:/.../data/media/gba"
    interrupt_flag: &Bound<'_, pyo3::types::PyBool>,
) -> Option<ScrapedMetadata> {
    
    // Default Dev credentials (or generic placeholders)
    let dev_id = "emumanager_dev";
    let dev_pass = "emumanager_dev";
    let softname = "EmuManager";

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

    // Intentar buscar por HASH (MD5/CRC) primero
    let mut search_params = query_params.clone();
    search_params.push(("crc", crc));
    search_params.push(("md5", md5));
    
    let url_infos = "https://www.screenscraper.fr/api2/jeuInfos.php";
    
    let mut response_json: Option<Value> = None;

    if interrupt_flag.is_true() { return None; }

    if let Ok(res) = client.get(url_infos).query(&search_params).send() {
        if res.status().is_success() {
            if let Ok(json) = res.json::<Value>() {
                response_json = Some(json);
            }
        }
    }

    // Fallback: Buscar por nombre si falla el hash
    if response_json.is_none() {
        if interrupt_flag.is_true() { return None; }
        // Limpiamos el nombre (quitar extension, regiones en parentesis, etc.)
        let clean_name = clean_filename_for_search(filename);
        let mut fallback_params = query_params.clone();
        fallback_params.push(("recherche", &clean_name));
        if !system_id.is_empty() {
            fallback_params.push(("systemeid", system_id));
        }

        let url_search = "https://www.screenscraper.fr/api2/jeuRecherche.php";
        if let Ok(res) = client.get(url_search).query(&fallback_params).send() {
            if res.status().is_success() {
                if let Ok(json) = res.json::<Value>() {
                    // juegoInfos envuelve en "response" -> "jeu"
                    // juegoRecherche envuelve en "response" -> "jeux" -> array
                    if let Some(jeux) = json.get("response").and_then(|r| r.get("jeux")).and_then(|j| j.as_array()) {
                        if !jeux.is_empty() {
                            response_json = Some(json); // Tomaremos el primer resultado luego
                        }
                    }
                }
            }
        }
    }

    let json = response_json?;
    
    if interrupt_flag.is_true() { return None; }

    // Extraer el nodo "jeu" principal
    let jeu = if let Some(j) = json.get("response").and_then(|r| r.get("jeu")) {
        j
    } else if let Some(jeux) = json.get("response").and_then(|r| r.get("jeux")).and_then(|j| j.as_array()) {
        if !jeux.is_empty() {
            &jeux[0]
        } else {
            return None;
        }
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

    // Descargar Media
    if let Some(medias) = jeu.get("medias").and_then(|m| m.as_array()) {
        let mut url_2d = None;
        let mut url_3d = None;
        
        for media in medias {
            if let (Some(m_type), Some(url)) = (media.get("type").and_then(|t| t.as_str()), media.get("url").and_then(|u| u.as_str())) {
                if m_type == "box-2D" {
                    url_2d = Some(url);
                } else if m_type == "box-3D" {
                    url_3d = Some(url);
                }
            }
        }

        let base_ext = Path::new(filename).file_stem().unwrap_or_default().to_string_lossy();

        if let Some(url) = url_3d {
            if interrupt_flag.is_true() { return Some(meta); }
            if let Ok(path) = download_image(&client, url, media_dir_base, "covers/3d", &base_ext) {
                meta.cover_3d_path = Some(path);
            }
        }

        if let Some(url) = url_2d {
            if interrupt_flag.is_true() { return Some(meta); }
            if let Ok(path) = download_image(&client, url, media_dir_base, "covers/2d", &base_ext) {
                meta.cover_2d_path = Some(path);
            }
        }
    }

    Some(meta)
}

fn extract_single(jeu: &Value, key: &str) -> Option<String> {
    jeu.get(key).and_then(|v| v.get("text")).and_then(|t| t.as_str()).map(|s| s.to_string())
}

fn extract_text(jeu: &Value, array_key: &str, text_key: &str) -> Option<String> {
    jeu.get(array_key)
        .and_then(|arr| arr.as_array())
        .and_then(|arr| arr.first())
        .and_then(|first| first.get("text").or_else(|| first.get("nom")).or_else(|| first.get(text_key)))
        .and_then(|t| t.as_str())
        .map(|s| s.to_string())
}

fn clean_filename_for_search(filename: &str) -> String {
    let path = Path::new(filename);
    let mut stem = path.file_stem().unwrap_or_default().to_string_lossy().to_string();
    
    // Quitar todo a partir del primer parentesis "(" o corchete "["
    if let Some(idx) = stem.find('(') {
        stem.truncate(idx);
    }
    if let Some(idx) = stem.find('[') {
        stem.truncate(idx);
    }
    
    stem.trim().to_string()
}

fn download_image(client: &Client, url: &str, base_dir: &str, sub_dir: &str, file_stem: &str) -> Result<String, ()> {
    let target_dir = Path::new(base_dir).join(sub_dir);
    if !target_dir.exists() {
        let _ = fs::create_dir_all(&target_dir);
    }

    // Determine extension from url (usually png or jpg)
    let ext = if url.to_lowercase().ends_with(".jpg") || url.to_lowercase().ends_with(".jpeg") {
        "jpg"
    } else {
        "png"
    };

    let target_file = target_dir.join(format!("{}.{}", file_stem, ext));
    
    if target_file.exists() {
        return Ok(target_file.to_string_lossy().to_string());
    }

    if let Ok(response) = client.get(url).send() {
        if response.status().is_success() {
            if let Ok(bytes) = response.bytes() {
                if let Ok(mut file) = fs::File::create(&target_file) {
                    if file.write_all(&bytes).is_ok() {
                        return Ok(target_file.to_string_lossy().to_string());
                    }
                }
            }
        }
    }

    Err(())
}
