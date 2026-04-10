use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use tokio::runtime::Runtime;
use once_cell::sync::Lazy;
use std::collections::HashMap;

pub mod emulation;
pub mod scraping;
pub mod library;
pub mod sync;
pub mod tools;

static RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    Runtime::new().expect("M.A.N.G.O (Fatal): Error al inicializar el Tokio Runtime.")
});

fn to_py_err(err: anyhow::Error) -> PyErr {
    pyo3::exceptions::PyRuntimeError::new_err(err.to_string())
}

#[pyfunction]
fn fetch_cores(py: Python<'_>) -> PyResult<Vec<String>> {
    let res = py.allow_threads(move || { RUNTIME.block_on(emulation::core_manager::fetch_available_cores_async()) });
    res.map_err(to_py_err)
}

#[pyfunction]
#[pyo3(signature = (core_name, dest_dir, progress_callback=None, status_callback=None))]
fn download_core(
    py: Python<'_>,
    core_name: String,
    dest_dir: String,
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>
) -> PyResult<String> {
    let res = py.allow_threads(move || {
        RUNTIME.block_on(emulation::core_manager::download_core_async(core_name, dest_dir, progress_callback, status_callback))
    });
    res.map_err(to_py_err)
}

#[pyfunction]
#[pyo3(signature = (url, dest_dir, expected_filename, progress_callback=None, status_callback=None))]
fn download_emulator(
    py: Python<'_>,
    url: String, 
    dest_dir: String, 
    expected_filename: String, 
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>
) -> PyResult<String> {
    let res = py.allow_threads(move || {
        RUNTIME.block_on(emulation::core_manager::download_emulator_async(url, dest_dir, expected_filename, progress_callback, status_callback))
    });
    res.map_err(to_py_err)
}

#[pyfunction]
#[pyo3(signature = (emu_id, system_id, url, dest_dir, executable, progress_callback=None, status_callback=None))]
fn install_emulator_orchestra(
    py: Python<'_>,
    emu_id: String,
    system_id: String,
    url: String,
    dest_dir: String,
    executable: String,
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>
) -> PyResult<String> {
    let res = py.allow_threads(move || {
        RUNTIME.block_on(emulation::core_manager::install_emulator_orchestra_async(emu_id, system_id, url, dest_dir, executable, progress_callback, status_callback))
    });
    res.map_err(to_py_err)
}

#[pyfunction]
#[pyo3(signature = (id, version, url, dest_dir, executable, progress_callback=None, status_callback=None))]
fn update_emulator(
    py: Python<'_>,
    id: String,
    version: String,
    url: String,
    dest_dir: String,
    executable: String,
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>
) -> PyResult<String> {
    let res = py.allow_threads(move || {
        RUNTIME.block_on(emulation::core_manager::update_emulator_async(id, version, url, dest_dir, executable, progress_callback, status_callback))
    });
    res.map_err(to_py_err)
}

#[pyfunction]
fn uninstall_emulator(
    py: Python<'_>,
    dest_dir: String
) -> PyResult<()> {
    let res = py.allow_threads(move || {
        RUNTIME.block_on(emulation::core_manager::remove_emulator_files_async(dest_dir))
    });
    res.map_err(to_py_err)
}

#[pyfunction]
fn set_log_callback(callback: Py<PyAny>) {
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
#[pyo3(signature = (db_path, ss_id, ss_pass, dev_id, dev_pass, media_dir, progress_cb=None, status_cb=None, gametdb_mode="web".to_string()))]
fn start_batch_scrape(
    py: Python<'_>,
    db_path: String,
    ss_id: String,
    ss_pass: String,
    dev_id: String,
    dev_pass: String,
    media_dir: String,
    progress_cb: Option<Py<PyAny>>,
    status_cb: Option<Py<PyAny>>,
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
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>,
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
fn search_games(
    py: Python<'_>,
    db_path: String,
    query: String,
    platform: String
) -> PyResult<Vec<PyObject>> {
    library::searcher::search_games(py, &db_path, &query, &platform)
}

#[pyfunction]
fn precharge_ecosystem(
    py: Python<'_>,
    db_path: String,
    media_path: String,
    emulators_path: String,
) -> PyResult<PyObject> {
    library::library_manager::precharge_ecosystem(py, &db_path, &media_path, &emulators_path)
}

#[pyfunction]
fn check_system_installed(system_id: String) -> bool {
    emulation::orchestrator::is_system_package_installed(&system_id)
}

#[pyfunction]
fn check_emulators_status(py: Python<'_>, targets: Vec<(String, String, String)>) -> PyResult<Py<PyList>> {
    let results = py.allow_threads(move || {
        emulation::orchestrator::check_emulators_status_batch(targets)
    });

    let list = PyList::empty(py);
    for r in results {
        let dict = PyDict::new(py);
        let _ = dict.set_item("id", r.id);
        let _ = dict.set_item("is_installed", r.is_installed);
        let _ = dict.set_item("source", r.source);
        let _ = dict.set_item("local_path", r.local_path);
        let _ = list.append(dict);
    }
    Ok(list.into())
}

#[pyfunction]
fn check_all_updates(py: Python<'_>, targets: HashMap<String, String>) -> PyResult<Py<PyList>> {
    let results = py.allow_threads(move || {
        RUNTIME.block_on(sync::updates::check_parallel_updates(targets))
    });
    
    let list = PyList::empty(py);
    for r in results {
        let dict = PyDict::new(py);
        let _ = dict.set_item("id", r.id);
        let _ = dict.set_item("remote_tag", r.remote_tag);
        let _ = dict.set_item("download_url", r.download_url);
        let _ = list.append(dict);
    }
    Ok(list.into())
}

#[pymodule]
fn mango_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
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
    m.add_function(wrap_pyfunction!(precharge_ecosystem, m)?)?;
    m.add_function(wrap_pyfunction!(check_system_installed, m)?)?;
    m.add_function(wrap_pyfunction!(check_emulators_status, m)?)?;
    Ok(())
}
