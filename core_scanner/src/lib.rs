use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::Path;
use std::fs::File;
use std::io::{Read, BufReader};
use walkdir::WalkDir;
use rayon::prelude::*;
use md5;
use crc32fast::Hasher;

/// Calcula MD5 y CRC32 de un archivo de forma eficiente
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

    // Recolectar archivos (I/O serie pero rápido)
    let files: Vec<_> = WalkDir::new(base_path)
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
                if extensions.is_empty() || extensions.iter().any(|e| e.to_lowercase() == ext_lower) {
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

#[pymodule]
fn core_scanner(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(scan_directory, m)?)?;
    Ok(())
}
