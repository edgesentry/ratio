# ratio_core（Python）

> English: [README.md](README.md)

**Ratio の Rust コア** への PyO3 バインディング。プロトタイプ／SLM 側から使う。製品 CLI は **`eds ratio …`**。このリポの開発用は `crates/ratio-core` の `ratio derive`。

```bash
cd crates/ratio-py
uv sync --group dev
uv run maturin develop --uv
uv run pytest
```
