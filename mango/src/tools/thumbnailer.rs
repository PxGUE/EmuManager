use std::path::Path;
use std::fs;
use image::GenericImageView;
use image::imageops::FilterType;

pub fn generate_thumbnail(original_path: &str, target_path: &str, width: u32) -> Result<(), String> {
    // 1. Verificar si ya existe para evitar trabajo redundante
    if Path::new(target_path).exists() {
        return Ok(());
    }

    // 2. Asegurar que el directorio de destino existe
    if let Some(parent) = Path::new(target_path).parent() {
        if !parent.exists() {
            fs::create_dir_all(parent).map_err(|e| format!("Fallo al crear directorio de miniaturas: {}", e))?;
        }
    }

    // 3. Abrir imagen original
    let img = image::open(original_path).map_err(|e| format!("No se pudo abrir la imagen original: {}", e))?;
    
    // 4. Calcular ratio y dimensiones
    let (w, h) = img.dimensions();
    if w == 0 { return Err("Ancho de imagen inválido".to_string()); }

    // --- OPTIMIZACIÓN DE RECURSOS ---
    // Si la imagen original ya tiene un tamaño razonable (menor o igual al ancho objetivo + un margen de 20px),
    // no desperdiciamos CPU redimensionando. Simplemente la copiamos al directorio de miniaturas.
    if w <= width + 20 {
        fs::copy(original_path, target_path).map_err(|e| format!("Error al copiar imagen pequeña: {}", e))?;
        return Ok(());
    }
    
    let aspect = h as f32 / w as f32;
    let target_height = (width as f32 * aspect) as u32;

    // 5. Redimensionar usando Lanczos3 (Alta calidad)
    let thumb = img.resize(width, target_height, FilterType::Lanczos3);

    // 6. Guardar
    thumb.save(target_path).map_err(|e| format!("Fallo al guardar miniatura: {}", e))?;

    Ok(())
}
