# Shareable-product envelope (PoC)

> Japanese: [PRODUCT_ENVELOPE.ja.md](PRODUCT_ENVELOPE.ja.md)

**Locked shortlist:** K1 (factory) → S1+S2 (maritime).  
**Locked device lines:** K1 = cell robot + vibration waveform; S1/S2 = vessel engine shaft vibration (same TD). Vendor TBD. Recorded / synthetic raw data is fine.

Use the **same envelope** for K and S. Vertical differences are only `domain`, vocabulary, and optional `physicalContext` / `provenance` fields.

Related: [`POC.md`](POC.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`DISCUSSION.md`](DISCUSSION.md)

Schema artifacts:

| File | Content |
|------|---------|
| [`../schemas/shareable-product.context.jsonld`](../schemas/shareable-product.context.jsonld) | Shared `@context` |
| [`../schemas/shareable-product.shacl.ttl`](../schemas/shareable-product.shacl.ttl) | Minimal SHACL |
| [`../examples/k1-cell-vibration.jsonld`](../examples/k1-cell-vibration.jsonld) | K1 example |
| [`../examples/s1-engine-vibration.jsonld`](../examples/s1-engine-vibration.jsonld) | S1 example (S2 = same body + queue provenance) |

---

## Design rules

1. **Result + meaning + terms of use** are required. Do not embed raw data.  
2. `rawDataPointer` is `local://` only (SHACL forbids public URLs).  
3. Official ODS context URLs may be placeholders; replace at real connect time.  
4. Inference may be stubbed (hand-fill `confidence` / `result`).

---

## Required fields

| Field | Type / form | Description |
|-------|-------------|-------------|
| `@context` | array | Shared context + optional domain additions |
| `@type` | array | Must include `ShareableProduct` |
| `id` | IRI / URN | Product instance ID |
| `sourceDevice` | DID or URN | Observing device / node |
| `timestamp` | xsd:dateTime | Event time (UTC recommended) |
| `domain` | enum | `factory` \| `maritime` |
| `scenario` | enum | `K1` \| `S1` \| `S2` (keep in sync with POC when extended) |
| `inference.task` | string | Task ID (e.g. `anomaly_detection`) |
| `inference.result` | string | Machine-readable result code |
| `inference.confidence` | 0..1 | Confidence |
| `dataGovernance.policyRef` | IRI / URN | Terms ref (e.g. raw data internal-only) |

## Recommended fields

| Field | Description |
|-------|-------------|
| `inference.physicalContext` | Summary only (RPM, temperature, etc.). No full traces |
| `dataGovernance.rawDataPointer` | In-domain pointer (`local://…`) |
| `dataGovernance.shaclConforms` | Validation boolean when emitted |
| `provenance.producedBy` | Ratio node / pipeline ID |
| `provenance.queueDepth` / `firstBufferedAt` | Store-and-forward provenance for **S2** |

---

## Result codes (initial PoC vocabulary)

Keep short and cross-site. May later promote to ontology IRIs.

| Code | Use |
|------|-----|
| `vibration_abnormal` | Vibration anomaly for K1 / S1 |
| `vibration_normal` | Normal |
| `quality_fail` | K1 extension (optional camera) |
| `link_flush` | Marker for S2 queue-flush events (if needed) |

---

## Validation flow (PoC)

Implementation: [`../poc`](../poc) (`uv sync` → `uv run ratio-poc`. Steps: [`../poc/README.md`](../poc/README.md))

```
thin TD (`examples/td/*.td.json`) → raw data → `data/raw/`
JSON-LD instance → data/out/
    → rdflib + pyshacl (schemas/shareable-product.shacl.ttl)
    → if conforms → ODS handoff stub (SDK not yet connected)
    → do not put raw-data files on the publish path
```

---

## Open (outside the envelope)

- Lock production ODS context / catalog URIs  
- Concrete cell / vessel / vendor (do not block on stubs)
