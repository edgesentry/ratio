# ODS handoff

> Japanese: [ODS_HANDOFF.ja.md](ODS_HANDOFF.ja.md)

Ratio does not reimplement ODP / Middleware. It hands only shareable products to the **provider industry API** expected by the official stack.

## ODS authentication and authorization (summary)

> Japanese: [認証・認可（概要）](ODS_HANDOFF.ja.md#odsの認証認可概要) · Full requirements: [`ODS_COMPLIANCE.md` §4](ODS_COMPLIANCE.md#4-authentication-and-authorization-client-requirements)

Participating **clients** must satisfy the official stack—not Ratio:

1. **Authenticate (L3):** register operator → `client_credentials` client → JWT with `operator_id`.
2. **Authorize (L2):** when AuthZEN is on, **OpenFGA** (ReBAC policy engine / **PDP** in the official SDK; [ODS_COMPLIANCE §4.1](ODS_COMPLIANCE.md#4-authentication-and-authorization-client-requirements)) must grant the operator on `/products/**`; Pull uses **L2** with Bearer JWT + **L2** API-Key (not L3 key).
3. **Provider (Ratio):** POST shareable products to industry API only; no JWT or AuthZEN logic on site.

Operational steps below; AuthZEN setup in [§7](#7-authzen-operator_id).

## Official components (external)

| Resource | URL |
|----------|-----|
| SDK Docker Compose (L2/L3, etc.) | https://github.com/open-dataspaces/SDK-docker-compose |
| Python client (L3 / Payment OpenAPI generation) | https://github.com/open-dataspaces/SDK-client-library-python |
| L2 Web API transfer | https://github.com/open-dataspaces/L2-dp-webapi |
| L3 Identity | https://github.com/open-dataspaces/L3-identity-component |
| Developer guide ch.4 | https://open-dataspaces.gitbook.io/ods-docs/developer-guide/04-deployment-and-configuration |

The Python SDK is mainly for **L3 authentication**, not a direct “publish data product” API. Data exchange follows the guide’s pattern: L2 forwards to industry services.

```
[consumer] --Bearer+API-Key--> [L2 :8090] --forward--> [Ratio industry :8787 /products]
                                                    ↑ raw data (data/raw) is not served
[provider Ratio] --POST products only--> industry (direct http or via L2)
```

## Ratio PoC modes

| Mode | Command | Meaning |
|------|---------|---------|
| `stub` | `uv run ratio-poc --scenario K1` | No network. Receipt only (default) |
| `http` | `uv run ratio-poc --ods http` | POST shareable product to industry URL (does not send raw data) |
| `l2` | `uv run ratio-poc --ods l2` | POST to official L2 gateway (default `http://127.0.0.1:8090`) with L3 Bearer |

`ratio-poc-serve` is **not** a substitute for official ODS (stand-in industry API upstream of L2). ODS-side benefits and what Ratio alone lacks: [`DISCUSSION.md`](DISCUSSION.md#4-benefits-on-the-ods-side).

Local industry stub (stand-in upstream of L2):

```bash
# Terminal A
cd poc && uv run ratio-poc-serve

# Terminal B
cd poc && uv run ratio-poc --scenario K1 --ods http --ods-url http://127.0.0.1:8787
curl -s http://127.0.0.1:8787/products | jq .
```

`ratio-poc-serve` serves only JSON-LD under `data/out` and does not serve `data/raw`.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `RATIO_ODS_URL` | Industry base URL (`http` default `http://127.0.0.1:8787`) |
| `RATIO_ODS_L2_URL` | L2 gateway (`l2` default `http://127.0.0.1:8090`) |
| `RATIO_ODS_L3_URL` | L3 app (token fetch; default `http://localhost:8080`) |
| `RATIO_ODS_API_KEY` | For L3 token fetch (e.g. `API-Key-Sample`) |
| `RATIO_ODS_L2_API_KEY` | L2 `VALID_API_KEYS` (e.g. `2dfd3409-ce01-4451-96fa-7e10c9681422y`) |
| `RATIO_ODS_BEARER` | Hand-placed L3 JWT (takes precedence if set) |
| `RATIO_ODS_CLIENT_ID` / `RATIO_ODS_CLIENT_SECRET` | Auto-fetch via `/auth/token/client` when Bearer unset |
| `RATIO_ODS_USER_ID` | Optional. Sent as `X-ODS-UserId` |
| `RATIO_ODS_FGA_STORE_ID` / `RATIO_ODS_FGA_MODEL_ID` | OpenFGA (for scripts) |
| `RATIO_ODS_OPERATOR_ID` | Grant products permission to an operator |
| `RATIO_ODS_INDUSTRY_URI` | Industry as seen from L2 (default `http://host.docker.internal:8787`) |
| `RATIO_ODS_L2_MGMT_KEY` | For route registration (default `your-secret-management-api-key`) |

## Connecting official SDK-docker-compose (Ratio steps)

The official stack is **not bundled in this repository**. Clone and start it in a separate directory.

### 0. Prerequisites

- Docker / Compose available (see SDK README for machine sizing)
- Ratio industry: `cd poc && uv run ratio-poc-serve` (host `:8787`)
- Helper scripts: [`poc/scripts/ods/`](../poc/scripts/ods/)

### 1. Start the SDK (official README summary)

```bash
# Example: ~/work/open-dataspaces/SDK-docker-compose
git clone https://github.com/open-dataspaces/SDK-docker-compose.git
cd SDK-docker-compose
git clone --branch=v1.0.0 --depth=1 https://github.com/open-dataspaces/L2-dp-webapi.git
git clone --branch=v1.0.0 --depth=1 https://github.com/open-dataspaces/L3-identity-component.git
git clone --branch=v1.0.0 --depth=1 https://github.com/open-dataspaces/DCS-Payment.git

docker network create shared-network-ods
cd setup && bash setup_l3.sh && cd ..
docker compose -f l3/docker-compose.yml up -d
cd setup && bash setup_l2.sh && cd ..
docker compose up -d
```

For details, operator registration, and token lifetime extension, follow the official [SDK-docker-compose README](https://github.com/open-dataspaces/SDK-docker-compose) and [L3 tutorial](https://github.com/open-dataspaces/L3-identity-component/blob/v1.0.0/docs/tutorials/tutorials.md).

### 2. OpenFGA: authorize Ratio `/products`

Export `FGA_STORE_ID` / `FGA_MODEL_ID` from `l2/docker-compose.yml`.

```bash
export RATIO_ODS_FGA_STORE_ID=…   # l2/docker-compose.yml
export RATIO_ODS_FGA_MODEL_ID=…   # same
export RATIO_ODS_OPERATOR_ID=…    # operator_id from operator registration

cd /path/to/ratio
bash poc/scripts/ods/register-openfga-products.sh
```

### 3. L2 route: `/products/**` → Ratio industry

```bash
# On Mac/Windows Docker Desktop, default host.docker.internal works
export RATIO_ODS_INDUSTRY_URI=http://host.docker.internal:8787
bash poc/scripts/ods/register-ratio-routes.sh
```

On Linux, if `host.docker.internal` is missing, add `extra_hosts` in compose or set `RATIO_ODS_INDUSTRY_URI` to the host IP.

### 4. L3 token

```bash
export RATIO_ODS_L3_URL=http://localhost:8080
export RATIO_ODS_API_KEY=API-Key-Sample
export RATIO_ODS_CLIENT_ID=…      # operator client
export RATIO_ODS_CLIENT_SECRET=…

export RATIO_ODS_BEARER="$(bash poc/scripts/ods/fetch-l3-token.sh)"
```

Or set only `CLIENT_ID` / `SECRET` and let `ratio-poc --ods l2` fetch automatically.

### 5. Provider: register a product

```bash
cd poc
# Direct to industry (stub check)
uv run ratio-poc --scenario K1 --ods http --ods-url http://127.0.0.1:8787

# Or via L2 (with authorization)
uv run ratio-poc --scenario K1 --ods l2
```

### 6. Consumer: Pull the shareable product (A3)

Reference agent (`ratio-poc-pull`) is **RB11 Out** — not Ratio core. It uses the same L2 GET pattern as a shore / partner client: products only, refuse raw.

```bash
cd poc

# Against the industry stub (no SDK)
uv run ratio-poc-serve          # already running
uv run ratio-poc --scenario K1 --ods http --ods-url http://127.0.0.1:8787
uv run ratio-poc-pull --via http
uv run ratio-poc-pull --via http k1-<stem>
# Expect: JSON meaning summary; GET /raw/ is not 200; no RATIO_RAW_STUB

# Against official L2 (Bearer + L2 API-Key)
uv run ratio-poc-pull --via l2 k1-<stem>
```

Low-level curl smoke (optional):

```bash
bash poc/scripts/ods/verify-l2-pull.sh
bash poc/scripts/ods/verify-l2-pull.sh k1-<stem>
```

### 7. AuthZEN (`operator_id`)

See [`ODS_COMPLIANCE.md` §4](ODS_COMPLIANCE.md#4-authentication-and-authorization-client-requirements). AuthZEN authorization reads the JWT claim `operator_id`. Production-style path:

```bash
# 1) Register operator + client_credentials client (writes gitignored env)
export RATIO_ODS_SDK_DIR=~/work/open-dataspaces/SDK-docker-compose
export RATIO_ODS_CLIENT_SECRET=…   # system-auth-sample secret from l3/docker-compose.yml
bash poc/scripts/ods/register-operator.sh

# 2) Grant OpenFGA (endpoint tuples + operator membership)
set -a; source poc/scripts/ods/.local/operator.env; set +a
export RATIO_ODS_FGA_STORE_ID=…   # from l2/docker-compose.yml
export RATIO_ODS_FGA_MODEL_ID=…
bash poc/scripts/ods/register-openfga-products.sh

# 3) Enable AuthZEN and re-register /products/** routes
bash poc/scripts/ods/enable-authzen.sh true

# 4) Pull with operator token (JWT includes operator_id)
export RATIO_ODS_BEARER="$(bash poc/scripts/ods/fetch-l3-token.sh)"
cd poc && uv run ratio-poc-pull --via l2 k1-<stem>
# or: bash poc/scripts/ods/verify-l2-pull.sh k1-<stem>
```

Helpers: [`poc/scripts/ods/`](../poc/scripts/ods/). Operator secrets stay in `poc/scripts/ods/.local/` (gitignored).

For connectivity smoke tests **before** operator registration, temporarily setting `AUTHZEN_AUTHORIZATION_ENABLED=false` is acceptable. In production, keep AuthZEN enabled and complete the OpenFGA grant.

### Success criteria

| Check | Expectation |
|-------|-------------|
| `GET L2 /products/...` | JSON-LD shareable product |
| `uv run ratio-poc-pull --via l2 <stem>` | Meaning summary; `raw_in_body: false` |
| Waveform binary / `RATIO_RAW_STUB` in response | **Absent** |
| `GET …/raw` | 404 |
| `data/raw/` | Remains host-local |

### Colima / macOS notes (measured)

- Docker works with a Colima context. Watch port conflicts: OpenFGA playground `3000`→`3005`, MinIO `9000`→`9010`, etc. (when sharing the host with other stacks).
- Official `setup/setup_l3.sh` assumes GNU `grep -P` / gawk. On macOS, apply [`poc/scripts/ods/patch-setup-l3-macos.py`](../poc/scripts/ods/patch-setup-l3-macos.py) before running it.
- L2 API-Key is **`VALID_API_KEYS` in `l2/docker-compose.yml`**, not L3’s `API-Key-Sample`.
- Route path must be `/products/**` (`/products**` yields 404 for individual IDs).
- AuthZEN requires the JWT `operator_id` claim; see §7. Before operator registration, temporary `AUTHZEN_AUTHORIZATION_ENABLED=false` is OK for smoke tests (production: enabled + OpenFGA grant).

Compliance mapping: [`ODS_COMPLIANCE.md`](ODS_COMPLIANCE.md) (O1–O6, R1–R4).
