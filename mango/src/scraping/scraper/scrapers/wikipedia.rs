use crate::scraping::scraper::scrapers::{ScrapedMetadata, ScrapeQuery, MetadataSource, clean_filename_for_search};
use reqwest::Client;
use async_trait::async_trait;
use serde_json::Value;
use std::path::Path;

pub struct WikipediaSource;

#[async_trait]
impl MetadataSource for WikipediaSource {
    fn name(&self) -> &'static str { "Wikipedia" }

    async fn scrape(&self, query: &ScrapeQuery) -> Option<ScrapedMetadata> {
        let client = Client::builder()
            .user_agent("EmuManager/1.0 (Rust MANGO Engine; +https://github.com/PxGUE/EmuManager)")
            .build()
            .ok()?;

        let file_stem = Path::new(&query.filename).file_stem().unwrap_or_default().to_string_lossy();
        let search_name = clean_filename_for_search(&file_stem);
        
        // 1. Buscar la página más relevante
        // Añadimos "video game" para filtrar mejor los resultados
        let search_url = "https://en.wikipedia.org/w/api.php";
        let res = client.get(search_url)
            .query(&[
                ("action", "query"),
                ("list", "search"),
                ("srsearch", &format!("{} video game", search_name)),
                ("format", "json"),
                ("utf8", "1"),
                ("origin", "*")
            ])
            .send().await.ok()?;

        let json: Value = res.json().await.ok()?;
        let search_results = json.get("query")?.get("search")?.as_array()?;
        
        if search_results.is_empty() { return None; }
        
        // Tomamos el primer resultado (el más relevante según el motor de búsqueda de WP)
        let page_title = search_results[0].get("title")?.as_str()?;

        // 2. Obtener el extracto (Texto plano de la intro)
        let detail_res = client.get(search_url)
            .query(&[
                ("action", "query"),
                ("prop", "extracts"),
                ("exintro", "1"),
                ("explaintext", "1"), // Muy importante: texto plano sin HTML
                ("titles", page_title),
                ("format", "json"),
                ("origin", "*")
            ])
            .send().await.ok()?;

        let detail_json: Value = detail_res.json().await.ok()?;
        let pages = detail_json.get("query")?.get("pages")?.as_object()?;
        
        // La API de WP devuelve las páginas con el ID como llave
        let (_, page_data) = pages.iter().next()?;
        let extract = page_data.get("extract").and_then(|v| v.as_str());

        if let Some(description) = extract {
            if !description.is_empty() {
                return Some(ScrapedMetadata {
                    title: Some(page_title.to_string()),
                    description: Some(description.to_string()),
                    // Wikipedia no es ideal para covers estructurados sin parsing complejo de MediaWiki
                    // pero es excelente para llenar el "vacío" de metadatos de texto.
                    ..Default::default()
                });
            }
        }

        None
    }
}
