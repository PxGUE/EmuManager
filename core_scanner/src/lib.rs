use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::Path;
use std::fs::File;
use std::io::{Read, BufReader};
use walkdir::WalkDir;
use rayon::prelude::*;
use md5;
use crc32fast::Hasher;
use serde_json; // Added for scrape_game_metadata
use tokio::runtime::Runtime;

pub mod scraper;
pub mod core_manager;
pub mod batch_scraper;
pub mod searcher;
pub mod tools;

fn calculate_hashes(path: &str) -> (String, String, u64) {
    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => return ("".to_string(), "".to_string(), 0),
    };

    let mut reader = BufReader::new(file);
    let mut md5_context = md5::Context::new();
    let mut crc_hasher = Hasher::new();
    let mut buffer = [0; 65536]; // 64KB buffer
    let mut file_size = 0;

    loop {
        let count = match reader.read(&mut buffer) {
            Ok(0) => break,
            Ok(c) => c,
            Err(_) => break,
        };
        file_size += count as u64;
        md5_context.consume(&buffer[..count]);
        crc_hasher.update(&buffer[..count]);
    }

    let md5_digest = md5_context.compute();
    let crc32_val = crc_hasher.finalize();

    (
        format!("{:x}", md5_digest),
        format!("{:08x}", crc32_val),
        file_size
    )
}

/// Escanea un directorio y devuelve una lista de diccionarios con metadatos de archivos
#[pyfunction]
fn scan_directory(py: Python<'_>, path: String, extensions: Vec<String>) -> PyResult<Vec<PyObject>> {
    let base_path = Path::new(&path);
    if !base_path.exists() {
        return Ok(vec![]);
    }

    // Recolectar archivos con seguimiento de enlaces simbólicos activado
    let files: Vec<_> = WalkDir::new(base_path)
        .follow_links(true)
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_file())
        .collect();

    // Procesar metadatos y hashes en PARALELO con Rayon (CPU Intenso)
    let results: Vec<_> = files.into_par_iter()
        .filter_map(|entry| {
            let p = entry.path();
            if let Some(ext) = p.extension().and_then(|e| e.to_str()) {
                let ext_lower = ext.to_lowercase();
                
                // Normalizar la lista de extensiones recibida para ser insensible a mayúsculas
                if extensions.is_empty() || extensions.iter().any(|e| e.to_lowercase().trim_start_matches('.').to_string() == ext_lower) {
                    let path_str = p.to_string_lossy().into_owned();
                    let (md5_h, crc_h, size) = calculate_hashes(&path_str);
                    return Some((path_str, md5_h, crc_h, size));
                }
            }
            None
        })
        .collect();

    // Convertir a objetos Python (usando Bound API de PyO3 v0.23)
    let mut py_results = Vec::new();
    for (path_str, md5_h, crc_h, size) in results {
        let dict = PyDict::new(py);
        dict.set_item("path", path_str)?;
        dict.set_item("md5", md5_h)?;
        dict.set_item("crc32", crc_h)?;
        dict.set_item("size", size)?;
        py_results.push(dict.into_any().unbind());
    }

    Ok(py_results)
}

#[pyfunction]
fn scrape_game_metadata(
    _py: Python<'_>,
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
    interrupt_flag: Bound<'_, pyo3::types::PyBool>, 
) -> PyResult<String> {
    if interrupt_flag.is_true() {
        return Ok("{}".to_string());
    }
    
    let interrupt_arc = std::sync::atomic::AtomicBool::new(false);
    let rt = Runtime::new().unwrap();

    let meta_opt = rt.block_on(async {
        scraper::scrape_game(md5, crc, filename, platform, system_id, ss_id, ss_pass, dev_id, dev_pass, media_dir_base, &interrupt_arc).await
    });

    if let Some(meta) = meta_opt {
        if let Ok(json_str) = serde_json::to_string(&meta) {
            return Ok(json_str);
        }
    }
    Ok("{}".to_string())
}

#[pyfunction]
fn start_batch_scrape(
    py: Python<'_>,
    db_path: &str,
    ss_id: &str,
    ss_pass: &str,
    dev_id: &str,
    dev_pass: &str,
    media_dir_base: &str,
    progress_callback: Option<PyObject>,
    interrupt_flag: Option<PyObject>,
) -> PyResult<usize> {
    batch_scraper::run_batch_scrape(py, db_path, ss_id, ss_pass, dev_id, dev_pass, media_dir_base, progress_callback, interrupt_flag)
}

#[pyfunction]
fn fetch_cores(py: Python<'_>) -> PyResult<Vec<String>> {
    let rt = Runtime::new().unwrap();
    // allow_threads evita bloquear el intérprete de Python durante el I/O
    let res = py.allow_threads(|| {
        rt.block_on(core_manager::fetch_available_cores_async())
    });
    
    match res {
        Ok(cores) => Ok(cores),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
fn download_core(
    core_name: String,
    dest_dir: String,
    progress_callback: Option<PyObject>
) -> PyResult<String> {
    let rt = Runtime::new().unwrap();
    let res = Python::with_gil(|py| {
        py.allow_threads(|| {
            rt.block_on(core_manager::download_core_async(core_name, dest_dir, progress_callback))
        })
    });
    
    match res {
        Ok(path) => Ok(path),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
fn search_games(py: Python<'_>, db_path: String, query: String, platform_filter: String) -> PyResult<Vec<PyObject>> {
    searcher::search_games(py, &db_path, &query, &platform_filter)
}

#[pymodule]
fn mango_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(scan_directory, m)?)?;
    m.add_function(wrap_pyfunction!(scrape_game_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(fetch_cores, m)?)?;
    m.add_function(wrap_pyfunction!(download_core, m)?)?;
    m.add_function(wrap_pyfunction!(start_batch_scrape, m)?)?;
    m.add_function(wrap_pyfunction!(search_games, m)?)?;
    Ok(())
}
