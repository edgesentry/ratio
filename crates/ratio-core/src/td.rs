//! Thin WoT TD consume: require id/title; property hrefs must stay `local://`.

use std::fs;
use std::path::Path;

use serde_json::Value;
use thiserror::Error;

use crate::pointer::is_local_pointer;

#[derive(Debug, Error, PartialEq, Eq)]
pub enum TdError {
    #[error("TD file not found: {0}")]
    NotFound(String),
    #[error("TD missing required field '{0}'")]
    MissingField(&'static str),
    #[error("TD is not JSON: {0}")]
    Json(String),
    #[error("TD property href is not local://: {0}")]
    PublicHref(String),
}

#[derive(Debug, Clone)]
pub struct ThinTd {
    pub id: String,
    pub title: String,
    pub hrefs: Vec<String>,
}

pub fn load_td(path: &Path) -> Result<ThinTd, TdError> {
    if !path.is_file() {
        return Err(TdError::NotFound(path.display().to_string()));
    }
    let text = fs::read_to_string(path).map_err(|e| TdError::Json(e.to_string()))?;
    let td: Value = serde_json::from_str(&text).map_err(|e| TdError::Json(e.to_string()))?;
    let id = td
        .get("id")
        .and_then(|v| v.as_str())
        .filter(|s| !s.is_empty())
        .ok_or(TdError::MissingField("id"))?
        .to_string();
    let title = td
        .get("title")
        .and_then(|v| v.as_str())
        .filter(|s| !s.is_empty())
        .ok_or(TdError::MissingField("title"))?
        .to_string();
    let mut hrefs = Vec::new();
    if let Some(props) = td.get("properties").and_then(|v| v.as_object()) {
        for prop in props.values() {
            if let Some(forms) = prop.get("forms").and_then(|v| v.as_array()) {
                for form in forms {
                    if let Some(href) = form.get("href").and_then(|v| v.as_str()) {
                        hrefs.push(href.to_string());
                    }
                }
            }
        }
    }
    for href in &hrefs {
        if !is_local_pointer(href) {
            return Err(TdError::PublicHref(href.clone()));
        }
    }
    Ok(ThinTd { id, title, hrefs })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;

    fn repo_examples_td() -> std::path::PathBuf {
        std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../examples/td")
    }

    #[test]
    fn k1_td_is_factory_robot_with_local_waveform() {
        let td = load_td(&repo_examples_td().join("k1-robot.td.json")).unwrap();
        assert_eq!(td.id, "urn:td:factory-robot-01");
        assert!(!td.hrefs.is_empty());
        assert!(td.hrefs.iter().all(|h| h.starts_with("local://")));
        assert!(td.hrefs.iter().any(|h| h.contains("vibrationWaveform")));
    }

    #[test]
    fn maritime_td_is_shaft_vibration_local() {
        let td = load_td(&repo_examples_td().join("s-engine-vib.td.json")).unwrap();
        assert_eq!(td.id, "urn:td:vessel-engine-vib-01");
        assert!(td.hrefs.iter().any(|h| h.contains("shaftVibration")));
        assert!(td.hrefs.iter().all(|h| h.starts_with("local://")));
    }

    #[test]
    fn missing_file() {
        let err = load_td(Path::new("/no/such/td.json")).unwrap_err();
        assert!(matches!(err, TdError::NotFound(_)));
    }

    #[test]
    fn missing_id() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("bad.td.json");
        let mut f = fs::File::create(&path).unwrap();
        write!(f, r#"{{"title":"no id"}}"#).unwrap();
        assert_eq!(load_td(&path).unwrap_err(), TdError::MissingField("id"));
    }

    #[test]
    fn rejects_https_href() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("bad.td.json");
        fs::write(
            &path,
            r#"{
              "id": "urn:td:x",
              "title": "x",
              "properties": {
                "w": { "forms": [{ "href": "https://example.invalid/raw.bin" }] }
              }
            }"#,
        )
        .unwrap();
        assert!(matches!(load_td(&path), Err(TdError::PublicHref(_))));
    }
}
