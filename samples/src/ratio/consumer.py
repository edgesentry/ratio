"""Reference Pull consumer for A3 (RB11 Out — not the provider pipeline).

Pulls shareable products from the industry API or official L2 gateway.
Refuses bodies that embed raw data or a non-local pointer.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from typing import Any

from ratio.ods import resolve_bearer

RAW_STUB = "RATIO_RAW_STUB"
DEFAULT_HTTP = "http://127.0.0.1:8787"
DEFAULT_L2 = "http://127.0.0.1:8090"
DEFAULT_L2_KEY = "2dfd3409-ce01-4451-96fa-7e10c9681422y"


class ConsumerError(ValueError):
    """Pulled payload is not a shareable product (raw mixed in or incomplete)."""


def inspect_product(raw: str | bytes) -> dict[str, Any]:
    """Consumer-side checks: usable meaning, no raw payload."""
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    if RAW_STUB in text:
        raise ConsumerError("refusing Pull: raw stub bytes in body")
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConsumerError(f"refusing Pull: not JSON ({exc})") from exc
    if not isinstance(doc, dict):
        raise ConsumerError("refusing Pull: expected a JSON object")

    types = doc.get("@type") or doc.get("type") or []
    if isinstance(types, str):
        types = [types]
    if "ShareableProduct" not in types:
        raise ConsumerError("refusing Pull: not a ShareableProduct")

    pointer = (doc.get("dataGovernance") or {}).get("rawDataPointer")
    if pointer and not str(pointer).startswith("local://"):
        raise ConsumerError(
            f"refusing Pull: rawDataPointer must be local://, got {pointer!r}"
        )

    inference = doc.get("inference") or {}
    if not inference.get("result"):
        raise ConsumerError("refusing Pull: missing inference.result")

    return {
        "id": doc.get("id"),
        "domain": doc.get("domain"),
        "scenario": doc.get("scenario"),
        "sourceDevice": doc.get("sourceDevice"),
        "result": inference.get("result"),
        "confidence": inference.get("confidence"),
        "physicalContext": inference.get("physicalContext"),
        "policyRef": (doc.get("dataGovernance") or {}).get("policyRef"),
        "rawDataPointer": pointer,
        "raw_in_body": False,
    }


def consumer_headers(*, via: str, bearer: str | None = None) -> dict[str, str]:
    headers = {
        "Accept": "application/ld+json, application/json",
        "X-TrackingId": str(uuid.uuid4()),
    }
    user = os.environ.get("RATIO_ODS_USER_ID")
    if user:
        headers["X-ODS-UserId"] = user
    if via == "l2":
        key = (
            os.environ.get("RATIO_ODS_L2_API_KEY")
            or os.environ.get("RATIO_ODS_API_KEY")
            or DEFAULT_L2_KEY
        )
        token = resolve_bearer(bearer=bearer)
        headers["API-Key"] = key
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


def http_get(url: str, headers: dict[str, str], timeout_s: float = 30.0) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return int(resp.status), resp.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read()
    except urllib.error.URLError as exc:
        raise ConsumerError(f"Pull failed: {exc.reason}") from exc


def list_catalog(base_url: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    status, body = http_get(base_url.rstrip("/") + "/products", headers)
    if status != 200:
        raise ConsumerError(f"catalog GET failed HTTP {status}: {body[:500]!r}")
    payload = json.loads(body.decode("utf-8"))
    products = payload.get("products", payload)
    if not isinstance(products, list):
        raise ConsumerError("catalog response has no products list")
    return products


def pull_product(base_url: str, stem: str, headers: dict[str, str]) -> dict[str, Any]:
    if ".." in stem or "/" in stem:
        raise ConsumerError("invalid product id")
    status, body = http_get(base_url.rstrip("/") + f"/products/{stem}", headers)
    if status != 200:
        raise ConsumerError(f"product GET failed HTTP {status}: {body[:500]!r}")
    return inspect_product(body)


def assert_raw_not_served(base_url: str, headers: dict[str, str]) -> int:
    """Return HTTP status for GET /raw/. Fail if a body is served."""
    status, body = http_get(base_url.rstrip("/") + "/raw/", headers)
    text = body.decode("utf-8", errors="replace")
    if status == 200 or RAW_STUB in text:
        raise ConsumerError(
            f"raw path unexpectedly served HTTP {status} (A3 requires products only)"
        )
    return status


def resolve_base(via: str, base_url: str | None) -> str:
    if base_url:
        return base_url.rstrip("/")
    if via == "l2":
        return (os.environ.get("RATIO_ODS_L2_URL") or DEFAULT_L2).rstrip("/")
    return (os.environ.get("RATIO_ODS_URL") or DEFAULT_HTTP).rstrip("/")


def run(
    *,
    via: str = "http",
    base_url: str | None = None,
    stem: str | None = None,
    bearer: str | None = None,
) -> int:
    base = resolve_base(via, base_url)
    headers = consumer_headers(via=via, bearer=bearer)
    print(f"[consumer] Pull via={via} base={base}", file=sys.stderr)

    raw_status = assert_raw_not_served(base, headers)
    print(f"[consumer] GET /raw/ → HTTP {raw_status} (not served)", file=sys.stderr)

    if not stem:
        catalog = list_catalog(base, headers)
        print(json.dumps({"products": catalog, "raw_served": False}, indent=2, ensure_ascii=False))
        return 0

    summary = pull_product(base, stem, headers)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(
        f"[consumer] OK meaning={summary['result']} "
        f"device={summary['sourceDevice']} raw_in_body=false",
        file=sys.stderr,
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "A3 reference Pull consumer (RB11 Out). "
            "Fetches shareable products only; refuses raw payloads."
        )
    )
    parser.add_argument(
        "stem",
        nargs="?",
        default=None,
        help="Product stem (e.g. k1-aaaaaaaa). Omit to list /products",
    )
    parser.add_argument(
        "--via",
        choices=("http", "l2"),
        default="http",
        help="http = industry stub; l2 = official gateway (Bearer + L2 API-Key)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override base URL (else RATIO_ODS_URL / RATIO_ODS_L2_URL)",
    )
    args = parser.parse_args()
    try:
        raise SystemExit(run(via=args.via, base_url=args.base_url, stem=args.stem))
    except ConsumerError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
