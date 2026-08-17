# アーキテクチャ

> English: [ARCHITECTURE.md](ARCHITECTURE.md)

テーゼ **生クォンタを出さずに ODS に参加する** の実装スケッチ。

**構築方針:** OSS と公式 ODS SDK を構成する。Ratio は現場での導出・検証・生／プロダクト分離・ハンドオフ境界を所有する。  
参照: [`DISCUSSION.ja.md`](DISCUSSION.ja.md) · [`ODS_COMPLIANCE.ja.md`](ODS_COMPLIANCE.ja.md)

---

## 1. 既定パス（全体像）

```
[ L1 Devices ]
   PLC, cameras, sensors, robots …
        │  W3C WoT / Thing Description
        ▼
[ L2 Derive & validate ]  ← Ratio
   Inference + RDF/JSON-LD context + SHACL
        │  split
        ├──────────────────────────────┐
        ▼                              ▼
[ raw quanta — local custody ]   [ shareable product ]
  files / DuckDB / LanceDB         result + meaning + policyRef
                                   (+ in-domain raw pointer)
        │                              │
        │                              ▼
        │                    [ L3 Handoff / governance ]
        │                      DID·VC · ODRL refs · product package
        │                              │
        │                              ▼
        │                    [ L4 ODS participation ]
        │                      official Middleware / SDK (ODP)
        │                      discover + Pull of shareable product only
        └──── raw does not take this path by default ────┘
```

| 層 | テーゼ上の仕事 |
|----|----------------|
| **L1** | WoT TD で観測；独自デバイススキーマを発明しない |
| **L2** | 意味付き結果を導出；SHACL で検証 |
| **分離** | 生は残す；外に出うるのは共有可能プロダクト |
| **L3** | アイデンティティ・ポリシー参照・来歴をハンドオフ用にパッケージ |
| **L4** | **公式** ODS スタックで参加（O1–O6）— ODP フォークなし |

### 1.1 ODS の認証・認可

> English: [§1.1](ARCHITECTURE.md#11-ods-authentication-and-authorization) · 詳細: [`ODS_COMPLIANCE.ja.md` §4](ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件)

- **L3（認証）:** operator + `client_credentials` → `operator_id` 付き JWT（**O1**）。
- **L2（認可）:** ゲートウェイが JWT 検証、AuthZEN → OpenFGA でエンドポイントアクセス（**O4**、**O8**）。
- **Ratio:** industry API への共有可能プロダクトのみ；現場で JWT／AuthZEN は扱わない（**R1–R4**）。

---

## 2. 論理データフロー

```
WoT ingest → inference (ONNX/TensorRT, etc.)
         → [split]
              ├─ raw → DuckDB / LanceDB / local files (custody)
              └─ shareable product → JSON-LD(+SHACL) → SQLite(policy/state)
                                   → ODS Middleware/SDK (discover + Pull)
         → Arrow Memory Broker ←→ Python / Edge SLM (RAG: LanceDB)
```

---

## 3. 技術スタック配置

| 関心 | 技術 | 所有 |
|------|------|------|
| 薄い構成ランタイム | Rust | **Ratio**（シェルのみ） |
| グラフ推論・検証 | Oxigraph | **OSS** |
| ローカル生／成果物ストア | DuckDB、LanceDB、ファイル | **OSS** |
| 状態・資格・ポリシー記録 | SQLite | **OSS** |
| 言語横断 I/F | Apache Arrow + PyO3 | Arrow は **OSS**；Memory Broker は **Ratio** |
| 推論ランタイム | ONNX Runtime／TensorRT 等 | **OSS**／ベンダー |
| セマンティクス表現 | JSON-LD／CBOR-LD | **標準** |
| ODS 参加 | IPA ODS Middleware／SDK + ODP | **公式**—再実装しない |
| L2 認可（AuthZEN → OpenFGA） | OpenID AuthZEN API + OpenFGA | **公式 ODS SDK**—Ratio はスクリプトで有効化のみ |

---

## 4. 共有可能プロダクトが運ぶもの

**共有可能プロダクト**: Pull 可能なパッケージ。生バイトではない。定義の全文: [`DISCUSSION.ja.md`](DISCUSSION.ja.md)（「共有可能プロダクトとは」）

テーゼ整合（結果＋意味＋利用条件）:

1. **結果** — 判断または観測（生バイトではない）
2. **意味** — オントロジー／JSON-LD 文脈（どのデバイス、どんな特性、何を根拠に）
3. **利用条件** — ポリシー参照（例: ODRL）；生は既定で非egress
4. **任意のドメイン内ポインタ** — ローカル運用用の `rawDataPointer`。公開生 URL ではない

### ペイロード例

PoC 確定封筒・SHACL・K1／S1／S2 例: [`PRODUCT_ENVELOPE.ja.md`](PRODUCT_ENVELOPE.ja.md)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/td/v1",
    "https://open-dataspaces.org/v1/context.jsonld",
    { "manufacturing": "https://schema.org/manufacturing/" }
  ],
  "@type": ["Thing", "EdgeAIInferenceResult"],
  "id": "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "sourceDevice": "did:example:kitakyushu-factory-robot-01",
  "timestamp": "2026-08-16T14:00:00Z",
  "inference": {
    "task": "anomaly_detection",
    "result": "vibration_abnormal",
    "confidence": 0.96,
    "physicalContext": {
      "motorRPM": 1450,
      "temperatureCelsius": 42.5
    }
  },
  "dataGovernance": {
    "policyRef": "urn:odrl:policy:internal-only-rawdata",
    "rawDataPointer": "local://storage/raw_wave_20260816_001.bin"
  }
}
```

---

## 5. コア I/F（議論用スケッチ）

```
┌─────────────┐     PyO3      ┌──────────────────┐
│ Python / SLM│ ◄──────────► │ Ratio Rust Core  │
└─────────────┘   Arrow IPC   │  Oxigraph        │
       ▲                      │  SHACL / SPARQL  │
       │                      │  product package │
       └──── LanceDB / DuckDB / SQLite ──────────┘
                              │
                              ▼
                     ODS Middleware / SDK
```

決めること:

1. プロダクト組立用 Arrow RecordBatch 列（`device_id`、`ts`、`graph_delta`、`shacl_report`、…）
2. バッファ所有権／ゼロコピー境界
3. 連続現場導出のための同期 vs ストリーム

---

## 6. 最初の手順（PoC 順）

テーゼに従う: **保管 → 導出 → 参加**。

1. **取込** — 1デバイス系統の WoT TD；生はローカルストアへ  
2. **分離とプロダクト化** — JSON-LD 共有可能プロダクト＋SHACL；生は公開経路に載せない  
3. **参加** — ODS SDK: **プロダクトのみ** 登録／発見／提供  

PoC サイトは [`DISCUSSION.ja.md`](DISCUSSION.ja.md) の需要条件を満たすこと。  
想定サイトと境界: [`POC.ja.md`](POC.ja.md)（北九州が先、次いで瀬戸内）。

---

## 7. 非目標

- 生を ODS の主オファリングとして出荷すること
- ODP／ODS Middleware の再実装
- 初日からの ODS-RAM 完全カバー（MVP は [`ODS_COMPLIANCE.ja.md`](ODS_COMPLIANCE.ja.md) の O1–O6 経路）
- 独自デバイスプロトコルの乱立（WoT TD に寄せる）
- Oxigraph、DuckDB、LanceDB、SQLite、Arrow のフォーク
- ハードリアルタイム制御平面（せいぜい助言／ゲート）
