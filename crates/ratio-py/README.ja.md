# ratio_core（Python）

> English: [README.md](README.md)

**Ratio の Rust コア** への PyO3 バインディング。プロトタイプ／SLM 側から使う。エッジ本体は `crates/ratio-core` の `ratio` CLI。

```bash
cd crates/ratio-py
uv sync --group dev
uv run maturin develop --uv
uv run pytest
```
