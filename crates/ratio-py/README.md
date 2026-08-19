# ratio_core (Python)

> Japanese: [README.ja.md](README.ja.md)

PyO3 bindings to the **Ratio Rust core**. Use this from the prototype / SLM side. The edge runtime is the `ratio` CLI in `crates/ratio-core`.

```bash
cd crates/ratio-py
uv sync --group dev
uv run maturin develop --uv
uv run pytest
```
