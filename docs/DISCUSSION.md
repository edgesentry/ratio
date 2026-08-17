# Discussion framework

> Japanese: [DISCUSSION.ja.md](DISCUSSION.ja.md)

Focus: **participate in ODS without shipping raw data**.

Shared language for the thesis, what Ratio owns vs reuses, and how to validate demand. Intended readers care about W3C, IPA ODS, and keeping raw data on site.

ODS-dependent purpose and compliance: [`ODS_COMPLIANCE.md`](ODS_COMPLIANCE.md)  
Default-path architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)  
Assumed PoC sites (factory / maritime): [`POC.md`](POC.md)  
Shareable-product envelope: [`PRODUCT_ENVELOPE.md`](PRODUCT_ENVELOPE.md)  
ODS handoff: [`ODS_HANDOFF.md`](ODS_HANDOFF.md)  
Canonical scope: [`SCOPE.md`](SCOPE.md)

---

## Thesis (one sentence)

> Physical domains join ODS as Pull providers of governed, ontology-backed **shareable products** derived on site. **The default outward path is those products—not raw observation data.**

This is a **Ratio operational definition**, not a quotation from ODS-RAM.

---

## User goals · what we do with ODS · what we want

Lock three points separately. This is not “convey meaning only and skip ODS.”

### 1. User goals (business intent)

| User | Goal |
|------|------|
| **On-site domain owner** (factory, vessel, etc.) | Share and coordinate site state with partners / upstream systems **without** exporting raw data / know-how |
| **ODS consumer / Agentic AI / partner** | Discover and Pull permitted on-site decision material for operations and inference |
| **Standards implementer** (W3C / ODS) | Connect the above with public standards and the official stack—not a private dialect |

### 2. What this product (Ratio) wants to do with ODS

| Do | Do not |
|----|--------|
| Build **shareable products** on site (result + ontology context + terms) and register / discover / serve them via the **official ODS stack** | Put raw data as the primary ODS offering |
| **Materialize** DPQM concerns (data ↔ context pair) at the point of origin | Reimplement ODP / Middleware yourself |
| Carry product meaning and validation with W3C (JSON-LD / SHACL / WoT / DID · ODRL, etc.) | Call non-standard score-only blobs “ODS participation” |

### 3. What we want as outcomes

| Side | Desired outcome |
|------|-----------------|
| **Site** | Become an **ODS participant (provider)** without breaking secrecy, bandwidth, or intermittent links |
| **External users** | Pull products that answer **which device, what context, what is permitted**—even without raw data—so agents / ops can run |
| **Both** | **Governed interoperability** (transparency + control)—neither lake mirrors nor black-box scores |

In one sentence:

> Users want “on-site collaboration that protects raw data” and “legitimate external use.” Ratio joins ODS by carrying **only shareable products**, so the site gains participation eligibility and outsiders gain usable decision material.

### 4. Benefits on the ODS side

“ODS side” = data-space operators, other participants, and the substrate Agentic AI relies on.

| Benefit | Detail |
|---------|--------|
| **More real-data supply ports** | Factories, vessels, and other OT domains that could not feed a lake can join as Pull providers |
| **Dark / real-data quality** | Ontology-backed, validatable products flow—not scores alone (less GIGO) |
| **DPQM realized on site** | Data/context pairs separate at origin; less distortion from centralizing raw data then attaching meaning |
| **Governance and trust** | Exchange under terms of use; designs need not assume unauthorized raw data exfiltration |
| **Standards reach the field** | ODP / SDK apply beyond IT nodes into physical domains |

For ODS, the main gains are **broader industry / geography coverage of participating nodes** and **supply of Context-bearing real data**.

### 5. What Ratio alone cannot cover

Ratio stops at “make products on site and glue them into the official stack.” It is **not** a full substitute for being an ODS participant.  
Split gaps into **already supported by official ODS** vs **filled outside the official stack (domain / app / agreement)**.

#### 5.1 Already supported by official ODS (Ratio reuses and connects)

| Gap (Ratio does not own) | Req. | Official home |
|--------------------------|------|---------------|
| **L3 identity** (tokens, operator registration, etc.) | O1 | L3 Identity Component, `SDK-docker-compose`, `SDK-client-library-python` |
| **L2 transfer / transaction** | O4 | L2 Web API Transfer (`L2-dp-webapi`) |
| **Catalog / Discovery / metadata** | O2–O3 | L4 Discovery / Metadata (Discovery Service, Finder, etc.) |
| **Usage-control / contracting substrate** | O8 | ODS-RAM perspectives, ODP complements (Heuristic Contracting, etc.), L3-PAP, etc. |
| **Trust / quality assessment procedures** | O7 | ODP L1 assessment protocol family |
| **Ops / monitoring / logging** | O9–O10 | Middleware common functions, logging services, developer / user guide onboarding |

PoC `ratio-poc-serve` is **not** a substitute for the above (stand-in industry API upstream of L2). Production connects to official Compose / L2 / L3 / L4. Steps: [`ODS_HANDOFF.md`](ODS_HANDOFF.md).

#### 5.2 Not covered by official ODS alone / out of range (others own)

| Gap | Why official alone is not enough | Who fills it |
|-----|----------------------------------|--------------|
| **On-site product derivation and raw-data / product split** | ODS is distributed data management + Context layers—not an OT edge derivation engine | **Ratio** (this product’s role) |
| **Consumer apps / Agentic AI itself** | Using Pull’ed products in ops / inference is the user application | Partner apps, upstream AI (e.g. consumer-side agents) |
| **Domain ontology / vocabulary agreement** | Standards provide frames; industry-specific vocab agreement is domain owners’ work | Industry consortia; definition work with SAMM / SDK for semantics |
| **Concrete cell / vessel / vendor connect** | WoT TD etc. provide frames; device I/F and SI are per site | SI, existing IIoT / WoT gateways, domain owner |
| **Legal certification / safety liability (hard RT control, etc.)** | Outside data-space specs (or separate regimes) | Regulators, control vendors, domain owners |

**How to read this:** Many “gaps” are simply **not yet connected to official** (§5.1). What Ratio expands to fill is mainly on-site derivation—not Ratio reimplementing L2 / L3 / L4.

**Canonical scope (official ODS / Ratio / out-of-scope and owners):** [`SCOPE.md`](SCOPE.md)

Compliance IDs (O1–O10) detail: [`ODS_COMPLIANCE.md`](ODS_COMPLIANCE.md).

---

## Positioning

| Frame | Content |
|-------|---------|
| **For whom** | On-site domain owners (factory cells, vessels, robot lines, etc.) and ODS consumers / Agentic AI that want to Pull from them |
| **Problem** | ODS participation collapses into **shipping raw data** or **publishing meaningless scores**, so secrecy, bandwidth, and Pull cannot be satisfied together |
| **How we solve** | Derive and validate **shareable products** on site; keep raw data in-domain; join via the **official ODS stack** (Ratio = that composition layer) |
| **Similar** | Standalone edge AI; IIoT / WoT gateways; IT-side ODS nodes / connectors |
| **Difference** | Not score delivery, not mere protocol translation, not cloud-first ODS. Narrowed to **raw-data non-egress × meaning-bearing ODS participation** |
| **Advantage** | Use official ODP / Middleware / SDK without reimplementing; put standard meaning on products via W3C (JSON-LD / SHACL / WoT, etc.) |
| **Constraints** | No ODP / Middleware forks; OSS by default; no hard real-time control plane; do not become a universal OT multi-protocol GW product |
| **Scope** | Canonical: [`SCOPE.md`](SCOPE.md). Summary: thin ingest → derive / validate → split → official handoff. L2/L3/L4 reimplementation, deep SI, consumer apps, vocab agreement are out |

In one sentence:

> Enable physical domains that cannot ship raw data to join ODS by Pull’ing **only shareable products**. Resembles edge AI, GWs, and IT ODS nodes, but the difference is **raw-data non-egress × official-stack participation**. Do not rebuild control or ODP; keep scope to the product pipeline.

---

## Definitions

### What is a shareable product

A **shareable product** (also: meaning-bearing product) is the **only object** that leaves the domain for ODS by default.

It is not a raw-data file. It is a structured package consumers can interpret and act on:

| Required | Meaning | Example |
|----------|---------|---------|
| **Result** | Content of an observation or judgment | `vibration_abnormal`, confidence `0.96` |
| **Meaning** | Machine-readable context: *which* thing, *what* ontology / properties, *on what basis* | WoT / DID device ID; JSON-LD `@context`; physicalContext (RPM, °C); links to vocabularies |
| **Terms of use** | Who may use it for what | `policyRef` / ODRL-family refs |
| **Provenance / quality** (when claimed) | Why it is trustworthy enough to Pull | Timestamp, SHACL report ref, model / task ID |

**Meaning-bearing** means partners or Agentic AI can answer “what is this about?” without opening raw waveforms / images. Identifiers, vocabularies, and context travel **with** the result (DPQM-aligned: data concern paired with ontology / context concern).

| Is a shareable product | Is not |
|------------------------|--------|
| JSON-LD (etc.) judgment + `@context` + device ID + policyRef | Vocab-free `{ "anomaly": 0.98 }` |
| Validated against claimed SHACL shapes | Undocumented score CSV |
| Discoverable / servable as an ODS offering | `.bin` / video on the same Pull path by default |
| May carry an in-domain `rawDataPointer` | A public URL that downloads raw data by default |

Formal term in this document: **shareable product**. Use “meaning-bearing” only when contrasting opaque scores.

### Glossary

| Term | Meaning here |
|------|----------------|
| **Physical domain** | An OT / on-site domain owner that **generates** observations and may run local inference (factory cell, vessel, robot line)—not a corporate data lake alone. |
| **Raw data** | Payload bytes of physical observations or intermediate artifacts: waveforms, images, video, high-rate samples, proprietary process logs, feature blobs, etc. Held in-domain (files / DuckDB / LanceDB, etc.). |
| **Shareable product** | Above. Pull-able **result + meaning + terms** (+ provenance). **Not raw data**. A field materialization of DPQM Data Product + Ontology Product *concerns*. |
| **Shipping** | Copying / distributing raw data (payload bytes) **outside the domain boundary** as the default data-space participation path. |
| **Participating in ODS** | Membership and product provision via the **official ODS stack** (ODP / Middleware / SDK). Not “upload the factory to the cloud.” |

### What “participate in ODS” means concretely

Via the official ODS stack (Ratio does **not** reimplement ODP):

1. **Become a node** — authenticated identity for domain / node
2. **Publish / register products** — what exists, meaning, and terms are discoverable
3. **Serve via Pull** — deliver permitted content on request (not full Push to a central lake)
4. **Govern use** — who, what, for what purpose (policy / ODRL family, where applicable)

Normative mapping (O1–O6, etc.): [`ODS_COMPLIANCE.md`](ODS_COMPLIANCE.md)

### What “without shipping raw data” means concretely

```
[devices] → raw data → stay on local storage (domain custody)
                ↓
         derive / infer / validate
                ↓
         shareable product (Context + result + provenance + policyRef
                            + optional pointer to local raw data)
                ↓
         ODS (discover + Pull of the shareable product only)
```

| We claim | We do not claim |
|----------|-----------------|
| Raw data are not, by default, objects of data-space participation | Raw data is not processed on site (it is; that is the point) |
| Consumers get meaning-bearing products sufficient to act / decide | Consumers always get bit-identical sensor dumps |
| `rawDataPointer` may exist **in-domain** | That pointer is a public download URL |
| Under a **separately explicit policy**, governed raw-data export may later be allowed | “Do not ship raw data” bans all future bilateral contracts |

### Minimal example

- **Raw data (local only):** `raw_wave_20260816_001.bin`
- **Shareable product (ODS-Pull-able):** device *D* at time *T* reports `vibration_abnormal` @ 0.96, ontology *O*, SHACL *R*, policy `internal-only-rawdata`; raw data at `local://…`
- **Participation:** partner Pulls the product via ODP; without separate permission, the `.bin` never arrives

### Failure modes (outside the thesis)

- Mirroring camera / vibration streams to a central lake “for ODS”
- Publishing opaque scores without ontology / context (`anomaly: 0.98`)
- Putting raw-data files on the same Pull path as metadata without policy separation

---

## Intended readers

| Who | Interest | What Ratio answers |
|-----|----------|-------------------|
| **IPA ODS users** | ODP, DPQM, Pull, Context for Agentic AI | How a physical site provides discoverable products without shipping raw data |
| **W3C practitioners** | WoT, JSON-LD / RDF, SHACL, DID / VC, ODRL | Keep standards first-class in shareable products—not proprietary schemas |
| **Edge / OT owners** | Secrecy, bandwidth, intermittent links | Raw-data custody and on-site derivation before data-space handoff |

---

## Build policy

**Default: OSS and public standards / official ODS SDK.**  
**Build only** derivation, validation, raw data vs shareable product separation, and handoff glue into ODS.

| Prefer to reuse | Build as Ratio |
|-----------------|----------------|
| Oxigraph, DuckDB, LanceDB, SQLite, Arrow | Orchestration: ingest → derive / validate → split → ODS handoff |
| W3C WoT TD, JSON-LD / RDF, SHACL, DID / VC, ODRL | Shareable-product shape + Arrow Memory Broker contract |
| IPA ODS Middleware / SDK, ODP | Packaging at the handoff boundary to satisfy R1–R4 |
| ONNX Runtime / common inference runtimes | Domain PoC wiring (device lines, SHACL shapes) |

---

## When the thesis applies (demand conditions)

Ratio is justified only when **all three** hold:

1. Raw data **must not** leave by default (secrecy / bandwidth / policy), **and**
2. Someone outside the cell / vessel needs **meaning** (a local dashboard alone is not enough), **and**
3. You want **ODS Pull participation** (not one-off file exchange)

If any is missing: a cloud ODS node, plain edge AI, or non-ODS integration may suffice. Ratio is optional.

### Problems that motivate the thesis

| # | Problem | Relation to thesis |
|---|---------|-------------------|
| E3 | Bandwidth vs raw-data volume | Shipping raw data is often unrealistic |
| E4 | Secrecy of raw data and know-how | Raw data must not be a data-space object |
| E8 | Semantic gap | Shareable products must carry meaning |
| E2 | Constrained / intermittent links | Meta-only egress is realistic |
| E9 | Node trust | Identity + policy on Pull-able objects |

Out of Ratio scope (this thesis does not solve): hard real-time control (E1), universal OT multi-protocol GW products, appliance SKUs, legal certification, ODP reimplementation or store forks.

### In scope (what Ratio solves)

| Solve | How (reuse first) |
|-------|-------------------|
| Keep raw data local; make **shareable products** Pull-able | Local store + JSON-LD package; publish / serve via ODS SDK |
| Attach **context** to observations / inference | Oxigraph + JSON-LD / RDF; domain shapes as config |
| **Validate** before share (or action) | Oxigraph SHACL; policy / credentials in SQLite |
| Constrained egress | Pointers + policy; do not invent a new transport |
| Thin WoT TD at the boundary | Consume TDs; do not rebuild every fieldbus driver |

---

## Role inside EdgeSentry

- **EdgeSentry** — parent brand for on-site governance & security  
- **Ratio** — semantics / inference core that materializes the thesis (derive / validate shareable products; hand off to ODS)

---

## Why this OSS stack

| Component (OSS) | Thesis role | Why not reinvent |
|-----------------|-------------|------------------|
| **Rust** | Thin composition runtime | Custom code is shell only |
| **Oxigraph** | Meaning + SHACL validation | W3C-native engine |
| **DuckDB / LanceDB / files** | Local custody of raw data / artifacts | Storage is a solved problem |
| **SQLite** | Node state, DID / VC, policy records | Mature ACID |
| **Apache Arrow** | Bridge to Python / SLM | Standard memory format; Broker contract is Ratio |
| **IPA ODS SDK** | Participation (O1–O6) | Official path |

**Single principle:** raw data and heavy compute stay in-domain; **what rides ODS is the shareable product.**

---

## Alternatives that fail the thesis

| Pattern | Why it fails |
|---------|--------------|
| Cloud-centralized AI / lake mirror | Ships raw data (or equivalent) by default |
| Standalone edge AI scores only | No discoverable meaning for ODS consumers |
| Private API labeled “ODS” | Not official-stack participation (O6) |
| Build everything in-house | Drift from ODP / W3C; duplicate Middleware |

---

## Kickoff agenda (60–90 min)

### A. Lock the thesis (15 min)

- Agree raw data vs shareable product definitions for the target vertical
- Confirm demand conditions (all three)

### B. Scope and ownership (15 min)

- Ratio vs EdgeSentry vs ODS SDK / OSS
- Repo boundary: product pipeline only, or WoT collectors too?

### C. PoC verticals (25 min)

Assumed fields: **Factory** (industrial robots / factory OT), **Maritime** (maritime sensors / vessels). Boundary detail: [`POC.md`](POC.md)

| Order | Vertical | Thesis is shown when |
|-------|------|----------------------|
| 1 | Factory | Traceability / quality products are Pull-able; robot raw data stays |
| 2 | Maritime | Same pipeline; meta-only egress under intermittent links |

Lock: one device / sensor line for the first vertical slice in each domain.

### D. Next actions (10 min)

- Three tasks tagged reuse vs build — **locked** in [`POC.md`](POC.md#reuse-vs-build-both-verticals) (pipeline **Build**, SHACL **Build**+engine **Reuse**, ODS SDK **Reuse**)

---

## Weak phrasing → strong phrasing

| Weak | Strong |
|------|--------|
| “Extend ODS to the edge” | “Participate in ODS without shipping raw data” |
| “Our own data space” | “Official ODS Middleware / SDK; Ratio prepares shareable products” |
| “Our own graph DB” | “SHACL / SPARQL via Oxigraph; Ratio orchestrates” |
| “Upload to ODS” | “Register shareable products and serve via Pull” |
| “Metadata only” (ambiguous) | “Shareable product = result + meaning + terms; raw data stays local” |

---

## Definition of success

**Near term (PoC):**

- Ingest one device line; emit a meaning-bearing JSON-LD shareable product
- Raw data stays local; product is discoverable / servable via ODS SDK
- Inventory: each capability → OSS / SDK or Ratio-owned ([`POC.md` reuse vs build](POC.md#reuse-vs-build-both-verticals))

**Medium term:**

- SHACL before publish / action when claimed
- Enforceable policy refs at handoff
- Stable Arrow I/F for Python / SLM
- No parallel reinvention of ODP or stores
