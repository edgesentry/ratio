# Ratio 最小パイプライン（PoC）

テーゼ実証の最小経路:

```
スタブ WoT TD → 生を data/raw に保管 → 共有可能プロダクト JSON-LD
    → SHACL → ODS／industry ハンドオフ（stub | http）
S2: さらに data/queue にストア → リンク復帰で flush
```

生は **publish しない**。外に出る候補はプロダクトだけ。

パッケージ管理は **uv**（`pyproject.toml` + `uv.lock`）。

ODS 接続の詳細: [`../docs/ODS_HANDOFF.md`](../docs/ODS_HANDOFF.md)

## セットアップ

```bash
cd poc
uv sync
```

## 実行

```bash
cd poc

# 北九州 K1（既定 stub）
uv run ratio-poc --scenario K1

# industry スタブへ HTTP
uv run ratio-poc-serve          # 端末 A
uv run ratio-poc --scenario K1 --ods http --ods-url http://127.0.0.1:8787
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
