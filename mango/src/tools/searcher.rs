use crate::tools::fuzzy;
use serde_json::Value;

/// Filtra una lista de juegos (JSON de ScreenScraper) asegurando que pertenezcan al sistema correcto.
pub fn filter_by_platform(jeux: &Vec<Value>, target_system_id: &str) -> Vec<Value> {
    if target_system_id.is_empty() {
        return jeux.clone();
    }

    jeux.iter()
        .filter(|j| {
            if let Some(sys) = j.get("systeme") {
                if let Some(id) = sys.get("id").and_then(|id| id.as_str()) {
                    return id == target_system_id;
                }
                // A veces el ID viene como número en el JSON
                if let Some(id) = sys.get("id").and_then(|id| id.as_i64()) {
                    return id.to_string() == target_system_id;
                }
            }
            false
        })
        .cloned()
        .collect()
}

/// Realiza una búsqueda fuzzy sobre candidatos ya filtrados por plataforma.
pub fn find_best_match_with_platform(
    query: &str, 
    jeux: &Vec<Value>, 
    target_system_id: &str
) -> Option<Value> {
    let filtered = filter_by_platform(jeux, target_system_id);
    let mut candidates = Vec::new();
    let mut map = std::collections::HashMap::new();

    for j in &filtered {
        if let Some(names) = j.get("noms").and_then(|n| n.as_array()) {
            for n in names {
                if let Some(nom) = n.get("nom").and_then(|n| n.as_str()) {
                    candidates.push(nom.to_string());
                    map.insert(nom.to_string(), j.clone());
                }
            }
        }
    }

    if let Some(m) = fuzzy::find_best_match(query, candidates, 0.85) {
        return map.get(&m.name).cloned();
    }

    None
}
