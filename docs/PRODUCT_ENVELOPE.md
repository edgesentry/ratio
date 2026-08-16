# 共有可能プロダクト封筒（PoC）

**確定ショートリスト:** K1（北九州）→ S1+S2（瀬戸内）。ベンダー未定。録画／合成生でよい。

K／S で **同一封筒**を使う。サイト差は `domain`・語彙・任意の `physicalContext`／`provenance` 項目だけ。

関連: [`POC.md`](POC.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`DISCUSSION.md`](DISCUSSION.md)

スキーマ実体:

| ファイル | 内容 |
|----------|------|
| [`../schemas/shareable-product.context.jsonld`](../schemas/shareable-product.context.jsonld) | 共通 `@context` |
| [`../schemas/shareable-product.shacl.ttl`](../schemas/shareable-product.shacl.ttl) | 最小 SHACL |
| [`../examples/k1-cell-vibration.jsonld`](../examples/k1-cell-vibration.jsonld) | K1 例 |
| [`../examples/s1-engine-vibration.jsonld`](../examples/s1-engine-vibration.jsonld) | S1 例（S2 は同一本文＋キュー来歴） |

---

## 設計方針

1. **結果＋意味＋利用条件**を必須。生バイトは載せない。  
2. `rawDataPointer` は `local://` のみ（公開 URL 禁止を SHACL で拘束）。  
3. ODS 公式 context URL はプレースホルダ可。実接続時に差し替え。  
4. 推論本体はスタブ可（`confidence`／`result` を手で埋めてよい）。

---

## 必須フィールド

| フィールド | 型／形式 | 説明 |
|------------|----------|------|
| `@context` | array | 共通 context＋必要ならドメイン追記 |
| `@type` | array | 必ず `ShareableProduct` を含む |
| `id` | IRI／URN | プロダクトインスタンス ID |
| `sourceDevice` | DID または URN | 観測源デバイス／ノード |
| `timestamp` | xsd:dateTime | 事象時刻（UTC 推奨） |
| `domain` | 列挙 | `kitakyushu_factory` \| `setouchi_maritime` |
| `scenario` | 列挙 | `K1` \| `S1` \| `S2`（拡張時は POC と同期） |
| `inference.task` | string | タスク ID（例: `anomaly_detection`） |
| `inference.result` | string | 機械可読な結果コード |
| `inference.confidence` | 0..1 | 信頼度 |
| `dataGovernance.policyRef` | IRI／URN | 利用条件参照（生は内部のみ等） |

## 推奨フィールド

| フィールド | 説明 |
|------------|------|
| `inference.physicalContext` | 要約のみ（RPM、温度等）。フルトレース禁止 |
| `dataGovernance.rawDataPointer` | ドメイン内ポインタ（`local://…`） |
| `dataGovernance.shaclConforms` | 検証結果ブール（出す場合） |
| `provenance.producedBy` | Ratio ノード／パイプライン ID |
| `provenance.queueDepth` / `firstBufferedAt` | **S2** 用ストア＆フォワード来歴 |

---

## 結果コード（PoC 初期語彙）

サイト横断で短く固定。後でオントロジー IRI に昇格してよい。

| コード | 用途 |
|--------|------|
| `vibration_abnormal` | K1／S1 の振動異常 |
| `vibration_normal` | 正常 |
| `quality_fail` | K1 拡張（任意カメラ） |
| `link_flush` | S2 キューフラッシュ事象の標記（必要なら） |

---

## 検証フロー（PoC）

実装: [`../poc`](../poc)（`uv sync` → `uv run ratio-poc`。手順は [`../poc/README.md`](../poc/README.md)）

```
薄い TD（`examples/td/*.td.json`）→ raw → data/raw/
JSON-LD インスタンス → data/out/
    → rdflib + pyshacl（schemas/shareable-product.shacl.ttl）
    → conforms なら ODS ハンドオフ・スタブ（SDK 未接続）
    → 生ファイルは publish パスに載せない
```

---

## 未決（封筒以外）

- PoC 成功に外部消費者エージェントを含めるか（推奨: 含める）  
- 本番 ODS context／カタログ URI の確定  
- 具体セル／船／ベンダー（スタブで遮断しない）
