# EdgeSentry Ratio

> English: [README.md](README.md)

**物理ドメインが、生クォンタを出さずに ODS に参加できるようにする現場側の構成レイヤ。**

EdgeSentry（親ブランド：現場のガバナンス＆セキュリティ）配下のサブプロジェクト。  
Ratio は現場で **共有可能プロダクト**（結果＋意味＋利用条件）を用意し、**生ペイロード**はドメイン内に留め、**公式 ODS スタック**へ引き渡す。既定は OSS／公式 SDK。自社実装はオーケストレーションの糊だけ。

共有可能プロダクトの定義・ポジショニング → [`docs/DISCUSSION.ja.md`](docs/DISCUSSION.ja.md)

| 項目 | 内容 |
|------|------|
| 名称 | **Ratio**（ラテン語 *ratio*＝理性・推論・根拠） |
| テーゼ | 生クォンタを出さずに ODS に参加する（*participate in ODS without shipping raw quanta*） |
| 役割 | 現場で共有可能プロダクトを導出・検証するセマンティクス／推論コア |
| 標準 | W3C（WoT / JSON-LD / RDF / SHACL / DID·VC / ODRL）× IPA ODS（ODP / DPQM） |
| 方針 | 生はドメイン保管 · プロダクトを Pull · **OSS 既定** |

---

## 想定読者

- OT 生データをミラーせずに、現場を Pull 可能な提供者にしたい **IPA ODS** 利用者
- 実デバイスに WoT / JSON-LD / SHACL / DID·VC / ODRL を載せる **W3C** 実践者
- 秘匿・帯域・断続接続のため **生をローカルに留めつつ** データスペースへ参加したいチーム

**利用者の目的 / ODS で何をするか / 何を得たいか / ODS 側メリット / Ratio だけでは足りないこと** → [`docs/DISCUSSION.ja.md`](docs/DISCUSSION.ja.md#利用者の目的--ods-で何をするか--何を得たいか)

---

## エレベーターピッチ（30秒）

ODS はドメインオーナーが、湖へ全部 Push するのではなく、ガバナンスされた Data＋Ontology Product を Pull で提供する。  
物理現場ではそれが難しい：参加しようとするとセンサダンプを送るか、意味のないスコアだけ出すかの二択になりがち。

**Ratio** は現場で共有可能プロダクト（文脈＋結果＋ポリシー）を導出し、生バイトはローカルに残し、公式 ODS Middleware／SDK で参加する。

---

## 既定パス

```
[devices] → raw quanta → local custody
                ↓
         derive / validate (W3C)
                ↓
         shareable product only → ODS (discover + Pull)
```

テーゼ・スコープ・需要条件 → [`docs/DISCUSSION.ja.md`](docs/DISCUSSION.ja.md)  
**スコープ正本（公式 ODS／Ratio／外と担当）** → [`docs/SCOPE.ja.md`](docs/SCOPE.ja.md)  
PoC サイト（北九州／瀬戸内）→ [`docs/POC.ja.md`](docs/POC.ja.md)
アーキテクチャ → [`docs/ARCHITECTURE.ja.md`](docs/ARCHITECTURE.ja.md)  
ODS の目的と準拠要件（O1–O6, R1–R4）→ [`docs/ODS_COMPLIANCE.ja.md`](docs/ODS_COMPLIANCE.ja.md)  
ODS 認証・認可（参加クライアント要件）→ [`docs/ODS_COMPLIANCE.ja.md` §4](docs/ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件) · [`docs/ODS_HANDOFF.ja.md`](docs/ODS_HANDOFF.ja.md#odsの認証認可概要)
共有可能プロダクト封筒（K1／S1／S2）→ [`docs/PRODUCT_ENVELOPE.ja.md`](docs/PRODUCT_ENVELOPE.ja.md)  
最小パイプライン → [`poc/README.ja.md`](poc/README.ja.md)  
ODS ハンドオフ → [`docs/ODS_HANDOFF.ja.md`](docs/ODS_HANDOFF.ja.md)

---

## なぜこのスタックか

| 問い | 一行の答え |
|------|------------|
| なぜ現場で導出？ | 生を出さずに ODS 公開するなら、その前に共有可能プロダクトが必要 |
| なぜ Oxigraph？ | 意味と検証のための RDF／SPARQL／SHACL |
| なぜ DuckDB／LanceDB／ファイル？ | 生と派生物のローカル保管 |
| なぜ SQLite？ | ノード状態・資格情報・ポリシー記録 |
| なぜ Arrow？ | Python／SLM へのゼロコピー橋。Memory Broker は Ratio 所有 |
| なぜ ODS SDK？ | 公式の参加経路。ODP は再実装しない |
| 何を作る？ | 取込 → 導出／検証 → 生とプロダクトの分離 → ODS ハンドオフ |

---

## 議論アジェンダ（初回）

1. **テーゼの確認** — 生を出さない参加；共有可能プロダクトの中／外
2. **スコープと所有** — Ratio vs EdgeSentry vs OSS／ODS SDK
3. **PoC** — 北九州（ロボット／工場）→ 瀬戸内（海事）；[`docs/POC.ja.md`](docs/POC.ja.md)

---

## ステータス

- [x] テーゼと議論フレームワークを文書化
- [x] PoC サイト想定（北九州 → 瀬戸内）；候補シナリオは [`docs/POC.ja.md`](docs/POC.ja.md)
- [x] シナリオ・ショートリスト確定: **K1 → S1+S2**
- [x] 共有可能プロダクト封筒＋最小 SHACL（[`docs/PRODUCT_ENVELOPE.ja.md`](docs/PRODUCT_ENVELOPE.ja.md)）
- [x] 最小パイプライン試作（[`poc/`](poc/) — スタブ TD → 生保管 → プロダクト → SHACL → ODS stub/http）
- [x] ODS／industry ハンドオフ（[`docs/ODS_HANDOFF.ja.md`](docs/ODS_HANDOFF.ja.md)；公式 Compose は外部）
- [x] S2 ストア＆フォワード（`data/queue` + `--flush-queue`）
- [ ] サイトごとのデバイス／センサ系統の固定（スタブ可ならベンダー未定でも可）
- [x] 薄い TD ファイル化（[`examples/td/`](examples/td/)；`--td` で差し替え可）
- [ ] コア I/F（Arrow）草案
- [x] 公式 `SDK-docker-compose` 接続手順（[`ODS_HANDOFF.ja.md`](docs/ODS_HANDOFF.ja.md)；`--ods l2` + [`poc/scripts/ods/`](poc/scripts/ods/)；Compose は外部起動）
- [x] AuthZEN + `operator_id`（[`ODS_HANDOFF.ja.md` §7](docs/ODS_HANDOFF.ja.md#7-authzenoperator_id)；`register-operator.sh` / `enable-authzen.sh`）
- [x] ODS 認証・認可と参加クライアント要件（[`ODS_COMPLIANCE.ja.md` §4](docs/ODS_COMPLIANCE.ja.md#4-odsの認証認可参加クライアントの要件)）
- [ ] reuse vs build 一覧（草案は POC.ja.md）
