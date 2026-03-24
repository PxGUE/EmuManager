use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use reqwest::Client;
use std::path::{Path, PathBuf};
use std::fs::{self, File};
use std::io::{Read, Write};
use tokio::runtime::Runtime;
use futures_util::StreamExt;
use zip::ZipArchive;

/// Configuración de la URL del Buildbot de Libretro
#[cfg(target_os = "windows")]
const BUILDBOT_URL: &str = "http://buildbot.libretro.com/nightly/windows/x86_64/latest/";

#[cfg(target_os = "linux")]
const BUILDBOT_URL: &str = "http://buildbot.libretro.com/nightly/linux/x86_64/latest/";

#[cfg(target_os = "macos")]
const BUILDBOT_URL: &str = "http://buildbot.libretro.com/nightly/apple/osx/x86_64/latest/";


/// Retorna la lista de cores disponibles (parseando el HTML del index de libretro)
pub async fn fetch_available_cores_async() -> Result<Vec<String>, anyhow::Error> {
    let client = Client::builder()
        .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        .timeout(std::time::Duration::from_secs(15))
        .build()?;
        
    // Intentamos obtener el contenido. 
    let response = client.get(BUILDBOT_URL).send().await?.text().await?;
    
    let mut cores = Vec::new();
    let mut offset = 0;

    // Búsqueda robusta secuencial de todos los enlaces href en el documento
    while let Some(start_pos) = response[offset..].find("href=\"") {
        let link_start = offset + start_pos + 6;
        if let Some(end_offset) = response[link_start..].find("\"") {
            let link_end = link_start + end_offset;
            let full_link = &response[link_start..link_end];
            
            // Verificamos si es un enlace de core compatible
            if full_link.contains("_libretro") && full_link.ends_with(".zip") {
                if let Some(filename) = full_link.split('/').last() {
                    let clean_name = filename
                        .replace(".zip", "")
                        .replace(".7z", "")
                        .replace(".dll", "")
                        .replace(".so", "")
                        .replace(".dylib", "");
                    
                    if !clean_name.is_empty() {
                        cores.push(clean_name);
                    }
                }
            }
            offset = link_end;
        } else {
            break;
        }
    }
    
    cores.sort();
    cores.dedup();
    
    if cores.is_empty() {
        return Err(anyhow::anyhow!("No se detectaron núcleos válidos. Respuesta del servidor (fragmento): {}", if response.len() > 100 { &response[..100] } else { &response }));
    }
    
    Ok(cores)
}

/// Descarga y descomprime un core
pub async fn download_core_async(
    core_name: String, 
    dest_dir: String, 
    progress_callback: Option<PyObject>
) -> Result<String, anyhow::Error> {
    let client = Client::new();
    
    #[cfg(target_os = "windows")]
    let ext = ".dll.zip";
    #[cfg(target_os = "linux")]
    let ext = ".so.zip";
    #[cfg(target_os = "macos")]
    let ext = ".dylib.zip";
    
    #[cfg(not(any(target_os = "windows", target_os = "linux", target_os = "macos")))]
    let ext = ".zip"; // Fallback genérico
    
    let filename = format!("{}{}", core_name, ext);
    let url = format!("{}{}", BUILDBOT_URL, filename);
    
    let dest_path = Path::new(&dest_dir);
    if !dest_path.exists() {
        fs::create_dir_all(&dest_path)?;
    }
    
    let zip_path = dest_path.join(&filename);
    
    // 1. Descargar el archivo ZIP usando Stream
    let res = client.get(&url).send().await?;
    if !res.status().is_success() {
        return Err(anyhow::anyhow!("Error HTTP: {}", res.status()));
    }
    
    let total_size = res.content_length().unwrap_or(0);
    let mut file = File::create(&zip_path)?;
    let mut downloaded: u64 = 0;
    let mut stream = res.bytes_stream();
    
    let mut last_reported_progress = -0.1;
    
    while let Some(chunk) = stream.next().await {
        let chunk = chunk?;
        file.write_all(&chunk)?;
        downloaded += chunk.len() as u64;
        
        // Reportar progreso a Python con limitación de frecuencia (cada 1%)
        if let Some(ref cb) = progress_callback {
            if total_size > 0 {
                let p = downloaded as f64 / total_size as f64;
                if (p - last_reported_progress).abs() >= 0.01 || p >= 1.0 {
                    last_reported_progress = p;
                    Python::with_gil(|py| {
                        let _ = cb.call1(py, (p,));
                    });
                }
            }
        }
    }
    
    // 2. Extraer el zip
    let zip_file = File::open(&zip_path)?;
    let mut archive = ZipArchive::new(zip_file)?;
    let mut extracted_file = String::new();
    
    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        let filename_in_zip = file.name().to_string();
        let outpath = dest_path.join(file.mangled_name());
        
        if (&*file.name()).ends_with('/') {
            fs::create_dir_all(&outpath)?;
        } else {
            if let Some(p) = outpath.parent() {
                if !p.exists() {
                    fs::create_dir_all(p)?;
                }
            }
            let mut outfile = File::create(&outpath)?;
            std::io::copy(&mut file, &mut outfile)?;
            
            // Si es el archivo de core, guardamos su ruta
            if filename_in_zip.contains("_libretro") && (filename_in_zip.ends_with(".dll") || filename_in_zip.ends_with(".so") || filename_in_zip.ends_with(".dylib")) {
                extracted_file = outpath.to_string_lossy().to_string();
            }
        }
    }
    
    // Limpieza
    let _ = fs::remove_file(&zip_path);
    
    // Si no detectamos el archivo por nombre, devolvemos el último extraído como fallback
    if extracted_file.is_empty() {
        extracted_file = dest_path.to_string_lossy().to_string();
    }
    
    Ok(extracted_file)
}
