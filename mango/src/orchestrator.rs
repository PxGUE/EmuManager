use std::process::Command;
use anyhow::Error;

/// Verifica si un paquete está instalado en el sistema (Solo para Linux Flatpak).
pub fn is_system_package_installed(id: &str) -> bool {
    #[cfg(target_os = "linux")]
    {
        let output = Command::new("flatpak")
            .args(&["info", id])
            .output();
        
        if let Ok(out) = output {
            return out.status.success();
        }
    }

    false
}

/// Instala un paquete usando el orquestador nativo (Solo Flatpak en Linux).
pub async fn install_via_system(id: &str) -> Result<(), Error> {
    #[cfg(target_os = "linux")]
    {
        // flatpak install -y flathub ID
        let status = Command::new("flatpak")
            .args(&["install", "-y", "flathub", id])
            .status()?;
        
        if !status.success() {
            return Err(anyhow::anyhow!("Fallo en la instalación vía Flatpak. Código: {:?}", status.code()));
        }
    }

    #[cfg(target_os = "windows")]
    {
        // En Windows no usamos orquestadores de sistema por políticas de portabilidad
        return Err(anyhow::anyhow!("Orquestación de sistema desactivada en Windows."));
    }

    Ok(())
}

/// Busca ejecutables en el PATH (Usado solo para autodetección si Flatpak falla).
pub fn find_system_executable(name: &str) -> Option<String> {
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
