use pyo3::prelude::*;
use pyo3::types::PyDict;
use rusqlite::{Connection, Result};
use std::path::Path;
use std::collections::HashMap;

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
    let ra_base = emu_base.join("retroarch");
    
    // Detectar RetroArch (universal)
    #[cfg(target_os = "windows")]
    let ra_exe = "retroarch.exe";
    #[cfg(not(target_os = "windows"))]
    let ra_exe = "RetroArch.AppImage";
    
    let has_retroarch = ra_base.join(ra_exe).exists();
    let cores_dir = ra_base.join("cores");

    // 1. Obtener lista de plataformas con juegos
    let mut stmt = conn.prepare("SELECT DISTINCT platform FROM games")
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let platforms_iter = stmt.query_map([], |row| row.get(0))
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    
    let platforms: Vec<String> = platforms_iter
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
            "SELECT SUM(play_time_seconds) FROM play_stats s JOIN games g ON s.game_id = g.id WHERE g.platform = ?",
            [&platform],
            |row| row.get(0),
        ).unwrap_or(0);

        // C. Detectar emuladores instalados
        let mut cores = Vec::new();
        let mut has_retroarch = has_retroarch;

        // Check Libretro Cores en disco
        if let Some(suggestions) = core_map.get(platform.as_str()) {
            for (cid, cname) in suggestions {
                let core_filename = format!("{}_libretro", cid);
                let core_path = cores_dir.join(&platform);
                
                #[cfg(target_os = "windows")]
                let dot_ext = ".dll";
                #[cfg(not(target_os = "windows"))]
                let dot_ext = ".so";
                
                if core_path.join(format!("{}{}", core_filename, dot_ext)).exists() {
                    cores.push(cname.to_string());
                }
            }
        }

        // Check Standalone específicos
        let mut standalones = Vec::new();
        let standalone_id = match platform.as_str() {
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

        // D. Formatear texto de emuladores (Lógica Inteligente)
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

        // E. Formatear tiempo dinámico
        let play_time_str = {
            let h = play_time / 3600;
            let m = (play_time % 3600) / 60;
            if h > 0 {
                format!("{}h {}m", h, m)
            } else if m > 0 {
                format!("{}m", m)
            } else {
                "0h".to_string()
            }
        };

        // F. Empaquetar para Python
        let dict = PyDict::new(py);
        dict.set_item("platform", &platform)?;
        dict.set_item("gameCount", game_count.to_string())?;
        dict.set_item("playTime", play_time_str)?;
        dict.set_item("hasCore", has_any)?;
        dict.set_item("emulatorName", emu_text)?;
        
        results.push(dict.into_any().unbind());
    }

    Ok(results)
}
