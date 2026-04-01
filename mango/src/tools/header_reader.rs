use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;

/// Extrae el Serial/GameID de la cabecera de la ROM según la plataforma.
/// Soporta Wii, GameCube, NDS y 3DS (Base para GameTDB).
pub fn extract_serial(path: &str, platform: &str) -> Option<String> {
    let path_obj = Path::new(path);
    if !path_obj.exists() { return None; }

    let mut file = match File::open(path_obj) {
        Ok(f) => f,
        Err(_) => return None,
    };
    
    match platform.to_lowercase().as_str() {
        "wii" | "gc" | "gamecube" => {
            // Wii/GC: Los primeros 6 bytes son el GameID (ej: RSPE01)
            // Esto funciona para .iso y .wbfs (en la mayoría de los casos)
            let mut buffer = [0u8; 6];
            if file.read_exact(&mut buffer).is_ok() {
                let id = String::from_utf8_lossy(&buffer).to_string();
                if id.chars().all(|c| c.is_alphanumeric()) {
                    return Some(id);
                }
            }
        },
        "nds" | "ds" => {
            // NDS: Offset 0x0C, longitud 4 caracteres (ej: NTRJ)
            let mut buffer = [0u8; 4];
            if file.seek(SeekFrom::Start(0x0C)).is_ok() {
                if file.read_exact(&mut buffer).is_ok() {
                    let id = String::from_utf8_lossy(&buffer).to_string();
                    if id.chars().all(|c| c.is_alphanumeric()) {
                        return Some(id);
                    }
                }
            }
        },
        "3ds" => {
            // 3DS: Product Code en offset 0x118 (10 bytes, ej: CTR-P-AMQE)
            let mut buffer = [0u8; 10];
            if file.seek(SeekFrom::Start(0x118)).is_ok() {
                if file.read_exact(&mut buffer).is_ok() {
                    let code = String::from_utf8_lossy(&buffer).to_string();
                    if code.starts_with("CTR") || code.starts_with("KTR") {
                        return Some(code);
                    }
                }
            }
        },
        _ => return None
    }

    None
}
