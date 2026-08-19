# Ratio scope

> Japanese: [SCOPE.ja.md](SCOPE.ja.md)

Lock three tiers: **① official ODS** → **② Ratio** → **③ out of scope (who builds it)**.

Related: [`DISCUSSION.md`](DISCUSSION.md) · [`ODS_COMPLIANCE.md`](ODS_COMPLIANCE.md) · [`ODS_HANDOFF.md`](ODS_HANDOFF.md) · [`LAYOUT.md`](LAYOUT.md)

---

## In one sentence

> **Official ODS** owns data-space participation (auth, transfer, discovery, contracting substrate).  
> **Ratio** derives and validates shareable products on site, separates raw data, and hands off to the official stack.  
> **Everything else** (thick vocabulary agreement, deep SI, consumer apps, safety liability) belongs to domain / SI / users / regulators.

```
[ OT site ] --(thin TD consume)--> [ Ratio: derive · SHACL · split · handoff ]
                                      │ shareable product only
                                      ▼
                               [ Official ODS: L3 / L2 / L4 / … ]
                                      │ Pull
                                      ▼
                               [ Consumer app / Agentic AI ]  ← outside Ratio
```

---

## ① Official ODS (reuse and connect; Ratio does not reimplement)

| Area | Content | Official home |
|------|---------|---------------|
| Identity | Node / operator auth, tokens | L3, `SDK-client-library-python`, `SDK-docker-compose` |
| Transfer / transaction | Pull / API transfer when permitted | L2 Web API Transfer |
| Discovery / metadata | Catalog, Discovery, metadata exchange | L4 Discovery / Metadata |
| Usage control / contracting substrate | Who, for what purpose | ODS-RAM perspectives, ODP complements, L3-PAP, etc. |
| Trust / quality procedures | Assessment protocols | ODP L1 family |
| Ops / monitoring / onboarding | Logging, guides, Compose / Helm | Middleware common functions, official guides |

Compliance mapping: [`ODS_COMPLIANCE.md`](ODS_COMPLIANCE.md) (O1–O10).  
Connection: [`ODS_HANDOFF.md`](ODS_HANDOFF.md).  
PoC reuse vs build inventory: [`POC.md`](POC.md#reuse-vs-build-both-verticals) (RB1–RB11).

`ratio-serve` is **not** a substitute for the official stack (stand-in industry API upstream of L2).

---

## ② Ratio scope (the “point-of-origin glue” the official stack does not provide)

Pipeline: **thin ingest → derive / validate → split raw data vs product → handoff to official**.

| In scope | Out of scope (easy to misread) |
|----------|--------------------------------|
| Shareable-product envelope (result + ontology context + terms) | Making raw data the primary ODS offering |
| Minimal `@context` / shared SHACL (products must be validatable) | Industry-consortium ontology standardization itself |
| **Thin** PoC / site shapes and result codes (shipped as config) | Becoming “the sole authority on vocabulary” |
| **Thin** WoT TD consume, stub TDs, pipeline on recorded / synthetic raw data | Universal OT multi-protocol gateway product |
| Local raw-data custody guidance and `local://` pointer policy | Hard real-time control plane |
| Validation orchestration via Oxigraph and other OSS | Reimplementing ODP / L2 / L3 / L4 |
| Handoff to official stack (or temporary industry URL) | Consumer business UI / production Agentic products |

### Vocabulary · TD · consumers (2 / 3 / 4)

| # | Area | Ratio | Notes |
|---|------|-------|-------|
| **2** | Vocabulary / SHACL | **Minimal only** | Envelope + shared SHACL + PoC shapes are Ratio. Industry agreement and large vocab governance are out |
| **3** | WoT TD / ingest | **Thin layer only** | TD consume, stubs, one-line adapters are Ratio. Deep vendor SI is out |
| **4** | Reference Pull consumer | **Not in the core** | Sample: `ratio-pull` ([`samples/`](../samples/)). Production apps stay out. Not a Ratio core duty |

---

## ③ Out of scope — who should build it

| Area | Who builds | Notes |
|------|------------|-------|
| **Production connect & ops** for L2 / L3 / L4 / contract / trust / ops | Domain owner + (if needed) DSSP / integrator deploying **official ODS** | Ratio is the client / upstream product side |
| **Industry ontology / vocabulary agreement** | Consortia, SDOs, domain owners | May use official SAMM / SDK for semantics. Ratio **consumes** the result |
| **Deep device SI** (all fieldbuses, safety PLC integration, etc.) | SI, control vendors, existing IIoT / WoT gateways | Ratio receives TD streams |
| **Consumer business apps / production Agentic AI** | Partners, user enterprises, upstream AI platforms | The Pull-and-operate side. Reference demos prefer separate repo / binary |
| **Legal certification / safety liability / hard RT** | Regulators, control vendors, domain owners | Outside data-space specs (or separate regimes) |
| **Reference Pull client (optional)** | Ratio team or community as a **separate artifact** | Sample: `ratio-pull`. Do not fold into Ratio core |

---

## Responsibility split (quick view)

| Layer | Owner |
|-------|-------|
| Devices / control | Vendors · SI · domain owner |
| Thin TD → product derive · split · validate · handoff | **Ratio** |
| Auth · transfer · discovery · contracting substrate · ops | **Official ODS** |
| Post-Pull business / agents | **User apps** |
| Social agreement on vocabulary | **Domain / consortium** |

---

## Non-goals (restated)

- Full middlewareization as “extend ODS to the edge”  
- Forking ODP / Middleware  
- Calling score-only blobs “ODS participation”  
- Replacing safety PLCs / hard RT  
