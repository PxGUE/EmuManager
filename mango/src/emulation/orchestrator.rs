#[cfg(target_os = "linux")]
use std::process::Command;
use anyhow::Error;

fn is_valid_flatpak_id(id: &str) -> bool {
    if id.is_empty() || id.starts_with('-') {
        return false;
    }
    id.chars().all(|c| c.is_ascii_alphanumeric() || c == '.' || c == '-')
}

fn is_valid_executable_name(name: &str) -> bool {
    if name.is_empty() || name.starts_with('-') {
        return false;
    }
    name.chars().all(|c| c.is_ascii_alphanumeric() || c == '.' || c == '-' || c == '_')
}

/// Verifica si un paquete está instalado en el sistema (Solo para Linux Flatpak).
pub fn is_system_package_installed(id: &str) -> bool {
    if !is_valid_flatpak_id(id) {
        return false;
    }

    #[cfg(target_os = "linux")]
    {
        let output = Command::new("flatpak")
            .args(&["info", "--", id])
            .output();
        
        if let Ok(out) = output {
            return out.status.success();
        }
    }

    false
}

/// Instala un paquete usando el orquestador nativo (Solo Flatpak en Linux).
pub async fn install_via_system(id: &str) -> Result<(), Error> {
    if !is_valid_flatpak_id(id) {
        return Err(anyhow::anyhow!("ID de paquete inválido"));
    }

    #[cfg(target_os = "linux")]
    {
        // flatpak install -y flathub ID
        let status = Command::new("flatpak")
            .args(&["install", "-y", "flathub", "--", id])
            .status()?;
        
        if !status.success() {
            return Err(anyhow::anyhow!("Fallo en la instalación vía Flatpak. Código: {:?}", status.code()));
        }
        Ok(())
    }

    #[cfg(target_os = "windows")]
    {
        // En Windows no usamos orquestadores de sistema por políticas de portabilidad
        Err(anyhow::anyhow!("Orquestación de sistema desactivada en Windows."))
    }
}

/// Busca ejecutables en el PATH (Usado solo para autodetección si Flatpak falla).
pub fn find_system_executable(name: &str) -> Option<String> {
    if !is_valid_executable_name(name) {
        return None;
    }

    #[cfg(target_os = "linux")]
    {
        let output = Command::new("which")
            .arg(name)
            .output();
        
        if let Ok(out) = output {
            if out.status.success() {
                let s = String::from_utf8_lossy(&out.stdout).trim().to_string();
                if !s.is_empty() {
                    return Some(s);
                }
            }
        }
    }
    
    // Windows: Ignoramos el PATH para forzar el uso del binario local de la carpeta /emulators/
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_valid_flatpak_id() {
        assert!(is_valid_flatpak_id("org.libretro.RetroArch"));
        assert!(is_valid_flatpak_id("net.pcsx2.PCSX2"));
        assert!(is_valid_flatpak_id("org.DolphinEmu.dolphin-emu"));
        assert!(!is_valid_flatpak_id(""));
        assert!(!is_valid_flatpak_id("-some-flag"));
        assert!(!is_valid_flatpak_id("org.libretro;rm -rf /"));
        assert!(!is_valid_flatpak_id("org.libretro.RetroArch "));
    }

    #[test]
    fn test_is_valid_executable_name() {
        assert!(is_valid_executable_name("retroarch"));
        assert!(is_valid_executable_name("Dolphin-x86_64.AppImage"));
        assert!(is_valid_executable_name("pcsx2_qt"));
        assert!(!is_valid_executable_name(""));
        assert!(!is_valid_executable_name("-v"));
        assert!(!is_valid_executable_name("which;ls"));
    }
}
