//! Assemble shareable-product metadata (result + meaning + terms). Not raw bytes.

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};
use serde_json::{json, Map, Value};

use crate::pointer::assert_local_pointer;
use crate::RAW_STUB_MARKER;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Domain {
    Factory,
    Maritime,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Scenario {
    K1,
    S1,
    S2,
}

impl Scenario {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::K1 => "K1",
            Self::S1 => "S1",
            Self::S2 => "S2",
        }
    }

    pub fn default_domain(self) -> Domain {
        match self {
            Self::K1 => Domain::Factory,
            Self::S1 | Self::S2 => Domain::Maritime,
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "K1" => Some(Self::K1),
            "S1" => Some(Self::S1),
            "S2" => Some(Self::S2),
            _ => None,
        }
    }
}

impl Domain {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Factory => "factory",
            Self::Maritime => "maritime",
        }
    }
}

#[derive(Debug, Clone)]
pub struct DeriveInput {
    pub scenario: Scenario,
    pub product_id: String,
    pub source_device: String,
    pub timestamp: String,
    pub raw_pointer: String,
    pub produced_by: String,
    pub task: String,
    pub result: String,
    pub confidence: f64,
    pub physical_context: BTreeMap<String, f64>,
    pub policy_ref: String,
    /// S2 store-and-forward: record when the product was first buffered.
    pub first_buffered_at: Option<String>,
}

impl DeriveInput {
    pub fn stub_for(
        scenario: Scenario,
        product_id: &str,
        timestamp: &str,
        raw_pointer: &str,
    ) -> Self {
        let (source_device, produced_by, confidence, physical_context) = match scenario {
            Scenario::K1 => (
                "did:example:factory-robot-01".into(),
                "urn:ratio:node:factory-poc-01".into(),
                0.96,
                BTreeMap::from([
                    ("motorRPM".into(), 1450.0),
                    ("temperatureCelsius".into(), 42.5),
                ]),
            ),
            Scenario::S1 | Scenario::S2 => (
                "did:example:vessel-engine-vib-01".into(),
                "urn:ratio:node:maritime-poc-01".into(),
                0.91,
                BTreeMap::from([
                    ("shaftRPM".into(), 98.0),
                    ("temperatureCelsius".into(), 61.2),
                ]),
            ),
        };
        Self {
            scenario,
            product_id: product_id.into(),
            source_device,
            timestamp: timestamp.into(),
            raw_pointer: raw_pointer.into(),
            produced_by,
            task: "anomaly_detection".into(),
            result: "vibration_abnormal".into(),
            confidence,
            physical_context,
            policy_ref: "urn:odrl:policy:internal-only-rawdata".into(),
            first_buffered_at: if scenario == Scenario::S2 {
                Some(timestamp.into())
            } else {
                None
            },
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShareableProduct {
    #[serde(rename = "@context")]
    pub context: Value,
    #[serde(rename = "@type")]
    pub types: Vec<String>,
    pub id: String,
    #[serde(rename = "sourceDevice")]
    pub source_device: String,
    pub timestamp: String,
    pub domain: String,
    pub scenario: String,
    pub inference: Value,
    #[serde(rename = "dataGovernance")]
    pub data_governance: Value,
    pub provenance: Value,
}

impl ShareableProduct {
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string_pretty(self)
    }

    pub fn to_value(&self) -> Result<Value, serde_json::Error> {
        serde_json::to_value(self)
    }
}

/// Default `@context` compact form (same keys as `schemas/shareable-product.context.jsonld`).
pub fn default_context() -> Value {
    json!({
        "@version": 1.1,
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "ratio": "https://edgesentry.dev/ratio/v0#",
        "ShareableProduct": "ratio:ShareableProduct",
        "id": "@id",
        "type": "@type",
        "sourceDevice": { "@id": "ratio:sourceDevice", "@type": "@id" },
        "timestamp": { "@id": "ratio:timestamp", "@type": "xsd:dateTime" },
        "domain": "ratio:domain",
        "scenario": "ratio:scenario",
        "inference": "ratio:inference",
        "task": "ratio:task",
        "result": "ratio:result",
        "confidence": { "@id": "ratio:confidence", "@type": "xsd:double" },
        "physicalContext": "ratio:physicalContext",
        "motorRPM": { "@id": "ratio:motorRPM", "@type": "xsd:double" },
        "temperatureCelsius": { "@id": "ratio:temperatureCelsius", "@type": "xsd:double" },
        "shaftRPM": { "@id": "ratio:shaftRPM", "@type": "xsd:double" },
        "dataGovernance": "ratio:dataGovernance",
        "policyRef": { "@id": "ratio:policyRef", "@type": "@id" },
        "rawDataPointer": "ratio:rawDataPointer",
        "shaclConforms": { "@id": "ratio:shaclConforms", "@type": "xsd:boolean" },
        "provenance": "ratio:provenance",
        "producedBy": { "@id": "ratio:producedBy", "@type": "@id" },
        "queueDepth": { "@id": "ratio:queueDepth", "@type": "xsd:integer" },
        "firstBufferedAt": { "@id": "ratio:firstBufferedAt", "@type": "xsd:dateTime" }
    })
}

#[derive(Debug, thiserror::Error)]
pub enum DeriveError {
    #[error(transparent)]
    Pointer(#[from] crate::pointer::PointerError),
    #[error("shareable product must not embed raw stub marker")]
    RawInProduct,
    #[error("confidence must be in [0, 1], got {0}")]
    Confidence(f64),
    #[error(transparent)]
    Json(#[from] serde_json::Error),
}

pub fn build_shareable_product(input: &DeriveInput) -> Result<ShareableProduct, DeriveError> {
    assert_local_pointer(&input.raw_pointer)?;
    if !(0.0..=1.0).contains(&input.confidence) {
        return Err(DeriveError::Confidence(input.confidence));
    }
    if input.raw_pointer.contains(RAW_STUB_MARKER) {
        return Err(DeriveError::RawInProduct);
    }

    let mut physical = Map::new();
    for (k, v) in &input.physical_context {
        physical.insert(k.clone(), json!(v));
    }

    let mut provenance = json!({ "producedBy": input.produced_by });
    if let Some(buf) = &input.first_buffered_at {
        provenance["firstBufferedAt"] = json!(buf);
    }

    let product = ShareableProduct {
        context: default_context(),
        types: vec!["ShareableProduct".into()],
        id: input.product_id.clone(),
        source_device: input.source_device.clone(),
        timestamp: input.timestamp.clone(),
        domain: input.scenario.default_domain().as_str().into(),
        scenario: input.scenario.as_str().into(),
        inference: json!({
            "task": input.task,
            "result": input.result,
            "confidence": input.confidence,
            "physicalContext": physical,
        }),
        data_governance: json!({
            "policyRef": input.policy_ref,
            "rawDataPointer": input.raw_pointer,
        }),
        provenance,
    };

    let blob = product.to_json()?;
    if blob.contains(RAW_STUB_MARKER) {
        return Err(DeriveError::RawInProduct);
    }
    Ok(product)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::envelope::validate_envelope;

    #[test]
    fn all_scenarios_are_metadata_only() {
        for (scenario, pointer, device, domain) in [
            (
                Scenario::K1,
                "local://storage/K1/raw_wave.bin",
                "did:example:factory-robot-01",
                "factory",
            ),
            (
                Scenario::S1,
                "local://storage/S1/raw_shaft.bin",
                "did:example:vessel-engine-vib-01",
                "maritime",
            ),
            (
                Scenario::S2,
                "local://storage/S2/raw_shaft.bin",
                "did:example:vessel-engine-vib-01",
                "maritime",
            ),
        ] {
            let product = build_shareable_product(&DeriveInput::stub_for(
                scenario,
                "urn:uuid:00000000-0000-0000-0000-000000000001",
                "2026-08-18T00:00:00Z",
                pointer,
            ))
            .unwrap();
            let blob = product.to_json().unwrap();
            assert!(!blob.contains(RAW_STUB_MARKER), "{scenario:?}");
            assert_eq!(product.source_device, device);
            assert_eq!(product.domain, domain);
            assert_eq!(product.scenario, scenario.as_str());
            assert!(product.data_governance["rawDataPointer"]
                .as_str()
                .unwrap()
                .starts_with("local://"));
            validate_envelope(&product.to_value().unwrap()).unwrap();
        }
    }

    #[test]
    fn k1_physical_context_is_motor() {
        let product = build_shareable_product(&DeriveInput::stub_for(
            Scenario::K1,
            "urn:uuid:00000000-0000-0000-0000-000000000001",
            "2026-08-18T00:00:00Z",
            "local://storage/K1/raw_wave.bin",
        ))
        .unwrap();
        let ctx = &product.inference["physicalContext"];
        assert!(ctx.get("motorRPM").is_some());
        assert!(ctx.get("shaftRPM").is_none());
    }

    #[test]
    fn maritime_physical_context_is_shaft() {
        for scenario in [Scenario::S1, Scenario::S2] {
            let product = build_shareable_product(&DeriveInput::stub_for(
                scenario,
                "urn:uuid:00000000-0000-0000-0000-000000000001",
                "2026-08-18T00:00:00Z",
                "local://storage/S1/raw_shaft.bin",
            ))
            .unwrap();
            let ctx = &product.inference["physicalContext"];
            assert!(ctx.get("shaftRPM").is_some());
            assert!(ctx.get("motorRPM").is_none());
        }
    }

    #[test]
    fn s1_does_not_mark_buffer() {
        let product = build_shareable_product(&DeriveInput::stub_for(
            Scenario::S1,
            "urn:uuid:00000000-0000-0000-0000-000000000002",
            "2026-08-18T00:00:00Z",
            "local://storage/S1/raw_shaft.bin",
        ))
        .unwrap();
        assert!(product.provenance.get("firstBufferedAt").is_none());
    }

    #[test]
    fn locked_domains_and_parse() {
        assert_eq!(Scenario::K1.default_domain(), Domain::Factory);
        assert_eq!(Scenario::S1.default_domain(), Domain::Maritime);
        assert_eq!(Scenario::S2.default_domain(), Domain::Maritime);
        assert!(Scenario::parse("K9").is_none());
        assert_eq!(Scenario::parse("K1"), Some(Scenario::K1));
    }

    #[test]
    fn rejects_confidence_out_of_range() {
        let mut input = DeriveInput::stub_for(
            Scenario::K1,
            "urn:uuid:1",
            "2026-08-18T00:00:00Z",
            "local://storage/K1/raw.bin",
        );
        input.confidence = 1.2;
        assert!(matches!(
            build_shareable_product(&input),
            Err(DeriveError::Confidence(_))
        ));
    }

    #[test]
    fn rejects_raw_stub_in_pointer() {
        let mut input = DeriveInput::stub_for(
            Scenario::K1,
            "urn:uuid:1",
            "2026-08-18T00:00:00Z",
            "local://storage/K1/raw.bin",
        );
        input.raw_pointer = format!("local://storage/{RAW_STUB_MARKER}");
        assert!(matches!(
            build_shareable_product(&input),
            Err(DeriveError::RawInProduct)
        ));
    }

    #[test]
    fn s2_marks_buffer() {
        let input = DeriveInput::stub_for(
            Scenario::S2,
            "urn:uuid:00000000-0000-0000-0000-000000000002",
            "2026-08-18T00:00:00Z",
            "local://storage/S2/raw_shaft.bin",
        );
        let product = build_shareable_product(&input).unwrap();
        assert_eq!(
            product.provenance["firstBufferedAt"].as_str().unwrap(),
            "2026-08-18T00:00:00Z"
        );
        validate_envelope(&product.to_value().unwrap()).unwrap();
    }

    #[test]
    fn rejects_public_pointer() {
        let mut input = DeriveInput::stub_for(
            Scenario::K1,
            "urn:uuid:1",
            "2026-08-18T00:00:00Z",
            "https://example.invalid/raw.bin",
        );
        input.raw_pointer = "https://example.invalid/raw.bin".into();
        assert!(build_shareable_product(&input).is_err());
    }
}
