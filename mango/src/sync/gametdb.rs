use std::fs;
use std::io::{self, Cursor};
use std::path::Path;
use reqwest::Client;
use zip::ZipArchive;
use pyo3::prelude::*;
use futures_util::StreamExt;

pub async fn download_and_extract_gametdb(
    platform: &str,
    cache_base: &str,
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>
) -> Result<String, String> {
    let plat_low = platform.to_lowercase();
    let (url, filename) = match plat_low.as_str() {
        "wii" | "gc" | "gamecube" => ("https://www.gametdb.com/wiitdb.zip", "wiitdb.xml"),
        "ds" | "nds" => ("https://www.gametdb.com/dstdb.zip", "dstdb.xml"),
        "3ds" => ("https://www.gametdb.com/3dstdb.zip", "3dstdb.xml"),
        _ => return Err(format!("Plataforma {} no soportada para GameTDB local", platform)),
    };

    let target_dir = Path::new(cache_base).join("gametdb").join(&plat_low);
    let target_file = target_dir.join(filename);

    // Si ya existe, no descargamos (el usuario puede borrar la carpeta para forzar actualización)
    if target_file.exists() {
        return Ok(target_file.to_string_lossy().to_string());
    }

    fs::create_dir_all(&target_dir).map_err(|e| e.to_string())?;

    Python::with_gil(|py| {
        if let Some(sc) = &status_callback {
            let _ = sc.bind(py).call1((format!("downloading_gametdb_db|{}", platform.to_uppercase()),));
        }
    });

    let client = Client::new();
    let response = client.get(url).send().await.map_err(|e| e.to_string())?;
    
    let total_size = response.content_length().unwrap_or(0);
    let mut downloaded = 0;
    let mut buffer = Vec::new();
    let mut stream = response.bytes_stream();

    while let Some(item) = stream.next().await {
        let chunk = item.map_err(|e| e.to_string())?;
        buffer.extend_from_slice(&chunk);
        downloaded += chunk.len() as u64;
        
        if total_size > 0 {
            let prog = (downloaded as f64 / total_size as f64) * 0.5; // La descarga es el 50%
            Python::with_gil(|py| {
                if let Some(pc) = &progress_callback {
                    let _ = pc.bind(py).call1((prog,));
                }
            });
        }
    }

    Python::with_gil(|py| {
        if let Some(sc) = &status_callback {
            let _ = sc.bind(py).call1(("extracting_gametdb_db",));
        }
    });

    let mut archive = ZipArchive::new(Cursor::new(buffer)).map_err(|e| e.to_string())?;
    for i in 0..archive.len() {
        let mut file = archive.by_index(i).map_err(|e| e.to_string())?;
        if file.name().to_lowercase().ends_with(".xml") {
            let mut out = fs::File::create(&target_file).map_err(|e| e.to_string())?;
            io::copy(&mut file, &mut out).map_err(|e| e.to_string())?;
            break; // Solo necesitamos el primer XML que coincida
        }
    }

    Ok(target_file.to_string_lossy().to_string())
}
