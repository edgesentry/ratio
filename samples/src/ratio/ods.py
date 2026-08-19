"""ODS handoff: publish shareable product only (never raw) via stub, HTTP, or L2.

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


def fetch_l3_bearer(
    *,
    l3_url: str | None = None,
    api_key: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
    timeout_s: float = 30.0,
) -> str | None:
    """Obtain L3 JWT via POST /auth/token/client when credentials are configured.

    Returns None if client id/secret are not set (caller may still use RATIO_ODS_BEARER).
    """
    cid = client_id or os.environ.get("RATIO_ODS_CLIENT_ID")
    secret = client_secret or os.environ.get("RATIO_ODS_CLIENT_SECRET")
    if not cid or not secret:
        return None
    base = (l3_url or os.environ.get("RATIO_ODS_L3_URL") or "http://localhost:8080").rstrip(
        "/"
    )
    key = api_key or os.environ.get("RATIO_ODS_API_KEY") or "API-Key-Sample"
    body = json.dumps({"client_id": cid, "client_secret": secret}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/auth/token/client",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "API-Key": key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    data = payload.get("data") if isinstance(payload, dict) else None
    token = (data or payload or {}).get("access_token")
    if not token:
        raise RuntimeError(f"L3 token response missing access_token: {payload!r}")
    return str(token)


def resolve_bearer(*, bearer: str | None = None) -> str | None:
    """Prefer explicit/env bearer; otherwise try L3 client-credentials fetch."""
    token = bearer or os.environ.get("RATIO_ODS_BEARER")
    if token:
        return token
    try:
        return fetch_l3_bearer()
    except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError, json.JSONDecodeError):
        return None


def stub_handoff(product_path: Path, conforms: bool, root: Path) -> HandoffResult:
    receipt = {
        "status": "stub",
        "mode": "stub",
        "message": "No network call; product ready for industry service / L2",
        "would_publish": str(product_path.relative_to(root)),
        "shaclConforms": conforms,
        "raw_on_publish_path": False,
        "next": "uv run ratio-serve  # then --ods http or --ods l2",
    }
    return HandoffResult(mode="stub", ok=True, receipt=receipt)


def http_handoff(
    product: dict[str, Any],
    product_path: Path,
    conforms: bool,
    root: Path,
    base_url: str,
    *,
    mode: str = "http",
    api_key: str | None = None,
    bearer: str | None = None,
    timeout_s: float = 30.0,
) -> HandoffResult:
    """POST shareable product to industry URL or L2 gateway (never raw)."""
    _assert_no_raw_in_body(product)
    if not conforms:
        return HandoffResult(
            mode=mode,
            ok=False,
            receipt={
                "status": "skipped",
                "mode": mode,
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
    if mode == "l2":
        key = (
            api_key
            or os.environ.get("RATIO_ODS_L2_API_KEY")
            or os.environ.get("RATIO_ODS_API_KEY")
        )
    else:
        key = api_key or os.environ.get("RATIO_ODS_API_KEY")
    token = resolve_bearer(bearer=bearer)
    if key:
        headers["API-Key"] = key
    if token:
        headers["Authorization"] = f"Bearer {token}"
    ods_user = os.environ.get("RATIO_ODS_USER_ID")
    if ods_user:
        headers["X-ODS-UserId"] = ods_user

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        receipt = {
            "status": "error",
            "mode": mode,
            "httpStatus": e.code,
            "url": url,
            "response": err_body[:2000],
            "would_publish": str(product_path.relative_to(root)),
            "shaclConforms": conforms,
            "raw_on_publish_path": False,
            "auth": "bearer" if token else "none",
        }
        return HandoffResult(mode=mode, ok=False, receipt=receipt)
    except urllib.error.URLError as e:
        hint = (
            "Start SDK gateway (L2 :8090) and ratio-serve; see docs/ODS_HANDOFF.md"
            if mode == "l2"
            else "Start industry stub: uv run ratio-serve"
        )
        receipt = {
            "status": "error",
            "mode": mode,
            "url": url,
            "error": str(e.reason),
            "hint": hint,
            "shaclConforms": conforms,
            "raw_on_publish_path": False,
        }
        return HandoffResult(mode=mode, ok=False, receipt=receipt)

    try:
        parsed = json.loads(resp_body) if resp_body else {}
    except json.JSONDecodeError:
        parsed = {"raw": resp_body[:2000]}

    receipt = {
        "status": "published",
        "mode": mode,
        "httpStatus": status,
        "url": url,
        "response": parsed,
        "would_publish": str(product_path.relative_to(root)),
        "shaclConforms": conforms,
        "raw_on_publish_path": False,
        "auth": "bearer" if token else "none",
    }
    return HandoffResult(mode=mode, ok=200 <= status < 300, receipt=receipt)


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
        return http_handoff(product, product_path, conforms, root, base, mode="http")
    if mode == "l2":
        base = (
            ods_url
            or os.environ.get("RATIO_ODS_L2_URL")
            or os.environ.get("RATIO_ODS_URL")
            or "http://127.0.0.1:8090"
        )
        return http_handoff(product, product_path, conforms, root, base, mode="l2")
    raise ValueError(f"unknown ods mode: {mode}")
