# Architecture

> Japanese: [ARCHITECTURE.ja.md](ARCHITECTURE.ja.md)

Implementation sketch for the thesis **participate in ODS without shipping raw quanta**.

**Build policy:** Compose OSS and the official ODS SDK. Ratio owns on-site derivation, validation, raw/product split, and the handoff boundary.  
See: [`DISCUSSION.md`](DISCUSSION.md) · [`ODS_COMPLIANCE.md`](ODS_COMPLIANCE.md)

---

## 1. Default path (overview)

```
[ L1 Devices ]
   PLC, cameras, sensors, robots …
        │  W3C WoT / Thing Description
        ▼
[ L2 Derive & validate ]  ← Ratio
   Inference + RDF/JSON-LD context + SHACL
        │  split
        ├──────────────────────────────┐
        ▼                              ▼
[ raw quanta — local custody ]   [ shareable product ]
  files / DuckDB / LanceDB         result + meaning + policyRef
                                   (+ in-domain raw pointer)
        │                              │
        │                              ▼
        │                    [ L3 Handoff / governance ]
        │                      DID·VC · ODRL refs · product package
        │                              │
        │                              ▼
        │                    [ L4 ODS participation ]
        │                      official Middleware / SDK (ODP)
        │                      discover + Pull of shareable product only
        └──── raw does not take this path by default ────┘
```

| Layer | Thesis job |
|-------|------------|
| **L1** | Observe via WoT TD; do not invent proprietary device schemas |
| **L2** | Derive meaning-bearing results; validate with SHACL |
| **Split** | Keep raw; only shareable products may leave |
| **L3** | Package identity, policy refs, and provenance for handoff |
| **L4** | Participate via the **official** ODS stack (O1–O6)—no ODP fork |

### 1.1 ODS authentication and authorization

> Japanese: [§1.1](ARCHITECTURE.ja.md#11-odsの認証認可) · Detail: [`ODS_COMPLIANCE.md` §4](ODS_COMPLIANCE.md#4-authentication-and-authorization-client-requirements)

- **L3 (authenticate):** operator + `client_credentials` → JWT with `operator_id` (**O1**).
- **L2 (authorize):** gateway validates JWT, AuthZEN → OpenFGA for endpoint access (**O4**, **O8**).
- **Ratio:** shareable products at industry API only; no JWT/AuthZEN on site (**R1–R4**).

---

## 2. Logical data flow

```
WoT ingest → inference (ONNX/TensorRT, etc.)
         → [split]
              ├─ raw → DuckDB / LanceDB / local files (custody)
              └─ shareable product → JSON-LD(+SHACL) → SQLite(policy/state)
                                   → ODS Middleware/SDK (discover + Pull)
         → Arrow Memory Broker ←→ Python / Edge SLM (RAG: LanceDB)
```

---

## 3. Technology placement

| Concern | Technology | Ownership |
|---------|------------|-----------|
| Thin composition runtime | Rust | **Ratio** (shell only) |
| Graph inference & validation | Oxigraph | **OSS** |
| Local raw / artifact store | DuckDB, LanceDB, files | **OSS** |
| State, credentials, policy records | SQLite | **OSS** |
| Cross-language I/F | Apache Arrow + PyO3 | Arrow is **OSS**; Memory Broker is **Ratio** |
| Inference runtime | ONNX Runtime / TensorRT, etc. | **OSS** / vendor |
| Semantics representation | JSON-LD / CBOR-LD | **Standard** |
| ODS participation | IPA ODS Middleware / SDK + ODP | **Official**—do not reimplement |
| L2 authorization (AuthZEN → OpenFGA) | OpenID AuthZEN API + OpenFGA | **Official ODS SDK**—Ratio enables via scripts only |

---

## 4. What a shareable product carries

**Shareable product:** a Pull-able package. Not raw bytes. Full definition: [`DISCUSSION.md`](DISCUSSION.md) (“What is a shareable product”)

Thesis alignment (result + meaning + terms of use):

1. **Result** — a judgment or observation (not raw bytes)
2. **Meaning** — ontology / JSON-LD context (which device, which properties, on what basis)
3. **Terms of use** — policy refs (e.g. ODRL); raw is non-egress by default
4. **Optional in-domain pointer** — `rawDataPointer` for local ops. Not a public raw URL

### Payload example

Locked PoC envelope, SHACL, and K1 / S1 / S2 examples: [`PRODUCT_ENVELOPE.md`](PRODUCT_ENVELOPE.md)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/td/v1",
    "https://open-dataspaces.org/v1/context.jsonld",
    { "manufacturing": "https://schema.org/manufacturing/" }
  ],
  "@type": ["Thing", "EdgeAIInferenceResult"],
  "id": "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "sourceDevice": "did:example:kitakyushu-factory-robot-01",
  "timestamp": "2026-08-16T14:00:00Z",
  "inference": {
    "task": "anomaly_detection",
    "result": "vibration_abnormal",
    "confidence": 0.96,
    "physicalContext": {
      "motorRPM": 1450,
      "temperatureCelsius": 42.5
    }
  },
  "dataGovernance": {
    "policyRef": "urn:odrl:policy:internal-only-rawdata",
    "rawDataPointer": "local://storage/raw_wave_20260816_001.bin"
  }
}
```

---

## 5. Core I/F (discussion sketch)

```
┌─────────────┐     PyO3      ┌──────────────────┐
│ Python / SLM│ ◄──────────► │ Ratio Rust Core  │
└─────────────┘   Arrow IPC   │  Oxigraph        │
       ▲                      │  SHACL / SPARQL  │
       │                      │  product package │
       └──── LanceDB / DuckDB / SQLite ──────────┘
                              │
                              ▼
                     ODS Middleware / SDK
```

Decide:

1. Arrow RecordBatch columns for product assembly (`device_id`, `ts`, `graph_delta`, `shacl_report`, …)
2. Buffer ownership / zero-copy boundaries
3. Sync vs stream for continuous on-site derivation

---

## 6. First steps (PoC order)

Follow the thesis: **custody → derive → participate**.

1. **Ingest** — one device line via WoT TD; raw into local store  
2. **Split and productize** — JSON-LD shareable product + SHACL; do not put raw on the publish path  
3. **Participate** — ODS SDK: register / discover / serve **products only**  

PoC sites must satisfy demand conditions in [`DISCUSSION.md`](DISCUSSION.md).  
Assumed sites and boundaries: [`POC.md`](POC.md) (Kitakyushu first, then Setouchi).

---

## 7. Non-goals

- Shipping raw as the primary ODS offering
- Reimplementing ODP / ODS Middleware
- Claiming full ODS-RAM coverage on day one (MVP is the O1–O6 path in [`ODS_COMPLIANCE.md`](ODS_COMPLIANCE.md))
- Proliferating proprietary device protocols (prefer WoT TD)
- Forking Oxigraph, DuckDB, LanceDB, SQLite, or Arrow
- Hard real-time control plane (advisory / gate at most)
