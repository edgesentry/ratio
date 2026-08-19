# ODS dependency: purpose and compliance requirements

> Japanese: [ODS_COMPLIANCE.ja.md](ODS_COMPLIANCE.ja.md)

Extracts the parts of the thesis **participate in ODS without shipping raw data** that depend on IPA Open Data Spaces (ODS), as distinct from on-site derivation or W3C-only concerns.  
The thesis wording is a **Ratio operational definition**, not a quotation from ODS-RAM. ODS-dependent elements follow.

Related: [`DISCUSSION.md`](DISCUSSION.md) · [`SCOPE.md`](SCOPE.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`ODS_HANDOFF.md`](ODS_HANDOFF.md)

---

## 1. Sentences under analysis

> A physical domain **participates in ODS** when, as an on-site domain owner, it becomes an **authenticated node** and provides **discoverable, Pull-able products** (result + meaning + terms of use) via the **official ODS stack**.  
> **Not shipping raw data** means that, on the **default participation path**, **raw data (payload bytes)** such as sensor video or waveforms are **not copied or distributed outside the domain**. What leaves is only the **shareable product** derived on site.

| Fragment | ODS-dependent? | Notes |
|----------|----------------|-------|
| Physical / on-site domain owner | No (general concept); role name “domain owner” aligns with ODS / data-mesh vocabulary | Edge reality + ODS role mapping |
| Authenticated **node** | **Yes** | Identity & Trust (ODP L3) |
| **Discoverable** products | **Yes** | Discovery and Search / Metadata Exchange (ODP L4) |
| **Pull-able** provision | **Yes** (ODS / data-mesh posture vs central Push) | Provision via ODS participation—not “upload everything” |
| Product = result + **meaning** + **terms** | **Yes** (DPQM: Data Product ↔ Ontology Product; usage control) | Meaning ≈ Ontology Product concern; terms ≈ policy / contract |
| Via **official ODS stack** | **Yes** | ODS-RAM + ODP + Middleware / SDK—do not reimplement |
| Raw data stay in-domain by default | **Partial** | Aligns with ODS “distributed / domain custody”; **default raw-data non-egress** is Ratio’s edge policy |
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
| Governance | Terms-bound exchange (not predicated on unauthorized raw data mirrors) |
| Reach of standards | Official stack extends to physical domains |

### What Ratio alone cannot cover

**Already supported by official ODS (connect and reuse):** L3 identity, L2 transfer, L4 Discovery / metadata, usage-control / contracting substrate, L1 trust / quality procedures, ops / monitoring / onboarding.

**Outside the official stack (others / Ratio’s role):** on-site product derivation and raw-data split (→ **Ratio**), consumer apps / Agentic AI, domain vocabulary agreement, device SI, legal / safety liability.

Full narrative: [`DISCUSSION.md`](DISCUSSION.md#4-benefits-on-the-ods-side) · Canonical scope: [`SCOPE.md`](SCOPE.md) · Connection: [`ODS_HANDOFF.md`](ODS_HANDOFF.md)

---

## 3. ODS compliance requirements (participation path)

Split into **required (MVP participation)** / **recommended (provider maturity)** / **Ratio-owned prerequisites** (needed so ODS participation does not force raw-data egress).

### 3.1 Required — MVP “I am an ODS participant (provider)”

| ID | Requirement | ODS anchor | How to comply |
|----|-------------|------------|---------------|
| O1 | A **domain-owned participant / node** with interoperable **identity & trust** | ODP Identity and Trust (L3); ODS-RAM trust | Official Middleware / SDK bindings; store credentials locally (e.g. SQLite)—do not invent a parallel IdP protocol |
| O2 | **Register / exchange metadata** so offerings can be described | ODP Metadata Exchange (L4) | What we primarily publish is shareable-product **metadata**—not raw-data files as the main offer |
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
| R1 | **Default non-egress** of raw data (payload bytes) | Domain custody; bandwidth / secrecy; ODS Pulls *products*, not lake mirrors |
| R2 | On-site **shareable-product derivation** (result + context + policy ref + optional in-domain pointer) | An ODS-valid object must exist before register / serve without shipping raw data |
| R3 | **SHACL (or equivalent) validation** before publish / action when claimed | Trustworthy products; works with W3C tooling (Oxigraph)—supports O5 / O7 |
| R4 | Clear handoff boundary into the ODS stack (no private ODP fork) | Protects O6 |

Individual client requirements for **O1** (identity), **O4** (transaction), and **O8** (usage control) on the official SDK path: [§4](#4-authentication-and-authorization-client-requirements).

---

## 4. Authentication and authorization (client requirements)

> Japanese: [§4 ODS の認証・認可](ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件) · Procedures: [`ODS_HANDOFF.md`](ODS_HANDOFF.md) · AuthZEN setup: [§7](ODS_HANDOFF.md#7-authzen-operator_id)

§3 lists **what** must hold (O1, O4, O8). This section details **how participating clients** satisfy authentication and authorization on the official stack. Ratio does not implement L2/L3; clients and operators follow the official SDK.

### 4.1 Two steps: authenticate, then authorize

| Step | ODP layer | Maps to | PoC component |
|------|-----------|---------|---------------|
| **Authentication** | **L3** Identity and Trust | **O1** | L3 + Keycloak → **JWT** (includes `operator_id` for registered operators) |
| **Authorization** | **L2** Transaction (+ usage control) | **O4**, **O8** | L2 gateway (**PEP**) → **AuthZEN** → OpenFGA (**PDP**) |

**OpenFGA** is an open-source authorization engine ([openfga.dev](https://openfga.dev/); CNCF) that stores **relationship-based access control (ReBAC)** policies as tuples—for example, “operator *O* may call endpoint `/products/**`”. In the official ODS SDK Docker stack, OpenFGA is the **PDP** (Policy Decision Point): the L2 gateway asks OpenFGA (via AuthZEN) whether a given operator may access a route, and allows or denies the Pull accordingly. Ratio does not embed OpenFGA; PoC operators register tuples with [`register-openfga-products.sh`](../samples/scripts/ods/register-openfga-products.sh).

**OpenID** and **AuthZEN** are standards **used inside** the official stack—not separate ODS-RAM layer names:

- **L3** uses OpenID-style flows (OAuth 2.0 `client_credentials`, JWT).
- **L2** uses the **OpenID AuthZEN Authorization API** to query OpenFGA when `AUTHZEN_AUTHORIZATION_ENABLED=true`.

### 4.2 O1 — Authentication (L3): client checklist

A consumer (or admin) client that calls L2 must first prove identity via L3:

| ID | Requirement | Notes |
|----|-------------|-------|
| A1 | **Operator registered** on L3 | Organization / participant record (`operator_id` issued) |
| A2 | **OAuth client** with `client_credentials` bound to that operator | Created via L3 `/auth/clients` |
| A3 | **JWT obtained** from L3 token endpoint | `client_id` + `client_secret` + L3 `API-Key` |
| A4 | JWT carries **`operator_id`** | Required when AuthZEN is enabled on L2 |

PoC helpers: [`register-operator.sh`](../samples/scripts/ods/register-operator.sh), [`fetch-l3-token.sh`](../samples/scripts/ods/fetch-l3-token.sh).

### 4.3 O4 / O8 — Authorization (L2 + AuthZEN): client checklist

When AuthZEN is enabled on the L2 gateway, a Pull client must additionally satisfy:

| ID | Requirement | Notes |
|----|-------------|-------|
| Z1 | **OpenFGA grant** for the operator on the L2 endpoint | e.g. `/products/**` tuples (**O8**) |
| Z2 | Call **L2** (not the provider industry API directly for governed Pull) | Official transaction path (**O4**) |
| Z3 | **`Authorization: Bearer <JWT>`** | Token from §4.2 |
| Z4 | **`API-Key: <L2 key>`** | From `VALID_API_KEYS` in L2 compose—**not** the L3 `API-Key-Sample` |
| Z5 | **Tracking headers** as required by L2 | e.g. `X-TrackingId`, `X-ODS-UserId` |

L2 validates the JWT, reads `operator_id`, asks OpenFGA via AuthZEN, and forwards allowed requests to the provider industry API.

PoC helpers: [`register-openfga-products.sh`](../samples/scripts/ods/register-openfga-products.sh), [`enable-authzen.sh`](../samples/scripts/ods/enable-authzen.sh), [`verify-l2-pull.sh`](../samples/scripts/ods/verify-l2-pull.sh), consumer `uv run ratio-pull`.

For **connectivity smoke tests only**, temporarily setting `AUTHZEN_AUTHORIZATION_ENABLED=false` is acceptable. In production, keep AuthZEN enabled and complete OpenFGA grants.

### 4.4 End-to-end flow (PoC)

```
[ Consumer client ]
  1) POST L3 token     client_credentials + L3 API-Key  →  JWT (operator_id)
  2) GET  L2 /products/{id}
        Bearer JWT + L2 API-Key + X-TrackingId + X-ODS-UserId
        L2: validate JWT → AuthZEN/OpenFGA (operator_id × endpoint) → forward
  3) Response: JSON-LD shareable product (no raw data)

[ Provider (Ratio) ]
  POST shareable product → industry API (:8787)
  L2 route /products/** registered upstream
  Does NOT issue JWTs or evaluate AuthZEN; raw data stays local (R1)
```

### 4.5 Requirements by participant role

| Role | Must satisfy | Ratio’s job |
|------|--------------|-------------|
| **Consumer** (Pull) | A1–A4, Z1–Z5 when AuthZEN on; never expect raw data via L2 | Document and script against official stack; do not reimplement L2/L3 |
| **Provider** (Ratio site) | Serve **shareable products** on industry API; L2 route `/products/**` registered | Derive, SHACL, raw-data / product split, handoff (**R2–R4**) |
| **Operator / admin** | Run official SDK; register operators, clients, FGA tuples, routes | PoC helper scripts only |

### 4.6 What Ratio does not do

- Issue or validate JWTs (L3 / Keycloak)
- Evaluate AuthZEN or store ReBAC policies (L2 / OpenFGA)
- Replace ODP Identity and Trust or Transaction layers

**Ratio** supplies ODS-ready **shareable products** at the industry boundary; **ODS** owns authn/authz on the participation path.

---

## 5. Traceability: slogan → ODS vs Ratio

```
Authenticated node          → O1          (ODS)
Discoverable                → O2, O3      (ODS)
Pull-able products          → O4, P3      (ODS)
Result + meaning + terms    → O5, O7–O8   (ODS) + R2–R3 (Ratio prepare)
Official ODS stack          → O6, O10     (ODS)
Raw not shipped by default  → R1          (Ratio policy; compatible with ODS custody)
```

---

## 6. External references

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

### OpenID (L2 authorization API)

| Resource | URL |
|----------|-----|
| OpenID AuthZEN Authorization API 1.0 | https://openid.net/specs/openid-authzen-authorization-api-1_0.html |

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

## 7. Maintenance

When ODS-RAM or ODP revisions rename layers / protocols, update **§3 requirement anchors** and **§6 URLs** first. Keep Ratio’s edge policy (R1–R4) separate so compliance drift does not silently rewrite “do not ship raw data.”
