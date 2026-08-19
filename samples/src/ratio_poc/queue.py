"""Store-and-forward queue for shareable products (S2 / intermittent link).

Raw never enters the queue — only validated JSON-LD products.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def queue_dir(root: Path) -> Path:
    path = root / "data" / "queue"
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_queued(root: Path) -> list[Path]:
    return sorted(queue_dir(root).glob("*.jsonld"))


def queue_depth(root: Path) -> int:
    return len(list_queued(root))


def enqueue(root: Path, product: dict[str, Any], stem: str) -> Path:
    """Write product into the queue and refresh provenance queue fields."""
    qdir = queue_dir(root)
    path = qdir / f"{stem}.jsonld"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prov = product.setdefault("provenance", {})
    if "firstBufferedAt" not in prov:
        prov["firstBufferedAt"] = now
    # depth includes this item once written
    path.write_text(
        json.dumps(product, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    prov["queueDepth"] = queue_depth(root)
    path.write_text(
        json.dumps(product, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


def dequeue(root: Path, stem: str) -> None:
    path = queue_dir(root) / f"{stem}.jsonld"
    if path.is_file():
        path.unlink()


def load_queued(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def refresh_depths(root: Path) -> None:
    """Rewrite queueDepth on all queued products after removals."""
    depth = queue_depth(root)
    for path in list_queued(root):
        doc = load_queued(path)
        doc.setdefault("provenance", {})["queueDepth"] = depth
        path.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
