# Repository layout

> Japanese: [LAYOUT.ja.md](LAYOUT.ja.md)

Ratio keeps **product** code, **samples**, and **data examples** apart. There is no `poc/` directory.

Related: [`SCOPE.md`](SCOPE.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

## Names

| Layer | Name | Meaning |
|-------|------|---------|
| GitHub repository | **ratio** | The product (Rust + Python + samples) |
| Rust workspace (alias) | **ratio-rs** | The Rust side under `crates/` |
| Crate | **ratio-core** | Split, envelope, queue; `ratio-client` later |
| Product CLI | **`eds ratio …`** | EdgeSentry entry (`eds` in edgesentry-rs). Example: `eds ratio derive` |
| In-repo dev binary | `ratio derive` | `cargo run -p ratio-core --bin ratio`. Not the product command |
| Python module | `ratio_core` | PyO3. Separate from the CLI brand |

---

## At a glance

```
ratio/
  crates/                 Product
    ratio-core/           Rust core (split, envelope, TD, queue). Product CLI is `eds ratio …`
    ratio-py/             Python bindings (PyO3 / Arrow; prototype / SLM)
  samples/                Samples (how to join official ODS; not a product stand-in)
  examples/               Envelope examples (JSON-LD products, thin TDs)
  schemas/                Shared `@context` and SHACL
  docs/                   Thesis, scope, architecture, handoff
  data/                   Runtime raw data / artifacts (gitignored)
```

| Location | Role | Unit tests |
|----------|------|------------|
| `crates/ratio-core` | On-site composition. Raw data does not leave | `cargo test -p ratio-core` |
| `crates/ratio-py` | Same core from Python | `cd crates/ratio-py && uv run pytest` |
| `crates/ratio-client` | (Planned) Rust HTTP handoff of metadata only to industry / L2 | Client unit tests |
| `samples/` | How to run Compose / L2 / industry stub / reference Pull | `cd samples && uv run pytest` (sample health; contracts move into the core over time) |
| `examples/` | Product and TD documents | Read by core `tests/canonical_examples.rs` |
| `docs/POC*.md` | Factory / maritime **validation scenarios** (not a directory name) | — |

---

## Product (`crates/`)

- **ratio-core** — `local://` split, shareable-product assembly, envelope gate, thin TD, S2 queue. Product CLI: **`eds ratio derive`** (in-repo dev: `ratio derive`)
- **ratio-py** — module `ratio_core`. Arrow IPC carries metadata rows only (no waveform bytes)
- **ratio-client** — not created yet. Official L2 / industry HTTP handoff lives here. Do not reimplement ODP

The Python bindings are not a second implementation of the core. They are the prototype / SLM entry to the same Rust.

---

## Samples (`samples/`)

How to **wire** the official ODS stack (L2 / L3 / AuthZEN). Not where the product lives.

- Pipeline CLIs (historical names): `uv run ratio-poc` / `ratio-poc-serve` / `ratio-poc-pull`
- ODS helpers: [`samples/scripts/ods/`](../samples/scripts/ods/)
- Steps: [`ODS_HANDOFF.md`](ODS_HANDOFF.md)

`ratio-poc-serve` is not a substitute for official ODS. `ratio-poc-pull` is RB11 Out (reference consumer).

---

## Examples and schemas

- `examples/td/` — locked device-line thin WoT TDs (`href` is `local://`)
- `examples/*.jsonld` — K1 / S1 / S2 shareable-product examples
- `schemas/` — envelope `@context` and minimal SHACL

---

## Where tests live

| What you are checking | Where |
|-----------------------|--------|
| Raw data never in the product; TD / queue / envelope | `crates/ratio-core` |
| Same contract via bindings | `crates/ratio-py/tests` |
| Industry stub, handoff receipts, reference Pull | `samples/tests` (sample still works) |

CI: Rust workspace → `samples` pytest → `ratio-py` maturin / pytest.

---

## Intentionally absent

- `demo/` — no show-directory
- Production consumer UIs, reimplementation of ODP / L2 / L3, a universal OT gateway
