"""Bindings to the Ratio Rust core (derive + local:// split + Arrow IPC)."""

from __future__ import annotations

import io
import json

import pytest

ratio_core = pytest.importorskip("ratio_core")


def test_local_pointer() -> None:
    assert ratio_core.local_pointer_ok("local://storage/K1/raw.bin")
    assert not ratio_core.local_pointer_ok("https://example.invalid/raw.bin")
    with pytest.raises(ValueError):
        ratio_core.require_local_pointer("https://example.invalid/raw.bin")


def test_derive_k1_has_no_raw_stub() -> None:
    blob = ratio_core.derive_stub_product_json("K1", "local://storage/K1/raw_wave.bin")
    product = json.loads(blob)
    assert ratio_core.RAW_STUB_MARKER not in blob
    ratio_core.validate_product_json(blob)
    assert product["scenario"] == "K1"
    assert product["dataGovernance"]["rawDataPointer"].startswith("local://")


def test_derive_rejects_https_pointer() -> None:
    with pytest.raises(ValueError):
        ratio_core.derive_stub_product_json("K1", "https://example.invalid/raw.bin")


def test_arrow_ipc_columns() -> None:
    pyarrow = pytest.importorskip("pyarrow")
    blob = ratio_core.derive_stub_product_json("S1", "local://storage/S1/raw_shaft.bin")
    ipc = ratio_core.products_json_to_arrow_ipc(f"[{blob}]")
    table = pyarrow.ipc.open_stream(io.BytesIO(ipc)).read_all()
    assert table.num_rows == 1
    assert "waveform" not in table.column_names
    assert table.column("raw_data_pointer")[0].as_py().startswith("local://")
    assert table.column("envelope_ok")[0].as_py() is True
