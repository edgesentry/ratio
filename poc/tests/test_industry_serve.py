"""Industry stub serves shareable products only; raw paths stay 404."""

from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from ratio_poc import industry_serve as serve
from ratio_poc.cli import SCENARIOS, build_product


def _product() -> dict:
    return build_product(
        "K1",
        SCENARIOS["K1"],
        "urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "2026-08-18T00:00:00Z",
        "local://storage/K1/raw_wave.bin",
    )


@pytest.fixture
def industry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[str, Path]:
    monkeypatch.setattr(serve, "DATA_OUT", tmp_path / "data" / "out")
    monkeypatch.setattr(serve, "DATA_RAW", tmp_path / "data" / "raw")
    serve.DATA_OUT.mkdir(parents=True)
    serve.DATA_RAW.mkdir(parents=True)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[:2]
    try:
        yield f"{host}:{port}", tmp_path
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def _request(
    addr: str,
    method: str,
    path: str,
    body: bytes | None = None,
    content_type: str = "application/ld+json",
) -> tuple[int, bytes]:
    conn = HTTPConnection(addr, timeout=5)
    try:
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = content_type
            headers["Content-Length"] = str(len(body))
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        return resp.status, resp.read()
    finally:
        conn.close()


def test_health_and_raw_not_served(industry: tuple[str, Path]) -> None:
    addr, store = industry
    status, body = _request(addr, "GET", "/health")
    assert status == 200
    payload = json.loads(body)
    assert payload["raw_dir_exposed"] is False

    (store / "data" / "raw" / "secret.bin").write_bytes(b"RATIO_RAW_STUB\n")
    status, _ = _request(addr, "GET", "/raw/secret.bin")
    assert status == 404
    status, _ = _request(addr, "GET", "/products/raw")
    assert status == 400


def test_post_and_get_product_without_raw(industry: tuple[str, Path]) -> None:
    addr, _ = industry
    product = _product()
    status, body = _request(
        addr, "POST", "/products", json.dumps(product).encode("utf-8")
    )
    assert status == 201
    receipt = json.loads(body)
    assert receipt["raw_on_publish_path"] is False
    pull = receipt["pull"]
    status, got = _request(addr, "GET", pull)
    assert status == 200
    doc = json.loads(got)
    assert doc["id"] == product["id"]
    assert "RATIO_RAW_STUB" not in got.decode("utf-8")


def test_post_refuses_embedded_raw(industry: tuple[str, Path]) -> None:
    addr, _ = industry
    product = _product()
    product["leaked"] = "RATIO_RAW_STUB"
    status, body = _request(
        addr, "POST", "/products", json.dumps(product).encode("utf-8")
    )
    assert status == 400
    assert "raw" in json.loads(body)["error"]


def test_post_refuses_public_pointer(industry: tuple[str, Path]) -> None:
    addr, _ = industry
    product = _product()
    product["dataGovernance"]["rawDataPointer"] = "https://example.invalid/raw.bin"
    status, _ = _request(addr, "POST", "/products", json.dumps(product).encode("utf-8"))
    assert status == 400
