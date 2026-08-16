"""ODS handoff: publish shareable product only (never raw) via stub or HTTP.

Official stack references:
- SDK-docker-compose: https://github.com/open-dataspaces/SDK-docker-compose
- Python client (L3/Payment OpenAPI): https://github.com/open-dataspaces/SDK-client-library-python
- L2 Web API transfer sits in front of a provider industry service.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class HandoffResult:
    mode: str
    ok: bool
    receipt: dict[str, Any]


def _assert_no_raw_in_body(product: dict[str, Any]) -> None:
    """Refuse accidental raw embedding before any network call."""
    blob = json.dumps(product)
    if "RATIO_RAW_STUB" in blob:
        raise ValueError("refusing handoff: raw stub bytes found in product body")
    gov = product.get("dataGovernance") or {}
    pointer = gov.get("rawDataPointer")
    if pointer and not str(pointer).startswith("local://"):
        raise ValueError(
            f"refusing handoff: rawDataPointer must be local://, got {pointer!r}"
        )


def stub_handoff(product_path: Path, conforms: bool, root: Path) -> HandoffResult:
    receipt = {
        "status": "stub",
        "mode": "stub",
        "message": "No network call; product ready for industry service / L2",
        "would_publish": str(product_path.relative_to(root)),
        "shaclConforms": conforms,
        "raw_on_publish_path": False,
        "next": "uv run ratio-poc-serve  # then --ods http",
    }
    return HandoffResult(mode="stub", ok=True, receipt=receipt)


def http_handoff(
    product: dict[str, Any],
    product_path: Path,
    conforms: bool,
    root: Path,
    base_url: str,
    *,
    api_key: str | None = None,
    bearer: str | None = None,
    timeout_s: float = 30.0,
) -> HandoffResult:
    """POST shareable product to provider industry URL (L2 upstream target)."""
    _assert_no_raw_in_body(product)
    if not conforms:
        return HandoffResult(
            mode="http",
            ok=False,
            receipt={
                "status": "skipped",
                "mode": "http",
                "message": "SHACL failed; refusing ODS/industry publish",
                "shaclConforms": False,
                "raw_on_publish_path": False,
            },
        )

    url = base_url.rstrip("/") + "/products"
    body = json.dumps(product, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/ld+json",
        "Accept": "application/json",
        "X-TrackingId": str(uuid.uuid4()),
    }
    key = api_key or os.environ.get("RATIO_ODS_API_KEY")
    token = bearer or os.environ.get("RATIO_ODS_BEARER")
    if key:
        headers["API-Key"] = key
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        receipt = {
            "status": "error",
            "mode": "http",
            "httpStatus": e.code,
            "url": url,
            "response": err_body[:2000],
            "would_publish": str(product_path.relative_to(root)),
            "shaclConforms": conforms,
            "raw_on_publish_path": False,
        }
        return HandoffResult(mode="http", ok=False, receipt=receipt)
    except urllib.error.URLError as e:
        receipt = {
            "status": "error",
            "mode": "http",
            "url": url,
            "error": str(e.reason),
            "hint": "Start industry stub: uv run ratio-poc-serve",
            "shaclConforms": conforms,
            "raw_on_publish_path": False,
        }
        return HandoffResult(mode="http", ok=False, receipt=receipt)

    try:
        parsed = json.loads(resp_body) if resp_body else {}
    except json.JSONDecodeError:
        parsed = {"raw": resp_body[:2000]}

    receipt = {
        "status": "published",
        "mode": "http",
        "httpStatus": status,
        "url": url,
        "response": parsed,
        "would_publish": str(product_path.relative_to(root)),
        "shaclConforms": conforms,
        "raw_on_publish_path": False,
    }
    return HandoffResult(mode="http", ok=200 <= status < 300, receipt=receipt)


def handoff(
    *,
    mode: str,
    product: dict[str, Any],
    product_path: Path,
    conforms: bool,
    root: Path,
    ods_url: str | None = None,
) -> HandoffResult:
    if mode == "stub":
        return stub_handoff(product_path, conforms, root)
    if mode == "http":
        base = ods_url or os.environ.get("RATIO_ODS_URL") or "http://127.0.0.1:8787"
        return http_handoff(product, product_path, conforms, root, base)
    raise ValueError(f"unknown ods mode: {mode}")
