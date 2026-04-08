use pyo3::prelude::*;
use pyo3::types::PyDict;
use rusqlite::{Connection, Result};
use std::path::{Path, PathBuf};
use std::collections::HashMap;
use std::fs::{self, File};
use walkdir::WalkDir;
use rayon::prelude::*;
use md5;
use std::sync::Arc;
use crate::tools::header_reader;
use chrono;

/// Estructura de mapeo plataforma -> núcleos
fn get_core_map() -> HashMap<&'static str, Vec<(&'static str, &'static str)>> {
    let mut m = HashMap::new();
    m.insert("snes", vec![("snes9x", "Snes9x"), ("bsnes", "bsnes"), ("mesen-s", "Mesen-S")]);
    m.insert("nes", vec![("fceumm", "FCEUmm"), ("nestopia", "Nestopia"), ("mesen", "Mesen")]);
    m.insert("gba", vec![("mgba", "mGBA"), ("vba_next", "VBA-Next")]);
    m.insert("n64", vec![("mupen64plus_next", "Mupen64Plus-Next"), ("parallel_n64", "ParaLLEl N64")]);
    m.insert("ps1", vec![("beetle_psx_hw", "Beetle PSX HW"), ("pcsx_rearmed", "PCSX ReARMed")]);
    m.insert("ps2", vec![("pcsx2", "PCSX2")]);
    m.insert("psp", vec![("ppsspp", "PPSSPP")]);
    m.insert("ds", vec![("desmume", "DeSmuME"), ("melonds", "melonDS")]);
    m.insert("gc", vec![("dolphin", "Dolphin")]);
    m.insert("wii", vec![("dolphin", "Dolphin")]);
    m.insert("megadrive", vec![("genesis_plus_gx", "Genesis Plus GX"), ("picodrive", "PicoDrive")]);
    m.insert("dreamcast", vec![("flycast", "Flycast")]);
    m.insert("gb", vec![("gambatte", "Gambatte")]);
    m.insert("gbc", vec![("gambatte", "Gambatte")]);
    m
}

/// Detecta la ruta real de RetroArch basándose en la base de emuladores.
fn detect_retroarch(emu_base: &Path) -> Option<PathBuf> {
    let ra_base = emu_base.join("retroarch");
    
    #[cfg(target_os = "windows")]
    let ra_exe_name = "retroarch.exe";
    #[cfg(not(target_os = "windows"))]
    let ra_exe_name = "RetroArch.AppImage";
    
    if ra_base.join(ra_exe_name).exists() {
        return Some(ra_base.join(ra_exe_name));
    } else if let Ok(entries) = fs::read_dir(&ra_base) {
        for entry in entries.flatten() {
            if entry.path().is_dir() && entry.path().join(ra_exe_name).exists() {
                return Some(entry.path().join(ra_exe_name));
            }
        }
    }
    None
}

/// Formatea una duración en segundos a un string legible (ej: 1h 30m o 45m).
fn format_duration(seconds: i64) -> String {
    let h = seconds / 3600;
    let m = (seconds % 3600) / 60;
    if h > 0 {
        format!("{}h {}m", h, m)
    } else if m > 0 {
        format!("{}m", m)
    } else {
        "0h".to_string()
    }
}

/// Obtiene los núcleos Libretro disponibles para una plataforma dada.
fn get_available_libretro_cores(
    platform: &str,
    cores_dir: &Path,
    core_map: &HashMap<&str, Vec<(&str, &str)>>,
) -> Vec<String> {
    let mut cores = Vec::new();
    if let Some(suggestions) = core_map.get(platform) {
        for (cid, cname) in suggestions {
            let core_filename = format!("{}_libretro", cid);
            let core_path = cores_dir.join(platform);

            #[cfg(target_os = "windows")]
            let dot_ext = ".dll";
            #[cfg(not(target_os = "windows"))]
            let dot_ext = ".so";

            if core_path.join(format!("{}{}", core_filename, dot_ext)).exists() {
                cores.push(cname.to_string());
            }
        }
    }
    cores
}

/// Obtiene los emuladores standalone disponibles para una plataforma dada.
fn get_available_standalones(
    platform: &str,
    emu_base: &Path,
) -> Vec<String> {
    let mut standalones = Vec::new();
    let standalone_id = match platform {
        "gc" | "wii" => Some("dolphin"),
        "psp" => Some("ppsspp"),
        "ps2" => Some("pcsx2"),
        "ps1" => Some("duckstation"),
        "ps3" => Some("rpcs3"),
        "switch" => Some("ryujinx"),
        "vita" => Some("vita3k"),
        _ => None
    };

    if let Some(id) = standalone_id {
        if emu_base.join(id).exists() {
            standalones.push(id.to_uppercase());
        }
    }
    standalones
}

/// Formatea la lista de emuladores disponibles en un string legible.
fn format_emulator_list(
    cores: Vec<String>,
    standalones: Vec<String>,
    has_retroarch: bool,
) -> (bool, String) {
    let mut final_list = Vec::new();
    if has_retroarch {
        if !cores.is_empty() {
            final_list.push(format!("RetroArch ({})", cores.join(", ")));
        } else {
            final_list.push("RetroArch".to_string());
        }
    } else if !cores.is_empty() {
        final_list.push(format!("Cores Libretro: {}", cores.join(", ")));
    }

    final_list.extend(standalones);

    let has_any = !final_list.is_empty();
    let emu_text = if has_any { final_list.join(" | ") } else { "Sin emuladores".to_string() };

    (has_any, emu_text)
}

/// Determina los emuladores disponibles para una plataforma.
fn get_platform_emulators(
    platform: &str,
    emu_base: &Path,
    cores_dir: &Path,
    core_map: &HashMap<&str, Vec<(&str, &str)>>,
    has_retroarch: bool,
) -> (bool, String) {
    let cores = get_available_libretro_cores(platform, cores_dir, core_map);
    let standalones = get_available_standalones(platform, emu_base);
    format_emulator_list(cores, standalones, has_retroarch)
}

/// Genera el resumen de consolas consultando la BD de forma nativa.
pub fn get_consoles_summary_native(
    py: Python<'_>,
    db_path: &str,
    emulators_path: &str,
) -> PyResult<Vec<PyObject>> {
    let conn = Connection::open(db_path)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let core_map = get_core_map();
    let emu_base = Path::new(emulators_path);
    let has_retroarch = detect_retroarch(emu_base).is_some();
    let cores_dir = emu_base.join("cores");

    // 1. Obtener lista de plataformas con juegos
    let mut stmt = conn.prepare("SELECT DISTINCT platform FROM games")
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let platforms: Vec<String> = stmt.query_map([], |row| row.get(0))
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?
        .filter_map(Result::ok)
        .collect();

    let mut results = Vec::new();

    // 2. Procesar totalizadores para cada plataforma activa
    for platform in platforms {
        // A. Contar juegos
        let game_count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM games WHERE platform = ?",
            [&platform],
            |row| row.get(0),
        ).unwrap_or(0);

        if game_count == 0 { continue; }

        // B. Sumar tiempo
        let play_time: i64 = conn.query_row(
            "SELECT SUM(play_time_seconds) FROM games g LEFT JOIN play_stats s ON g.id = s.game_id WHERE g.platform = ?",
            [&platform],
            |row| row.get(0),
        ).unwrap_or(0);

        // C. Detectar emuladores instalados y formatear
        let (has_any, emu_text) = get_platform_emulators(&platform, emu_base, &cores_dir, &core_map, has_retroarch);

        // D. Empaquetar para Python
        let dict = PyDict::new(py);
        dict.set_item("platform", &platform)?;
        dict.set_item("gameCount", game_count.to_string())?;
        dict.set_item("playTime", format_duration(play_time))?;
        dict.set_item("hasCore", has_any)?;
        dict.set_item("emulatorName", emu_text)?;
        
        results.push(dict.into_any().unbind());
    }

    Ok(results)
}

/// Genera el resumen total del dashboard en un solo pase.
pub fn fetch_dashboard_stats(
    py: Python<'_>,
    db_path: &str,
) -> PyResult<PyObject> {
    let conn = Connection::open(db_path)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let dict = PyDict::new(py);

    // 1. Total de juegos
    let total_games: i64 = conn.query_row("SELECT COUNT(*) FROM games", [], |row| row.get(0)).unwrap_or(0);
    dict.set_item("total_games", total_games)?;

    // 2. Favoritos
    let total_favorites: i64 = conn.query_row("SELECT COUNT(*) FROM game_metadata WHERE is_favorite = 1", [], |row| row.get(0)).unwrap_or(0);
    dict.set_item("total_favorites", total_favorites)?;

    // 3. Tiempo Total
    let total_sec: i64 = conn.query_row("SELECT SUM(play_time_seconds) FROM play_stats", [], |row| row.get(0)).unwrap_or(0);
    dict.set_item("total_play_time", format_duration(total_sec))?;

    // 4. Último Juego Jugado
    let mut last_game_id: i64 = -1;
    if let Ok(mut stmt) = conn.prepare("
        SELECT g.id, COALESCE(g.display_name, m.title), g.platform, m.cover_2d_path, s.last_played_at
        FROM games g
        LEFT JOIN game_metadata m ON g.id = m.game_id
        LEFT JOIN play_stats s ON g.id = s.game_id
        WHERE s.last_played_at IS NOT NULL
        ORDER BY s.last_played_at DESC
        LIMIT 1
    ") {
        if let Ok(game_row) = stmt.query_row([], |row| {
            let id: i64 = row.get(0)?;
            last_game_id = id;
            let title: String = row.get(1)?;
            let plat: String = row.get(2)?;
            let cover_raw: Option<String> = row.get(3)?;
            let cover_path = cover_raw.unwrap_or_default().replace("\\", "/");
            let date: String = row.get(4)?;
            Ok((id, title, plat.to_uppercase(), cover_path, date))
        }) {
            let lg_dict = PyDict::new(py);
            lg_dict.set_item("id", game_row.0)?;
            lg_dict.set_item("title", game_row.1)?;
            lg_dict.set_item("platform", game_row.2)?;
            lg_dict.set_item("cover", game_row.3)?;
            lg_dict.set_item("date", game_row.4)?;
            dict.set_item("last_game", lg_dict)?;
        } else {
            dict.set_item("last_game", py.None())?;
        }
    } else {
        dict.set_item("last_game", py.None())?;
    }

    // 5. Top Plataformas
    if let Ok(mut stmt) = conn.prepare("
        SELECT platform, COUNT(*) as c 
        FROM games 
        GROUP BY platform 
        ORDER BY c DESC 
        LIMIT 5
    ") {
        let mut top_plats = Vec::new();
        if let Ok(rows) = stmt.query_map([], |row| {
            let p: String = row.get(0)?;
            let c: i64 = row.get(1)?;
            Ok((p, c))
        }) {
            let mut most_played_sys = String::from("N/A");
            for (idx, row_res) in rows.enumerate() {
                if let Ok((plat, cnt)) = row_res {
                    if idx == 0 { most_played_sys = plat.to_uppercase(); }
                    let pd = PyDict::new(py);
                    pd.set_item("id", plat)?;
                    pd.set_item("count", cnt)?;
                    top_plats.push(pd.into_any().unbind());
                }
            }
            dict.set_item("top_platforms", top_plats)?;
            dict.set_item("most_played_system", most_played_sys)?;
        }
    }

    // 6. Juegos Recientes
    if let Ok(mut stmt) = conn.prepare("
        SELECT g.id, COALESCE(g.display_name, m.title), g.platform, m.cover_2d_path, s.last_played_at, 
               COALESCE(s.play_time_seconds, 0) as playtime
        FROM games g
        LEFT JOIN game_metadata m ON g.id = m.game_id
        LEFT JOIN play_stats s ON g.id = s.game_id
        WHERE g.id != ?1 AND s.last_played_at IS NOT NULL
        ORDER BY playtime DESC, g.id DESC
        LIMIT 6
    ") {
        let mut recent = Vec::new();
        if let Ok(rows) = stmt.query_map([&last_game_id], |row| {
            let id: i64 = row.get(0)?;
            let title: String = row.get(1)?;
            let plat: String = row.get(2)?;
            let cover_raw: Option<String> = row.get(3)?;
            let cover_path = cover_raw.unwrap_or_default().replace("\\", "/");
            let sec: i64 = row.get(5)?;
            Ok((id, title, plat.to_uppercase(), cover_path, sec))
        }) {
            for row_res in rows {
                if let Ok((id, title, plat, cover, sec)) = row_res {
                    let rd = PyDict::new(py);
                    rd.set_item("id", id)?;
                    rd.set_item("title", title)?;
                    rd.set_item("platform", plat)?;
                    rd.set_item("cover", cover)?;
                    rd.set_item("playTime", format_duration(sec))?;
                    recent.push(rd.into_any().unbind());
                }
            }
        }
        dict.set_item("recent_games", recent)?;
    }

    Ok(dict.into_any().unbind())
}

/// Realiza una carga masiva y optimizada de todo lo necesario para el arranque.
/// Combina estadísticas, calentamiento de caché de archivos y verificación de emuladores.
pub fn precharge_ecosystem(
    py: Python<'_>,
    db_path: &str,
    media_path: &str,
    emulators_path: &str,
) -> PyResult<PyObject> {
    // 1. Obtener estadísticas base de la DB (Bloqueante pero rápido)
    let stats = fetch_dashboard_stats(py, db_path)?;
    
    // 2. Calentamiento de archivos (Paralelo - Rayon)
    // Leemos los primeros bytes de las carátulas para forzar el caché del OS
    let media_root = PathBuf::from(media_path);
    if media_root.exists() {
        let entries: Vec<PathBuf> = WalkDir::new(media_root)
            .max_depth(3)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_file())
            .take(100) // Solo las primeras 100 para no demorar el arranque
            .map(|e| e.path().to_path_buf())
            .collect();

        // Lectura paralela real liberando el GIL
        py.allow_threads(move || {
            entries.into_par_iter().for_each(|p| {
                if let Ok(mut f) = File::open(p) {
                    use std::io::Read;
                    let mut buf = [0u8; 4096];
                    let _ = f.read(&mut buf);
                }
            });
        });
    }

    // 3. Verificación de salud de Emuladores (Paralelo)
    let emu_root = PathBuf::from(emulators_path);
    let mut emu_status = Vec::new();
    if emu_root.exists() {
        let targets = vec!["retroarch", "dolphin", "pcsx2", "ppsspp", "duckstation"];
        for target in targets {
            let p = emu_root.join(target);
            if p.exists() {
                emu_status.push(target);
            }
        }
    }

    // 4. Integrar todo en el diccionario final
    let main_dict = stats.bind(py).downcast::<PyDict>()
        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Error interno al castear stats"))?;
    
    main_dict.set_item("installed_emulators", emu_status)?;
    main_dict.set_item("precharge_timestamp", chrono::Local::now().to_rfc3339())?;

    Ok(main_dict.clone().into_any().unbind())
}

/// Limpia el nombre de un archivo eliminando tags de región y corchetes.
fn normalize_title(raw: &str) -> String {
    let mut clean = String::with_capacity(raw.len());
    let mut depth = 0;
    
    for c in raw.chars() {
        match c {
            '(' | '[' => depth += 1,
            ')' | ']' => if depth > 0 { depth -= 1 },
            _ => if depth == 0 { clean.push(c); }
        }
    }
    
    // Normalizar espacios y trim
    clean.split_whitespace().collect::<Vec<_>>().join(" ")
}

fn get_platform_from_ext(ext: &str) -> String {
    let lower = ext.to_lowercase();
    match lower.as_str() {
        "smc" | "sfc" | "fig" | "swc" => "snes",
        "nes" | "fds" => "nes",
        "gb" => "gb",
        "gba" => "gba",
        "gbc" => "gbc",
        "z64" | "n64" | "v64" => "n64",
        "iso" | "bin" | "cue" | "img" | "mdf" | "pbp" => "ps1",
        "gz" | "chd" => "ps2",
        "cso" => "psp",
        "nds" => "ds",
        "gcm" | "rvz" => "gc",
        "wbfs" => "wii",
        "md" | "gen" | "smd" => "megadrive",
        "sms" => "mastersystem",
        "gg" => "gamegear",
        "cdi" | "gdi" => "dreamcast",
        _ => "unknown",
    }.to_string()
}

fn get_platform_from_path(p: &Path) -> Option<String> {
    let check_part = |part: &str| -> Option<&'static str> {
        match part {
            "snes" | "super nintendo" | "super famicom" | "sfc" => Some("snes"),
            "nes" | "nintendo entertainment system" | "famicom" => Some("nes"),
            "gb" | "gameboy" | "game boy" => Some("gb"),
            "gba" | "gameboy advance" | "game boy advance" => Some("gba"),
            "gbc" | "gameboy color" | "game boy color" => Some("gbc"),
            "n64" | "nintendo 64" => Some("n64"),
            "ps1" | "playstation" | "psx" => Some("ps1"),
            "ps2" | "playstation 2" | "ps2 iso" => Some("ps2"),
            "psp" | "playstation portable" => Some("psp"),
            "ds" | "nintendo ds" | "nds" => Some("ds"),
            "gc" | "gamecube" | "game cube" => Some("gc"),
            "wii" => Some("wii"),
            "megadrive" | "genesis" | "sega genesis" | "md" => Some("megadrive"),
            "mastersystem" | "master system" | "sms" => Some("mastersystem"),
            "gamegear" | "game gear" => Some("gamegear"),
            "dreamcast" | "dc" => Some("dreamcast"),
            _ => None,
        }
    };

    if let Some(parent) = p.parent() {
        if let Some(name) = parent.file_name().and_then(|n| n.to_str()) {
            if let Some(plat) = check_part(&name.to_lowercase()) {
                return Some(plat.to_string());
            }
        }
        if let Some(grandparent) = parent.parent() {
            if let Some(name) = grandparent.file_name().and_then(|n| n.to_str()) {
                if let Some(plat) = check_part(&name.to_lowercase()) {
                    return Some(plat.to_string());
                }
            }
        }
    }
    None
}

fn peek_zip_platform(path_str: &str) -> String {
    if let Ok(file) = File::open(path_str) {
        if let Ok(mut archive) = zip::ZipArchive::new(file) {
            for i in 0..archive.len() {
                if let Ok(f) = archive.by_index(i) {
                    if !f.is_dir() {
                        let name = f.name();
                        if let Some(ext) = Path::new(name).extension().and_then(|e| e.to_str()) {
                            let plat = get_platform_from_ext(ext);
                            if plat != "unknown" { return plat; }
                        }
                    }
                }
            }
        }
    }
    "unknown".to_string()
}

/// Representa un juego identificado durante el escaneo.
struct ScannedGame {
    path: String,
    hash: String,
    size: u64,
    display_name: String,
    platform: String,
    serial: Option<String>,
}

/// Obtiene un mapa de los juegos ya registrados en la base de datos para evitar re-procesar.
fn get_existing_games_map(db_path: &str) -> HashMap<String, (u64, String)> {
    Connection::open(db_path)
        .and_then(|conn| {
            let mut stmt = conn.prepare("SELECT file_path, file_size, COALESCE(serial, '') FROM games")?;
            let rows = stmt.query_map([], |row| {
                Ok((row.get::<_, String>(0)?, (row.get::<_, i64>(1)? as u64, row.get::<_, String>(2)?)))
            })?;
            let mut map = HashMap::new();
            for row in rows {
                if let Ok((path, data)) = row {
                    map.insert(path, data);
                }
            }
            Ok(map)
        })
        .unwrap_or_default()
}

/// Recolecta todos los archivos en un directorio que coincidan con las extensiones permitidas.
fn collect_files_to_scan(root: &Path, extensions: &[String]) -> Vec<PathBuf> {
    WalkDir::new(root)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .map(|e| e.path().to_path_buf())
        .filter(|p| {
            if let Some(ext) = p.extension() {
                let ext_str = ext.to_string_lossy().to_lowercase();
                extensions.iter().any(|e| e.to_lowercase() == ext_str)
            } else {
                false
            }
        })
        .collect()
}

/// Identifica un archivo de juego, extrayendo metadatos y calculando su hash.
fn identify_game_file(p: &Path) -> Option<ScannedGame> {
    let path_str = p.to_string_lossy().to_string();
    let meta = fs::metadata(p).ok()?;
    let size = meta.len();
    let raw_name = p.file_stem()?.to_string_lossy();
    let display_name = normalize_title(&raw_name);
    let mut platform = get_platform_from_path(p);
    let ext = p.extension().and_then(|e| e.to_str()).unwrap_or("").to_lowercase();

    if platform.is_none() && ext == "zip" {
        let peek = peek_zip_platform(&path_str);
        if peek != "unknown" { platform = Some(peek); }
    }
    let final_platform = platform.unwrap_or_else(|| get_platform_from_ext(&ext));
    
    // EXTRAER SERIAL
    let serial = header_reader::extract_serial(&path_str, &final_platform);

    let mut file = File::open(p).ok()?;
    let mut hasher = md5::Context::new();
    if std::io::copy(&mut file, &mut hasher).is_ok() {
        let hash = format!("{:x}", hasher.compute());
        Some(ScannedGame {
            path: path_str,
            hash,
            size,
            display_name,
            platform: final_platform,
            serial,
        })
    } else {
        None
    }
}

/// Inserta o actualiza el registro de un juego en la base de datos.
fn upsert_game_record(tx: &rusqlite::Transaction<'_>, game: &ScannedGame) -> Result<usize> {
    let serial_owned = game.serial.clone().unwrap_or_default();
    let changed = tx.execute(
        "INSERT INTO games (file_hash, file_path, display_name, platform, file_size, serial)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6)
         ON CONFLICT(file_hash) DO UPDATE SET
            serial = CASE WHEN serial IS NULL OR serial = '' THEN ?6 ELSE serial END,
            file_path = ?2",
        [&game.hash, &game.path, &game.display_name, &game.platform, &game.size.to_string(), &serial_owned],
    ).unwrap_or(0);

    let _ = tx.execute(
        "INSERT OR IGNORE INTO game_metadata (game_id, title)
         SELECT id, ? FROM games WHERE file_hash = ?",
        [game.display_name.clone(), game.hash.clone()],
    );

    Ok(changed)
}

/// Informa del progreso de registro a los callbacks de Python.
fn report_registration_progress(
    pc: &Option<Py<PyAny>>,
    sc: &Option<Py<PyAny>>,
    current_idx: usize,
    total: usize,
    game_name: &str,
) {
    if current_idx % 25 == 0 || current_idx == total {
        let progress = 0.9 + ((current_idx as f64 / total as f64) * 0.1);
        Python::with_gil(|py| {
            if let Some(pc_cb) = pc {
                let _ = pc_cb.bind(py).call1((progress,));
            }
            if let Some(sc_cb) = sc {
                let _ = sc_cb.bind(py).call1((format!("scan_registering|{}", game_name),));
            }
        });
    }
}

/// Registra una lista de juegos escaneados en la base de datos de forma masiva.
fn register_scanned_games(
    py: Python<'_>,
    db_path: &str,
    results: Vec<ScannedGame>,
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>,
) -> PyResult<usize> {
    let pc_final = progress_callback.as_ref().map(|cb| cb.clone_ref(py));
    let sc_final = status_callback.as_ref().map(|cb| cb.clone_ref(py));
    
    let db_path_owned = db_path.to_string();
    py.allow_threads(move || {
        let mut conn = Connection::open(&db_path_owned)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        
        let tx = conn.transaction()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
            
        let mut new_games = 0;
        let mut current_idx = 0;
        let total_new = results.len();

        for game in results {
            current_idx += 1;
            if upsert_game_record(&tx, &game).unwrap_or(0) > 0 {
                new_games += 1;
            }
            report_registration_progress(&pc_final, &sc_final, current_idx, total_new, &game.display_name);
        }

        tx.commit().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(new_games)
    })
}

/// Escanea un directorio buscando juegos y los registra directamente en la base de datos de forma nativa.
/// Optimiza todo el proceso liberando el GIL y usando un escaneo diferencial (solo hashea nuevos o cambiados).
pub fn scan_directory_to_db(
    py: Python<'_>,
    db_path: String,
    root_path: String,
    extensions: Vec<String>,
    progress_callback: Option<Py<PyAny>>,
    status_callback: Option<Py<PyAny>>,
) -> PyResult<usize> {
    let root = Path::new(&root_path);
    if !root.exists() {
        return Ok(0);
    }

    let existing_map = get_existing_games_map(&db_path);
    let files = collect_files_to_scan(root, &extensions);
    let total_files = files.len();
    if total_files == 0 { return Ok(0); }

    if let Some(sc) = &status_callback {
        let _ = sc.bind(py).call1(("scan_starting",));
    }

    let pc_arc_thread = progress_callback.as_ref().map(|cb| cb.clone_ref(py));
    let sc_arc_thread = status_callback.as_ref().map(|cb| cb.clone_ref(py));

    use std::sync::atomic::{AtomicUsize, Ordering};
    let results_count = Arc::new(AtomicUsize::new(0));

    Python::with_gil(|py| {
        if let Some(sc) = &status_callback {
            let _ = sc.bind(py).call1(("scan_preparing",));
        }
    });

    let results: Vec<ScannedGame> = py.allow_threads(move || {
        files.into_par_iter()
            .filter_map(|p| {
                let path_str = p.to_string_lossy().to_string();
                let meta = fs::metadata(&p).ok()?;
                let size = meta.len();

                let processed = results_count.fetch_add(1, Ordering::SeqCst) + 1;

                if processed % 5 == 0 || processed == total_files {
                    let progress = (processed as f64 / total_files as f64) * 0.9;
                    let game_name = p.file_stem().and_then(|s| s.to_str()).unwrap_or("...").to_string();

                    Python::with_gil(|py| {
                        if let Some(pc) = &pc_arc_thread {
                            let _ = pc.bind(py).call1((progress,));
                        }
                        if let Some(sc) = &sc_arc_thread {
                            let _ = sc.bind(py).call1((format!("scan_identifying|{}", game_name),));
                        }
                    });
                }

                if let Some((old_size, old_serial)) = existing_map.get(&path_str) {
                    if *old_size == size && !old_serial.is_empty() { return None; }
                }

                identify_game_file(&p)
            })
            .collect()
    });

    if results.is_empty() {
        if let Some(pc) = &progress_callback { let _ = pc.bind(py).call1((1.0,)); }
        return Ok(0);
    }

    register_scanned_games(py, &db_path, results, progress_callback, status_callback)
}

/// Escanea un directorio buscando juegos y calcula sus hashes en paralelo.
pub fn scan_directory(
    py: Python<'_>,
    root_path: &str,
    extensions: Vec<String>
) -> PyResult<Vec<PyObject>> {
    let root = Path::new(root_path);
    if !root.exists() {
        return Ok(Vec::new());
    }

    let files = collect_files_to_scan(root, &extensions);

    let results: Vec<ScannedGame> = py.allow_threads(move || {
        files.into_par_iter()
            .filter_map(|p| identify_game_file(&p))
            .collect()
    });

    let mut py_results = Vec::with_capacity(results.len());
    for game in results {
        let dict = PyDict::new(py);
        dict.set_item("path", game.path)?;
        dict.set_item("md5", game.hash)?;
        dict.set_item("size", game.size)?;
        dict.set_item("display_name", game.display_name)?;
        dict.set_item("platform", game.platform)?;
        dict.set_item("serial", game.serial.unwrap_or_default())?;
        py_results.push(dict.into_any().unbind());
    }

    Ok(py_results)
}
