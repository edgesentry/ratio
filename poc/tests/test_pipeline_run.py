"""End-to-end CLI run/flush against an isolated data store."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ratio_poc import cli
from ratio_poc.queue import list_queued, queue_depth


RAW_STUB = "RATIO_RAW_STUB"


def _jsonld(store: Path, scenario: str) -> Path:
    matches = list((store / "data" / "out").glob(f"{scenario.lower()}-*.jsonld"))
    assert len(matches) == 1, matches
    return matches[0]


def test_run_k1_stub_keeps_raw_local(isolated_store: Path) -> None:
    assert cli.run("K1", ods_mode="stub") == 0
    raw_files = list((isolated_store / "data" / "raw" / "K1").glob("raw_wave_*.bin"))
    assert len(raw_files) == 1
    assert RAW_STUB.encode() in raw_files[0].read_bytes()

    product = json.loads(_jsonld(isolated_store, "K1").read_text(encoding="utf-8"))
    blob = json.dumps(product)
    assert RAW_STUB not in blob
    assert product["domain"] == "factory"
    assert product["sourceDevice"] == "did:example:factory-robot-01"
    assert product["dataGovernance"]["rawDataPointer"].startswith("local://storage/K1/")
    assert product["dataGovernance"]["shaclConforms"] is True
    receipts = list((isolated_store / "data" / "out").glob("*.ods-stub.json"))
    assert len(receipts) == 1
    receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
    assert receipt["raw_on_publish_path"] is False


def test_run_s1_uses_maritime_device(isolated_store: Path) -> None:
    assert cli.run("S1", ods_mode="stub") == 0
    product = json.loads(_jsonld(isolated_store, "S1").read_text(encoding="utf-8"))
    assert product["domain"] == "maritime"
    assert product["sourceDevice"] == "did:example:vessel-engine-vib-01"
    assert product["inference"]["physicalContext"]["shaftRPM"] == 98
    assert RAW_STUB not in json.dumps(product)


def test_run_s2_stub_queues_product_not_raw(isolated_store: Path) -> None:
    assert cli.run("S2", ods_mode="stub") == 0
    raw_files = list((isolated_store / "data" / "raw" / "S2").glob("raw_shaft_*.bin"))
    assert len(raw_files) == 1
    queued = list_queued(isolated_store)
    assert len(queued) == 1
    queued_doc = json.loads(queued[0].read_text(encoding="utf-8"))
    assert RAW_STUB not in json.dumps(queued_doc)
    assert queued_doc["scenario"] == "S2"
    assert queued_doc["provenance"]["queueDepth"] == 1
    # stub S2 does not hand off
    assert not list((isolated_store / "data" / "out").glob("*.ods-stub.json"))


def test_flush_queue_stub_dequeues(isolated_store: Path) -> None:
    assert cli.run("S2", ods_mode="stub") == 0
    assert queue_depth(isolated_store) == 1
    assert cli.flush_queue("stub", None) == 0
    assert queue_depth(isolated_store) == 0
    receipts = list((isolated_store / "data" / "out").glob("*.ods-stub.json"))
    assert len(receipts) == 1


def test_run_unknown_scenario_exits() -> None:
    with pytest.raises(SystemExit, match="unknown scenario"):
        cli.run("K9")
