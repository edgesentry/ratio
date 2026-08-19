"""Shareable product construction and SHACL (raw stays local://)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ratio.cli import SCENARIOS, build_product, load_context, run_shacl, write_raw

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


RAW_STUB = "RATIO_RAW_STUB"
POINTER = "local://storage/K1/raw_wave_test.bin"


def _product(scenario: str, pointer: str = POINTER, **overrides: object) -> dict:
    cfg = SCENARIOS[scenario]
    product = build_product(
        scenario,
        cfg,
        "urn:uuid:00000000-0000-0000-0000-000000000001",
        "2026-08-18T00:00:00Z",
        pointer,
        use_queue=bool(cfg.get("queue")),
    )
    product.update(overrides)
    return product


@pytest.mark.parametrize("scenario", ["K1", "S1", "S2"])
def test_built_product_conforms_and_has_no_raw(scenario: str) -> None:
    product = _product(scenario)
    blob = json.dumps(product)
    assert RAW_STUB not in blob
    assert product["dataGovernance"]["rawDataPointer"].startswith("local://")
    assert product["sourceDevice"] == SCENARIOS[scenario]["source_device"]
    assert product["domain"] == SCENARIOS[scenario]["domain"]
    assert product["scenario"] == scenario
    conforms, report = run_shacl(product)
    assert conforms, report


def test_k1_physical_context_is_motor() -> None:
    product = _product("K1")
    ctx = product["inference"]["physicalContext"]
    assert ctx["motorRPM"] == 1450
    assert "shaftRPM" not in ctx


def test_maritime_physical_context_is_shaft() -> None:
    for scenario in ("S1", "S2"):
        ctx = _product(scenario)["inference"]["physicalContext"]
        assert ctx["shaftRPM"] == 98
        assert "motorRPM" not in ctx


def test_s2_product_marks_queue_buffer() -> None:
    product = _product("S2")
    assert product["provenance"]["firstBufferedAt"] == "2026-08-18T00:00:00Z"
    assert "firstBufferedAt" not in _product("S1")["provenance"]


def test_shacl_rejects_public_raw_pointer() -> None:
    product = _product("K1", pointer="https://example.invalid/raw.bin")
    conforms, report = run_shacl(product)
    assert not conforms
    assert "local://" in report or "rawDataPointer" in report


def test_shacl_rejects_unknown_domain() -> None:
    product = _product("K1")
    product["domain"] = "unknown"
    conforms, _ = run_shacl(product)
    assert not conforms


def test_write_raw_stays_under_local_pointer(isolated_store: Path) -> None:
    path, pointer = write_raw("K1", SCENARIOS["K1"], "20260818_000000")
    assert path.is_file()
    assert path.read_bytes().startswith(b"RATIO_RAW_STUB\n")
    assert pointer == "local://storage/K1/raw_wave_20260818_000000.bin"
    assert isolated_store / "data" / "raw" / "K1" in path.parents
    product = _product("K1", pointer=pointer)
    assert RAW_STUB not in json.dumps(product)


def test_canonical_examples_conform_with_inlined_context() -> None:
    context = load_context()
    examples = [
        EXAMPLES / "k1-cell-vibration.jsonld",
        EXAMPLES / "s1-engine-vibration.jsonld",
        EXAMPLES / "s2-store-and-forward.jsonld",
    ]
    for path in examples:
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc = deepcopy(doc)
        doc["@context"] = context
        assert RAW_STUB not in json.dumps(doc)
        assert str(doc["dataGovernance"]["rawDataPointer"]).startswith("local://")
        conforms, report = run_shacl(doc)
        assert conforms, f"{path.name}: {report}"
