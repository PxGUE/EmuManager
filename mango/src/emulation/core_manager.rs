use pyo3::prelude::*;
use reqwest::Client;
use std::path::{Path};
use std::fs::{self, File};
use std::io::{Write};
use futures_util::StreamExt;
use zip::ZipArchive;
use crate::{mango_info, mango_error};

/// Configuración de la URL del Buildbot de Libretro
#[cfg(target_os = "windows")]
const BUILDBOT_URL: &str = "http://buildbot.libretro.com/nightly/windows/x86_64/latest/";
#[cfg(target_os = "linux")]
const BUILDBOT_URL: &str = "http://buildbot.libretro.com/nightly/linux/x86_64/latest/";
#[cfg(target_os = "macos")]
const BUILDBOT_URL: &str = "http://buildbot.libretro.com/nightly/apple/osx/x86_64/latest/";

/// Retorna la lista de cores disponibles
pub async fn fetch_available_cores_async() -> Result<Vec<String>, anyhow::Error> {
    let client = Client::builder().user_agent("Mozilla/5.0").timeout(std::time::Duration::from_secs(15)).build()?;
    let response = client.get(BUILDBOT_URL).send().await?.text().await?;
    let mut cores = Vec::new();
    let mut offset = 0;
    while let Some(sp) = response[offset..].find("href=\"") {
        let ls = offset + sp + 6;
        if let Some(eo) = response[ls..].find("\"") {
            let le = ls + eo;
            let fl = &response[ls..le];
            if fl.contains("_libretro") && fl.ends_with(".zip") {
                if let Some(fnm) = fl.split('/').last() {
                    let cn = fnm.replace(".dll.zip", "").replace(".so.zip", "").replace(".zip", "");
                    if !cn.is_empty() { cores.push(cn); }
                }
            }
            offset = le;
        } else { break; }
    }
    cores.sort(); cores.dedup();
    Ok(cores)
}

/// Descarga core con PROGRESO MULTI-FASE (Red -> Disco)
pub async fn download_core_async(core_name: String, dest_dir: String, progress_callback: Option<Py<PyAny>>, status_callback: Option<Py<PyAny>>) -> Result<String, anyhow::Error> {
    let client = Client::new();
    #[cfg(target_os = "windows")] let ext = ".dll.zip";
    #[cfg(target_os = "linux")] let ext = ".so.zip";
    #[cfg(target_os = "macos")] let ext = ".dylib.zip";
    #[cfg(not(any(target_os = "windows", target_os = "linux", target_os = "macos")))] let ext = ".zip";
    
    let url = format!("{}{}{}", BUILDBOT_URL, core_name, ext);
    let dp = Path::new(&dest_dir);
    if !dp.exists() { fs::create_dir_all(&dp)?; }
    let zip_p = dp.join(format!("{}{}", core_name, ext));
    
    mango_info!("Orchestra: Iniciando descarga de núcleo '{}'", core_name);
    if let Some(ref scb) = status_callback { Python::with_gil(|py| { let _ = scb.call1(py, ("emu_status_connecting",)); }); }
    
    let res = client.get(&url).send().await?;
    let total = res.content_length().unwrap_or(0);
    let mut file = File::create(&zip_p)?;
    let mut d: u64 = 0;
    let mut s = res.bytes_stream();
    let mut lp = -0.1;
    
    if let Some(ref scb) = status_callback { Python::with_gil(|py| { let _ = scb.call1(py, ("emu_status_downloading",)); }); }
    while let Some(chunk) = s.next().await {
        let chunk = chunk?;
        file.write_all(&chunk)?;
        d += chunk.len() as u64;
        if let Some(ref cb) = progress_callback {
            if total > 0 {
                let p = (d as f64 / total as f64) * 0.7; // 70%
                if (p - lp).abs() >= 0.01 { lp = p; Python::with_gil(|py| { let _ = cb.call1(py, (p,)); }); }
            }
        }
    }
    
    mango_info!("Orchestra: Extrayendo núcleo '{}'...", core_name);
    if let Some(ref scb) = status_callback { Python::with_gil(|py| { let _ = scb.call1(py, ("emu_status_extracting",)); }); }
    let zf = File::open(&zip_p)?;
    let mut arc = ZipArchive::new(zf)?;
    let tf = arc.len();
    let mut ext_p = String::new();
    for i in 0..tf {
        let mut f = arc.by_index(i)?;
        let op = dp.join(f.mangled_name());
        if !(&*f.name()).ends_with('/') {
            let mut outfield = File::create(&op)?;
            std::io::copy(&mut f, &mut outfield)?;
            ext_p = op.to_string_lossy().to_string();
        }
        if let Some(ref cb) = progress_callback {
            let p = 0.7 + ((i as f64 / tf as f64) * 0.3);
            if (p - lp).abs() >= 0.05 { lp = p; Python::with_gil(|py| { let _ = cb.call1(py, (p,)); }); }
        }
    }
    let _ = fs::remove_file(&zip_p);
    
    // --- Post-procesamiento: Permisos Unix ---
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let p = Path::new(&ext_p);
        if p.exists() {
            let mut perms = fs::metadata(p)?.permissions();
            perms.set_mode(0o755);
            fs::set_permissions(p, perms)?;
        }
    }
    
    if let Some(ref scb) = status_callback { Python::with_gil(|py| { let _ = scb.call1(py, ("emu_status_installed",)); }); }
    if let Some(ref cb) = progress_callback { Python::with_gil(|py| { let _ = cb.call1(py, (1.0,)); }); }
    mango_info!("Orchestra: Núcleo '{}' instalado con éxito.", core_name);
    Ok(ext_p)
}

/// Descarga e instala un emulador con PROGRESO MULTI-FASE REAL
pub async fn download_emulator_async(url: String, dest_dir: String, expected_filename: String, progress_callback: Option<Py<PyAny>>, status_callback: Option<Py<PyAny>>) -> Result<String, anyhow::Error> {
    let client = Client::builder()
        .user_agent("EmuManager/M.A.N.G.O")
        .connect_timeout(std::time::Duration::from_secs(20))
        .timeout(std::time::Duration::from_secs(1200)) // 20 min para archivos grandes
        .build()?;
    let dp = Path::new(&dest_dir);
    if !dp.exists() { fs::create_dir_all(&dp)?; }
    let tmp = url.split('/').last().unwrap_or("dl.tmp");
    let dl_p = dp.join(tmp);
    
    mango_info!("Orchestra: Iniciando misión para emulador '{}'", expected_filename);
    if let Some(ref scb) = status_callback { Python::with_gil(|py| { let _ = scb.call1(py, ("emu_status_connecting",)); }); }
    
    let res = client.get(&url).send().await?;
    let total = res.content_length().unwrap_or(0);
    let mut file = File::create(&dl_p)?;
    let mut d: u64 = 0;
    let mut s = res.bytes_stream();
    let mut lp = -0.1;

    if let Some(ref scb) = status_callback { Python::with_gil(|py| { let _ = scb.call1(py, ("emu_status_downloading",)); }); }
    while let Some(chunk) = s.next().await {
        let chunk = chunk?;
        file.write_all(&chunk)?;
        d += chunk.len() as u64;
        if let Some(ref cb) = progress_callback {
            if total > 0 {
                let p = (d as f64 / total as f64) * 0.7;
                if (p - lp).abs() >= 0.01 { lp = p; Python::with_gil(|py| { let _ = cb.call1(py, (p,)); }); }
            }
        }
    }

    mango_info!("Orchestra: Extrayendo archivos del emulador...");
    if let Some(ref scb) = status_callback { Python::with_gil(|py| { let _ = scb.call1(py, ("emu_status_extracting",)); }); }
    
    let ext = tmp.to_lowercase();
    if ext.ends_with(".zip") {
        let zf = File::open(&dl_p)?;
        let mut a = ZipArchive::new(zf)?;
        let t = a.len();
        for i in 0..t {
            let mut f = a.by_index(i)?;
            let op = dp.join(f.mangled_name());
            if !(&*f.name()).ends_with('/') {
                if let Some(p) = op.parent() { fs::create_dir_all(p)?; }
                let mut outf = File::create(&op)?;
                std::io::copy(&mut f, &mut outf)?;
            }
            if let Some(ref cb) = progress_callback {
                let p = 0.7 + ((i as f64 / t as f64) * 0.3);
                if (p - lp).abs() >= 0.05 { lp = p; Python::with_gil(|py| { let _ = cb.call1(py, (p,)); }); }
            }
        }
    } else if ext.ends_with(".7z") {
        if let Some(ref cb) = progress_callback { Python::with_gil(|py| { let _ = cb.call1(py, (0.85,)); }); }
        // Nota:sevenz_rust::decompress_file es sincrónica, el hilo se bloqueará aquí hasta completar.
        sevenz_rust::decompress_file(&dl_p, dp)?;
    } else {
        fs::rename(&dl_p, dp.join(&expected_filename))?;
    }
    
    let _ = fs::remove_file(&dl_p);
    
    let final_exe = dp.join(&expected_filename);
    
    // --- Lógica de Auto-Configuración M.A.N.G.O Inteligente ---
    // Buscamos si el ejecutable está en la raíz o en una subcarpeta (Buildbot style)
    let mut real_exe_path = None;
    if final_exe.exists() {
        real_exe_path = Some(final_exe.clone());
    } else if let Ok(entries) = fs::read_dir(&dp) {
        for entry in entries.flatten() {
            if entry.path().is_dir() {
                let sub_exe = entry.path().join(&expected_filename);
                if sub_exe.exists() {
                    real_exe_path = Some(sub_exe);
                }
            }
        }
    }

    let return_path = if let Some(exe_path) = real_exe_path {
        let is_retroarch = expected_filename.to_lowercase().ends_with("retroarch.exe");
        if is_retroarch {
            let exe_dir = exe_path.parent().unwrap();
            
            mango_info!("Orchestra: RetroArch detectado. Generando configuración maestra (Portable)...");
            if let Some(ref scb) = status_callback { 
                Python::with_gil(|py| { let _ = scb.call1(py, ("emu_status_configuring",)); }); 
            }
            
            let mut cfg_content = String::new();
            let mut relative_parts = String::from(":\\..");
            if exe_dir != dp { relative_parts.push_str("\\.."); }
            relative_parts.push_str("\\cores");

            cfg_content.push_str(&format!("libretro_directory = \"{}\"\n", relative_parts));
            cfg_content.push_str("system_directory = \":\\system\"\n");
            cfg_content.push_str("savefile_directory = \":\\saves\"\n");
            cfg_content.push_str("savestate_directory = \":\\states\"\n");
            cfg_content.push_str("video_driver = \"gl\"\n");
            cfg_content.push_str("config_save_on_exit = \"true\"\n");
            cfg_content.push_str("menu_driver = \"xmb\"\n");
            cfg_content.push_str("menu_show_advanced_settings = \"true\"\n");
            
            let _ = fs::create_dir_all(exe_dir.join("cores"));
            let _ = fs::create_dir_all(exe_dir.join("system"));
            let _ = fs::create_dir_all(exe_dir.join("saves"));
            let _ = fs::create_dir_all(exe_dir.join("states"));

            let cfg_path = exe_dir.join("retroarch.cfg");
            let _ = fs::write(&cfg_path, cfg_content);
        }
        exe_path.to_string_lossy().to_string()
    } else {
        final_exe.to_string_lossy().to_string()
    };

    // --- Post-procesamiento: Permisos Unix ---
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let p = Path::new(&return_path);
        if p.exists() {
            let mut perms = fs::metadata(p)?.permissions();
            perms.set_mode(0o755);
            let _ = fs::set_permissions(p, perms);
        }
    }

    if let Some(ref scb) = status_callback { Python::with_gil(|py| { let _ = scb.call1(py, ("emu_status_installed",)); }); }
    if let Some(ref cb) = progress_callback { Python::with_gil(|py| { let _ = cb.call1(py, (1.0,)); }); }
    mango_info!("Orchestra: Emulador '{}' listo en {}", expected_filename, return_path);
    Ok(return_path)
}

pub async fn update_emulator_async(u: String, d: String, e: String, c: Option<Py<PyAny>>, s: Option<Py<PyAny>>) -> Result<String, anyhow::Error> {
    download_emulator_async(u, d, e, c, s).await
}

pub async fn remove_emulator_files_async(t: String) -> Result<(), anyhow::Error> {
    let p = Path::new(&t);
    if p.exists() { if p.is_dir() { fs::remove_dir_all(p)?; } else { fs::remove_file(p)?; } }
    Ok(())
}
