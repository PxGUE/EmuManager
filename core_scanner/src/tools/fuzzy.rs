use strsim::jaro_winkler;

pub struct FuzzyMatch {
    pub name: String,
    pub similarity: f64,
}

pub fn clean_name(input: &str) -> String {
    let mut clean = input.to_string();
    
    // Quitar todo a partir del primer parentesis "(" o corchete "["
    if let Some(idx) = clean.find('(') { clean.truncate(idx); }
    if let Some(idx) = clean.find('[') { clean.truncate(idx); }
    
    clean.trim().to_lowercase()
}

pub fn compare(local: &str, api: &str) -> f64 {
    let s1 = clean_name(local);
    let s2 = clean_name(api);
    jaro_winkler(&s1, &s2)
}

pub fn find_best_match(local_name: &str, candidates: Vec<String>, threshold: f64) -> Option<FuzzyMatch> {
    let mut best_sim = 0.0;
    let mut best_name = String::new();
    
    for candidate in candidates {
        let sim = compare(local_name, &candidate);
        if sim > best_sim {
            best_sim = sim;
            best_name = candidate;
        }
    }
    
    if best_sim >= threshold {
        Some(FuzzyMatch {
            name: best_name,
            similarity: best_sim,
        })
    } else {
        None
    }
}
