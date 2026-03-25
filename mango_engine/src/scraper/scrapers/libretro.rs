use crate::scraper::scrapers::{ScrapedMetadata, download_image, clean_filename_for_search};
use reqwest::Client;
use std::path::{Path, PathBuf};
use std::fs;
use pyo3::prelude::*;
use crate::tools::fuzzy;

pub async fn scrape_game(
    filename: &str,
    platform: &str,
    media_dir_base: &str,
    interrupt_flag: &std::sync::atomic::AtomicBool,
) -> Option<ScrapedMetadata> {
    Python::with_gil(|py| {
        crate::batch_scraper::log_to_python(py, "debug", &format!(
            "[LIBRETRO] Iniciando búsqueda para: '{}' (Plataforma enviada: '{}')", 
            filename, platform
        ));
    });

    let repo_name = match platform.to_lowercase().as_str() {
        "gba" | "game boy advance" | "nintendo game boy advance" => "Nintendo - Game Boy Advance",
        "snes" | "super nintendo" | "nintendo super nintendo entertainment system" => "Nintendo - Super Nintendo Entertainment System",
        "nes" | "nintendo entertainment system" => "Nintendo - Nintendo Entertainment System",
        "n64" | "nintendo 64" => "Nintendo - Nintendo 64",
        "ps1" | "playstation" | "sony playstation" => "Sony - PlayStation",
        "ps2" | "playstation 2" | "sony playstation 2" => "Sony - PlayStation 2",
        "psp" | "playstation portable" | "sony playstation portable" => "Sony - PlayStation Portable",
        "ds" | "nintendo ds" => "Nintendo - Nintendo DS",
        "gb" | "game boy" | "nintendo game boy" => "Nintendo - Game Boy",
        "gbc" | "game boy color" | "nintendo game boy color" => "Nintendo - Game Boy Color",
        "gc" | "gamecube" | "game cube" | "nintendo gamecube" => "Nintendo - GameCube",
        "wii" | "nintendo wii" => "Nintendo - Wii",
        "megadrive" | "genesis" | "sega mega drive - genesis" => "Sega - Mega Drive - Genesis",
        _ => {
            Python::with_gil(|py| {
                crate::batch_scraper::log_to_python(py, "warning", &format!(
                    "[LIBRETRO] Plataforma no soportada en Libretro: '{}'", platform
                ));
            });
            return None;
        }
    };

    let client = Client::builder()
        .user_agent("EmuManager/1.0 (Rust MANGO Engine)")
        .build()
        .ok()?;

    let file_stem = Path::new(filename).file_stem().unwrap_or_default().to_string_lossy().to_string();
    let clean_local = clean_filename_for_search(&file_stem);

    let base_url = "https://thumbnails.libretro.com/";
    let type_folder = "Named_Boxarts";
    
    // 1. Obtener Índice (Mapa de Libretro)
    let index = get_libretro_index(&client, repo_name, type_folder).await.unwrap_or_default();
    
    if index.is_empty() {
        Python::with_gil(|py| {
            crate::batch_scraper::log_to_python(py, "warning", &format!(
                "[LIBRETRO] No se pudo obtener el catálogo para: '{}'", repo_name
            ));
        });
        return None; 
    }

    // 2. Búsqueda Inteligente (Fuzzy) sobre el índice local
    if let Some(match_result) = fuzzy::find_best_match(&clean_local, index, 0.85) {
        Python::with_gil(|py| {
            crate::batch_scraper::log_to_python(py, "info", &format!(
                "[LIBRETRO] ¡Match Inteligente! '{}' -> '{}' (Sim: {:.2})", 
                clean_local, match_result.name, match_result.similarity
            ));
        });

        // La URL final debe ser el nombre exacto del índice (escapado)
        let escaped_name = urlencoding::encode(&match_result.name);
        let target_url = format!("{}{}/{}/{}.png", base_url, repo_name, type_folder, escaped_name);

        if let Ok(path) = download_image(&client, &target_url, media_dir_base, "covers/2d", &file_stem).await {
            return Some(ScrapedMetadata {
                title: Some(match_result.name),
                developer: None,
                publisher: None,
                release_date: None,
                genre: None,
                description: None,
                cover_2d_path: Some(path),
                cover_3d_path: None,
            });
        }
    }

    None
}

async fn get_libretro_index(client: &Client, repo: &str, folder: &str) -> Option<Vec<String>> {
    let cache_dir = Path::new("data/cache");
    if !cache_dir.exists() { let _ = fs::create_dir_all(cache_dir); }
    
    let cache_file = cache_dir.join(format!("libretro_{}.txt", repo.to_lowercase().replace(" ", "_")));
    
    // 1. Intentar Caché
    if cache_file.exists() {
        if let Ok(content) = fs::read_to_string(&cache_file) {
            let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
            if !lines.is_empty() { return Some(lines); }
        }
    }

    // 2. Scraping del listado HTTP (Directory Listing)
    // Libretro NO tiene .index archivos en todos los nodos, pero sí Directory Listing de Apache
    let repo_encoded = urlencoding::encode(repo);
    let url = format!("https://thumbnails.libretro.com/{}/{}/", repo_encoded, folder);
    
    if let Ok(res) = client.get(&url).send().await {
        if res.status().is_success() {
            if let Ok(html) = res.text().await {
                let mut lines = Vec::new();
                
                // Extraer nombres de archivos de los tags <a href="...">
                // Buscamos patrones como: href="Game Name (Region).png"
                for line in html.lines() {
                    if line.contains(".png\"") {
                        if let Some(start) = line.find("href=\"") {
                            let part = &line[start + 6..];
                            if let Some(end) = part.find(".png\"") {
                                let encoded_fname = &part[..end];
                                // Decodificar el nombre (Ej: %20 -> espacio)
                                if let Ok(decoded) = urlencoding::decode(encoded_fname) {
                                    lines.push(decoded.into_owned());
                                }
                            }
                        }
                    }
                }
                
                if !lines.is_empty() {
                    let _ = fs::write(&cache_file, lines.join("\n"));
                    return Some(lines);
                }
            }
        }
    }

    None
}
