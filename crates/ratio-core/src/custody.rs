//! Local raw custody. Bytes stay under `data/raw`; the product only gets `local://`.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};

use crate::RAW_STUB_MARKER;

pub fn raw_pointer(scenario: &str, file_name: &str) -> String {
    format!("local://storage/{scenario}/{file_name}")
}

/// Write a stub waveform (PoC). Returns the file path and the in-domain pointer.
pub fn write_raw_stub(
    root: &Path,
    scenario: &str,
    prefix: &str,
    stamp: &str,
) -> io::Result<(PathBuf, String)> {
    let dir = root.join("data").join("raw").join(scenario);
    fs::create_dir_all(&dir)?;
    let name = format!("{prefix}_{stamp}.bin");
    let path = dir.join(&name);
    let mut body = RAW_STUB_MARKER.as_bytes().to_vec();
    body.extend_from_slice(b"\n");
    body.extend_from_slice(stamp.as_bytes());
    body.extend_from_slice(b"\n");
    fs::write(&path, body)?;
    Ok((path, raw_pointer(scenario, &name)))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::product::{build_shareable_product, DeriveInput, Scenario};

    #[test]
    fn write_raw_stays_under_local_pointer() {
        let dir = tempfile::tempdir().unwrap();
        let (path, pointer) =
            write_raw_stub(dir.path(), "K1", "raw_wave", "20260818_000000").unwrap();
        assert!(path.is_file());
        assert!(fs::read(&path)
            .unwrap()
            .starts_with(RAW_STUB_MARKER.as_bytes()));
        assert_eq!(pointer, "local://storage/K1/raw_wave_20260818_000000.bin");
        assert!(crate::pointer::is_local_pointer(&pointer));
        assert!(path.starts_with(dir.path().join("data").join("raw").join("K1")));
        let product = build_shareable_product(&DeriveInput::stub_for(
            Scenario::K1,
            "urn:uuid:00000000-0000-0000-0000-000000000001",
            "2026-08-18T00:00:00Z",
            &pointer,
        ))
        .unwrap();
        assert!(!product.to_json().unwrap().contains(RAW_STUB_MARKER));
    }
}
