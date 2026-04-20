use std::fs::File;
use std::io::Read;
use std::path::Path;

/// Extrae el Serial/GameID de la cabecera de la ROM según la plataforma.
/// Soporta Wii, GameCube, NDS y 3DS (Base para GameTDB).
pub fn extract_serial(path: &str, platform: &str) -> Option<String> {
    let path_obj = Path::new(path);
    if !path_obj.exists() { return None; }

    // 0. Soporte para ZIP: Si es un archivo comprimido, asomarnos al primer archivo para leer su cabecera
    if path.to_lowercase().ends_with(".zip") {
        if let Ok(file_zip) = File::open(path_obj) {
            if let Ok(mut archive) = zip::ZipArchive::new(file_zip) {
                if archive.len() > 0 {
                    if let Ok(mut first_file) = archive.by_index(0) {
                        // Creamos un buffer temporal con los primeros 1MB (suficiente para cualquier cabecera)
                        let mut head_buf = vec![0u8; 128 * 1024]; // 128KB es más que suficiente
                        let n = match first_file.read(&mut head_buf) {
                            Ok(bytes) => bytes,
                            Err(_) => 0
                        };
                        if n > 0 {
                            return extract_serial_from_buffer(&head_buf[..n], platform);
                        }
                    }
                }
            }
        }
        return None;
    }

    let mut file = match File::open(path_obj) {
        Ok(f) => f,
        Err(_) => return None,
    };
    
    // Leemos los primeros 256KB para tener un buffer de cabecera completo
    let mut buffer = vec![0u8; 256 * 1024];
    let n = match file.read(&mut buffer) {
        Ok(bytes) => bytes,
        Err(_) => return None
    };

    extract_serial_from_buffer(&buffer[..n], platform)
}

/// Lógica interna para extraer el Serial desde un buffer de memoria de la cabecera.
fn extract_serial_from_buffer(buffer: &[u8], platform: &str) -> Option<String> {
    if buffer.is_empty() { return None; }
    let len = buffer.len();

    match platform.to_lowercase().as_str() {
        "wii" | "gc" | "gamecube" => {
            if len >= 6 {
                let id = String::from_utf8_lossy(&buffer[0..6]).to_string();
                if id.chars().all(|c| c.is_alphanumeric()) { return Some(id); }
            }
        },
        "nds" | "ds" => {
            if len >= 0x10 {
                let id = String::from_utf8_lossy(&buffer[0x0C..0x10]).to_string();
                if id.chars().all(|c| c.is_alphanumeric()) { return Some(id); }
            }
        },
        "3ds" => {
            if len >= 0x118 + 10 {
                let code = String::from_utf8_lossy(&buffer[0x118..0x118+10]).to_string();
                if code.starts_with("CTR") || code.starts_with("KTR") { return Some(code); }
            }
        },
        "gba" => {
            // GBA: Offset 0xAC (Game Code, 4b) + 0xB0 (Maker Code, 2b) -> FIX: Era 0xB2
            if len >= 0xB2 {
                let gc = &buffer[0xAC..0xB0];
                let mc = &buffer[0xB0..0xB2];
                let id = format!("{}{}", String::from_utf8_lossy(gc), String::from_utf8_lossy(mc));
                if id.chars().all(|c| c.is_alphanumeric()) { return Some(id); }
            }
        },
        "n64" => {
            if len >= 0x3F {
                let id = String::from_utf8_lossy(&buffer[0x3B..0x3F]).to_string();
                if id.chars().all(|c| c.is_alphanumeric()) { return Some(id); }
            }
        },
        "megadrive" | "genesis" => {
            if len >= 0x180 + 14 {
                let id = String::from_utf8_lossy(&buffer[0x180..0x180+14]).trim().replace("-", "");
                if !id.is_empty() { return Some(id); }
            }
        },
        "snes" => {
            // SNES: LoROM (0x7FB2) o HiROM (0xFFB2)
            // No consideramos offset SMC aquí porque el ZIP peeking ya nos da el stream limpio 
            // pero el buffer file-based podría tenerlo.
            // Para simplicidad, probamos con y sin offset de 512.
            let targets = [0x7FB2usize, 0xFFB2usize, 0x7FB2 + 512, 0xFFB2 + 512];
            for t in targets {
                if len >= t + 4 {
                    let id = String::from_utf8_lossy(&buffer[t..t+4]).to_string();
                    if id.chars().all(|c| c.is_alphanumeric() || c == '-') && !id.trim().is_empty() {
                        return Some(id);
                    }
                }
            }
        },
        "ps1" | "ps2" | "playstation" | "playstation2" => {
            let content = String::from_utf8_lossy(buffer).to_uppercase();
            if let Some(pos) = content.find("BOOT = CDROM:\\") {
                let start = pos + 14;
                if let Some(end) = content[start..].find(';') {
                    let raw_serial = &content[start..start+end];
                    let clean = raw_serial.trim().replace("_", "-").replace(".", "").replace("\\", "");
                    if clean.len() >= 4 { return Some(clean); }
                }
            }
            let prefixes = ["SLUS-", "SLES-", "SCES-", "SCUS-", "SLPS-", "SLPM-"];
            for p in prefixes {
                if let Some(pos) = content.find(p) {
                    if content.len() >= pos + 10 {
                        let serial = &content[pos..pos+10].replace("_", "-").replace(".", "");
                        return Some(serial.to_string());
                    }
                }
            }
        },
        _ => {}
    }
    None
}
