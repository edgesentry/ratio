//! S2 store-and-forward: queue shareable-product metadata only — never raw bytes.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::envelope::validate_envelope;
use crate::RAW_STUB_MARKER;

#[derive(Debug, thiserror::Error)]
pub enum QueueError {
    #[error(transparent)]
    Io(#[from] io::Error),
    #[error(transparent)]
    Json(#[from] serde_json::Error),
    #[error("queued document failed envelope checks: {0}")]
    Envelope(String),
    #[error("queue must not contain raw stub marker")]
    RawInQueue,
}

pub fn queue_dir(root: &Path) -> PathBuf {
    root.join("data").join("queue")
}

pub fn list_queued(root: &Path) -> io::Result<Vec<PathBuf>> {
    let dir = queue_dir(root);
    if !dir.is_dir() {
        return Ok(Vec::new());
    }
    let mut paths: Vec<PathBuf> = fs::read_dir(dir)?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().and_then(|s| s.to_str()) == Some("jsonld"))
        .collect();
    paths.sort();
    Ok(paths)
}

pub fn queue_depth(root: &Path) -> io::Result<usize> {
    Ok(list_queued(root)?.len())
}

pub fn load_queued(path: &Path) -> Result<Value, QueueError> {
    let text = fs::read_to_string(path)?;
    if text.contains(RAW_STUB_MARKER) {
        return Err(QueueError::RawInQueue);
    }
    Ok(serde_json::from_str(&text)?)
}

pub fn enqueue(root: &Path, mut product: Value, stem: &str) -> Result<PathBuf, QueueError> {
    if product.to_string().contains(RAW_STUB_MARKER) {
        return Err(QueueError::RawInQueue);
    }
    validate_envelope(&product).map_err(|e| QueueError::Envelope(e.to_string()))?;
    let dir = queue_dir(root);
    fs::create_dir_all(&dir)?;
    let path = dir.join(format!("{stem}.jsonld"));
    let ts = product
        .get("timestamp")
        .and_then(|v| v.as_str())
        .unwrap_or("1970-01-01T00:00:00Z")
        .to_string();
    {
        let prov = product
            .as_object_mut()
            .ok_or_else(|| {
                io::Error::new(io::ErrorKind::InvalidInput, "product must be a JSON object")
            })?
            .entry("provenance")
            .or_insert_with(|| serde_json::json!({}));
        if prov.get("firstBufferedAt").is_none() {
            prov["firstBufferedAt"] = serde_json::json!(ts);
        }
    }
    fs::write(&path, serde_json::to_string_pretty(&product)?)?;
    let depth = queue_depth(root)?;
    product["provenance"]["queueDepth"] = serde_json::json!(depth);
    fs::write(&path, serde_json::to_string_pretty(&product)? + "\n")?;
    Ok(path)
}

pub fn dequeue(root: &Path, stem: &str) -> io::Result<()> {
    let path = queue_dir(root).join(format!("{stem}.jsonld"));
    if path.is_file() {
        fs::remove_file(path)?;
    }
    Ok(())
}

pub fn refresh_depths(root: &Path) -> Result<(), QueueError> {
    let depth = queue_depth(root)?;
    for path in list_queued(root)? {
        let mut doc = load_queued(&path)?;
        doc["provenance"]["queueDepth"] = serde_json::json!(depth);
        fs::write(&path, serde_json::to_string_pretty(&doc)? + "\n")?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::product::{build_shareable_product, DeriveInput, Scenario};

    fn s2_product(note: &str) -> Value {
        build_shareable_product(&DeriveInput::stub_for(
            Scenario::S2,
            &format!("urn:uuid:00000000-0000-0000-0000-00000000000{note}"),
            "2026-08-18T00:00:00Z",
            "local://storage/S2/raw_shaft.bin",
        ))
        .unwrap()
        .to_value()
        .unwrap()
    }

    #[test]
    fn enqueue_writes_product_without_raw() {
        let dir = tempfile::tempdir().unwrap();
        let path = enqueue(dir.path(), s2_product("1"), "s2-aaaa1111").unwrap();
        assert_eq!(path.parent().unwrap(), queue_dir(dir.path()));
        let queued = load_queued(&path).unwrap();
        let blob = queued.to_string();
        assert!(!blob.contains(RAW_STUB_MARKER));
        assert!(queued["dataGovernance"]["rawDataPointer"]
            .as_str()
            .unwrap()
            .starts_with("local://"));
        assert_eq!(queued["provenance"]["queueDepth"], 1);
        assert!(queued["provenance"]["firstBufferedAt"].as_str().is_some());
    }

    #[test]
    fn dequeue_and_refresh_depths() {
        let dir = tempfile::tempdir().unwrap();
        enqueue(dir.path(), s2_product("1"), "s2-one").unwrap();
        enqueue(dir.path(), s2_product("2"), "s2-two").unwrap();
        assert_eq!(queue_depth(dir.path()).unwrap(), 2);
        dequeue(dir.path(), "s2-one").unwrap();
        refresh_depths(dir.path()).unwrap();
        let remaining = load_queued(&queue_dir(dir.path()).join("s2-two.jsonld")).unwrap();
        assert_eq!(remaining["provenance"]["queueDepth"], 1);
        assert_eq!(queue_depth(dir.path()).unwrap(), 1);
    }

    #[test]
    fn refuses_raw_stub_in_body() {
        let dir = tempfile::tempdir().unwrap();
        let mut product = s2_product("1");
        product["inference"]["result"] = serde_json::json!(RAW_STUB_MARKER);
        assert!(matches!(
            enqueue(dir.path(), product, "bad"),
            Err(QueueError::RawInQueue)
        ));
    }
}
