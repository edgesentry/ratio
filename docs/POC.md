# PoC verticals

> Japanese: [POC.ja.md](POC.ja.md)

Assumed fields for validating the thesis **participate in ODS without shipping raw data**.

| Vertical | Typical OT | Typical assets |
|----------|------------|----------------|
| **Factory** | Industrial robots / factory | Robot arms, PLCs, line cameras, vibration / temperature sensors |
| **Maritime** | Maritime sensors / vessels | Shipboard sensors, AIS-adjacent telemetry, cameras, machinery / vibration, intermittent links |

These are **thesis-validation contexts**, not a promise to ship two products at once. Advance one vertical slice first; use the other as the second proof.

Demand conditions (all three required per vertical):

1. Do not ship raw data by default  
2. Someone outside the cell / vessel needs **meaning**  
3. ODS **Pull** participation is required (not only a local dashboard)

---

## Industrial robots / factory

### Who

- Domain owner: factory / cell operator (and SI partners)  
- Consumers: partner OEMs, quality / traceability agents, Agentic AI on ODS  

### Domain-specific problem

Robot / camera / vibration raw data cannot leave the plant (IP, privacy, bandwidth), while partners need **judgment + context** via data-space Pull (which robot, which process, why)—not a lake mirror.

### Raw data vs shareable product (proposed boundary)

| Keep local (raw data) | Shareable product (ODS-Pull-able) |
|-------------------------|-----------------------------------|
| Camera frames / video | Anomaly or quality **result** + confidence |
| Vibration / force / torque waveforms | Device ID (WoT / DID), cell / line ID, timestamp |
| Proprietary teach / process logs | Ontology vocabulary for fault / process class |
| High-rate PLC dumps | Summarized physical context (e.g. RPM, temperature)—not full traces |
| | `policyRef` (raw data internal-only); optional local-only `rawDataPointer` |
| | SHACL report ref when claimed |

### Thesis is shown when

Traceability / quality / DPP-like **products** are discoverable via Pull, and robot video / waveforms do not ride the ODS path by default.

### First vertical slice (**locked**)

| Item | Lock |
|------|------|
| Device | One weld / assemble **cell robot** (stub TD; vendor TBD) |
| Sensor / raw data | **Vibration waveform** only (`vibrationWaveform` → `local://`; synthetic or recorded `.bin`) |
| TD | [`examples/td/k1-robot.td.json`](../examples/td/k1-robot.td.json) · DID `did:example:factory-robot-01` |
| Product context | `physicalContext.motorRPM`, `temperatureCelsius` (summaries, not traces) |
| Out of this slice | Line camera, force/torque, PLC dumps, K2–K5 |

Path: ingest TD → store waveform locally → one JSON-LD shareable product → ODS SDK Pull. Camera stays a later optional extension (`quality_fail`), not required to show the thesis.

---

## Maritime sensors / vessels

### Who

- Domain owner: operator / shipboard system owner  
- Consumers: shore fleet ops, partners, Agentic AI on ODS when the link is up  

### Domain-specific problem

Links are intermittent and bandwidth-poor. Hull / machinery / camera raw data should stay onboard. Shore needs **meaning-bearing state / events** when the vessel can participate in ODS.

### Raw data vs shareable product (proposed boundary)

| Keep local (raw data) | Shareable product (ODS-Pull-able) |
|-------------------------|-----------------------------------|
| High-rate vibration / acoustic samples | Event / judgment **result** + confidence |
| Camera / CCTV video | Vessel / node DID, sensor WoT id, timestamp |
| Dense NMEA / bus logs (full text) | Coarse ops context as policy allows (no full track dump without separate permission) |
| | Ontology vocabulary for alert / state class |
| | `policyRef`; local-only `rawDataPointer` |
| | SHACL report ref when claimed |

### Thesis is shown when

The shipboard node serves **meta products only** across constrained / intermittent links, and raw data stays on shipboard storage.

### First vertical slice (**locked**)

| Item | Lock |
|------|------|
| Device | One **vessel engine vibration** sensor (stub TD; vendor TBD) |
| Sensor / raw data | **Shaft vibration** only (`shaftVibration` → `local://`; synthetic or recorded `.bin`) |
| TD | [`examples/td/s-engine-vib.td.json`](../examples/td/s-engine-vib.td.json) · DID `did:example:vessel-engine-vib-01` |
| Product context | `physicalContext.shaftRPM`, `temperatureCelsius` |
| S1 vs S2 | **Same device line.** S1 transfers when online; S2 queues the product (not the waveform) until the link returns |
| Out of this slice | CCTV, full NMEA / bus dumps, bilge / environment sensors |

Path: same envelope as factory; raw data stays onboard; only the shareable product may wait in `data/queue`.

---

## Candidate scenarios (vendor TBD)

Concrete vendors and cells are **TBD**. Prefer scenarios that best show the difference from standalone edge AI, IIoT gateways, and IT-side ODS nodes.

### Advantage lens (scoring candidates)

| Advantage | Scenario shows this when |
|-----------|--------------------------|
| **A1 raw-data non-egress** | Raw data is clearly sensitive or huge (video, waveforms); sending it to ODS is unrealistic |
| **A2 meaning-bearing product** | Bare scores are not actionable; device / process / voyage context is required |
| **A3 official ODS Pull** | Cross-org or shore / partner consumers want discover / serve—not only plant HMI |
| **A4 same pipeline, two physics** | Factory and vessel share the product envelope; only shapes / config change |
| **A5 thin SI via WoT** | Multi-vendor or mixed sensors where TD beats proprietary schemas |
| **Avoid** | Hard real-time replacement of safety PLCs; “demo dashboard with no ODS consumer” |

Legend: **S** = strong advantage demo, **M** = medium, **W** = weak / easy to confuse with non-Ratio tools.

---

### Factory candidates

| ID | Scenario (vendor-agnostic) | Raw data that stays | Shareable product (summary) | A1 | A2 | A3 | A5 | Notes |
|----|----------------------------|----------------|-----------------------------|----|----|----|----|-------|
| **K1** | **Weld / assembly cell anomaly** — vibration or force on one arm + optional line camera | Waveforms; camera frames | `vibration_abnormal` / quality NG + robot WoT id + cell / process + physicalContext + policyRef | S | S | S | M | Default best. Clear that “score alone is useless”; partners care *which cell / process*. |
| **K2** | **End-of-line visual quality gate** — camera judgment only | Images / video | Defect class + confidence + station / DID + defect vocab + policyRef | S | S | S | M | Strong A1 (video). Watch ontology so it does not look like “plain AOI cloud upload.” |
| **K3** | **DPP / CFP breadcrumbs from the cell** — process events as data-space products | Full process logs, teach | Passport-related **events** (part ID refs, process, energy / quality summary) + meaning + policy—not a full genealogy DB | M | S | S | W | Strong A3 for policy / traceability narratives; high ontology agreement cost. |
| **K4** | **Multi-vendor arm swap** — same product shape across two brands (stubs OK) | Vendor-specific raw data | Same shareable-product schema; only TD backend differs | M | M | M | S | Aimed at **A5**. A3 is weak unless consumers are scripted. |
| **K5** | **SHACL action advisory** — validate commands / context before share or operator confirm | Command traces, state dumps | SHACL conform / violate report in the product (+ device context) | M | S | M | M | Validation advantage. Stay **advisory** (not a safety PLC). Avoid over-scoping into E1. |
| **K6** | **Predictive maintenance ticket** — motor / gearbox model score | Long vibration history | Maintenance class + rationale summary + device ID—not the archive body | S | M | M | M | Common edge-AI story. Collapses into boxed Kaggle unless **meaning + ODS Pull** are forced. |

**Factory recommended shortlist**

| Priority | Pick | Why advantage shows |
|----------|------|---------------------|
| **1st** | **K1** | Shows A1+A2+A3 together; stub-friendly without full vision |
| **2nd** | **K1+K4** | After K1, swap TD backends to prove thin multi-vendor SI |
| **Alternate** | **K2** | When counterpart language is “camera / IP” more than vibration |
| **Later** | **K3** | After the product envelope moves—high ontology cost |
| **Not main axis** | **K5** | Addon validation after K1 products exist |
| **Avoid as sole PoC** | **K6** | Easy to look like generic edge ML |

---

### Maritime candidates

| ID | Scenario (vendor-agnostic) | Raw data that stays | Shareable product (summary) | A1 | A2 | A3 | Link load | Notes |
|----|----------------------------|----------------|-----------------------------|----|----|----|-----------|-------|
| **S1** | **Machinery / shaft vibration event** — detect onboard; shore Pull when linked | High-rate samples | Event class + confidence + vessel / sensor DID + coarse ops context + policyRef | S | S | S | S | Default maritime best. Bandwidth story is obvious. |
| **S2** | **Store-and-forward alert queue** — offline buffer; flush on link | Same raw data as S1 | Same product; **queue depth / freshness** in provenance | S | S | S | S | Make intermittent links the demo *feature*—not an excuse. |
| **S3** | **Bridge / CCTV incident summary** — video does not leave by default | Video | Incident type + time window + camera id + policy; pointer local | S | S | M | S | Strong A1 and privacy; confirm a shore consumer exists. |
| **S4** | **Environment / bilge / tank threshold events** | Dense sensor logs | Threshold event + meaning + vessel id | M | M | M | M | Easy hardware; weak “why not MQTT dashboard?” without a real ODS consumer. |
| **S5** | **Cross-org partner (yard / insurance / charter) Pull** — S1 product to an explicit second org | Same as S1 | Product + stricter terms | S | S | S | M | Maximizes A3; depends more on partner willingness than tech. |
| **S6** | **Dense NMEA shore mirror** | — | — | W | W | W | W | **Anti-candidate.** Looks like telemetry Push; thesis failure. |

**Maritime recommended shortlist**

| Priority | Pick | Why advantage shows |
|----------|------|---------------------|
| **1st** | **S1 + S2** | Vibration event + store-and-forward covers A1–A3 + link load at once |
| **Alternate** | **S3** | When stakeholders lead with camera / privacy |
| **Amplifier** | **S5** | When a second org can Pull—turns the PoC into a data-space story |
| **Weak alone** | **S4** | Only with a required ODS consumer agent |
| **Reject** | **S6** | Contradicts raw-data non-egress |

---

### Combinations where “one Ratio, two domains” shows best

| Pair | Narrative | Advantage in one line |
|------|-----------|----------------------|
| **K1 → S1/S2** | Factory anomaly product, then same envelope + queue onboard | “Same shareable-product path; what changes is physics and link policy, not the substrate.” |
| **K2 → S3** | Vision-centric; raw video data does not leave | “Camera IP stays; only incident / quality meaning rides ODS.” |
| **K3 → S5** | Traceability + cross-org Pull | Strong policy / ODS narrative; high coordination cost |

**Shortlist locked:** **K1**, then **S1+S2**. Lock the product JSON-LD envelope, core SHACL shapes, and ODS handoff—not robot brands or class societies (stubs OK).

---

### “Good candidate” questions in partner conversations

For each proposed cell / vessel, ask:

1. What raw data is painful / expensive to send to ODS?  
2. Who outside needs meaning and will Pull via ODS (lab consumers OK)?  
3. Can we proceed 90 days on stub TD + recorded raw data even if access slips?  

If (2) is “local SCADA screen only,” Ratio’s advantage will not show—pick another candidate.

---

## Shared vs domain-specific

| Shared (build once) | Domain-specific (config / shapes) |
|---------------------|---------------------------------|
| Raw data vs product split pipeline | Device TDs, ontology vocab, SHACL shapes |
| JSON-LD product envelope | Policy refs and allowed physicalContext fields |
| Oxigraph validation hooks | Existing inference / task IDs |
| ODS SDK handoff | Identity (vessel vs factory-cell DID) |
| Local store (DuckDB / files / …) | Retention and pointer policy |

---

## Order

| Order | Vertical | Why first |
|-------|------|-----------|
| **1** | **Factory** | Continuous links ease ODS SDK bring-up; multi-vendor robot / SI narrative is clear |
| **2** | **Maritime** | Same pipeline under intermittent egress—proves the constrained-link side of the thesis |

Do not fork the architecture into two. Prove the factory vertical end-to-end; load maritime shapes and store-and-forward onto the same binary / config.

---

## reuse vs build (both verticals)

Ownership tiers: [`SCOPE.md`](SCOPE.md). This table is the **PoC inventory**—each capability is **Reuse** (OSS / standard / official ODS), **Build** (Ratio), or **Out** (SI / consumer / consortium). Architecture intent (Oxigraph, DuckDB, Arrow) may differ from what the PoC uses today.

### Three tagged tasks (DISCUSSION §D)

| Task | Tag | Status |
|------|-----|--------|
| Shareable-product pipeline (ingest → split → handoff) | **Build** | Done — [`samples/`](../samples/) |
| SHACL shapes + validation timing | **Build** shapes; **Reuse** RDF/SHACL engine | Done — `schemas/` + pyshacl (Oxigraph later) |
| ODS SDK connect (L2/L3, AuthZEN) | **Reuse** official stack; **Build** packaging + helper scripts | Done — [`ODS_HANDOFF.md`](ODS_HANDOFF.md) |

### Inventory

| ID | Capability | Decision | Reuse | Ratio builds | PoC now | Later |
|----|------------|----------|-------|--------------|---------|-------|
| RB1 | Device ingest | **Reuse** GW/stubs + **Build** thin consume | WoT TD; existing IIoT / WoT GW | Thin TD load (`--td`); no multi-protocol GW | Stub TDs in `examples/td/` | Device lines locked (K1 / S1–S2) |
| RB2 | Inference / judgment | **Reuse** runtime; **Build** optional glue | ONNX Runtime / vendor models | Orchestrate when claimed; PoC may stub | Stub result in envelope | Optional ONNX on site |
| RB3 | Graph / SHACL | **Reuse** engine; **Build** shapes | RDF / SHACL (pyshacl now; Oxigraph intended) | Envelope shapes, validation **before** publish | pyshacl + `schemas/` | Oxigraph in Rust core |
| RB4 | Raw-data / product custody | **Reuse** stores; **Build** split | Files now; DuckDB / LanceDB / SQLite intended | Split rules; `local://` pointer; never publish raw data | `data/raw`, `data/out`, `data/queue` | DuckDB / LanceDB / SQLite |
| RB5 | Shareable-product envelope | **Build** | JSON-LD / ODRL as standards | Envelope, `@context`, policyRef, PoC examples | [`PRODUCT_ENVELOPE.md`](PRODUCT_ENVELOPE.md) | Production catalog / context URIs |
| RB6 | ODS participation O1–O6 | **Reuse** SDK; **Build** handoff | IPA Middleware / SDK (L3 identity, L2 transfer, AuthZEN→OpenFGA) | Product POST; industry stub; route/FGA helper scripts | `--ods stub\|http\|l2` + `samples/scripts/ods/` | L4 Discovery when connecting a real catalog |
| RB7 | Cross-language I/F | **Reuse** Arrow; **Build** broker | Apache Arrow + PyO3 | Memory Broker using Arrow (Ratio) | **v0** — [`crates/ratio-py`](../crates/ratio-py) `ratio_core` (IPC columns are metadata only) | Zero-copy bounds / streaming |
| RB8 | Composition runtime | **Build** | — | Thin orchestrator | **v0** — [`crates/ratio-core`](../crates/ratio-core); product CLI is `eds ratio derive` | Oxigraph; point `samples` at the bindings |
| RB9 | Industry ontology agreement | **Out** | SAMM / domain vocab when published | Consume only; minimal PoC codes | Thin K1/S1/S2 codes | Consortium vocab |
| RB10 | Deep device SI | **Out** | Vendor / SI / existing GW | Thin adapter only | Stubs | Field SI |
| RB11 | Pull consumer / Agentic AI | **Out** (optional separate demo) | Official L2 Pull client pattern | Not Ratio core | `ratio-poc-pull` + `verify-l2-pull.sh` | Production consumer UI / agent |

**Do not build:** ODP / L2 / L3 / L4, AuthZEN PDP, Keycloak, OpenFGA, a private data-space protocol, a universal OT gateway, production consumer UIs.

---

## Locked decisions

| Item | Decision |
|------|----------|
| Shortlist | **K1 → S1+S2** (locked) |
| Device / sensor lines | **Locked** — factory: cell robot + vibration waveform (K1); maritime: engine shaft vibration (S1/S2, same TD). Vendor TBD; stubs + recorded / synthetic raw data |
| Vendor / cell / vessel brand | TBD (does not block envelope / pipeline) |
| Shared envelope | [`PRODUCT_ENVELOPE.md`](PRODUCT_ENVELOPE.md) and `schemas/` · `examples/` |
| reuse vs build | Locked in the inventory above (RB1–RB11) |
| A3 Pull consumer | **Yes** for PoC success — reference agent `ratio-poc-pull` (RB11 **Out**, not Ratio core) |

---

## Open (lock next)

1. Production ODS context / catalog URIs  
2. Concrete vendor / cell / vessel brand (device **line** is locked above; brand does not block)
