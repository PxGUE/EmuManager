use std::process::Command;
use std::time::Instant;
// use pyo3::prelude::*; (Removed unused)

/// Lanza un juego utilizando un emulador/frontend externo.
/// Retorna la duración de la sesión en SEGUNDOS.
pub fn launch_and_track(
    emulator_path: &str, 
    core_path: Option<String>, 
    game_path: &str
) -> Result<u64, String> {
    let start_time = Instant::now();
    
    let mut command = Command::new(emulator_path);
    
    // Si se proporciona un core (Libretro style), lo añadimos como argumento -L
    if let Some(core) = core_path {
        command.arg("-L").arg(core);
    }
    
    // Añadimos la ruta del juego
    command.arg(game_path);
    
    // Ejecutar y esperar
    match command.spawn() {
        Ok(mut child) => {
            match child.wait() {
                Ok(_) => {
                    let duration = start_time.elapsed().as_secs();
                    Ok(duration)
                },
                Err(e) => Err(format!("Error esperando al proceso: {}", e))
            }
        },
        Err(e) => Err(format!("No se pudo iniciar el emulador: {}. ¿Es correcta la ruta?", e))
    }
}
