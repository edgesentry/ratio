"""S2 store-and-forward queue holds shareable products, never raw."""

from __future__ import annotations

import json
from pathlib import Path

from ratio_poc.cli import SCENARIOS, build_product
from ratio_poc.queue import dequeue, enqueue, load_queued, queue_depth, refresh_depths


RAW_STUB = "RATIO_RAW_STUB"


def _product(stem_note: str = "a") -> dict:
    return build_product(
        "S2",
        SCENARIOS["S2"],
        f"urn:uuid:00000000-0000-0000-0000-00000000000{stem_note}",
        "2026-08-18T00:00:00Z",
        "local://storage/S2/raw_shaft.bin",
        use_queue=True,
    )


def test_enqueue_writes_product_without_raw(tmp_path: Path) -> None:
    product = _product("1")
    path = enqueue(tmp_path, product, "s2-aaaa1111")
    assert path.parent == tmp_path / "data" / "queue"
    queued = load_queued(path)
    blob = json.dumps(queued)
    assert RAW_STUB not in blob
    assert queued["dataGovernance"]["rawDataPointer"].startswith("local://")
    assert queued["provenance"]["queueDepth"] == 1
    assert queued["provenance"]["firstBufferedAt"]


def test_dequeue_and_refresh_depths(tmp_path: Path) -> None:
    enqueue(tmp_path, _product("1"), "s2-one")
    enqueue(tmp_path, _product("2"), "s2-two")
    assert queue_depth(tmp_path) == 2
    dequeue(tmp_path, "s2-one")
    refresh_depths(tmp_path)
    remaining = load_queued(tmp_path / "data" / "queue" / "s2-two.jsonld")
    assert remaining["provenance"]["queueDepth"] == 1
    assert queue_depth(tmp_path) == 1
