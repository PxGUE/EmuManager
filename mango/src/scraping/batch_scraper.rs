use crate::scraping::scraper::{scrape_game, ScrapedMetadata};
use rusqlite::{params, Connection};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use pyo3::prelude::*;
use std::path::Path;
use std::thread;
use std::time::Duration;
use futures::stream::{self, StreamExt};

pub fn log_to_python(py: Python<'_>, level: &str, message: &str) {
    let script = format!(
        "from core.logger import EmuLog; EmuLog.{}(\"[MANGO] {}\")",
        level, message.replace("\"", "\\\"")
    );
    let _ = py.run_bound(&script, None, None);
}

// Versión que captura el GIL internamente para mayor seguridad en hilos
fn log_to_python_safe(level: &str, message: &str) {
    Python::with_gil(|py| {
        log_to_python(py, level, message);
    });
}

struct PendingGame {
    id: i64,
    md5: String,
    filename: String,
    platform: String,
    system_id: String,
    media_dir: String,
}

fn map_platform_to_sysid(platform: &str) -> String {
    match platform.to_lowercase().as_str() {
        "gba" => "12", "snes" => "4", "nes" => "3", "n64" => "14",
        "gb" => "9", "gbc" => "10", "megadrive" => "1", "mastersystem" => "2",
        "gamegear" => "21", "ps1" => "57", "ps2" => "58", "psp" => "61",
        "gc" => "38", "wii" => "5", "ds" => "15", "dreamcast" => "16",
        _ => ""
    }.to_string()
}

pub fn run_batch_scrape(
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
    
    let mut conn = Connection::open(db_path)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("DB Open error: {}", e)))?;
    
    let mut pending = Vec::new();
    {
        let mut stmt = conn.prepare(
            "SELECT g.id, g.file_hash, g.file_path, g.platform 
             FROM games g 
             LEFT JOIN game_metadata m ON g.id = m.game_id
             WHERE m.cover_2d_path IS NULL OR m.cover_2d_path = ''"
        ).map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("SQL error: {}", e)))?;
        
        let game_iter = stmt.query_map([], |row| {
            let id: i64 = row.get(0)?;
            let md5: String = row.get(1)?;
            let file_path: String = row.get(2)?;
            let platform: String = row.get(3)?;

            let filename = Path::new(&file_path).file_name().unwrap_or_default().to_string_lossy().to_string();
            let system_id = map_platform_to_sysid(&platform);
            let media_dir = Path::new(media_dir_base).join(&platform).to_string_lossy().to_string();

            Ok(PendingGame {
                id, md5, filename, platform, system_id, media_dir,
            })
        }).unwrap();
        
        for game in game_iter {
            if let Ok(g) = game { pending.push(g); }
        }
    }
    
    let total_pending = pending.len();
    if total_pending == 0 { 
        log_to_python(py, "info", "Biblioteca al día. No se requiere scraping de arte.");
        return Ok(0); 
    }
    
    let runtime = tokio::runtime::Runtime::new().unwrap();
    let interrupt_arc = Arc::new(AtomicBool::new(false));

    // Determinar si debemos usar ScreenScraper basándonos en credenciales + validación
    let ss_available = if ss_id.is_empty() || ss_pass.is_empty() {
        log_to_python(py, "warning", "Credenciales de ScreenScraper no configuradas. Usando modo de rescate (Libretro).");
        false
    } else {
        log_to_python(py, "info", "Validando conexión con ScreenScraper...");
        let auth_ok = runtime.block_on(async {
            let client = reqwest::Client::new();
            let res = client.get("https://www.screenscraper.fr/api2/ssuserInfos.php")
                .query(&[
                    ("devid", dev_id),
                    ("devpassword", dev_pass),
                    ("softname", "EmuManagerApp"),
                    ("ssid", ss_id),
                    ("sspassword", ss_pass),
                    ("output", "json")
                ])
                .send().await;
            
            if let Ok(r) = res {
                r.status().is_success()
            } else {
                false
            }
        });

        if !auth_ok {
            log_to_python(py, "error", "Fallo de autenticación en ScreenScraper. Continuando en modo de rescate (Libretro).");
            false
        } else {
            true
        }
    };

    log_to_python(py, "info", &format!("Iniciando scraping masivo optimizado de {} juegos.", total_pending));
    
    let total = total_pending as f64;
    let mut success_count = 0;

    // Clonar callbacks para moverlos a los hilos hilos
    let progress_arc = Arc::new(progress_callback);

    // --- M.A.N.G.O NITRO + STABLE PARALLEL MODE ---
    let results = py.allow_threads(|| {
        runtime.block_on(async {
            stream::iter(pending.iter().enumerate())
                .map(|(index, game)| {
                    let prog_cb = progress_arc.clone();
                    let game_name = game.filename.clone();
                    let skip_ss = !ss_available;
                    
                    async move {
                        if index > 0 && !skip_ss {
                            tokio::time::sleep(tokio::time::Duration::from_millis(200)).await;
                        }
                        
                        let dummy_flag = AtomicBool::new(false);
                        let meta = scrape_game(
                            &game.md5, "", &game.filename, &game.platform, &game.system_id,
                            ss_id, ss_pass, dev_id, dev_pass, &game.media_dir,
                            &dummy_flag,
                            skip_ss,
                        ).await;
                        
                        let has_media = if let Some(ref m) = meta {
                            m.cover_2d_path.is_some() || m.cover_3d_path.is_some()
                        } else {
                            false
                        };

                        if has_media {
                            log_to_python_safe("info", &format!("[OK] Carátula obtenida: {}", game_name));
                        } else {
                            log_to_python_safe("warning", &format!("[SKIP] Sin medios para: {}", game_name));
                        }

                        if let Some(ref cb) = *prog_cb {
                            Python::with_gil(|py| {
                                let p = (index as f64 + 1.0) / total;
                                let msg = format!("{}: {}", if has_media { "OK" } else { "---" }, game_name);
                                let _ = cb.call1(py, (p, msg));
                            });
                        }
                        
                        (index, game.id, meta)
                    }
                })
                .buffer_unordered(2) // Paralelismo seguro y estable
                .collect::<Vec<_>>()
                .await
        })
    });

    // --- ACTUALIZACIÓN FINAL DE BASE DE DATOS ---
    for (_index, game_id, metadata_opt) in results {
        if let Some(meta) = metadata_opt {
            let _ = conn.execute(
                "UPDATE game_metadata SET 
                    title = COALESCE(?, title), developer = COALESCE(?, developer), publisher = COALESCE(?, publisher), 
                    release_date = COALESCE(?, release_date), genre = COALESCE(?, genre), description = COALESCE(?, description), 
                    cover_2d_path = COALESCE(?, cover_2d_path), cover_3d_path = COALESCE(?, cover_3d_path)
                 WHERE game_id = ?",
                params![
                    meta.title, meta.developer, meta.publisher,
                    meta.release_date, meta.genre, meta.description,
                    meta.cover_2d_path, meta.cover_3d_path,
                    game_id
                ]
            );
            
            // Solo sumar si realmente se descargó alguna imagen
            if meta.cover_2d_path.is_some() || meta.cover_3d_path.is_some() {
                success_count += 1;
            }
        }
    }

    Ok(success_count)
}
