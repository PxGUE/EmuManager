use pyo3::prelude::*;
use std::path::Path;
use walkdir::WalkDir;
use rayon::prelude::*;

/// Escanea un directorio en paralelo y devuelve una lista de archivos que coinciden con las extensiones.
/// Ejemplo (["iso", "cue", "bin"])
#[pyfunction]
fn scan_directory(path: String, extensions: Vec<String>) -> PyResult<Vec<String>> {
    let base_path = Path::new(&path);
    if !base_path.exists() {
        return Ok(vec![]);
    }

    // Recolectar recursivamente archivos usando WalkDir (I/O)
    let files: Vec<_> = WalkDir::new(base_path)
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_file())
        .collect();

    // Procesar en paralelo con Rayon (Acelerando búsquedas masivas)
    let matched_files: Vec<String> = files.into_par_iter()
        .filter_map(|entry| {
            let path = entry.path();
            if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                if extensions.is_empty() || extensions.contains(&ext.to_string()) {
                    return Some(path.to_string_lossy().into_owned());
                }
            }
            None
        })
        .collect();

    Ok(matched_files)
}

/// A Python module implemented in Rust.
#[pymodule]
fn core_scanner(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(scan_directory, m)?)?;
    Ok(())
}
