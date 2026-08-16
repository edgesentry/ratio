# Ratio 最小パイプライン（PoC）

テーゼ実証の最小経路:

```
薄い WoT TD（examples/td/*.td.json）→ 生を data/raw に保管 → 共有可能プロダクト JSON-LD
    → SHACL → ODS／industry ハンドオフ（stub | http | l2）
S2: さらに data/queue にストア → リンク復帰で flush
```

生は **publish しない**。外に出る候補はプロダクトだけ。TD の `forms.href` は `local://`（生の egress なし）。

| シナリオ | TD |
|----------|-----|
| K1 | [`examples/td/k1-robot.td.json`](../examples/td/k1-robot.td.json) |
| S1 / S2 | [`examples/td/s-engine-vib.td.json`](../examples/td/s-engine-vib.td.json)（同一センサ；S2 はキュー方針のみ異なる） |

パッケージ管理は **uv**（`pyproject.toml` + `uv.lock`）。

ODS 接続の詳細: [`../docs/ODS_HANDOFF.md`](../docs/ODS_HANDOFF.md)  
L2 ルート／OpenFGA／L3 トークン補助: [`scripts/ods/`](scripts/ods/)

## セットアップ

```bash
cd poc
uv sync
```

## 実行

```bash
cd poc

# 北九州 K1（既定 TD + stub handoff）
uv run ratio-poc --scenario K1

# TD を差し替え（薄い SI）
uv run ratio-poc --scenario K1 --td ../examples/td/k1-robot.td.json

# industry スタブへ HTTP
uv run ratio-poc-serve          # 端末 A
uv run ratio-poc --scenario K1 --ods http --ods-url http://127.0.0.1:8787

# 公式 L2 ゲートウェイへ（SDK-docker-compose 起動後；Bearer は env または自動取得）
uv run ratio-poc --scenario K1 --ods l2
```

### S2 ストア＆フォワード（瀬戸内）

```bash
# 船上: リンク無しでもキューに積む（生は raw のまま）
uv run ratio-poc --scenario S2 --offline
# または stub（S2 は自動でキューして終了）
uv run ratio-poc --scenario S2

# リンク復帰後: キューを industry へ flush
uv run ratio-poc-serve   # 陸上／到達可能な industry
uv run ratio-poc --flush-queue --ods http --ods-url http://127.0.0.1:8787

# オンライン時にその場で転送を試す（失敗時はキュー残存、終了コード 0）
uv run ratio-poc --scenario S2 --ods http --ods-url http://127.0.0.1:8787
```

成果物:

- `data/raw/` — 生（ローカルのみ）
- `data/out/` — プロダクトとレシート
- `data/queue/` — S2 未送信の共有可能プロダクト（生は入れない）

## 含まないもの（意図的）

- 実ロボット／船上センサ
- `SDK-docker-compose` 一式の同梱（外部起動。手順は ODS_HANDOFF.md）
- Arrow／PyO3／Rust コア
