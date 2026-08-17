# Ratio minimal pipeline (PoC)

> Japanese: [README.ja.md](README.ja.md)

Minimal path to demonstrate the thesis:

```
thin WoT TD (examples/td/*.td.json) → custody raw data in `data/raw` → shareable-product JSON-LD
    → SHACL → ODS / industry handoff (stub | http | l2)
S2: also store in data/queue → flush when the link returns
```

Raw data is **not published**. Only products are candidates to leave. TD `forms.href` values are `local://` (no raw-data egress).

| Scenario | TD |
|----------|-----|
| K1 | [`examples/td/k1-robot.td.json`](../examples/td/k1-robot.td.json) |
| S1 / S2 | [`examples/td/s-engine-vib.td.json`](../examples/td/s-engine-vib.td.json) (same sensor; S2 differs only in queue policy) |

Package management is **uv** (`pyproject.toml` + `uv.lock`).

ODS connection details: [`../docs/ODS_HANDOFF.md`](../docs/ODS_HANDOFF.md)  
L2 route / OpenFGA / L3 token helpers: [`scripts/ods/`](scripts/ods/)

## Setup

```bash
cd poc
uv sync
```

## Run

```bash
cd poc

# Factory K1 (default TD + stub handoff)
uv run ratio-poc --scenario K1

# Swap TD (thin SI)
uv run ratio-poc --scenario K1 --td ../examples/td/k1-robot.td.json

# HTTP to industry stub
uv run ratio-poc-serve          # Terminal A
uv run ratio-poc --scenario K1 --ods http --ods-url http://127.0.0.1:8787

# Official L2 gateway (after SDK-docker-compose is up; Bearer via env or auto-fetch)
uv run ratio-poc --scenario K1 --ods l2
```

### S2 store-and-forward (maritime)

```bash
# Onboard: enqueue even without a link (raw data stays in data/raw)
uv run ratio-poc --scenario S2 --offline
# Or stub (S2 auto-queues and exits)
uv run ratio-poc --scenario S2

# After link returns: flush queue to industry
uv run ratio-poc-serve   # shore / reachable industry
uv run ratio-poc --flush-queue --ods http --ods-url http://127.0.0.1:8787

# When online, try transfer in place (on failure queue remains; exit code 0)
uv run ratio-poc --scenario S2 --ods http --ods-url http://127.0.0.1:8787
```

Artifacts:

- `data/raw/` — raw data (local only)
- `data/out/` — products and receipts
- `data/queue/` — S2 unsent shareable products (no raw data)

## Intentionally excluded

- Real robots / shipboard sensors
- Bundling full `SDK-docker-compose` (start externally; see ODS_HANDOFF.md)
- Arrow / PyO3 / Rust core
