# PoC sites

> Japanese: [POC.ja.md](POC.ja.md)

Assumed fields for validating the thesis **participate in ODS without shipping raw quanta**.

| Site | Domain | Typical assets |
|------|--------|----------------|
| **Kitakyushu** | Industrial robots / factory OT | Robot arms, PLCs, line cameras, vibration / temperature sensors |
| **Setouchi** | Maritime sensors / vessels | Shipboard sensors, AIS-adjacent telemetry, cameras, machinery / vibration, intermittent links |

These are **thesis-validation contexts**, not a promise to ship two products at once. Advance one vertical slice first; use the other as the second proof.

Demand conditions (all three required per site):

1. Do not ship raw by default  
2. Someone outside the cell / vessel needs **meaning**  
3. ODS **Pull** participation is required (not only a local dashboard)

---

## Kitakyushu — industrial robots / factory

### Who

- Domain owner: factory / cell operator (and SI partners)  
- Consumers: partner OEMs, quality / traceability agents, Agentic AI on ODS  

### Site-specific problem

Robot / camera / vibration raw cannot leave the plant (IP, privacy, bandwidth), while partners need **judgment + context** via data-space Pull (which robot, which process, why)—not a lake mirror.

### Raw vs shareable product (proposed boundary)

| Keep local (raw quanta) | Shareable product (ODS-Pull-able) |
|-------------------------|-----------------------------------|
| Camera frames / video | Anomaly or quality **result** + confidence |
| Vibration / force / torque waveforms | Device ID (WoT / DID), cell / line ID, timestamp |
| Proprietary teach / process logs | Ontology vocabulary for fault / process class |
| High-rate PLC dumps | Summarized physical context (e.g. RPM, temperature)—not full traces |
| | `policyRef` (raw internal-only); optional local-only `rawDataPointer` |
| | SHACL report ref when claimed |

### Thesis is shown when

Traceability / quality / DPP-like **products** are discoverable via Pull, and robot video / waveforms do not ride the ODS path by default.

### First vertical slice (proposal)

1. One robot + one sensor line via WoT TD (or stub TD)  
2. Synthetic or recorded vibration / camera → local store  
3. Emit one JSON-LD shareable product (judgment + meaning + policyRef)  
4. Register / serve via ODS SDK  

---

## Setouchi — maritime sensors / vessels

### Who

- Domain owner: operator / shipboard system owner  
- Consumers: shore fleet ops, partners, Agentic AI on ODS when the link is up  

### Site-specific problem

Links are intermittent and bandwidth-poor. Hull / machinery / camera raw should stay onboard. Shore needs **meaning-bearing state / events** when the vessel can participate in ODS.

### Raw vs shareable product (proposed boundary)

| Keep local (raw quanta) | Shareable product (ODS-Pull-able) |
|-------------------------|-----------------------------------|
| High-rate vibration / acoustic samples | Event / judgment **result** + confidence |
| Camera / CCTV video | Vessel / node DID, sensor WoT id, timestamp |
| Dense NMEA / bus logs (full text) | Coarse ops context as policy allows (no full track dump without separate permission) |
| | Ontology vocabulary for alert / state class |
| | `policyRef`; local-only `rawDataPointer` |
| | SHACL report ref when claimed |

### Thesis is shown when

The shipboard node serves **meta products only** across constrained / intermittent links, and raw stays on shipboard storage.

### First vertical slice (proposal)

1. One sensor type (e.g. machinery vibration or bilge / environment) + stub WoT TD  
2. Raw in shipboard store; products queued for ODS only when the link returns  
3. Same shareable-product shape as Kitakyushu where possible (portable pipeline)  
4. Participate via ODS SDK when connected  

---

## Candidate scenarios (vendor TBD)

Concrete vendors and cells are **TBD**. Prefer scenarios that best show the difference from standalone edge AI, IIoT gateways, and IT-side ODS nodes.

### Advantage lens (scoring candidates)

| Advantage | Scenario shows this when |
|-----------|--------------------------|
| **A1 raw non-egress** | Raw is clearly sensitive or huge (video, waveforms); shipping is absurd |
| **A2 meaning-bearing product** | Bare scores are not actionable; device / process / voyage context is required |
| **A3 official ODS Pull** | Cross-org or shore / partner consumers want discover / serve—not only plant HMI |
| **A4 same pipeline, two physics** | Factory and vessel share the product envelope; only shapes / config change |
| **A5 thin SI via WoT** | Multi-vendor or mixed sensors where TD beats proprietary schemas |
| **Avoid** | Hard real-time replacement of safety PLCs; “demo dashboard with no ODS consumer” |

Legend: **S** = strong advantage demo, **M** = medium, **W** = weak / easy to confuse with non-Ratio tools.

---

### Kitakyushu candidates

| ID | Scenario (vendor-agnostic) | Raw that stays | Shareable product (summary) | A1 | A2 | A3 | A5 | Notes |
|----|----------------------------|----------------|-----------------------------|----|----|----|----|-------|
| **K1** | **Weld / assembly cell anomaly** — vibration or force on one arm + optional line camera | Waveforms; camera frames | `vibration_abnormal` / quality NG + robot WoT id + cell / process + physicalContext + policyRef | S | S | S | M | Default best. Clear that “score alone is useless”; partners care *which cell / process*. |
| **K2** | **End-of-line visual quality gate** — camera judgment only | Images / video | Defect class + confidence + station / DID + defect vocab + policyRef | S | S | S | M | Strong A1 (video). Watch ontology so it does not look like “plain AOI cloud upload.” |
| **K3** | **DPP / CFP breadcrumbs from the cell** — process events as data-space products | Full process logs, teach | Passport-related **events** (part ID refs, process, energy / quality summary) + meaning + policy—not a full genealogy DB | M | S | S | W | Strong A3 for policy / traceability narratives; high ontology agreement cost. |
| **K4** | **Multi-vendor arm swap** — same product shape across two brands (stubs OK) | Vendor-specific raw | Same shareable-product schema; only TD backend differs | M | M | M | S | Aimed at **A5**. A3 is weak unless consumers are scripted. |
| **K5** | **SHACL action advisory** — validate commands / context before share or operator confirm | Command traces, state dumps | SHACL conform / violate report in the product (+ device context) | M | S | M | M | Validation advantage. Stay **advisory** (not a safety PLC). Avoid over-scoping into E1. |
| **K6** | **Predictive maintenance ticket** — motor / gearbox model score | Long vibration history | Maintenance class + rationale summary + device ID—not the archive body | S | M | M | M | Common edge-AI story. Collapses into boxed Kaggle unless **meaning + ODS Pull** are forced. |

**Kitakyushu recommended shortlist**

| Priority | Pick | Why advantage shows |
|----------|------|---------------------|
| **1st** | **K1** | Shows A1+A2+A3 together; stub-friendly without full vision |
| **2nd** | **K1+K4** | After K1, swap TD backends to prove thin multi-vendor SI |
| **Alternate** | **K2** | When counterpart language is “camera / IP” more than vibration |
| **Later** | **K3** | After the product envelope moves—high ontology cost |
| **Not main axis** | **K5** | Addon validation after K1 products exist |
| **Avoid as sole PoC** | **K6** | Easy to look like generic edge ML |

---

### Setouchi candidates

| ID | Scenario (vendor-agnostic) | Raw that stays | Shareable product (summary) | A1 | A2 | A3 | Link load | Notes |
|----|----------------------------|----------------|-----------------------------|----|----|----|-----------|-------|
| **S1** | **Machinery / shaft vibration event** — detect onboard; shore Pull when linked | High-rate samples | Event class + confidence + vessel / sensor DID + coarse ops context + policyRef | S | S | S | S | Default maritime best. Bandwidth story is obvious. |
| **S2** | **Store-and-forward alert queue** — offline buffer; flush on link | Same raw as S1 | Same product; **queue depth / freshness** in provenance | S | S | S | S | Make intermittent links the demo *feature*—not an excuse. |
| **S3** | **Bridge / CCTV incident summary** — video does not leave by default | Video | Incident type + time window + camera id + policy; pointer local | S | S | M | S | Strong A1 and privacy; confirm a shore consumer exists. |
| **S4** | **Environment / bilge / tank threshold events** | Dense sensor logs | Threshold event + meaning + vessel id | M | M | M | M | Easy hardware; weak “why not MQTT dashboard?” without a real ODS consumer. |
| **S5** | **Cross-org partner (yard / insurance / charter) Pull** — S1 product to an explicit second org | Same as S1 | Product + stricter terms | S | S | S | M | Maximizes A3; depends more on partner willingness than tech. |
| **S6** | **Dense NMEA shore mirror** | — | — | W | W | W | W | **Anti-candidate.** Looks like telemetry Push; thesis failure. |

**Setouchi recommended shortlist**

| Priority | Pick | Why advantage shows |
|----------|------|---------------------|
| **1st** | **S1 + S2** | Vibration event + store-and-forward covers A1–A3 + link load at once |
| **Alternate** | **S3** | When stakeholders lead with camera / privacy |
| **Amplifier** | **S5** | When a second org can Pull—turns the PoC into a data-space story |
| **Weak alone** | **S4** | Only with a required ODS consumer agent |
| **Reject** | **S6** | Contradicts raw non-egress |

---

### Combinations where “one Ratio, two domains” shows best

| Pair | Narrative | Advantage in one line |
|------|-----------|----------------------|
| **K1 → S1/S2** | Factory anomaly product, then same envelope + queue onboard | “Same shareable-product path; what changes is physics and link policy, not the substrate.” |
| **K2 → S3** | Vision-centric; raw video does not leave | “Camera IP stays; only incident / quality meaning rides ODS.” |
| **K3 → S5** | Traceability + cross-org Pull | Strong policy / ODS narrative; high coordination cost |

**Shortlist locked:** **K1**, then **S1+S2**. Lock the product JSON-LD envelope, core SHACL shapes, and ODS handoff—not robot brands or class societies (stubs OK).

---

### “Good candidate” questions in partner conversations

For each proposed cell / vessel, ask:

1. What raw is painful / expensive to ship?  
2. Who outside needs meaning and will Pull via ODS (lab consumers OK)?  
3. Can we proceed 90 days on stub TD + recorded raw even if access slips?  

If (2) is “local SCADA screen only,” Ratio’s advantage will not show—pick another candidate.

---

## Shared vs site-specific

| Shared (build once) | Site-specific (config / shapes) |
|---------------------|---------------------------------|
| Raw vs product split pipeline | Device TDs, ontology vocab, SHACL shapes |
| JSON-LD product envelope | Policy refs and allowed physicalContext fields |
| Oxigraph validation hooks | Existing inference / task IDs |
| ODS SDK handoff | Identity (vessel vs factory-cell DID) |
| Local store (DuckDB / files / …) | Retention and pointer policy |

---

## Order

| Order | Site | Why first |
|-------|------|-----------|
| **1** | **Kitakyushu** | Continuous links ease ODS SDK bring-up; multi-vendor robot / SI narrative is clear |
| **2** | **Setouchi** | Same pipeline under intermittent egress—proves the constrained-link side of the thesis |

Do not fork the architecture into two. Prove Kitakyushu end-to-end; load maritime shapes and store-and-forward onto the same binary / config for Setouchi.

---

## reuse vs build (both sites)

| Capability | Reuse | Build (Ratio) |
|------------|-------|---------------|
| Graph / SHACL | Oxigraph | Shapes and validation timing |
| Local raw / product store | DuckDB / LanceDB / files / SQLite | Split rules + pointer policy |
| ODS participation O1–O6 | IPA ODS Middleware / SDK | Product packaging at handoff |
| Device access | Existing WoT / IIoT GW or stubs | Thin TD consume only |
| Inference runtime | ONNX Runtime / vendor | Optional; PoC may stub judgments |

---

## Locked decisions

| Item | Decision |
|------|----------|
| Shortlist | **K1 → S1+S2** (locked) |
| Vendor / cell / vessel | TBD (proceed with stubs + recorded / synthetic raw) |
| Shared envelope | [`PRODUCT_ENVELOPE.md`](PRODUCT_ENVELOPE.md) and `schemas/` · `examples/` |

---

## Open (lock next)

1. Include an external consumer agent in PoC success? (recommended for A3)  
2. Production ODS context / catalog URIs  
3. Concrete vendor / cell / vessel (do not block envelope / pipeline)
