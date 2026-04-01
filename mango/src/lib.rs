use pyo3::prelude::*;
use tokio::runtime::Runtime;
use std::sync::Arc;
use once_cell::sync::Lazy;

mod emulation;
mod scraping;
mod library;
pub mod sync;
mod tools;

static RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    Runtime::new().expect("M.A.N.G.O (Fatal): Error al inicializar el Tokio Runtime.")
});

#[pyfunction]
#[pyo3(signature = ())]
fn fetch_cores(py: Python<'_>) -> PyResult<Vec<String>> {
    let res = py.allow_threads(move || { RUNTIME.block_on(emulation::core_manager::fetch_available_cores_async()) });
    match res {
        Ok(cores) => Ok(cores),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
#[pyo3(signature = (core_name, dest_dir, progress_callback=None, status_callback=None))]
fn download_core(
    py: Python<'_>,
    core_name: String,
    dest_dir: String,
    progress_callback: Option<PyObject>,
    status_callback: Option<PyObject>
) -> PyResult<String> {
    let res = py.allow_threads(move || {
        RUNTIME.block_on(emulation::core_manager::download_core_async(core_name, dest_dir, progress_callback, status_callback))
    });
    match res {
        Ok(path) => Ok(path),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
#[pyo3(signature = (url, dest_dir, expected_filename, progress_callback=None, status_callback=None))]
fn download_emulator(
    py: Python<'_>,
    url: String, 
    dest_dir: String, 
    expected_filename: String, 
    progress_callback: Option<PyObject>,
    status_callback: Option<PyObject>
) -> PyResult<String> {
    let res = py.allow_threads(move || {
        RUNTIME.block_on(emulation::core_manager::download_emulator_async(url, dest_dir, expected_filename, progress_callback, status_callback))
    });
    match res {
        Ok(path) => Ok(path),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
#[pyo3(signature = (_emu_id, system_id, portable_url, dest_dir, executable_name, progress_callback=None, status_callback=None))]
fn install_emulator_orchestra(
    py: Python<'_>,
    _emu_id: String,
    system_id: String,
    portable_url: String,
    dest_dir: String,
    executable_name: String,
    progress_callback: Option<PyObject>,
    status_callback: Option<PyObject>
) -> PyResult<String> {
    if !system_id.is_empty() {
        let sid = system_id.clone();
        if let Ok(_) = py.allow_threads(move || RUNTIME.block_on(emulation::orchestrator::install_via_system(&sid))) {
            if let Some(path) = emulation::orchestrator::find_system_executable(&executable_name) { return Ok(path); }
            return Ok("SYSTEM_INSTALLED".to_string());
        }
    }
    
    if !portable_url.is_empty() {
        let res = py.allow_threads(move || {
            RUNTIME.block_on(emulation::core_manager::download_emulator_async(portable_url, dest_dir, executable_name, progress_callback, status_callback))
        });
        match res {
            Ok(path) => return Ok(path),
            Err(e) => return Err(pyo3::exceptions::PyRuntimeError::new_err(format!("Fallo total: {}", e))),
        }
    }
    
    Err(pyo3::exceptions::PyRuntimeError::new_err("No hay ID de sistema ni URL portable disponible."))
}

#[pyfunction]
#[pyo3(signature = (url, dest_dir, expected_filename, progress_callback=None, status_callback=None))]
fn update_emulator(
    py: Python<'_>,
    url: String, 
    dest_dir: String, 
    expected_filename: String, 
    progress_callback: Option<PyObject>,
    status_callback: Option<PyObject>
) -> PyResult<String> {
    let res = py.allow_threads(move || {
        RUNTIME.block_on(emulation::core_manager::update_emulator_async(url, dest_dir, expected_filename, progress_callback, status_callback))
    });
    match res {
        Ok(path) => Ok(path),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
#[pyo3(signature = (target_path))]
fn uninstall_emulator(py: Python<'_>, target_path: String) -> PyResult<()> {
    let res = py.allow_threads(move || {
        RUNTIME.block_on(emulation::core_manager::remove_emulator_files_async(target_path))
    });
    match res {
        Ok(_) => Ok(()),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
#[pyo3(signature = (callback))]
fn set_log_callback(callback: PyObject) {
    tools::logging::set_log_callback(callback);
}

#[pyfunction]
#[pyo3(signature = (db_path, emus_path))]
fn fetch_consoles_summary(
    py: Python<'_>,
    db_path: String,
    emus_path: String
) -> PyResult<Vec<PyObject>> {
    library::library_manager::get_consoles_summary_native(py, &db_path, &emus_path)
}

#[pyfunction]
#[pyo3(signature = (db_path))]
fn fetch_dashboard_stats(
    py: Python<'_>,
    db_path: String,
) -> PyResult<PyObject> {
    library::library_manager::fetch_dashboard_stats(py, &db_path)
}

#[pyfunction]
#[pyo3(signature = (path, extensions))]
fn scan_directory(
    py: Python<'_>,
    path: String,
    extensions: Vec<String>
) -> PyResult<Vec<PyObject>> {
    library::library_manager::scan_directory(py, &path, extensions)
}

#[pyfunction]
#[pyo3(signature = (db_path, ss_id, ss_pass, dev_id, dev_pass, media_dir, progress_cb=None, status_cb=None, gametdb_mode="web".to_string()))]
fn start_batch_scrape(
    py: Python<'_>,
    db_path: String,
    ss_id: String,
    ss_pass: String,
    dev_id: String,
    dev_pass: String,
    media_dir: String,
    progress_cb: Option<PyObject>,
    status_cb: Option<PyObject>,
    gametdb_mode: String,
) -> PyResult<usize> {
    scraping::batch_scraper::run_batch_scrape(py, db_path, ss_id, ss_pass, dev_id, dev_pass, media_dir, progress_cb, status_cb, gametdb_mode)
}

#[pyfunction]
#[pyo3(signature = (db_path, path, extensions, progress_callback=None, status_callback=None))]
fn scan_directory_to_db(
    py: Python<'_>,
    db_path: String,
    path: String,
    extensions: Vec<String>,
    progress_callback: Option<PyObject>,
    status_callback: Option<PyObject>,
) -> PyResult<usize> {
    library::library_manager::scan_directory_to_db(py, db_path, path, extensions, progress_callback, status_callback)
}

#[pyfunction]
#[pyo3(signature = (emu_path, rom_path, core_path=None))]
fn launch_game(
    py: Python<'_>,
    emu_path: String,
    rom_path: String,
    core_path: Option<String>
) -> PyResult<i64> {
    py.allow_threads(move || {
        match tools::launcher::launch_and_track(&emu_path, core_path, &rom_path) {
            Ok(duration) => Ok(duration as i64),
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e)),
        }
    })
}

#[pyfunction]
#[pyo3(signature = (db_path, query, platform))]
fn search_games(
    py: Python<'_>,
    db_path: String,
    query: String,
    platform: String
) -> PyResult<Vec<PyObject>> {
    library::searcher::search_games(py, &db_path, &query, &platform)
}

#[pyfunction]
#[pyo3(signature = (targets))]
fn check_all_updates(py: Python<'_>, targets: std::collections::HashMap<String, String>) -> PyResult<PyObject> {
    let results = py.allow_threads(move || {
        RUNTIME.block_on(sync::updates::check_parallel_updates(targets))
    });
    
    let list = pyo3::types::PyList::empty(py);
    for r in results {
        let dict = pyo3::types::PyDict::new(py);
        let _ = dict.set_item("id", r.id);
        let _ = dict.set_item("remote_tag", r.remote_tag);
        let _ = dict.set_item("download_url", r.download_url);
        let _ = list.append(dict);
    }
    Ok(list.into_any().unbind())
}

#[pymodule]
fn mango_engine(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fetch_cores, m)?)?;
    m.add_function(wrap_pyfunction!(download_core, m)?)?;
    m.add_function(wrap_pyfunction!(download_emulator, m)?)?;
    m.add_function(wrap_pyfunction!(install_emulator_orchestra, m)?)?;
    m.add_function(wrap_pyfunction!(update_emulator, m)?)?;
    m.add_function(wrap_pyfunction!(uninstall_emulator, m)?)?;
    m.add_function(wrap_pyfunction!(set_log_callback, m)?)?;
    m.add_function(wrap_pyfunction!(fetch_consoles_summary, m)?)?;
    m.add_function(wrap_pyfunction!(fetch_dashboard_stats, m)?)?;
    m.add_function(wrap_pyfunction!(scan_directory, m)?)?;
    m.add_function(wrap_pyfunction!(scan_directory_to_db, m)?)?;
    m.add_function(wrap_pyfunction!(start_batch_scrape, m)?)?;
    m.add_function(wrap_pyfunction!(search_games, m)?)?;
    m.add_function(wrap_pyfunction!(launch_game, m)?)?;
    m.add_function(wrap_pyfunction!(check_all_updates, m)?)?;
    Ok(())
}
