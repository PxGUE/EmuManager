use rusqlite::Connection;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use fuzzy_matcher::FuzzyMatcher;
use fuzzy_matcher::skim::SkimMatcherV2;

struct GameRow {
    id: i64,
    file_hash: String,
    file_path: String,
    display_name: String,
    title: String,
    platform: String,
    cover_2d: String,
    cover_3d: String,
    score: i64,
}

pub fn search_games(
    py: Python<'_>,
    db_path: &str,
    query: &str,
    platform_filter: &str,
) -> PyResult<Vec<PyObject>> {
    
    let conn = Connection::open(db_path)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("DB Open error: {}", e)))?;
        
    let mut sql = "SELECT g.id, g.file_hash, g.file_path, g.display_name, g.platform, m.title, m.cover_2d_path, m.cover_3d_path 
                   FROM games g 
                   JOIN game_metadata m ON g.id = m.game_id".to_string();
                   
    let mut params: Vec<String> = Vec::new();
    
    if !platform_filter.is_empty() && platform_filter.to_lowercase() != "all" {
        sql.push_str(" WHERE g.platform = ?1");
        params.push(platform_filter.to_string());
    }
    
    let mut stmt = conn.prepare(&sql)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("SQL Error: {}", e)))?;
        
    let row_iter = stmt.query_map(rusqlite::params_from_iter(params), |row| {
        Ok(GameRow {
            id: row.get(0)?,
            file_hash: row.get(1)?,
            file_path: row.get(2)?,
            display_name: row.get::<_, Option<String>>(3)?.unwrap_or_default(),
            platform: row.get(4)?,
            title: row.get::<_, Option<String>>(5)?.unwrap_or_default(),
            cover_2d: row.get::<_, Option<String>>(6)?.unwrap_or_default(),
            cover_3d: row.get::<_, Option<String>>(7)?.unwrap_or_default(),
            score: 0,
        })
    }).map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Query execution error: {}", e)))?;

    let matcher = SkimMatcherV2::default();
    let mut results = Vec::new();
    
    let is_query_empty = query.trim().is_empty();

    for row_res in row_iter {
        if let Ok(mut g) = row_res {
            if is_query_empty {
                results.push(g);
            } else {
                // Fuzzymatch on Display Name. Fallback to Title then file_path
                let mut best_score = matcher.fuzzy_match(&g.display_name, query).unwrap_or(0);
                if best_score == 0 {
                    best_score = matcher.fuzzy_match(&g.title, query).unwrap_or(0);
                }
                if best_score == 0 {
                    best_score = matcher.fuzzy_match(&g.file_path, query).unwrap_or(0);
                }
                
                if best_score > 0 {
                    g.score = best_score;
                    results.push(g);
                }
            }
        }
    }
    
    if !is_query_empty {
        results.sort_by(|a, b| b.score.cmp(&a.score)); // Sort desc by score
    } else {
        // Optional: sort alphabetically by title if no query
        results.sort_by(|a, b| a.title.to_lowercase().cmp(&b.title.to_lowercase()));
    }

    let mut py_list = Vec::with_capacity(results.len());
    
    for g in results {
        let dict = PyDict::new(py);
        dict.set_item("id", g.id)?;
        dict.set_item("file_hash", g.file_hash)?;
        dict.set_item("file_path", g.file_path)?;
        dict.set_item("display_name", g.display_name)?;
        dict.set_item("title", g.title)?;
        dict.set_item("platform", g.platform)?;
        dict.set_item("cover_2d_path", g.cover_2d)?;
        dict.set_item("cover_3d_path", g.cover_3d)?;
        py_list.push(dict.into_any().unbind());
    }

    Ok(py_list)
}
