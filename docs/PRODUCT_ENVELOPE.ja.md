# 共有可能プロダクトの書式（PoC）

> English: [PRODUCT_ENVELOPE.md](PRODUCT_ENVELOPE.md)

**確定ショートリスト:** K1（工場）→ S1+S2（海事）。  
**確定デバイス系統:** K1＝セルロボット＋振動波形；S1/S2＝船舶機関シャフト振動（同一 TD）。ベンダー未定。録画／合成の生データでよい。

K／S で **同じ書式**を使う。分野差は `domain`・語彙・任意の `physicalContext`／`provenance` 項目だけ。

関連: [`POC.ja.md`](POC.ja.md) · [`ARCHITECTURE.ja.md`](ARCHITECTURE.ja.md) · [`DISCUSSION.ja.md`](DISCUSSION.ja.md)

スキーマ実体:

| ファイル | 内容 |
|----------|------|
| [`../schemas/shareable-product.context.jsonld`](../schemas/shareable-product.context.jsonld) | 共通 `@context` |
| [`../schemas/shareable-product.shacl.ttl`](../schemas/shareable-product.shacl.ttl) | 最小 SHACL |
| [`../examples/k1-cell-vibration.jsonld`](../examples/k1-cell-vibration.jsonld) | K1 例 |
| [`../examples/s1-engine-vibration.jsonld`](../examples/s1-engine-vibration.jsonld) | S1 例（S2 は同一本文＋キューの記録） |

---

## 設計方針

1. **結果＋意味＋利用条件**を必須。生データは載せない。  
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
| `domain` | 列挙 | `factory` \| `maritime` |
| `scenario` | 列挙 | `K1` \| `S1` \| `S2`（拡張時は POC と同期） |
| `inference.task` | string | タスク ID（例: `anomaly_detection`） |
| `inference.result` | string | 機械可読な結果コード |
| `inference.confidence` | 0..1 | 信頼度 |
| `dataGovernance.policyRef` | IRI／URN | 利用条件参照（生データは内部のみ等） |

## 推奨フィールド

| フィールド | 説明 |
|------------|------|
| `inference.physicalContext` | 要約のみ（RPM、温度等）。フルトレース禁止 |
| `dataGovernance.rawDataPointer` | ドメイン内ポインタ（`local://…`） |
| `dataGovernance.shaclConforms` | 検証結果ブール（出す場合） |
| `provenance.producedBy` | Ratio ノード／パイプライン ID |
| `provenance.queueDepth` / `firstBufferedAt` | **S2** 用ストア＆フォワードの記録 |

---

## 結果コード（PoC 初期語彙）

分野横断で短く固定。後でオントロジー IRI に昇格してよい。

| コード | 用途 |
|--------|------|
| `vibration_abnormal` | K1／S1 の振動異常 |
| `vibration_normal` | 正常 |
| `quality_fail` | K1 拡張（任意カメラ） |
| `link_flush` | S2 キューフラッシュ事象の標記（必要なら） |

---

## 検証フロー（PoC）

実装: [`../samples`](../samples)（`uv sync` → `uv run ratio`。手順は [`../samples/README.ja.md`](../samples/README.ja.md)）

```
薄い TD（`examples/td/*.td.json`）→ 生データ → `data/raw/`
JSON-LD インスタンス → data/out/
    → rdflib + pyshacl（schemas/shareable-product.shacl.ttl）
    → conforms なら ODS への引き渡し（スタブ。SDK 未接続）
    → 生データファイルは publish パスに載せない
```

---

## 未決（書式以外）

- 本番 ODS context／カタログ URI の確定  
- 具体セル／船／ベンダー（スタブで遮断しない）
