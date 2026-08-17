# ODS 依存: 目的と準拠要件

> English: [ODS_COMPLIANCE.md](ODS_COMPLIANCE.md)

テーゼ **生クォンタを出さずに ODS に参加する** のうち、IPA Open Data Spaces（ODS）に依存する部分を切り出す（現場導出や W3C のみの関心と区別する）。  
テーゼの文言は **Ratio の運用定義**であり ODS-RAM の引用ではない。ODS 依存の要素は以下。

関連: [`DISCUSSION.ja.md`](DISCUSSION.ja.md) · [`SCOPE.ja.md`](SCOPE.ja.md) · [`ARCHITECTURE.ja.md`](ARCHITECTURE.ja.md)

---

## 1. 分析対象の文

> 物理ドメインが **ODS に参加する**とは、現場のドメインオーナーとして **認証されたノード**になり、**発見可能で Pull 可能なプロダクト**（結果＋意味＋利用条件）を **公式 ODS スタック**経由で提供すること。  
> **生クォンタを出さない**とは、その参加の **既定経路**において、センサ映像・波形などの **生ペイロードバイトをドメイン外へコピー／配信しない**こと。外に出るのは現場で導出した **共有可能プロダクト**だけである。

| 断片 | ODS 依存か | 注記 |
|------|------------|------|
| 物理／現場のドメインオーナー | いいえ（一般概念）；役割名「ドメインオーナー」は ODS／データメッシュ語彙と整合 | エッジ現実＋ODS 役割マッピング |
| 認証された **ノード** | **はい** | Identity & Trust（ODP L3） |
| **発見可能**なプロダクト | **はい** | Discovery and Search／Metadata Exchange（ODP L4） |
| **Pull 可能**な提供 | **はい**（ODS／データメッシュの設計姿勢 vs 中央 Push） | ODS 参加経由の提供。「全部アップロード」ではない |
| プロダクト＝結果＋**意味**＋**利用条件** | **はい**（DPQM: Data Product ↔ Ontology Product；利用制御） | 意味 ≈ Ontology Product 関心；利用条件 ≈ ポリシー／契約 |
| **公式 ODS スタック**経由 | **はい** | ODS-RAM＋ODP＋Middleware／SDK—再実装しない |
| 生ペイロードは既定でドメイン内 | **部分的** | ODS の「分散保管／ドメイン保管」と整合；**既定の生非egress**は Ratio のエッジ方針 |
| 導出された共有可能プロダクトのみ egress | **部分的** | 形状は ODS 準備が必要；**何を**現場導出するかは Ratio |

---

## 2. 目的（なぜ ODS に合わせるか）

| ID | 目的 | Ratio 読者にとっての意味 |
|----|------|--------------------------|
| P1 | 単一中央データ湖なしに **組織横断で相互運用** | パートナー／Agentic AI は統治されたプロダクトを消費し、OT ストアのミラーではない |
| P2 | **データと文脈を対**で扱う（DPQM） | 不透明スコアでは不足；Ontology Product 級の意味が必要 |
| P3 | 中央 Push より **Pull／提供**を優先 | 現場の秘匿・帯域・ドメイン所有と一致 |
| P4 | **規範プロトコルと参照実装**を再利用 | 独自「データスペース方言」を避け、ODP＋公式 Middleware／SDK |
| P5 | 信頼できる形で **Agentic AI 向け Context**を供給 | 消費者への透明性＋ドメインオーナーの制御 |

Ratio における「ODS 準拠」の非目標:

- 独自プロトコルスタックで ODS Middleware を置き換えること
- 初日に ODS-RAM 全面カバーを主張すること（最小参加経路から）
- ノードが上記 ODP 役割を話さないまま「エッジ推論製品＝ODS」と同一視すること

### ODS 側から見たメリット（Ratio が供給するとき）

| メリット | 内容 |
|----------|------|
| 実データの供給口 | 湖に出せない OT ドメインが Pull 提供者として参加 |
| Context 品質 | オントロジー付き・検証可能な製品（スコアのみより GIGO が減る） |
| DPQM の現場実装 | データと文脈の対が発生点で分離される |
| 統治 | 利用条件付き連携（生の無断ミラーを前提にしない） |
| 標準の射程 | 公式スタックが物理ドメインまで届く |

### Ratio だけでは足りないもの

**公式 ODS でサポート済み（接続・再利用する）:** L3 アイデンティティ、L2 転送、L4 Discovery／メタデータ、利用制御・契約の基盤、L1 信頼／品質手順、運用・監視・オンボーディング。

**公式の外（他者／Ratio の役割）:** 現場での製品導出・生分離（→ **Ratio**）、消費者アプリ／Agentic AI、ドメイン語彙合意、実機 SI、法的・安全責任。

叙述の全文: [`DISCUSSION.ja.md`](DISCUSSION.ja.md#4-ods-側のメリット) · スコープ正本: [`SCOPE.ja.md`](SCOPE.ja.md) · 接続: [`ODS_HANDOFF.ja.md`](ODS_HANDOFF.ja.md)

---

## 3. ODS 準拠要件（参加経路）

**必須（MVP 参加）**／**推奨（提供者成熟）**／**Ratio 所有の前提**（ODS 参加が生 egress を強制しないために必要）に区分。

### 3.1 必須 — MVP「私は ODS 参加者（提供者）である」

| ID | 要件 | ODS アンカー | 準拠の進め方 |
|----|------|--------------|--------------|
| O1 | 相互運用可能な **アイデンティティ＆トラスト**を持つ **ドメイン所有の参加者／ノード** | ODP Identity and Trust（L3）；ODS-RAM trust | 公式 Middleware／SDK バインディング；資格はローカル（例: SQLite）保管—並行 IdP プロトコルを発明しない |
| O2 | オファリングを記述できるよう **メタデータを登録／交換** | ODP Metadata Exchange（L4） | 主オファリングは共有可能プロダクトのメタ。生ファイルを主にしない |
| O3 | 消費者が見つけられる **発見／検索** | ODP Discovery and Search（L4） | カタログは統治されたプロダクトを指す |
| O4 | ODS 整合の **トランザクション的アクセス**（許可時に提供） | ODP Transaction（L2） | Middleware／SDK 経由で共有可能プロダクトの Pull／提供 |
| O5 | **DPQM** 整合のプロダクト（データ関心＋オントロジー／文脈関心の対） | ODS-RAM Architecture／DPQM | 現場は結果 **と** 意味（JSON-LD／RDF＋形状）を出す；スコアのみの塊にしない |
| O6 | **ODP 準拠スタック**で実装（参照 Middleware／SDK 推奨） | ODP；オンボーディング；GitHub `open-dataspaces` | **構成**する。ODP を再実装しない |

### 3.2 推奨 — 提供者としての成熟

| ID | 要件 | ODS アンカー |
|----|------|--------------|
| O7 | オファリング上の **データ信頼／信頼性・品質**シグナル | ODP L1 評価プロトコル |
| O8 | ODS パースペクティブに沿った **利用制御／契約**（誰が、何目的） | ODS-RAM perspectives；適用可能な ODP Heuristic Contracting（P1） |
| O9 | 配備に応じた運用基本: logging／monitoring／notifier | ODP Common Functionalities |
| O10 | オンボーディングと運用は公式開発者／利用者ガイドに従う | Introductory guides |

### 3.3 Ratio 所有の前提（ODS プロトコル要件ではないが、現場で P3／P1 を保つために必要）

| ID | 要件 | 理由 |
|----|------|------|
| R1 | 生ペイロードバイトの **既定非egress** | ドメイン保管；帯域／秘匿；ODS は *プロダクト* の Pull であり湖ミラーではない |
| R2 | 現場での **共有可能プロダクト導出**（結果＋文脈＋ポリシー参照＋任意のドメイン内ポインタ） | 生を出さずに登録／提供するには ODS 妥当な対象が先に必要 |
| R3 | 主張する場合、公開／行動前の **SHACL（または同等）検証** | 信頼できるプロダクト；W3C ツール（Oxigraph）と連携—O5／O7 を支える |
| R4 | 明確な境界で ODS スタックへハンドオフ（私的 ODP フォークなし） | O6 を守る |

---

## 4. トレーサビリティ: スローガン → ODS vs Ratio

```
Authenticated node          → O1          (ODS)
Discoverable                → O2, O3      (ODS)
Pull-able products          → O4, P3      (ODS)
Result + meaning + terms    → O5, O7–O8   (ODS) + R2–R3 (Ratio prepare)
Official ODS stack          → O6, O10     (ODS)
Raw not shipped by default  → R1          (Ratio policy; compatible with ODS custody)
```

---

## 5. 外部参照

### IPA／Open Data Spaces（一次）

| 資源 | URL |
|------|-----|
| ODS ホーム（IPA） | https://www.ipa.go.jp/en/digital/opendataspaces/ |
| ODS ドキュメントハブ（GitBook） | https://open-dataspaces.gitbook.io/ods-docs/ |
| ドキュメント索引（`llms.txt`） | https://open-dataspaces.gitbook.io/ods-docs/llms.txt |
| ODS-RAM V2 | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/v2 |
| ODS-RAM — Architecture（DPQM） | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/02-architecture |
| ODS-RAM — Layers | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/03-layers |
| ODS-RAM — Perspectives | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/04-perspectives |
| ODS-RAM — Protocols | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/05-protocols |
| ODS-RAM — Onboarding & ops | https://open-dataspaces.gitbook.io/ods-docs/ods-ram/06-onboarding |
| ODP overview | https://open-dataspaces.gitbook.io/ods-docs/odp/overview |
| ODP V1 | https://open-dataspaces.gitbook.io/ods-docs/odp/v1 |
| ODP — Identity and Trust（L3） | https://open-dataspaces.gitbook.io/ods-docs/odp/fundamental-protocols/identity-and-trust-l3 |
| ODP — Metadata Exchange（L4） | https://open-dataspaces.gitbook.io/ods-docs/odp/fundamental-protocols/metadata-exchange-l4 |
| ODP — Discovery and Search（L4） | https://open-dataspaces.gitbook.io/ods-docs/odp/fundamental-protocols/discovery-and-search-l4 |
| ODP — Transaction（L2） | https://open-dataspaces.gitbook.io/ods-docs/odp/fundamental-protocols/transaction-l2 |
| 利用者向け入門ガイド | https://open-dataspaces.gitbook.io/ods-docs/introductory-guide/open-data-spaces-introductory-guidebook-for-users |
| 開発者向け入門ガイド | https://open-dataspaces.gitbook.io/ods-docs/developer-guide/developer-guide |
| 設計思想（Why Open Dataspaces） | https://www.ipa.go.jp/en/digital/architecture-guidelines/open-dataspaces-design-philosophy.html |
| 設計思想 PDF（EN） | https://www.ipa.go.jp/en/digital/architecture-guidelines/individual-link/p1o1lf000001xv4n-att/WhyOpenDataspaces_en.pdf |
| 成果物プレスリリース（2026-04-01） | https://www.ipa.go.jp/en/pressrelease/press20260401.html |
| GitHub 組織（Middleware／SDK） | https://github.com/open-dataspaces |

### W3C（プロダクトの意味／アイデンティティ／ポリシー側）

| 資源 | URL |
|------|-----|
| JSON-LD 1.1 | https://www.w3.org/TR/json-ld11/ |
| RDF 1.2 concepts（または現行 RDF TR） | https://www.w3.org/TR/rdf12-concepts/ |
| SHACL | https://www.w3.org/TR/shacl/ |
| Web of Things（WoT）Thing Description | https://www.w3.org/TR/wot-thing-description/ |
| DID Core | https://www.w3.org/TR/did-core/ |
| Verifiable Credentials | https://www.w3.org/TR/vc-data-model-2.0/ |
| ODRL | https://www.w3.org/TR/odrl-model/ |

---

## 6. 保守

ODS-RAM や ODP の改訂で層／プロトコル名が変わったら、先に **§3 の要件アンカー**と **§5 の URL**を更新する。Ratio のエッジ方針（R1–R4）は分離しておき、準拠のドリフトが「生を出さない」の定義を黙って書き換えないようにする。
