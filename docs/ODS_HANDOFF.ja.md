# ODS ハンドオフ

> English: [ODS_HANDOFF.md](ODS_HANDOFF.md)

Ratio は ODP／Middleware を再実装しない。共有可能プロダクトだけを、公式スタックが想定する **提供者インダストリ API** へ渡す。

## ODS の認証・認可（概要）

> English: [Authentication and authorization (summary)](ODS_HANDOFF.md#ods-authentication-and-authorization-summary) · 要件の正本: [`ODS_COMPLIANCE.ja.md` §4](ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件)

参加**クライアント**が公式スタックの要件を満たす（Ratio ではない）:

1. **認証（L3）:** operator 登録 → `client_credentials` クライアント → `operator_id` 付き JWT。
2. **認可（L2）:** AuthZEN 有効時、**OpenFGA**（公式 SDK 内の ReBAC 認可エンジン／**PDP**；[ODS_COMPLIANCE.ja.md §4.1](ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件)）で operator に `/products/**` を付与；Pull は **L2** へ Bearer JWT + **L2** API-Key（L3 キーではない）。
3. **提供者（Ratio）:** 共有可能プロダクトを industry API へ POST のみ；現場で JWT／AuthZEN は扱わない。

以下が運用手順。AuthZEN 設定は [§7](#7-authzenoperator_id)。

## 公式コンポーネント（外部）

| 資源 | URL |
|------|-----|
| SDK Docker Compose（L2/L3 等） | https://github.com/open-dataspaces/SDK-docker-compose |
| Python クライアント（L3／Payment OpenAPI 生成） | https://github.com/open-dataspaces/SDK-client-library-python |
| L2 Web API 転送 | https://github.com/open-dataspaces/L2-dp-webapi |
| L3 Identity | https://github.com/open-dataspaces/L3-identity-component |
| 開発者ガイド ch.4 | https://open-dataspaces.gitbook.io/ods-docs/developer-guide/04-deployment-and-configuration |

Python SDK が直接「データ製品を publish」するのではなく、主に **L3 認証**向け。データ交換は L2 がインダストリサービスへ転送する形（ガイドの構成図）。

```
[消費者] --Bearer+API-Key--> [L2 :8090] --転送--> [Ratio industry :8787 /products]
                                                    ↑ 生 (data/raw) は載せない
[提供者 Ratio] --POST プロダクトのみ--> industry（直接 http または L2 経由）
```

## Ratio PoC のモード

| モード | コマンド | 意味 |
|--------|----------|------|
| `stub` | `uv run ratio-poc --scenario K1` | ネットなし。レシートのみ（既定） |
| `http` | `uv run ratio-poc --ods http` | 共有可能プロダクトを industry URL へ POST（生は送らない） |
| `l2` | `uv run ratio-poc --ods l2` | 公式 L2 ゲートウェイ（既定 `http://127.0.0.1:8090`）へ POST；L3 Bearer 付き |

`ratio-poc-serve` は **公式 ODS の代替ではない**（L2 上流 industry API の仮置き）。ODS 側メリットと Ratio 単体の不足: [`DISCUSSION.ja.md`](DISCUSSION.ja.md#4-ods-側のメリット)。

ローカル industry スタブ（L2 上流の仮置き）:

```bash
# 端末 A
cd poc && uv run ratio-poc-serve

# 端末 B
cd poc && uv run ratio-poc --scenario K1 --ods http --ods-url http://127.0.0.1:8787
curl -s http://127.0.0.1:8787/products | jq .
```

`ratio-poc-serve` は `data/out` の JSON-LD のみ提供し、`data/raw` は提供しない。

## 環境変数

| 変数 | 用途 |
|------|------|
| `RATIO_ODS_URL` | industry ベース URL（`http` 既定 `http://127.0.0.1:8787`） |
| `RATIO_ODS_L2_URL` | L2 ゲートウェイ（`l2` 既定 `http://127.0.0.1:8090`） |
| `RATIO_ODS_L3_URL` | L3 アプリ（トークン取得；既定 `http://localhost:8080`） |
| `RATIO_ODS_API_KEY` | L3 トークン取得用（例: `API-Key-Sample`） |
| `RATIO_ODS_L2_API_KEY` | L2 `VALID_API_KEYS`（例: `2dfd3409-ce01-4451-96fa-7e10c9681422y`） |
| `RATIO_ODS_BEARER` | 手置きの L3 JWT（あれば優先） |
| `RATIO_ODS_CLIENT_ID` / `RATIO_ODS_CLIENT_SECRET` | 未設定の Bearer 時に `/auth/token/client` で自動取得 |
| `RATIO_ODS_USER_ID` | 任意。`X-ODS-UserId` に載せる |
| `RATIO_ODS_FGA_STORE_ID` / `RATIO_ODS_FGA_MODEL_ID` | OpenFGA（スクリプト用） |
| `RATIO_ODS_OPERATOR_ID` | 事業者への products 権限付与用 |
| `RATIO_ODS_INDUSTRY_URI` | L2 から見た industry（既定 `http://host.docker.internal:8787`） |
| `RATIO_ODS_L2_MGMT_KEY` | ルート登録用（既定 `your-secret-management-api-key`） |

## 公式 SDK-docker-compose 接続（Ratio 手順）

公式スタックは **本リポジトリに同梱しない**。別ディレクトリで clone／起動する。

### 0. 前提

- Docker / Compose 利用可（SDK README のマシンスペック目安あり）
- Ratio industry: `cd poc && uv run ratio-poc-serve`（ホスト `:8787`）
- 作業用スクリプト: [`poc/scripts/ods/`](../poc/scripts/ods/)

### 1. SDK 起動（公式 README 要約）

```bash
# 例: ~/work/open-dataspaces/SDK-docker-compose
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

詳細・事業者登録・トークン寿命延長は公式 [SDK-docker-compose README](https://github.com/open-dataspaces/SDK-docker-compose) と [L3 チュートリアル](https://github.com/open-dataspaces/L3-identity-component/blob/v1.0.0/docs/tutorials/tutorials.md) に従う。

### 2. OpenFGA: Ratio `/products` 認可

`l2/docker-compose.yml` の `FGA_STORE_ID` / `FGA_MODEL_ID` を環境へ。

```bash
export RATIO_ODS_FGA_STORE_ID=…   # l2/docker-compose.yml
export RATIO_ODS_FGA_MODEL_ID=…   # 同上
export RATIO_ODS_OPERATOR_ID=…    # 事業者登録で得た operator_id

cd /path/to/ratio
bash poc/scripts/ods/register-openfga-products.sh
```

### 3. L2 ルート: `/products/**` → Ratio industry

```bash
# Mac/Windows Docker Desktop なら既定の host.docker.internal で可
export RATIO_ODS_INDUSTRY_URI=http://host.docker.internal:8787
bash poc/scripts/ods/register-ratio-routes.sh
```

Linux では `host.docker.internal` が無い場合、compose に `extra_hosts` を足すか、ホスト IP を `RATIO_ODS_INDUSTRY_URI` に指定する。

### 4. L3 トークン

```bash
export RATIO_ODS_L3_URL=http://localhost:8080
export RATIO_ODS_API_KEY=API-Key-Sample
export RATIO_ODS_CLIENT_ID=…      # 事業者クライアント
export RATIO_ODS_CLIENT_SECRET=…

export RATIO_ODS_BEARER="$(bash poc/scripts/ods/fetch-l3-token.sh)"
```

または `CLIENT_ID`/`SECRET` だけ設定し、`ratio-poc --ods l2` に自動取得させる。

### 5. 提供者: プロダクト登録

```bash
cd poc
# industry へ直接（スタブ確認）
uv run ratio-poc --scenario K1 --ods http --ods-url http://127.0.0.1:8787

# または L2 経由（認可付き）
uv run ratio-poc --scenario K1 --ods l2
```

### 6. 消費者: L2 Pull 確認

```bash
bash poc/scripts/ods/verify-l2-pull.sh
bash poc/scripts/ods/verify-l2-pull.sh k1-<stem>
# /raw は 404 期待（生は industry も L2 も出さない）
```

### 7. AuthZEN（`operator_id`）

[`ODS_COMPLIANCE.ja.md` §4](ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件) を参照。AuthZEN 認可は JWT クレーム `operator_id` を読む。本番寄りの手順:

```bash
# 1) 事業者＋client_credentials クライアント登録（gitignore の env に書き出し）
export RATIO_ODS_SDK_DIR=~/work/open-dataspaces/SDK-docker-compose
export RATIO_ODS_CLIENT_SECRET=…   # l3/docker-compose.yml の system-auth-sample 秘密
bash poc/scripts/ods/register-operator.sh

# 2) OpenFGA 付与（endpoint タプル＋事業者メンバーシップ）
set -a; source poc/scripts/ods/.local/operator.env; set +a
export RATIO_ODS_FGA_STORE_ID=…   # l2/docker-compose.yml から
export RATIO_ODS_FGA_MODEL_ID=…
bash poc/scripts/ods/register-openfga-products.sh

# 3) AuthZEN 有効化＋ /products/** ルート再登録
bash poc/scripts/ods/enable-authzen.sh true

# 4) 事業者トークンで Pull（JWT に operator_id が載る）
export RATIO_ODS_BEARER="$(bash poc/scripts/ods/fetch-l3-token.sh)"
bash poc/scripts/ods/verify-l2-pull.sh k1-<stem>
```

補助スクリプト: [`poc/scripts/ods/`](../poc/scripts/ods/)。秘密情報は `poc/scripts/ods/.local/`（gitignore）。

事業者登録前の疎通では一時的に `AUTHZEN_AUTHORIZATION_ENABLED=false` も可。本番では有効＋OpenFGA 付与。

### 成功の見方

| 確認 | 期待 |
|------|------|
| `GET L2 /products/...` | JSON-LD の共有可能プロダクト |
| レスポンスに波形バイナリ／`RATIO_RAW_STUB` | **無い** |
| `GET …/raw` | 404 |
| `data/raw/` | ホストローカルのまま |

### Colima / macOS メモ（実測）

- Docker は Colima コンテキストで可。ポート競合に注意: OpenFGA playground `3000`→`3005`、MinIO `9000`→`9010` など（他スタックと共有時）。
- 公式 `setup/setup_l3.sh` は GNU `grep -P` / gawk 前提。macOS では [`poc/scripts/ods/patch-setup-l3-macos.py`](../poc/scripts/ods/patch-setup-l3-macos.py) を当ててから実行。
- L2 の API-Key は L3 の `API-Key-Sample` ではなく **`l2/docker-compose.yml` の `VALID_API_KEYS`**。
- ルート Path は `/products/**`（`/products**` だと個別 ID が 404 になる）。
- AuthZEN は JWT の `operator_id` クレームが必要。事業者登録前の疎通確認では一時的に `AUTHZEN_AUTHORIZATION_ENABLED=false` も可（本番では有効＋OpenFGA 付与）。

準拠要件の対応: [`ODS_COMPLIANCE.ja.md`](ODS_COMPLIANCE.ja.md)（O1–O6、R1–R4）。
