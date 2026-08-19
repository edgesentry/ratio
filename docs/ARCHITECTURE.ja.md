# アーキテクチャ

> English: [ARCHITECTURE.md](ARCHITECTURE.md)

「生データを出さずに ODS に参加する」という主張の実装スケッチ。

**構築方針:** OSS と公式 ODS SDK を構成する。Ratio は現場での導出・検証・生データ／プロダクト分離・引き渡しの境界を所有する。  
参照: [`DISCUSSION.ja.md`](DISCUSSION.ja.md) · [`ODS_COMPLIANCE.ja.md`](ODS_COMPLIANCE.ja.md)

---

## 1. 基本の流れ（全体像）

```
[ L1 デバイス ]
   PLC、カメラ、センサ、ロボット …
        │  W3C WoT / Thing Description
        ▼
[ L2 導出・検証 ]  ← Ratio
   推論 + RDF/JSON-LD 文脈 + SHACL
        │  分離
        ├──────────────────────────────┐
        ▼                              ▼
[ 生データ — ローカル保管 ]     [ 共有可能プロダクト ]
  ファイル / DuckDB / LanceDB     結果 + 意味 + policyRef
                                   （＋ドメイン内の生データポインタ）
        │                              │
        │                              ▼
        │                    [ L3 引き渡し／統治 ]
        │                      DID·VC · ODRL 参照 · プロダクトパッケージ
        │                              │
        │                              ▼
        │                    [ L4 ODS 参加 ]
        │                      公式 Middleware / SDK（ODP）
        │                      共有可能プロダクトのみ発見 + Pull
        └──── 生データは既定でこの経路を通らない ────┘
```

| 層 | 主張における仕事 |
|----|----------------|
| **L1** | WoT TD で観測；独自デバイススキーマを発明しない |
| **L2** | 意味付き結果を導出；SHACL で検証 |
| **分離** | 生データは残す；外に出せるのは共有可能プロダクト |
| **L3** | アイデンティティ・ポリシー参照・作成の記録を引き渡し用にまとめる |
| **L4** | **公式** ODS スタックで参加（O1–O6）— ODP フォークなし |

### 1.1 ODS の認証・認可

> English: [§1.1](ARCHITECTURE.md#11-ods-authentication-and-authorization) · 詳細: [`ODS_COMPLIANCE.ja.md` §4](ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件)

- **L3（認証）:** operator + `client_credentials` → `operator_id` 付き JWT（**O1**）。
- **L2（認可）:** ゲートウェイが JWT 検証、AuthZEN → OpenFGA でエンドポイントアクセス（**O4**、**O8**）。
- **Ratio:** industry API への共有可能プロダクトのみ；現場で JWT／AuthZEN は扱わない（**R1–R4**）。

---

## 2. 論理データフロー

```
WoT 取込 → 推論（ONNX/TensorRT 等）
         → [分離]
              ├─ 生データ → DuckDB / LanceDB / ローカルファイル（保管）
              └─ 共有可能プロダクト → JSON-LD(+SHACL) → SQLite（ポリシー/状態）
                                   → ODS Middleware/SDK（発見 + Pull）
         → Memory Broker（Arrow）←→ Python / Edge SLM（RAG: LanceDB）
```

---

## 3. 技術スタック配置

| 関心 | 技術 | 所有 |
|------|------|------|
| 薄い構成ランタイム | Rust | **Ratio**（シェルのみ） |
| グラフ推論・検証 | Oxigraph | **OSS** |
| ローカル生データ／成果物ストア | DuckDB、LanceDB、ファイル | **OSS** |
| 状態・資格・ポリシー記録 | SQLite | **OSS** |
| 言語横断 I/F | Apache Arrow + PyO3 | Arrow は **OSS**。それを使う Memory Broker の役割は **Ratio** |
| 推論ランタイム | ONNX Runtime／TensorRT 等 | **OSS**／ベンダー |
| セマンティクス表現 | JSON-LD／CBOR-LD | **標準** |
| ODS 参加 | IPA ODS Middleware／SDK + ODP | **公式**—再実装しない |
| L2 認可（AuthZEN → OpenFGA） | OpenID AuthZEN API + OpenFGA | **公式 ODS SDK**—Ratio はスクリプトで有効化のみ |

---

## 4. 共有可能プロダクトが運ぶもの

**共有可能プロダクト**: Pull 可能なパッケージ。生データではない。定義の全文: [`DISCUSSION.ja.md`](DISCUSSION.ja.md)（「共有可能プロダクトとは」）

主張との整合（結果＋意味＋利用条件）:

1. **結果** — 判断または観測（生データではない）
2. **意味** — オントロジー／JSON-LD 文脈（どのデバイス、どんな特性、何を根拠に）
3. **利用条件** — ポリシー参照（例: ODRL）；生データは既定で非egress
4. **任意のドメイン内ポインタ** — ローカル運用用の `rawDataPointer`。公開の生データ URL ではない

### ペイロード例

PoC で確定した書式・SHACL・K1／S1／S2 例: [`PRODUCT_ENVELOPE.ja.md`](PRODUCT_ENVELOPE.ja.md)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/td/v1",
    "https://open-dataspaces.org/v1/context.jsonld",
    { "manufacturing": "https://schema.org/manufacturing/" }
  ],
  "@type": ["Thing", "EdgeAIInferenceResult"],
  "id": "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "sourceDevice": "did:example:factory-robot-01",
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

## 5. コア I/F（v0）

```
┌─────────────┐     PyO3      ┌───────────────────┐
│ Python / SLM│ ◄──────────►  │ Ratio Rust コア    │
└─────────────┘   Arrow IPC   │  分離・プロダクト組立 │
                              │  書式ゲート         │
                              ▼
                     ODS への引き渡しは `poc/`（公式 SDK）
```

実装: [`crates/ratio-core`](../crates/ratio-core)（`ratio derive`）と [`crates/ratio-py`](../crates/ratio-py)（モジュール `ratio_core`）。

v0 Arrow 列: `device_id`、`ts`、`scenario`、`result`、`raw_data_pointer`（`local://`）、`product_json`、`envelope_ok`。波形バイトは列にしない。Oxigraph のフル SHACL は後；いまは書式ゲート（`local://`・必須項目）。

---

## 6. 最初の手順（PoC 順）

主張に従う: **保管 → 導出 → 参加**。

1. **取込** — ロック済みデバイス系統の WoT TD（工場: ロボット振動；海事: シャフト振動）；生データはローカルストアへ  
2. **分離とプロダクト化** — JSON-LD 共有可能プロダクト＋SHACL；生データは公開経路に載せない  
3. **参加** — ODS SDK: **プロダクトのみ** 登録／発見／提供  

PoC 分野は [`DISCUSSION.ja.md`](DISCUSSION.ja.md) の需要条件を満たすこと。  
想定分野と境界: [`POC.ja.md`](POC.ja.md)（工場が先、次いで海事）。

---

## 7. 目標の範囲外

- 生データを ODS で主に提供すること
- ODP／ODS Middleware の再実装
- 初日からの ODS-RAM 完全カバー（MVP は [`ODS_COMPLIANCE.ja.md`](ODS_COMPLIANCE.ja.md) の O1–O6 経路）
- 独自デバイスプロトコルの乱立（WoT TD に寄せる）
- Oxigraph、DuckDB、LanceDB、SQLite、Arrow のフォーク
- ハードリアルタイム制御（せいぜい助言／ゲート）
