# EdgeSentry Ratio

> Japanese: [README.ja.md](README.ja.md)

**An on-site composition layer that lets physical domains join ODS without shipping raw data.**

A subproject under EdgeSentry (parent brand: on-site governance & security).  
Ratio prepares **shareable products** (result + meaning + terms of use) at the edge, keeps **raw data** in-domain, and hands off to the **official ODS stack**. Default is OSS / official SDKs. Custom code is only the orchestration glue.

Shareable-product definition and positioning → [`docs/DISCUSSION.md`](docs/DISCUSSION.md)

| Item | Detail |
|------|--------|
| Name | **Ratio** (Latin *ratio* = reason, inference, rationale) |
| Thesis | Participate in ODS without shipping raw data |
| Role | On-site composition layer that turns a judgment’s rationale into a shareable product and hands it to official ODS |
| Standards | W3C (WoT / JSON-LD / RDF / SHACL / DID·VC / ODRL) × IPA ODS (ODP / DPQM) |
| Policy | Raw data stays in-domain · Pull products · **OSS by default** |

---

## Intended readers

- **IPA ODS** users who want sites as Pull-capable providers without mirroring OT raw data
- **W3C** practitioners putting WoT / JSON-LD / SHACL / DID·VC / ODRL on real devices
- Teams that must **keep raw data local** (secrecy, bandwidth, intermittent links) while joining a data space

**User goals / what we do with ODS / what we want / ODS-side benefits / what Ratio alone cannot cover** → [`docs/DISCUSSION.md`](docs/DISCUSSION.md#user-goals--what-we-do-with-ods--what-we-want)

---

## Elevator pitch (30 seconds)

ODS lets domain owners provide governed Data + Ontology Products via Pull—not dump everything into a lake.  
On physical sites that is hard: joining often collapses into either shipping sensor dumps or publishing meaningless scores.

**Ratio** derives shareable products (context + result + policy) on site, leaves raw data local, and participates via official ODS Middleware / SDK.

---

## Default path

```
[devices] → raw data → local custody
                ↓
         derive / validate (W3C)
                ↓
         shareable product only → ODS (discover + Pull)
```

Thesis, scope, demand conditions → [`docs/DISCUSSION.md`](docs/DISCUSSION.md)  
**Canonical scope (official ODS / Ratio / out-of-scope owners)** → [`docs/SCOPE.md`](docs/SCOPE.md)  
Repository layout → [`docs/LAYOUT.md`](docs/LAYOUT.md)  
PoC verticals (factory / maritime) → [`docs/POC.md`](docs/POC.md)  
Architecture → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)  
ODS purpose and compliance (O1–O6, R1–R4) → [`docs/ODS_COMPLIANCE.md`](docs/ODS_COMPLIANCE.md)  
ODS authn / authz (client requirements) → [`docs/ODS_COMPLIANCE.md` §4](docs/ODS_COMPLIANCE.md#4-authentication-and-authorization-client-requirements) · [`docs/ODS_HANDOFF.md`](docs/ODS_HANDOFF.md#ods-authentication-and-authorization-summary)
Shareable-product envelope (K1 / S1 / S2) → [`docs/PRODUCT_ENVELOPE.md`](docs/PRODUCT_ENVELOPE.md)  
ODS wiring (samples) → [`samples/README.md`](samples/README.md)  
Rust core / Python bindings → [`crates/ratio-core`](crates/ratio-core) · [`crates/ratio-py/README.md`](crates/ratio-py/README.md)  
ODS handoff (shareable-product metadata) → [`docs/ODS_HANDOFF.md`](docs/ODS_HANDOFF.md)

---

## Why this stack

| Question | One-line answer |
|----------|-----------------|
| Why derive on site? | Publishing to ODS without raw-data egress requires a shareable product first |
| Why Oxigraph? | RDF / SPARQL / SHACL for meaning and validation |
| Why DuckDB / LanceDB / files? | Local custody of raw data and derivatives |
| Why SQLite? | Node state, credentials, policy records |
| Why Arrow? | Zero-copy bridge to Python / SLM. Ratio plays the Memory Broker that uses Arrow |
| Why ODS SDK? | Official participation path. Do not reimplement ODP |
| What do we build? | Ingest → derive / validate → split raw data vs product → ODS handoff |

---

## Discussion agenda (kickoff)

1. **Confirm the thesis** — participation without shipping raw data; what is in/out of a shareable product
2. **Scope and ownership** — Ratio vs EdgeSentry vs OSS / ODS SDK
3. **PoC** — industrial robots / factory → maritime sensors / vessels; [`docs/POC.md`](docs/POC.md)

---

## Status

- [x] Document thesis and discussion framework
- [x] PoC verticals (factory → maritime); candidate scenarios in [`docs/POC.md`](docs/POC.md)
- [x] Scenario shortlist locked: **K1 → S1+S2**
- [x] Shareable-product envelope + minimal SHACL ([`docs/PRODUCT_ENVELOPE.md`](docs/PRODUCT_ENVELOPE.md))
- [x] ODS wiring sample ([`samples/`](samples/) — stub TD → raw-data custody → product → SHACL → ODS stub/http)
- [x] ODS / industry handoff ([`docs/ODS_HANDOFF.md`](docs/ODS_HANDOFF.md); official Compose is external)
- [x] S2 store-and-forward (`data/queue` + `--flush-queue`)
- [x] Lock per-vertical device / sensor lines ([`POC.md`](docs/POC.md); K1 robot vibration, S1/S2 shaft vibration; vendor TBD)
- [x] Thin TD files ([`examples/td/`](examples/td/); swappable via `--td`)
- [x] Core I/F v0 (Rust + PyO3 / Arrow; [`crates/ratio-core`](crates/ratio-core), [`crates/ratio-py`](crates/ratio-py))
- [x] Official `SDK-docker-compose` connection steps ([`ODS_HANDOFF.md`](docs/ODS_HANDOFF.md); `--ods l2` + [`samples/scripts/ods/`](samples/scripts/ods/); Compose started externally)
- [x] AuthZEN with `operator_id` ([`ODS_HANDOFF.md` §7](docs/ODS_HANDOFF.md#7-authzen-operator_id); `register-operator.sh` / `enable-authzen.sh`)
- [x] ODS authn/authz and client requirements ([`ODS_COMPLIANCE.md` §4](docs/ODS_COMPLIANCE.md#4-authentication-and-authorization-client-requirements))
- [x] reuse vs build inventory ([`POC.md`](docs/POC.md#reuse-vs-build-both-verticals); RB1–RB11)
- [x] A3 reference Pull consumer ([`ODS_HANDOFF.md` §6](docs/ODS_HANDOFF.md#6-consumer-pull-the-shareable-product-a3); `uv run ratio-pull`; RB11 Out)
