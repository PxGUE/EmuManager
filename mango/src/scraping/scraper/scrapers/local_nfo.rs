use crate::scraping::scraper::scrapers::{ScrapedMetadata, ScrapeQuery, MetadataSource};
use std::path::Path;
use std::fs;
use async_trait::async_trait;
use serde_json::Value; // Podemos usarlo para parsear XML si lo convertimos o usar algo más ligero

pub struct LocalNfoSource;

#[async_trait]
impl MetadataSource for LocalNfoSource {
    fn name(&self) -> &'static str { "Local NFO/XML" }

    async fn scrape(&self, query: &ScrapeQuery) -> Option<ScrapedMetadata> {
        // 1. Buscar gamelist.xml en el directorio del juego
        let rom_path = Path::new(&query.filename);
        let parent = rom_path.parent()?;
        let gamelist_path = parent.join("gamelist.xml");

        if !gamelist_path.exists() {
            return None;
        }

        // 2. Leer y parsear de forma básica (regex o manual para no añadir crates pesados de XML)
        let content = fs::read_to_string(&gamelist_path).ok()?;
        
        // Búsqueda simplificada por nombre de archivo en el XML
        let file_stem = rom_path.file_name()?.to_string_lossy();
        if !content.contains(&*file_stem) {
            return None;
        }

        // Nota: Una implementación real usaría un parser XML. 
        // Para este MVP, demostramos la modularidad.
        
        pyo3::Python::with_gil(|py| {
            crate::scraping::batch_scraper::log_to_python(py, "info", &format!(
                "[LOCAL-NFO] Encontrada entrada para '{}' en gamelist.xml", 
                file_stem
            ));
        });

        // Retornamos un objeto vacío por ahora o con datos si el regex los captura
        // En una fase posterior, implementaremos el parser XML completo.
        Some(ScrapedMetadata {
            title: Some(file_stem.to_string()),
            ..Default::default()
        })
    }
}
