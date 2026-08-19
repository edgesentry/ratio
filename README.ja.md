# EdgeSentry Ratio

> English: [README.md](README.md)

**物理ドメインが、生データを出さずに ODS に参加できるようにする現場側の構成レイヤ。**

EdgeSentry（親ブランド：現場のガバナンス＆セキュリティ）配下のサブプロジェクト。  
Ratio は現場で **共有可能プロダクト**（結果＋意味＋利用条件）を用意し、**生データ**はドメイン内に留め、**公式 ODS スタック**へ引き渡す。既定は OSS／公式 SDK。自社実装はオーケストレーションの糊だけ。

共有可能プロダクトの定義・ポジショニング → [`docs/DISCUSSION.ja.md`](docs/DISCUSSION.ja.md)

| 項目 | 内容 |
|------|------|
| 名称 | **Ratio**（ラテン語 *ratio*＝理性・推論・根拠） |
| 主張 | 生データを出さずに ODS に参加する（*participate in ODS without shipping raw data*） |
| 役割 | 現場で判断の根拠を共有可能プロダクトにし、公式 ODS へ引き渡す構成レイヤ |
| 標準 | W3C（WoT / JSON-LD / RDF / SHACL / DID·VC / ODRL）× IPA ODS（ODP / DPQM） |
| 方針 | 生データはドメイン保管 · プロダクトを Pull · **OSS 既定** |

---

## 想定読者

- OT 生データをミラーせずに、現場を Pull 可能な提供者にしたい **IPA ODS** 利用者
- 実デバイスに WoT / JSON-LD / SHACL / DID·VC / ODRL を載せる **W3C** 実践者
- 秘匿・帯域・通信の途切れのため **生データをローカルに留めつつ** データスペースへ参加したいチーム

**利用者の目的 / ODS で何をするか / 何を得たいか / ODS 側メリット / Ratio だけでは足りないこと** → [`docs/DISCUSSION.ja.md`](docs/DISCUSSION.ja.md#利用者の目的--ods-で何をするか--何を得たいか)

---

## エレベーターピッチ（30秒）

ODS はドメインオーナーが、データレイクへ全部 Push するのではなく、ガバナンスされた Data＋Ontology Product を Pull で提供する。  
物理現場ではそれが難しい：参加しようとするとセンサダンプを送るか、意味のないスコアだけ出すかの二択になりがち。

**Ratio** は現場で共有可能プロダクト（文脈＋結果＋ポリシー）を導出し、生データはローカルに残し、公式 ODS Middleware／SDK で参加する。

---

## 基本の流れ

```
[devices] → raw data → local custody
                ↓
         derive / validate (W3C)
                ↓
         shareable product only → ODS (discover + Pull)
```

主張・スコープ・需要条件 → [`docs/DISCUSSION.ja.md`](docs/DISCUSSION.ja.md)  
**スコープ正本（公式 ODS／Ratio／外と担当）** → [`docs/SCOPE.ja.md`](docs/SCOPE.ja.md)  
リポジトリ構成 → [`docs/LAYOUT.ja.md`](docs/LAYOUT.ja.md)  
PoC 分野（工場／海事）→ [`docs/POC.ja.md`](docs/POC.ja.md)
アーキテクチャ → [`docs/ARCHITECTURE.ja.md`](docs/ARCHITECTURE.ja.md)  
ODS の目的と準拠要件（O1–O6, R1–R4）→ [`docs/ODS_COMPLIANCE.ja.md`](docs/ODS_COMPLIANCE.ja.md)  
ODS 認証・認可（参加クライアント要件）→ [`docs/ODS_COMPLIANCE.ja.md` §4](docs/ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件) · [`docs/ODS_HANDOFF.ja.md`](docs/ODS_HANDOFF.ja.md#odsの認証認可概要)
共有可能プロダクトの書式（K1／S1／S2）→ [`docs/PRODUCT_ENVELOPE.ja.md`](docs/PRODUCT_ENVELOPE.ja.md)  
ODS へのつなぎ（サンプル）→ [`samples/README.ja.md`](samples/README.ja.md)  
Rust コア／Python バインディング → [`crates/ratio-core`](crates/ratio-core) · [`crates/ratio-py/README.ja.md`](crates/ratio-py/README.ja.md)  
ODS への引き渡し（共有可能プロダクトのメタデータ）→ [`docs/ODS_HANDOFF.ja.md`](docs/ODS_HANDOFF.ja.md)

---

## なぜこのスタックか

| 問い | 一行の答え |
|------|------------|
| なぜ現場で導出？ | 生データを出さずに ODS 公開するなら、その前に共有可能プロダクトが必要 |
| なぜ Oxigraph？ | 意味と検証のための RDF／SPARQL／SHACL |
| なぜ DuckDB／LanceDB／ファイル？ | 生データと派生物のローカル保管 |
| なぜ SQLite？ | ノード状態・資格情報・ポリシー記録 |
| なぜ Arrow？ | Python／SLM とゼロコピーでつなぐ。Arrow を使う Memory Broker の役割は Ratio が担う |
| なぜ ODS SDK？ | 公式の参加経路。ODP は再実装しない |
| 何を作る？ | 取込 → 導出／検証 → 生データとプロダクトの分離 → ODS への引き渡し |

---

## 議論アジェンダ（初回）

1. **主張の確認** — 生データを出さない参加；共有可能プロダクトの中／外
2. **スコープと所有** — Ratio vs EdgeSentry vs OSS／ODS SDK
3. **PoC** — 産業ロボット／工場 → 海事センサ／船舶；[`docs/POC.ja.md`](docs/POC.ja.md)

---

## ステータス

- [x] 主張と議論フレームワークを文書化
- [x] PoC 分野想定（工場 → 海事）；候補シナリオは [`docs/POC.ja.md`](docs/POC.ja.md)
- [x] シナリオ・ショートリスト確定: **K1 → S1+S2**
- [x] 共有可能プロダクトの書式＋最小 SHACL（[`docs/PRODUCT_ENVELOPE.ja.md`](docs/PRODUCT_ENVELOPE.ja.md)）
- [x] ODS つなぎのサンプル（[`samples/`](samples/) — スタブ TD → 生データの保管 → プロダクト → SHACL → ODS stub/http）
- [x] ODS／industry への引き渡し（[`docs/ODS_HANDOFF.ja.md`](docs/ODS_HANDOFF.ja.md)；公式 Compose は外部）
- [x] S2 ストア＆フォワード（`data/queue` + `--flush-queue`）
- [x] 分野ごとのデバイス／センサ系統の固定（[`POC.ja.md`](docs/POC.ja.md)；K1 ロボット振動、S1/S2 シャフト振動；ベンダー未定）
- [x] 薄い TD ファイル化（[`examples/td/`](examples/td/)；`--td` で差し替え可）
- [x] コア I/F v0（Rust + PyO3／Arrow；[`crates/ratio-core`](crates/ratio-core)、[`crates/ratio-py`](crates/ratio-py)）
- [x] 公式 `SDK-docker-compose` 接続手順（[`ODS_HANDOFF.ja.md`](docs/ODS_HANDOFF.ja.md)；`--ods l2` + [`samples/scripts/ods/`](samples/scripts/ods/)；Compose は外部起動）
- [x] AuthZEN + `operator_id`（[`ODS_HANDOFF.ja.md` §7](docs/ODS_HANDOFF.ja.md#7-authzenoperator_id)；`register-operator.sh` / `enable-authzen.sh`）
- [x] ODS 認証・認可と参加クライアント要件（[`ODS_COMPLIANCE.ja.md` §4](docs/ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件)）
- [x] reuse vs build 一覧（[`POC.ja.md`](docs/POC.ja.md#reuse-vs-build両分野)；RB1–RB11）
- [x] A3 参照 Pull 消費者（[`ODS_HANDOFF.ja.md` §6](docs/ODS_HANDOFF.ja.md#6-消費者-共有可能プロダクトを-pulla3)；`uv run ratio-pull`；RB11 Out）
