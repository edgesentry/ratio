# ODS dependency: purpose and compliance requirements

> Japanese: [ODS_COMPLIANCE.ja.md](ODS_COMPLIANCE.ja.md)

Extracts the parts of the thesis **participate in ODS without shipping raw quanta** that depend on IPA Open Data Spaces (ODS), as distinct from on-site derivation or W3C-only concerns.  
The thesis wording is a **Ratio operational definition**, not a quotation from ODS-RAM. ODS-dependent elements follow.

Related: [`DISCUSSION.md`](DISCUSSION.md) · [`SCOPE.md`](SCOPE.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

## 1. Sentences under analysis

> A physical domain **participates in ODS** when, as an on-site domain owner, it becomes an **authenticated node** and provides **discoverable, Pull-able products** (result + meaning + terms of use) via the **official ODS stack**.  
> **Not shipping raw quanta** means that, on the **default participation path**, **raw payload bytes** such as sensor video or waveforms are **not copied or distributed outside the domain**. What leaves is only the **shareable product** derived on site.

| Fragment | ODS-dependent? | Notes |
|----------|----------------|-------|
| Physical / on-site domain owner | No (general concept); role name “domain owner” aligns with ODS / data-mesh vocabulary | Edge reality + ODS role mapping |
| Authenticated **node** | **Yes** | Identity & Trust (ODP L3) |
| **Discoverable** products | **Yes** | Discovery and Search / Metadata Exchange (ODP L4) |
| **Pull-able** provision | **Yes** (ODS / data-mesh posture vs central Push) | Provision via ODS participation—not “upload everything” |
| Product = result + **meaning** + **terms** | **Yes** (DPQM: Data Product ↔ Ontology Product; usage control) | Meaning ≈ Ontology Product concern; terms ≈ policy / contract |
| Via **official ODS stack** | **Yes** | ODS-RAM + ODP + Middleware / SDK—do not reimplement |
| Raw payloads stay in-domain by default | **Partial** | Aligns with ODS “distributed / domain custody”; **default raw non-egress** is Ratio’s edge policy |
| Only derived shareable products egress | **Partial** | Shape must be ODS-ready; **what** is derived on site is Ratio |

---

## 2. Purpose (why align with ODS)

| ID | Purpose | Meaning for Ratio readers |
|----|---------|---------------------------|
| P1 | **Cross-organization interoperability** without a single central lake | Partners / Agentic AI consume governed products—not mirrors of OT stores |
| P2 | Treat **data and context as a pair** (DPQM) | Opaque scores are insufficient; Ontology Product–grade meaning is required |
| P3 | Prefer **Pull / provision** over central Push | Matches on-site secrecy, bandwidth, and domain ownership |
| P4 | Reuse **normative protocols and reference implementations** | Avoid a private “data-space dialect”; use ODP + official Middleware / SDK |
| P5 | Supply trustworthy **Context for Agentic AI** | Transparency for consumers + control for domain owners |

Non-goals for “ODS compliance” in Ratio:

- Replacing ODS Middleware with a proprietary protocol stack
- Claiming full ODS-RAM coverage on day one (start from the minimal participation path)
- Equating “edge inference product = ODS” when the node does not speak the ODP roles above

### Benefits from the ODS side (when Ratio supplies)

| Benefit | Detail |
|---------|--------|
| Real-data supply ports | OT domains that cannot feed a lake can join as Pull providers |
| Context quality | Ontology-backed, validatable products (less GIGO than scores alone) |
| DPQM realized on site | Data/context pairs separate at the point of origin |
| Governance | Terms-bound exchange (not predicated on unauthorized raw mirrors) |
| Reach of standards | Official stack extends to physical domains |

### What Ratio alone cannot cover

**Already supported by official ODS (connect and reuse):** L3 identity, L2 transfer, L4 Discovery / metadata, usage-control / contracting substrate, L1 trust / quality procedures, ops / monitoring / onboarding.

**Outside the official stack (others / Ratio’s role):** on-site product derivation and raw split (→ **Ratio**), consumer apps / Agentic AI, domain vocabulary agreement, device SI, legal / safety liability.

Full narrative: [`DISCUSSION.md`](DISCUSSION.md#4-benefits-on-the-ods-side) · Canonical scope: [`SCOPE.md`](SCOPE.md) · Connection: [`ODS_HANDOFF.md`](ODS_HANDOFF.md)

---

## 3. ODS compliance requirements (participation path)

Split into **required (MVP participation)** / **recommended (provider maturity)** / **Ratio-owned prerequisites** (needed so ODS participation does not force raw egress).

### 3.1 Required — MVP “I am an ODS participant (provider)”

| ID | Requirement | ODS anchor | How to comply |
|----|-------------|------------|---------------|
| O1 | A **domain-owned participant / node** with interoperable **identity & trust** | ODP Identity and Trust (L3); ODS-RAM trust | Official Middleware / SDK bindings; store credentials locally (e.g. SQLite)—do not invent a parallel IdP protocol |
| O2 | **Register / exchange metadata** so offerings can be described | ODP Metadata Exchange (L4) | Primary offering metadata is for shareable products—not raw files as the main offer |
| O3 | **Discovery / search** so consumers can find offerings | ODP Discovery and Search (L4) | Catalogs point at governed products |
| O4 | ODS-aligned **transactional access** (serve when permitted) | ODP Transaction (L2) | Pull / serve shareable products via Middleware / SDK |
| O5 | **DPQM**-aligned products (data concern + ontology / context concern as a pair) | ODS-RAM Architecture / DPQM | Site emits result **and** meaning (JSON-LD / RDF + shapes)—not score-only blobs |
| O6 | Implement on an **ODP-conformant stack** (reference Middleware / SDK recommended) | ODP; onboarding; GitHub `open-dataspaces` | **Compose**. Do not reimplement ODP |

### 3.2 Recommended — provider maturity

| ID | Requirement | ODS anchor |
|----|-------------|------------|
| O7 | **Data trust / reliability / quality** signals on offerings | ODP L1 assessment protocols |
| O8 | **Usage control / contracting** along ODS perspectives (who, for what) | ODS-RAM perspectives; applicable ODP Heuristic Contracting (P1) |
| O9 | Deployment-appropriate ops basics: logging / monitoring / notifier | ODP Common Functionalities |
| O10 | Follow official developer / user guides for onboarding and ops | Introductory guides |

### 3.3 Ratio-owned prerequisites (not ODS protocol requirements, but needed on site to preserve P3 / P1)

| ID | Requirement | Rationale |
|----|-------------|-----------|
| R1 | **Default non-egress** of raw payload bytes | Domain custody; bandwidth / secrecy; ODS Pulls *products*, not lake mirrors |
| R2 | On-site **shareable-product derivation** (result + context + policy ref + optional in-domain pointer) | An ODS-valid object must exist before register / serve without shipping raw |
| R3 | **SHACL (or equivalent) validation** before publish / action when claimed | Trustworthy products; works with W3C tooling (Oxigraph)—supports O5 / O7 |
| R4 | Clear handoff boundary into the ODS stack (no private ODP fork) | Protects O6 |

---

## 4. Traceability: slogan → ODS vs Ratio

```
Authenticated node          → O1          (ODS)
Discoverable                → O2, O3      (ODS)
Pull-able products          → O4, P3      (ODS)
Result + meaning + terms    → O5, O7–O8   (ODS) + R2–R3 (Ratio prepare)
Official ODS stack          → O6, O10     (ODS)
Raw not shipped by default  → R1          (Ratio policy; compatible with ODS custody)
```

---

## 5. External references

### IPA / Open Data Spaces (primary)

| Resource | URL |
|----------|-----|
| ODS home (IPA) | https://www.ipa.go.jp/en/digital/opendataspaces/ |
| ODS docs hub (GitBook) | https://open-dataspaces.gitbook.io/ods-docs/ |
| Docs index (`llms.txt`) | https://open-dataspaces.gitbook.io/ods-docs/llms.txt |
| ODS-RAM V2 | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/v2 |
| ODS-RAM — Architecture (DPQM) | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/02-architecture |
| ODS-RAM — Layers | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/03-layers |
| ODS-RAM — Perspectives | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/04-perspectives |
| ODS-RAM — Protocols | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/05-protocols |
| ODS-RAM — Onboarding & ops | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/06-onboarding |
| ODP overview | https://open-dataspaces.gitbook.io/ods-docs/odp/overview |
| ODP V1 | https://open-dataspaces.gitbook.io/ods-docs/odp/v1 |
| ODP — Identity and Trust (L3) | https://open-dataspaces.gitbook.io/ods-docs/odp/fundamental-protocols/identity-and-trust-l3 |
| ODP — Metadata Exchange (L4) | https://open-dataspaces.gitbook.io/ods-docs/odp/fundamental-protocols/metadata-exchange-l4 |
| ODP — Discovery and Search (L4) | https://open-dataspaces.gitbook.io/ods-docs/odp/fundamental-protocols/discovery-and-search-l4 |
| ODP — Transaction (L2) | https://open-dataspaces.gitbook.io/ods-docs/odp/fundamental-protocols/transaction-l2 |
| Introductory guide for users | https://open-dataspaces.gitbook.io/ods-docs/introductory-guide/open-data-spaces-introductory-guidebook-for-users |
| Introductory guide for developers | https://open-dataspaces.gitbook.io/ods-docs/developer-guide/developer-guide |
| Design philosophy (Why Open Dataspaces) | https://www.ipa.go.jp/en/digital/architecture-guidelines/open-dataspaces-design-philosophy.html |
| Design philosophy PDF (EN) | https://www.ipa.go.jp/en/digital/architecture-guidelines/individual-link/p1o1lf000001xv4n-att/WhyOpenDataspaces_en.pdf |
| Deliverables press release (2026-04-01) | https://www.ipa.go.jp/en/pressrelease/press20260401.html |
| GitHub org (Middleware / SDK) | https://github.com/open-dataspaces |

### W3C (product meaning / identity / policy side)

| Resource | URL |
|----------|-----|
| JSON-LD 1.1 | https://www.w3.org/TR/json-ld11/ |
| RDF 1.2 concepts (or current RDF TR) | https://www.w3.org/TR/rdf12-concepts/ |
| SHACL | https://www.w3.org/TR/shacl/ |
| Web of Things (WoT) Thing Description | https://www.w3.org/TR/wot-thing-description/ |
| DID Core | https://www.w3.org/TR/did-core/ |
| Verifiable Credentials | https://www.w3.org/TR/vc-data-model-2.0/ |
| ODRL | https://www.w3.org/TR/odrl-model/ |

---

## 6. Maintenance

When ODS-RAM or ODP revisions rename layers / protocols, update **§3 requirement anchors** and **§5 URLs** first. Keep Ratio’s edge policy (R1–R4) separate so compliance drift does not silently rewrite “do not ship raw.”
