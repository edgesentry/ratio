"""Locked thin TDs: local:// custody, no public raw href."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ratio.cli import SCENARIOS, load_td


def _hrefs(td: dict) -> list[str]:
    hrefs: list[str] = []
    for prop in (td.get("properties") or {}).values():
        for form in prop.get("forms") or []:
            hrefs.append(form["href"])
    return hrefs


def test_k1_td_is_factory_robot_with_local_waveform() -> None:
    td = load_td(SCENARIOS["K1"]["td_path"])
    assert td["id"] == "urn:td:factory-robot-01"
    assert "vibrationWaveform" in td["properties"]
    hrefs = _hrefs(td)
    assert hrefs
    assert all(h.startswith("local://") for h in hrefs)


def test_s1_and_s2_share_engine_td() -> None:
    s1 = SCENARIOS["S1"]
    s2 = SCENARIOS["S2"]
    assert s1["td_path"] == s2["td_path"]
    assert s1["source_device"] == s2["source_device"] == "did:example:vessel-engine-vib-01"
    td = load_td(s1["td_path"])
    assert td["id"] == "urn:td:vessel-engine-vib-01"
    assert "shaftVibration" in td["properties"]
    assert all(h.startswith("local://") for h in _hrefs(td))


def test_locked_domains() -> None:
    assert SCENARIOS["K1"]["domain"] == "factory"
    assert SCENARIOS["S1"]["domain"] == SCENARIOS["S2"]["domain"] == "maritime"
    assert SCENARIOS["S2"].get("queue") is True
    assert not SCENARIOS["K1"].get("queue")
    assert not SCENARIOS["S1"].get("queue")


def test_load_td_missing_file(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="TD file not found"):
        load_td(tmp_path / "missing.td.json")


def test_load_td_missing_id(tmp_path: Path) -> None:
    path = tmp_path / "bad.td.json"
    path.write_text(json.dumps({"title": "no id"}), encoding="utf-8")
    with pytest.raises(SystemExit, match="missing required field 'id'"):
        load_td(path)
