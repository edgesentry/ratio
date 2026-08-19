# ratio_core (Python)

> Japanese: [README.ja.md](README.ja.md)

PyO3 bindings to the **Ratio Rust core**. Use this from the prototype / SLM side. The product CLI is **`eds ratio …`**. In-repo dev command is `ratio derive` in `crates/ratio-core`.

```bash
cd crates/ratio-py
uv sync --group dev
uv run maturin develop --uv
uv run pytest
```
