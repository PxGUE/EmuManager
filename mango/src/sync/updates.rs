use serde::{Deserialize, Serialize};
use reqwest::header::USER_AGENT;
use std::collections::HashMap;
use tokio::task;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct UpdateResult {
    pub id: String,
    pub remote_tag: String,
    pub download_url: Option<String>,
}

async fn fetch_latest_github_release(repo: &str) -> Option<(String, String)> {
    let url = format!("https://api.github.com/repos/{}/releases/latest", repo);
    let client = reqwest::Client::new();
    
    match client.get(&url)
        .header(USER_AGENT, "EmuManager-Mango")
        .timeout(std::time::Duration::from_secs(10))
        .send()
        .await {
        Ok(res) => {
            if res.status().is_success() {
                if let Ok(json) = res.json::<serde_json::Value>().await {
                    let tag = json.get("tag_name").and_then(|v| v.as_str())?.to_string();
                    let html_url = json.get("html_url").and_then(|v| v.as_str())?.to_string();
                    return Some((tag, html_url));
                }
            }
            None
        }
        Err(_) => None,
    }
}

pub async fn check_parallel_updates(targets: HashMap<String, String>) -> Vec<UpdateResult> {
    let mut tasks = Vec::new();

    for (id, repo) in targets {
        tasks.push(task::spawn(async move {
            if let Some((tag, url)) = fetch_latest_github_release(&repo).await {
                return Some(UpdateResult {
                    id,
                    remote_tag: tag,
                    download_url: Some(url),
                });
            }
            None
        }));
    }

    let mut results = Vec::new();
    for t in tasks {
        if let Ok(Some(res)) = t.await {
            results.push(res);
        }
    }
    results
}
