# ODS ハンドオフ

Ratio は ODP／Middleware を再実装しない。共有可能プロダクトだけを、公式スタックが想定する **提供者インダストリ API** へ渡す。

## 公式コンポーネント（外部）

| 資源 | URL |
|------|-----|
| SDK Docker Compose（L2/L3 等） | https://github.com/open-dataspaces/SDK-docker-compose |
| Python クライアント（L3／Payment OpenAPI 生成） | https://github.com/open-dataspaces/SDK-client-library-python |
| L2 Web API 転送 | https://github.com/open-dataspaces/L2-dp-webapi |
| L3 Identity | https://github.com/open-dataspaces/L3-identity-component |
| 開発者ガイド ch.4 | https://open-dataspaces.gitbook.io/ods-docs/developer-guide/04-deployment-and-configuration |

Python SDK が直接「データ製品を publish」するのではなく、主に **L3 認証**向け。データ交換は L2 がインダストリサービスへ転送する形（ガイドの構成図）。

## Ratio PoC のモード

| モード | コマンド | 意味 |
|--------|----------|------|
| `stub` | `uv run ratio-poc --scenario K1` | ネットなし。レシートのみ（既定） |
| `http` | `uv run ratio-poc --ods http` | 共有可能プロダクトを industry URL へ POST（生は送らない） |

`ratio-poc-serve` は **公式 ODS の代替ではない**（L2 上流 industry API の仮置き）。ODS 側メリットと Ratio 単体の不足: [`DISCUSSION.md`](DISCUSSION.md#4-ods-側のメリット)。

ローカル industry スタブ（L2 上流の仮置き）:

```bash
# 端末 A
cd poc && uv run ratio-poc-serve

# 端末 B
cd poc && uv run ratio-poc --scenario K1 --ods http --ods-url http://127.0.0.1:8787
curl -s http://127.0.0.1:8787/products | jq .
```

`ratio-poc-serve` は `data/out` の JSON-LD のみ提供し、`data/raw` は提供しない。

## 環境変数（http）

| 変数 | 用途 |
|------|------|
| `RATIO_ODS_URL` | industry ベース URL（既定 `http://127.0.0.1:8787`） |
| `RATIO_ODS_API_KEY` | ガイド記載の `API-Key` ヘッダ |
| `RATIO_ODS_BEARER` | L3 発行トークン（`Authorization: Bearer …`） |

## 本番 ODS スタック接続（次段）

1. `SDK-docker-compose` で L2／L3／Keycloak 等を起動  
2. ガイドに従い参加者・認可を設定  
3. L2 の転送先を、共有可能プロダクトのみ返す industry API（本スタブまたは本番実装）に向ける  
4. `RATIO_ODS_BEARER` 等を L3 トークンに差し替え、`--ods http` の URL を L2／industry の実際のエンドポイントに変更  
5. 必要なら `SDK-client-library-python` 生成物で L3 トークン取得を自動化  

準拠要件の対応: [`ODS_COMPLIANCE.md`](ODS_COMPLIANCE.md)（O1–O6、R1–R4）。
