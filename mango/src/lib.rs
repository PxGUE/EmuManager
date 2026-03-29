use pyo3::prelude::*;
use tokio::runtime::Runtime;
use std::sync::Arc;
mod emulation;
mod scraping;
mod library;
mod tools;

#[pyfunction]
fn fetch_cores(py: Python<'_>) -> PyResult<Vec<String>> {
    let rt = Runtime::new().unwrap();
    let res = py.allow_threads(move || { rt.block_on(emulation::core_manager::fetch_available_cores_async()) });
    match res {
        Ok(cores) => Ok(cores),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
fn download_core(
    py: Python<'_>,
    core_name: String,
    dest_dir: String,
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>
) -> PyResult<String> {
    let rt = Runtime::new().unwrap();
    let pc = progress_callback.as_ref().map(|cb| cb.clone_ref(py));
    let sc = status_callback.as_ref().map(|cb| cb.clone_ref(py));
    let res = py.allow_threads(move || {
        rt.block_on(emulation::core_manager::download_core_async(core_name, dest_dir, pc, sc))
    });
    match res {
        Ok(path) => Ok(path),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
fn download_emulator(
    py: Python<'_>,
    url: String, 
    dest_dir: String, 
    expected_filename: String, 
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>
) -> PyResult<String> {
    let rt = Runtime::new().unwrap();
    let pc = progress_callback.as_ref().map(|cb| cb.clone_ref(py));
    let sc = status_callback.as_ref().map(|cb| cb.clone_ref(py));
    let res = py.allow_threads(move || {
        rt.block_on(emulation::core_manager::download_emulator_async(url, dest_dir, expected_filename, pc, sc))
    });
    match res {
        Ok(path) => Ok(path),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
fn install_emulator_orchestra(
    py: Python<'_>,
    _emu_id: String,
    system_id: String,
    portable_url: String,
    dest_dir: String,
    executable_name: String,
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>
) -> PyResult<String> {
    let rt = Arc::new(Runtime::new().unwrap());
    
    if !system_id.is_empty() {
        let sid = system_id.clone();
        let rt_shared = rt.clone();
        if let Ok(_) = py.allow_threads(move || rt_shared.block_on(emulation::orchestrator::install_via_system(&sid))) {
            if let Some(path) = emulation::orchestrator::find_system_executable(&executable_name) { return Ok(path); }
            return Ok("SYSTEM_INSTALLED".to_string());
        }
    }
    
    if !portable_url.is_empty() {
        let pc = progress_callback.as_ref().map(|cb| cb.clone_ref(py));
        let sc = status_callback.as_ref().map(|cb| cb.clone_ref(py));
        let rt_shared = rt.clone();
        let res = py.allow_threads(move || {
            rt_shared.block_on(emulation::core_manager::download_emulator_async(portable_url, dest_dir, executable_name, pc, sc))
        });
        match res {
            Ok(path) => return Ok(path),
            Err(e) => return Err(pyo3::exceptions::PyRuntimeError::new_err(format!("Fallo total: {}", e))),
        }
    }
    
    Err(pyo3::exceptions::PyRuntimeError::new_err("No hay ID de sistema ni URL portable disponible."))
}

#[pyfunction]
fn update_emulator(
    py: Python<'_>,
    url: String, 
    dest_dir: String, 
    expected_filename: String, 
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>
) -> PyResult<String> {
    let rt = Runtime::new().unwrap();
    let pc = progress_callback.as_ref().map(|cb| cb.clone_ref(py));
    let sc = status_callback.as_ref().map(|cb| cb.clone_ref(py));
    let res = py.allow_threads(move || {
        rt.block_on(emulation::core_manager::update_emulator_async(url, dest_dir, expected_filename, pc, sc))
    });
    match res {
        Ok(path) => Ok(path),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
fn uninstall_emulator(py: Python<'_>, target_path: String) -> PyResult<()> {
    let rt = Runtime::new().unwrap();
    let res = py.allow_threads(move || {
        rt.block_on(emulation::core_manager::remove_emulator_files_async(target_path))
    });
    match res {
        Ok(_) => Ok(()),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
    }
}

#[pyfunction]
fn set_log_callback(callback: PyObject) {
    tools::logging::set_log_callback(callback);
}

#[pyfunction]
fn fetch_consoles_summary(
    py: Python<'_>,
    db_path: String,
    emus_path: String
) -> PyResult<Vec<PyObject>> {
    library::library_manager::get_consoles_summary_native(py, &db_path, &emus_path)
}

#[pyfunction]
fn fetch_dashboard_stats(
    py: Python<'_>,
    db_path: String,
) -> PyResult<PyObject> {
    library::library_manager::fetch_dashboard_stats(py, &db_path)
}

#[pyfunction]
fn scan_directory(
    py: Python<'_>,
    path: String,
    extensions: Vec<String>
) -> PyResult<Vec<PyObject>> {
    library::library_manager::scan_directory(py, &path, extensions)
}

#[pyfunction]
fn start_batch_scrape(
    py: Python<'_>,
    db_path: String,
    ss_id: String,
    ss_pass: String,
    dev_id: String,
    dev_pass: String,
    media_dir: String,
    progress_cb: Option<PyObject>,
    interrupt_flag: Option<PyObject>,
) -> PyResult<usize> {
    scraping::batch_scraper::run_batch_scrape(py, &db_path, &ss_id, &ss_pass, &dev_id, &dev_pass, &media_dir, progress_cb, interrupt_flag)
}

#[pyfunction]
fn launch_game(
    py: Python<'_>,
    emu_path: String,
    rom_path: String,
    core_path: Option<String>
) -> PyResult<i64> {
    py.allow_threads(move || {
        // Nota: El orden en launcher.rs es (emu, core, game)
        match tools::launcher::launch_and_track(&emu_path, core_path, &rom_path) {
            Ok(duration) => Ok(duration as i64),
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e)),
        }
    })
}

#[pyfunction]
fn search_games(
    py: Python<'_>,
    db_path: String,
    query: String,
    platform: String
) -> PyResult<Vec<PyObject>> {
    library::searcher::search_games(py, &db_path, &query, &platform)
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
    m.add_function(wrap_pyfunction!(start_batch_scrape, m)?)?;
    m.add_function(wrap_pyfunction!(search_games, m)?)?;
    m.add_function(wrap_pyfunction!(launch_game, m)?)?;
    Ok(())
}
