use crate::scraping::scraper::scrape_game;
use rusqlite::{params, Connection};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use pyo3::prelude::*;
use std::path::Path;
// use std::thread; (Removed unused)
// use std::time::Duration; (Removed unused)
use futures::stream::{self, StreamExt};


pub fn log_to_python(py: Python<'_>, level: &str, message: &str) {
    if let Ok(m) = py.import("core.logger") {
        if let Ok(logger) = m.getattr("EmuLog") {
            let _ = logger.call_method1(level, (format!("[MANGO] {}", message),));
        }
    }
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
    serial: String,
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
    db_path: String,
    ss_id: String,
    ss_pass: String,
    dev_id: String,
    dev_pass: String,
    media_dir_base: String,
    progress_callback: Option<PyObject>,
    status_callback: Option<PyObject>,
    gametdb_mode: String,
    cancel_check: Option<Py<PyAny>>,
) -> PyResult<usize> {
    // Resetear señal de aborto global al iniciar
    crate::reset_abort_signal();
    
    let conn = Connection::open(&db_path)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("DB Open error: {}", e)))?;
    
    let mut pending = Vec::new();
    {
        let mut stmt = conn.prepare(
            "SELECT g.id, g.file_hash, g.file_path, g.platform, g.serial 
             FROM games g 
             LEFT JOIN game_metadata m ON g.id = m.game_id
             WHERE m.cover_2d_path IS NULL OR m.cover_2d_path = '' 
                OR m.description IS NULL OR m.description = ''"
        ).map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("SQL error: {}", e)))?;
        
        let game_iter = stmt.query_map([], |row| {
            let id: i64 = row.get(0)?;
            let md5: String = row.get(1)?;
            let file_path: String = row.get(2)?;
            let platform: String = row.get(3)?;
            let serial: String = row.get::<_, Option<String>>(4)?.unwrap_or_default();

            let filename = Path::new(&file_path).file_name().unwrap_or_default().to_string_lossy().to_string();
            let system_id = map_platform_to_sysid(&platform);
            let media_dir = Path::new(&media_dir_base).join(&platform).to_string_lossy().to_string();

            Ok(PendingGame {
                id, md5, filename, platform, system_id, media_dir, serial,
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
    
    // Determinar si debemos usar ScreenScraper basándonos en credenciales + validación
    let _ss_available = if ss_id.is_empty() || ss_pass.is_empty() {
        log_to_python(py, "warning", "Credenciales de ScreenScraper no configuradas. Usando modo de rescate (Libretro).");
        false
    } else {
        log_to_python(py, "info", "Validando conexión con ScreenScraper...");
        let auth_ok = crate::RUNTIME.block_on(async {
            let client = reqwest::Client::new();
            let res = client.get("https://www.screenscraper.fr/api2/ssuserInfos.php")
                .query(&[
                    ("devid", dev_id.as_str()),
                    ("devpassword", dev_pass.as_str()),
                    ("softname", "EmuManagerApp"),
                    ("ssid", ss_id.as_str()),
                    ("sspassword", ss_pass.as_str()),
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

    log_to_python(py, "info", &format!("Iniciando scraping masivo optimizado de {} juegos. (Modo GameTDB: {})", total_pending, gametdb_mode));
    
    let total = total_pending as f64;
    let mut success_count = 0;

    // Clonar para los hilos
    let ss_id_arc = Arc::new(ss_id);
    let ss_pass_arc = Arc::new(ss_pass);
    let dev_id_arc = Arc::new(dev_id);
    let dev_pass_arc = Arc::new(dev_pass);
    let gtdb_mode_arc = Arc::new(gametdb_mode);
    let media_dir_arc = Arc::new(media_dir_base);
    let progress_arc = Arc::new(progress_callback);
    let status_arc = Arc::new(status_callback);
    let cancelled = Arc::new(AtomicBool::new(false));
    let cancel_check_arc = Arc::new(cancel_check);

    // --- M.A.N.G.O NITRO + STABLE PARALLEL MODE ---
    let results = py.allow_threads(|| {
        crate::RUNTIME.block_on(async {
            stream::iter(pending.into_iter().enumerate())
                .map(move |(index, game)| {
                    let prog_cb = progress_arc.clone();
                    let stat_cb = status_arc.clone();
                    
                    let game_name = game.filename.clone();
                    let platform = game.platform.to_lowercase();
                    let skip_ss = (**ss_id_arc).is_empty();
                    let gtdb_mode_flag = gtdb_mode_arc.clone();
                    let media_base_dir = media_dir_arc.clone();
                    
                    let s_id = ss_id_arc.clone();
                    let s_pass = ss_pass_arc.clone();
                    let d_id = dev_id_arc.clone();
                    let d_pass = dev_pass_arc.clone();
                    let is_cancelled = cancelled.clone();
                    let cc_check = cancel_check_arc.clone();
                    
                    async move {
                        if is_cancelled.load(Ordering::SeqCst) || crate::ABORT_ALL.load(Ordering::SeqCst) {
                            return (index, game.id, None);
                        }

                        // Check actual cancel from Python (is_active_check)
                        if let Some(ref cc) = *cc_check {
                            let is_active = Python::with_gil(|py| {
                                cc.bind(py).call0().map(|r| r.extract::<bool>().unwrap_or(true)).unwrap_or(true)
                            });
                            if !is_active {
                                is_cancelled.store(true, Ordering::SeqCst);
                                return (index, game.id, None);
                            }
                        }

                        // 1. GESTIÓN ON-DEMAND DE GAMETDB LOCAL
                        if *gtdb_mode_flag == "local" {
                            if platform == "wii" || platform == "gc" || platform == "gamecube" || platform == "ds" || platform == "nds" || platform == "3ds" {
                                let _ = crate::sync::gametdb::download_and_extract_gametdb(
                                    &*platform, 
                                    &(*media_base_dir).replace("media", "cache"),
                                    prog_cb.as_ref().as_ref().map(|cb| Python::with_gil(|py| cb.clone_ref(py))),
                                    stat_cb.as_ref().as_ref().map(|cb| Python::with_gil(|py| cb.clone_ref(py))),
                                ).await;
                            }
                        }

                        // 2. DELAY ESTRATÉGICO (Solo si usamos ScreenScraper para evitar 429)
                        if index > 0 && !skip_ss {
                            tokio::time::sleep(tokio::time::Duration::from_millis(150)).await;
                        }
                        
                        let meta = scrape_game(
                            &game.md5, "", &game.filename, &game.platform, &game.system_id,
                            &s_id, &s_pass, &d_id, &d_pass, &game.media_dir,
                            skip_ss, &game.serial, &*gtdb_mode_flag,
                        ).await;
                        
                        let has_media = if let Some(ref m) = meta {
                            m.cover_2d_path.is_some() || m.cover_3d_path.is_some()
                        } else {
                            false
                        };

                        if let Some(ref m) = meta {
                            // GENERACIÓN DE MINIATURA NATIVA (Async-safe via spawn_blocking)
                            if let Some(ref p2d) = m.cover_2d_path {
                                let source = p2d.clone();
                                let target = p2d.replace("covers/2d", ".cache/thumbs/256w");
                                let _ = tokio::task::spawn_blocking(move || {
                                    let _ = crate::tools::thumbnailer::generate_thumbnail(&source, &target, 256);
                                }).await;
                            }

                            log_to_python_safe("info", &format!("[OK] Carátula obtenida: {}", game_name));
                        } else {
                            log_to_python_safe("warning", &format!("[SKIP] Sin medios para: {}", game_name));
                        }

                        if let Some(ref cb) = *prog_cb {
                            Python::with_gil(|py| {
                                let p = (index as f64 + 1.0) / total;
                                let msg = format!("{}: {}", if has_media { "OK" } else { "---" }, game_name);
                                let _ = cb.bind(py).call1((p, msg));
                            });
                        }
                        
                        if let Some(ref cb) = *stat_cb {
                            Python::with_gil(|py| {
                                let msg = format!("Scraping {}...", game_name);
                                let _ = cb.bind(py).call1((msg,));
                            });
                        }
                        
                        (index, game.id, meta)
                    }
                })
                .buffer_unordered(6) // Nitro boost: Paralelismo aumentado para mayor eficiencia
                .collect::<Vec<_>>()
                .await
        })
    });

    // --- ACTUALIZACIÓN FINAL DE BASE DE DATOS ---
    for (_index, game_id, metadata_opt) in results {
        if let Some(meta) = metadata_opt {
            let _ = conn.execute(
                "INSERT OR REPLACE INTO game_metadata (
                    game_id, title, developer, publisher, release_date, genre, description, 
                    cover_2d_path, cover_3d_path
                ) VALUES (
                    ?,
                    COALESCE(?, (SELECT title FROM game_metadata WHERE game_id = ?)),
                    COALESCE(?, (SELECT developer FROM game_metadata WHERE game_id = ?)),
                    COALESCE(?, (SELECT publisher FROM game_metadata WHERE game_id = ?)),
                    COALESCE(?, (SELECT release_date FROM game_metadata WHERE game_id = ?)),
                    COALESCE(?, (SELECT genre FROM game_metadata WHERE game_id = ?)),
                    COALESCE(?, (SELECT description FROM game_metadata WHERE game_id = ?)),
                    COALESCE(?, (SELECT cover_2d_path FROM game_metadata WHERE game_id = ?)),
                    COALESCE(?, (SELECT cover_3d_path FROM game_metadata WHERE game_id = ?))
                )",
                params![
                    game_id,
                    meta.title, game_id,
                    meta.developer, game_id,
                    meta.publisher, game_id,
                    meta.release_date, game_id,
                    meta.genre, game_id,
                    meta.description, game_id,
                    meta.cover_2d_path, game_id,
                    meta.cover_3d_path, game_id
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
