# リポジトリ構成

> English: [LAYOUT.md](LAYOUT.md)

Ratio のコードは **製品** と **サンプル** と **例（データ）** に分ける。`poc/` は使わない。

関連: [`SCOPE.ja.md`](SCOPE.ja.md) · [`ARCHITECTURE.ja.md`](ARCHITECTURE.ja.md)

---

## 名前

| 層 | 名前 | 意味 |
|----|------|------|
| GitHub リポジトリ | **ratio** | 製品（Rust＋Python＋サンプル） |
| Rust ワークスペース（通称） | **ratio-rs** | `crates/` の Rust 側 |
| クレート | **ratio-core** | 分離・書式・キュー。あとから `ratio-client` |
| 製品 CLI | **`eds ratio …`** | EdgeSentry 共通入り口（edgesentry-rs の `eds`）。例: `eds ratio derive` |
| このリポの開発用バイナリ | `ratio derive` | `cargo run -p ratio-core --bin ratio`。本番コマンドではない |
| Python モジュール | `ratio_core` | PyO3。CLI ブランドとは別 |
| サンプルの Python パッケージ | `ratio` | `samples/src/ratio` — ODS つなぎ。コアではない |

---

## 一眼

```
ratio/
  crates/                 製品
    ratio-core/           Rust コア（分離・書式・TD・キュー）。製品 CLI は `eds ratio …`
    ratio-py/             Python バインディング（PyO3／Arrow。プロトタイプ／SLM）
  samples/                サンプル（公式 ODS へのつなぎ。製品の代替ではない）
  examples/               書式の例（JSON-LD プロダクト、薄い TD）
  schemas/                共有 `@context` と SHACL
  docs/                   主張・スコープ・アーキ・引き渡し
  data/                   実行時の生データ／成果物（gitignore）
```

| 置き場 | 役割 | 単体テスト |
|--------|------|------------|
| `crates/ratio-core` | 現場の構成。生データは出さない | `cargo test -p ratio-core` |
| `crates/ratio-py` | 同じコアを Python から叩く | `cd crates/ratio-py && uv run pytest` |
| `crates/ratio-client` | （予定）Rust から industry／L2 へメタデータだけ渡す | クライアントの単体テスト |
| `samples/` | Compose／L2／industry スタブ／参照 Pull の動かし方 | `cd samples && uv run pytest`（契約の確認。正本はコアへ移していく） |
| `examples/` | プロダクトと TD の文書例 | コアの `tests/canonical_examples.rs` が読む |
| `docs/POC*.md` | 工場／海事の **検証シナリオ**（ディレクトリ名ではない） | — |

---

## 製品（`crates/`）

- **ratio-core** — `local://` 分離、共有可能プロダクトの組立、書式ゲート、薄い TD、S2 キュー。製品 CLI: **`eds ratio derive`**（このリポの開発用は `ratio derive`）
- **ratio-py** — モジュール `ratio_core`。Arrow IPC はメタデータ行だけ（波形バイトは載せない）
- **ratio-client** — 未作成。公式 L2／industry への HTTP 引き渡しをここに置く。ODP は再実装しない

Python バインディングはコアの別実装ではない。同じ Rust をプロトタイプ／SLM から使う口である。

---

## サンプル（`samples/`）

公式 ODS スタック（L2／L3／AuthZEN）への **つなぎ方**。本体の置き場ではない。

- パッケージ: `samples/src/ratio`（import は `ratio`）
- パイプライン CLI（歴史的な名前のまま）: `uv run ratio-poc` / `ratio-poc-serve` / `ratio-poc-pull`
- ODS 補助: [`samples/scripts/ods/`](../samples/scripts/ods/)
- 手順: [`ODS_HANDOFF.ja.md`](ODS_HANDOFF.ja.md)

`ratio-poc-serve` は公式の代替ではない。`ratio-poc-pull` は RB11 Out（参照消費者）。

---

## 例とスキーマ

- `examples/td/` — ロック済みデバイス系統の薄い WoT TD（`href` は `local://`）
- `examples/*.jsonld` — K1／S1／S2 の共有可能プロダクト例
- `schemas/` — 書式の `@context` と最小 SHACL

---

## テストの分担

| 確認したいこと | どこ |
|----------------|------|
| 生データがプロダクトに乗らない、TD／キュー／書式 | `crates/ratio-core` |
| バインディング経由で同じ契約 | `crates/ratio-py/tests` |
| industry スタブ、引き渡しレシート、参照 Pull | `samples/tests`（サンプルが壊れていないこと） |

CI: Rust ワークスペース → `samples` の pytest → `ratio-py` の maturin／pytest。

---

## 意図的に置かないもの

- `demo/` — ショー用ディレクトリは作らない
- 本番消費者 UI、ODP／L2／L3 の再実装、万能 OT ゲートウェイ
