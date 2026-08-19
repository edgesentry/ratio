//! Split rule: raw payloads never leave as a public URL; pointers stay `local://`.

use thiserror::Error;

#[derive(Debug, Error, PartialEq, Eq)]
pub enum PointerError {
    #[error("rawDataPointer must use local:// (got {0})")]
    NotLocal(String),
    #[error("rawDataPointer is empty")]
    Empty,
}

/// True when the pointer is an in-domain `local://` URI (no public raw URL).
pub fn is_local_pointer(pointer: &str) -> bool {
    pointer.starts_with("local://") && pointer.len() > "local://".len()
}

pub fn assert_local_pointer(pointer: &str) -> Result<(), PointerError> {
    if pointer.is_empty() {
        return Err(PointerError::Empty);
    }
    if !is_local_pointer(pointer) {
        return Err(PointerError::NotLocal(pointer.to_string()));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accepts_local_storage() {
        assert!(is_local_pointer("local://storage/K1/raw_wave.bin"));
        assert_eq!(
            assert_local_pointer("local://storage/K1/raw_wave.bin"),
            Ok(())
        );
    }

    #[test]
    fn rejects_https_and_bare_local() {
        assert!(!is_local_pointer("https://example.invalid/raw.bin"));
        assert!(!is_local_pointer("local://"));
        assert!(assert_local_pointer("https://cdn.example/raw.bin").is_err());
        assert!(assert_local_pointer("").is_err());
        assert!(!is_local_pointer("file:///tmp/raw.bin"));
        assert!(!is_local_pointer("http://example.invalid/raw.bin"));
    }
}
