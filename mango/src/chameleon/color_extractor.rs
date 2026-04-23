use image::{GenericImageView, DynamicImage};
use std::path::Path;
use anyhow::{Result, anyhow};

/// Extrae el color dominante (acento) de una imagen de forma optimizada.
pub fn extract_vibrant_color(image_path: &str) -> Result<(u8, u8, u8)> {
    let path = Path::new(image_path);
    if !path.exists() {
        return Err(anyhow!("Archivo de imagen no encontrado: {}", image_path));
    }

    // 1. Cargar la imagen (Solo la decodificamos)
    let img = image::open(path)?;
    
    // 2. Redimensionar para procesamiento rápido (64x64 es suficiente para color dominante)
    let scaled = img.thumbnail(64, 64);
    
    // 3. Analizar píxeles buscando el más "vibrante"
    // Usaremos una métrica simple de saturación y brillo para evitar grises/negros
    let mut best_color = (0, 0, 0);
    let mut max_score: f32 = -1.0;

    for (_, _, pixel) in scaled.pixels() {
        let r = pixel[0] as f32;
        let g = pixel[1] as f32;
        let b = pixel[2] as f32;
        let a = pixel[3] as f32;

        if a < 128.0 { continue; } // Ignorar transparentes

        // Cálculo de saturación básica
        let max = r.max(g).max(b);
        let min = r.min(g).min(b);
        let delta = max - min;
        let l = (max + min) / 2.0 / 255.0;
        
        let s = if max == 0.0 { 0.0 } else { delta / max };

        // Puntuamos el color: Queremos algo saturado y con brillo medio (no muy oscuro ni quemado)
        // La fórmula de puntuación prioriza saturación (s) y evita extremos de luminosidad (l)
        let score = s * (1.0 - (l - 0.5).abs() * 2.0);

        if score > max_score {
            max_score = score;
            best_color = (pixel[0], pixel[1], pixel[2]);
        }
    }

    // Si no encontramos nada vibrante, devolvemos un promedio simple
    if max_score < 0.05 {
        return get_average_color(&scaled);
    }

    Ok(best_color)
}

fn get_average_color(img: &DynamicImage) -> Result<(u8, u8, u8)> {
    let mut r_total: u64 = 0;
    let mut g_total: u64 = 0;
    let mut b_total: u64 = 0;
    let mut count: u64 = 0;

    for (_, _, pixel) in img.pixels() {
        if pixel[3] < 128 { continue; }
        r_total += pixel[0] as u64;
        g_total += pixel[1] as u64;
        b_total += pixel[2] as u64;
        count += 1;
    }

    if count == 0 { return Ok((100, 100, 100)); }

    Ok((
        (r_total / count) as u8,
        (g_total / count) as u8,
        (b_total / count) as u8,
    ))
}
