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
            let mut buffer = [0u8; 6];
            if file.read_exact(&mut buffer).is_ok() {
                let id = String::from_utf8_lossy(&buffer).to_string();
                if id.chars().all(|c| c.is_alphanumeric()) { return Some(id); }
            }
        },
        "nds" | "ds" => {
            // NDS: Offset 0x0C, longitud 4 caracteres (ej: NTRJ)
            let mut buffer = [0u8; 4];
            if file.seek(SeekFrom::Start(0x0C)).is_ok() {
                if file.read_exact(&mut buffer).is_ok() {
                    let id = String::from_utf8_lossy(&buffer).to_string();
                    if id.chars().all(|c| c.is_alphanumeric()) { return Some(id); }
                }
            }
        },
        "3ds" => {
            // 3DS: Product Code en offset 0x118 (10 bytes, ej: CTR-P-AMQE)
            let mut buffer = [0u8; 10];
            if file.seek(SeekFrom::Start(0x118)).is_ok() {
                if file.read_exact(&mut buffer).is_ok() {
                    let code = String::from_utf8_lossy(&buffer).to_string();
                    if code.starts_with("CTR") || code.starts_with("KTR") { return Some(code); }
                }
            }
        },
        "gba" => {
            // GBA: Offset 0xAC (Game Code, 4b) + 0xB2 (Maker Code, 2b)
            let mut gc = [0u8; 4];
            let mut mc = [0u8; 2];
            if file.seek(SeekFrom::Start(0xAC)).is_ok() && file.read_exact(&mut gc).is_ok() {
                if file.seek(SeekFrom::Start(0xB2)).is_ok() && file.read_exact(&mut mc).is_ok() {
                    let id = format!("{}{}", String::from_utf8_lossy(&gc), String::from_utf8_lossy(&mc));
                    if id.chars().all(|c| c.is_alphanumeric()) { return Some(id); }
                }
            }
        },
        "n64" => {
            // N64: Offset 0x3B (Serial, 4 bytes)
            let mut buffer = [0u8; 4];
            if file.seek(SeekFrom::Start(0x3B)).is_ok() && file.read_exact(&mut buffer).is_ok() {
                let id = String::from_utf8_lossy(&buffer).to_string();
                if id.chars().all(|c| c.is_alphanumeric()) { return Some(id); }
            }
        },
        "megadrive" | "genesis" => {
            // Mega Drive: Offset 0x180 (Serial, 14 bytes)
            let mut buffer = [0u8; 14];
            if file.seek(SeekFrom::Start(0x180)).is_ok() && file.read_exact(&mut buffer).is_ok() {
                let id = String::from_utf8_lossy(&buffer).trim().replace("-", "");
                if !id.is_empty() { return Some(id); }
            }
        },
        "snes" => {
            // SNES: GameID oficial en 0x7FB2 (LoROM) o 0xFFB2 (HiROM)
            // Consideramos también el offset de 512B si es .smc
            let is_smc = path.to_lowercase().ends_with(".smc");
            let base_offset: u64 = if is_smc { 512 } else { 0 };
            
            let mut buffer = [0u8; 4];
            let targets = [0x7FB2u64, 0xFFB2u64];
            for t in targets {
                if file.seek(SeekFrom::Start(base_offset + t)).is_ok() && file.read_exact(&mut buffer).is_ok() {
                    let id = String::from_utf8_lossy(&buffer).to_string();
                    if id.chars().all(|c| c.is_alphanumeric() || c == '-') && !id.trim().is_empty() {
                        return Some(id);
                    }
                }
            }
        },
        "ps1" | "ps2" | "playstation" | "playstation2" => {
            // Sniffer de PlayStation: Buscamos el descriptor "SYSTEM.CNF" en los primeros sectores
            // Escaneamos los primeros 128KB para cubrir variaciones de sector (2048 vs 2352 bytes)
            let mut buffer = vec![0u8; 131072]; 
            if file.read_exact(&mut buffer).is_ok() {
                let content = String::from_utf8_lossy(&buffer).to_uppercase();
                // Patrón BOOT de Sony: "BOOT = CDROM:\\SLUS_XXX.XX;1" o similar
                if let Some(pos) = content.find("BOOT = CDROM:\\") {
                    let start = pos + 14;
                    // Buscamos el final de la cadena de serial (punto y coma o espacio)
                    if let Some(end) = content[start..].find(';') {
                        let raw_serial = &content[start..start+end];
                        let clean = raw_serial.trim().replace("_", "-").replace(".", "").replace("\\", "");
                        if clean.len() >= 4 { return Some(clean); }
                    }
                }
                // Fallback: búsqueda por patrón directo SLUS/SLES/SCES/SCUS
                let prefixes = ["SLUS-", "SLES-", "SCES-", "SCUS-", "SLPS-", "SLPM-"];
                for p in prefixes {
                    if let Some(pos) = content.find(p) {
                        let serial = &content[pos..pos+10].replace("_", "-").replace(".", "");
                        return Some(serial.to_string());
                    }
                }
            }
        },
        _ => return None
    }

    None
}
