"""A3 reference Pull consumer: meaning only, never raw."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

import pytest

from ratio_poc.cli import SCENARIOS, build_product
from ratio_poc.consumer import (
    ConsumerError,
    assert_raw_not_served,
    consumer_headers,
    inspect_product,
    list_catalog,
    pull_product,
    run,
)
from ratio_poc.industry_serve import Handler as IndustryHandler
import ratio_poc.industry_serve as serve


def _product() -> dict:
    return build_product(
        "K1",
        SCENARIOS["K1"],
        "urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "2026-08-18T00:00:00Z",
        "local://storage/K1/raw_wave.bin",
    )


@pytest.fixture
def industry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setattr(serve, "DATA_OUT", tmp_path / "data" / "out")
    monkeypatch.setattr(serve, "DATA_RAW", tmp_path / "data" / "raw")
    serve.DATA_OUT.mkdir(parents=True)
    serve.DATA_RAW.mkdir(parents=True)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), IndustryHandler)
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[:2]
    try:
        yield f"http://{host}:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def _publish(base: str, product: dict) -> str:
    from http.client import HTTPConnection
    from urllib.parse import urlparse as parse_url

    parsed = parse_url(base)
    conn = HTTPConnection(parsed.hostname, parsed.port, timeout=5)
    body = json.dumps(product).encode("utf-8")
    try:
        conn.request(
            "POST",
            "/products",
            body=body,
            headers={"Content-Type": "application/ld+json", "Content-Length": str(len(body))},
        )
        resp = conn.getresponse()
        payload = json.loads(resp.read())
        assert resp.status == 201, payload
        return str(payload["pull"]).rsplit("/", 1)[-1]
    finally:
        conn.close()


def test_inspect_accepts_shareable_product() -> None:
    summary = inspect_product(json.dumps(_product()))
    assert summary["result"] == "vibration_abnormal"
    assert summary["sourceDevice"] == "did:example:factory-robot-01"
    assert summary["raw_in_body"] is False
    assert str(summary["rawDataPointer"]).startswith("local://")


def test_inspect_refuses_raw_stub() -> None:
    product = _product()
    product["leaked"] = "RATIO_RAW_STUB"
    with pytest.raises(ConsumerError, match="raw stub"):
        inspect_product(json.dumps(product))


def test_inspect_refuses_public_pointer() -> None:
    product = _product()
    product["dataGovernance"]["rawDataPointer"] = "https://example.invalid/raw.bin"
    with pytest.raises(ConsumerError, match="local://"):
        inspect_product(json.dumps(product))


def test_inspect_refuses_missing_type() -> None:
    product = _product()
    product["@type"] = ["SomethingElse"]
    with pytest.raises(ConsumerError, match="ShareableProduct"):
        inspect_product(json.dumps(product))


def test_pull_from_industry_stub(industry: str) -> None:
    stem = _publish(industry, _product())
    headers = consumer_headers(via="http")
    summary = pull_product(industry, stem, headers)
    assert summary["scenario"] == "K1"
    assert summary["domain"] == "factory"
    catalog = list_catalog(industry, headers)
    assert any(item.get("id") == _product()["id"] for item in catalog)
    assert assert_raw_not_served(industry, headers) == 404


def _stdout_json(text: str) -> dict:
    start = text.find("{")
    assert start >= 0, text
    return json.loads(text[start:])


def test_run_prints_meaning(industry: str, capsys: pytest.CaptureFixture[str]) -> None:
    stem = _publish(industry, _product())
    assert run(via="http", base_url=industry, stem=stem) == 0
    out = _stdout_json(capsys.readouterr().out)
    assert out["result"] == "vibration_abnormal"
    assert out["raw_in_body"] is False


def test_run_lists_catalog(industry: str, capsys: pytest.CaptureFixture[str]) -> None:
    _publish(industry, _product())
    assert run(via="http", base_url=industry) == 0
    payload = _stdout_json(capsys.readouterr().out)
    assert payload["raw_served"] is False
    assert payload["products"]


def test_consumer_flags_leaky_raw_server() -> None:
    class Leaky(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            return

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            body = b"RATIO_RAW_STUB\n" if path.startswith("/raw") else b'{"error":"no"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Leaky)
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[:2]
    try:
        with pytest.raises(ConsumerError, match="raw path unexpectedly served"):
            assert_raw_not_served(f"http://{host}:{port}", {})
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def test_l2_headers_include_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATIO_ODS_L2_API_KEY", "l2-key-test")
    monkeypatch.setenv("RATIO_ODS_BEARER", "jwt-test")
    monkeypatch.delenv("RATIO_ODS_CLIENT_ID", raising=False)
    headers = consumer_headers(via="l2")
    assert headers["API-Key"] == "l2-key-test"
    assert headers["Authorization"] == "Bearer jwt-test"
    assert "Accept" in headers
