# Ratio サンプル（ODS へのつなぎ）

> English: [README.md](README.md)

製品は [`crates/`](../crates/ratio-core)。ここは **公式 ODS へのつなぎ方** のサンプルであり、コアの代替ではない。構成の正本: [`docs/LAYOUT.ja.md`](../docs/LAYOUT.ja.md)

主張を確かめる最小経路:

```
薄い WoT TD（examples/td/*.td.json）→ 生データを `data/raw` に保管 → 共有可能プロダクト JSON-LD
    → SHACL → ODS／industry への引き渡し（stub | http | l2）
S2: さらに data/queue にストア → 通信が戻ったら flush
```

生データは **publish しない**。外に出る候補はプロダクトだけ。TD の `forms.href` は `local://`（生データの egress なし）。

| シナリオ | デバイス系統（ロック済み） | TD |
|----------|----------------------------|-----|
| K1 | 工場セルロボット · `vibrationWaveform` | [`examples/td/k1-robot.td.json`](../examples/td/k1-robot.td.json) |
| S1 / S2 | 船舶機関 · `shaftVibration`（S2 は同一系統＋キュー） | [`examples/td/s-engine-vib.td.json`](../examples/td/s-engine-vib.td.json) |

パッケージ管理は **uv**（`pyproject.toml` + `uv.lock`）。

ODS 接続の詳細: [`../docs/ODS_HANDOFF.ja.md`](../docs/ODS_HANDOFF.ja.md)  
L2 ルート／OpenFGA／L3 トークン補助: [`scripts/ods/`](scripts/ods/)

## セットアップ

```bash
cd samples
uv sync
```

## テスト

```bash
cd samples
uv sync --group dev
uv run pytest
```

## 実行

```bash
cd samples

# 工場 K1（既定 TD + stub）
uv run ratio --scenario K1

# TD を差し替え（薄い SI）
uv run ratio --scenario K1 --td ../examples/td/k1-robot.td.json

# industry スタブへ HTTP
uv run ratio-serve          # 端末 A
uv run ratio --scenario K1 --ods http --ods-url http://127.0.0.1:8787

# 公式 L2 ゲートウェイへ（SDK-docker-compose 起動後；Bearer は env または自動取得）
uv run ratio --scenario K1 --ods l2
```

### S2 ストア＆フォワード（海事）

```bash
# 船上: 通信がなくてもキューに積む（生データは `data/raw` のまま）
uv run ratio --scenario S2 --offline
# または stub（S2 は自動でキューして終了）
uv run ratio --scenario S2

# 通信が戻ったあと: キューを industry へ flush
uv run ratio-serve   # 陸上／到達可能な industry
uv run ratio --flush-queue --ods http --ods-url http://127.0.0.1:8787

# オンライン時にその場で転送を試す（失敗時はキュー残存、終了コード 0）
uv run ratio --scenario S2 --ods http --ods-url http://127.0.0.1:8787
```

### A3 消費者 Pull（RB11 Out）

提供者パイプラインではない。陸上／パートナーのスタンドインで、**プロダクトだけ**を Pull する。

```bash
cd samples
uv run ratio-serve          # 端末 A
uv run ratio --scenario K1 --ods http --ods-url http://127.0.0.1:8787
uv run ratio-pull --via http
uv run ratio-pull --via http k1-<stem>

# 公式 L2（SDK-docker-compose ＋ Bearer の後）
uv run ratio-pull --via l2 k1-<stem>
```

消費者は意味の要約を出し、本文に生データや非 `local://` ポインタがあれば非ゼロ終了。`GET /raw/` は 200 であってはならない。

成果物:

- `data/raw/` — 生データ（ローカルのみ）
- `data/out/` — プロダクトとレシート
- `data/queue/` — S2 未送信の共有可能プロダクト（生データは入れない）

## 含まないもの（意図的）

- 実ロボット／船上センサ
- `SDK-docker-compose` 一式の同梱（外部起動。手順は ODS_HANDOFF.ja.md）
- Arrow／PyO3／Rust コア（本体は [`crates/`](../crates/ratio-core)；このディレクトリは ODS 引き渡しのサンプル）
- 本番消費者 UI（A3 デモは `ratio-pull` のみ）
