"""Shared fixtures. Isolate data/raw, data/out, data/queue from the live PoC store."""

from __future__ import annotations

from pathlib import Path

import pytest

from ratio import cli


@pytest.fixture
def isolated_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect CLI store paths so tests never write into the repo data/ tree."""
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setattr(cli, "DATA_RAW", tmp_path / "data" / "raw")
    monkeypatch.setattr(cli, "DATA_OUT", tmp_path / "data" / "out")
    return tmp_path
