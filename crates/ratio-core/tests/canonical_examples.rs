//! Parity with `samples/tests`: canonical examples must pass the in-process envelope gate.

use ratio_core::{validate_envelope, RAW_STUB_MARKER};
use serde_json::Value;
use std::fs;
use std::path::PathBuf;

fn examples_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../examples")
}

#[test]
fn canonical_examples_have_no_raw_and_pass_envelope() {
    for name in [
        "k1-cell-vibration.jsonld",
        "s1-engine-vibration.jsonld",
        "s2-store-and-forward.jsonld",
    ] {
        let path = examples_dir().join(name);
        let text = fs::read_to_string(&path).unwrap_or_else(|e| panic!("{name}: {e}"));
        assert!(
            !text.contains(RAW_STUB_MARKER),
            "{name} embeds raw stub marker"
        );
        let doc: Value = serde_json::from_str(&text).unwrap();
        assert!(
            doc["dataGovernance"]["rawDataPointer"]
                .as_str()
                .unwrap()
                .starts_with("local://"),
            "{name}"
        );
        validate_envelope(&doc).unwrap_or_else(|e| panic!("{name}: {e}"));
    }
}

#[test]
fn s1_and_s2_share_engine_device_line() {
    let s1: Value = serde_json::from_str(
        &fs::read_to_string(examples_dir().join("s1-engine-vibration.jsonld")).unwrap(),
    )
    .unwrap();
    let s2: Value = serde_json::from_str(
        &fs::read_to_string(examples_dir().join("s2-store-and-forward.jsonld")).unwrap(),
    )
    .unwrap();
    assert_eq!(s1["sourceDevice"], s2["sourceDevice"]);
    assert_eq!(s1["domain"], "maritime");
    assert_eq!(s2["scenario"], "S2");
    assert!(s2["provenance"]["firstBufferedAt"].as_str().is_some());
    assert!(s1["provenance"].get("firstBufferedAt").is_none());
}
