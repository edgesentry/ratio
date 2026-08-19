//! Envelope checks that match the PoC SHACL intent (local pointer, required fields).
//! Full SHACL remains Oxigraph / pyshacl; this is the in-process gate before publish.

use serde_json::Value;
use thiserror::Error;

use crate::pointer::{assert_local_pointer, PointerError};
use crate::product::{Domain, Scenario};
use crate::RAW_STUB_MARKER;

#[derive(Debug, Error, PartialEq, Eq)]
pub enum EnvelopeError {
    #[error("missing field {0}")]
    Missing(&'static str),
    #[error("invalid domain (want factory|maritime)")]
    Domain,
    #[error("invalid scenario (want K1|S1|S2)")]
    Scenario,
    #[error("confidence must be in [0, 1]")]
    Confidence,
    #[error("{0}")]
    Pointer(String),
    #[error("product body must not contain raw stub marker")]
    RawInBody,
}

impl From<PointerError> for EnvelopeError {
    fn from(err: PointerError) -> Self {
        EnvelopeError::Pointer(err.to_string())
    }
}

pub fn validate_envelope(product: &Value) -> Result<(), EnvelopeError> {
    let blob = product.to_string();
    if blob.contains(RAW_STUB_MARKER) {
        return Err(EnvelopeError::RawInBody);
    }

    require(product, "id")?;
    require(product, "sourceDevice")?;
    require(product, "timestamp")?;

    let domain = product
        .get("domain")
        .and_then(|v| v.as_str())
        .ok_or(EnvelopeError::Missing("domain"))?;
    if domain != Domain::Factory.as_str() && domain != Domain::Maritime.as_str() {
        return Err(EnvelopeError::Domain);
    }

    let scenario = product
        .get("scenario")
        .and_then(|v| v.as_str())
        .ok_or(EnvelopeError::Missing("scenario"))?;
    if Scenario::parse(scenario).is_none() {
        return Err(EnvelopeError::Scenario);
    }

    let inference = product
        .get("inference")
        .ok_or(EnvelopeError::Missing("inference"))?;
    require(inference, "task")?;
    require(inference, "result")?;
    let confidence = inference
        .get("confidence")
        .and_then(|v| v.as_f64())
        .ok_or(EnvelopeError::Missing("inference.confidence"))?;
    if !(0.0..=1.0).contains(&confidence) {
        return Err(EnvelopeError::Confidence);
    }

    let gov = product
        .get("dataGovernance")
        .ok_or(EnvelopeError::Missing("dataGovernance"))?;
    require(gov, "policyRef")?;
    if let Some(ptr) = gov.get("rawDataPointer") {
        let s = ptr
            .as_str()
            .ok_or(EnvelopeError::Missing("dataGovernance.rawDataPointer"))?;
        assert_local_pointer(s)?;
    }

    Ok(())
}

fn require(obj: &Value, key: &'static str) -> Result<(), EnvelopeError> {
    match obj.get(key) {
        Some(Value::Null) | None => Err(EnvelopeError::Missing(key)),
        Some(Value::String(s)) if s.is_empty() => Err(EnvelopeError::Missing(key)),
        Some(_) => Ok(()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::product::{build_shareable_product, DeriveInput, Scenario};
    use serde_json::json;

    fn k1() -> Value {
        build_shareable_product(&DeriveInput::stub_for(
            Scenario::K1,
            "urn:uuid:00000000-0000-0000-0000-000000000001",
            "2026-08-18T00:00:00Z",
            "local://storage/K1/raw_wave.bin",
        ))
        .unwrap()
        .to_value()
        .unwrap()
    }

    #[test]
    fn ok_product() {
        validate_envelope(&k1()).unwrap();
    }

    #[test]
    fn rejects_unknown_domain() {
        let mut p = k1();
        p["domain"] = json!("unknown");
        assert_eq!(validate_envelope(&p), Err(EnvelopeError::Domain));
    }

    #[test]
    fn rejects_https_pointer() {
        let mut p = k1();
        p["dataGovernance"]["rawDataPointer"] = json!("https://example.invalid/raw.bin");
        assert!(validate_envelope(&p).is_err());
    }
}
