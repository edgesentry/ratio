"""ODS handoff refuses raw payloads; stub/http never put raw on the publish path."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request

import pytest

from ratio.cli import SCENARIOS, build_product
from ratio.ods import (
    _assert_no_raw_in_body,
    fetch_l3_bearer,
    handoff,
    http_handoff,
    resolve_bearer,
    stub_handoff,
)


def _product(*, pointer: str = "local://storage/K1/raw_wave.bin") -> dict:
    return build_product(
        "K1",
        SCENARIOS["K1"],
        "urn:uuid:00000000-0000-0000-0000-000000000002",
        "2026-08-18T00:00:00Z",
        pointer,
    )


def test_assert_no_raw_rejects_stub_bytes() -> None:
    product = _product()
    product["leaked"] = "RATIO_RAW_STUB"
    with pytest.raises(ValueError, match="raw stub bytes"):
        _assert_no_raw_in_body(product)


def test_assert_no_raw_rejects_public_pointer() -> None:
    with pytest.raises(ValueError, match="must be local://"):
        _assert_no_raw_in_body(_product(pointer="https://example.invalid/raw.bin"))


def test_assert_no_raw_accepts_local_product() -> None:
    _assert_no_raw_in_body(_product())


def test_stub_handoff_marks_raw_off_publish_path(tmp_path: Path) -> None:
    product_path = tmp_path / "data" / "out" / "k1-demo.jsonld"
    product_path.parent.mkdir(parents=True)
    product_path.write_text("{}", encoding="utf-8")
    result = stub_handoff(product_path, conforms=True, root=tmp_path)
    assert result.ok
    assert result.mode == "stub"
    assert result.receipt["raw_on_publish_path"] is False
    assert result.receipt["would_publish"] == "data/out/k1-demo.jsonld"


def test_http_handoff_skips_when_shacl_fails(tmp_path: Path) -> None:
    result = http_handoff(
        _product(),
        tmp_path / "out.jsonld",
        conforms=False,
        root=tmp_path,
        base_url="http://127.0.0.1:9",
    )
    assert not result.ok
    assert result.receipt["status"] == "skipped"
    assert result.receipt["raw_on_publish_path"] is False


def test_http_handoff_posts_jsonld_without_raw(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict = {}

    class FakeResp:
        status = 201

        def read(self) -> bytes:
            return b'{"status":"accepted","raw_on_publish_path":false}'

        def __enter__(self) -> FakeResp:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    def fake_urlopen(req: Request, timeout: float = 0) -> FakeResp:
        captured["url"] = req.full_url
        captured["body"] = req.data
        captured["content_type"] = req.get_header("Content-type")
        return FakeResp()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.delenv("RATIO_ODS_BEARER", raising=False)
    monkeypatch.delenv("RATIO_ODS_CLIENT_ID", raising=False)
    monkeypatch.delenv("RATIO_ODS_CLIENT_SECRET", raising=False)
    product = _product()
    result = http_handoff(
        product,
        tmp_path / "k1.jsonld",
        conforms=True,
        root=tmp_path,
        base_url="http://industry.test:8787",
    )
    assert result.ok
    assert captured["url"] == "http://industry.test:8787/products"
    assert captured["content_type"] == "application/ld+json"
    body = captured["body"].decode("utf-8")
    assert "RATIO_RAW_STUB" not in body
    assert json.loads(body)["id"] == product["id"]
    assert result.receipt["raw_on_publish_path"] is False


def test_http_handoff_treats_http_error_as_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_urlopen(req: Request, timeout: float = 0) -> None:
        raise HTTPError(
            req.full_url, 503, "unavailable", hdrs=None, fp=BytesIO(b"down")
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = http_handoff(
        _product(),
        tmp_path / "k1.jsonld",
        conforms=True,
        root=tmp_path,
        base_url="http://industry.test",
    )
    assert not result.ok
    assert result.receipt["httpStatus"] == 503
    assert result.receipt["raw_on_publish_path"] is False


def test_http_handoff_treats_url_error_as_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_urlopen(req: Request, timeout: float = 0) -> None:
        raise URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = http_handoff(
        _product(),
        tmp_path / "k1.jsonld",
        conforms=True,
        root=tmp_path,
        base_url="http://industry.test",
    )
    assert not result.ok
    assert "ratio-serve" in result.receipt["hint"]


def test_handoff_unknown_mode_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown ods mode"):
        handoff(
            mode="ftp",
            product=_product(),
            product_path=tmp_path / "x.jsonld",
            conforms=True,
            root=tmp_path,
        )


def test_resolve_bearer_prefers_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATIO_ODS_BEARER", "env-token")
    monkeypatch.delenv("RATIO_ODS_CLIENT_ID", raising=False)
    assert resolve_bearer() == "env-token"


def test_fetch_l3_bearer_returns_none_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("RATIO_ODS_CLIENT_ID", raising=False)
    monkeypatch.delenv("RATIO_ODS_CLIENT_SECRET", raising=False)
    assert fetch_l3_bearer() is None


def test_fetch_l3_bearer_reads_access_token(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResp:
        def read(self) -> bytes:
            return b'{"data":{"access_token":"jwt-from-l3"}}'

        def __enter__(self) -> FakeResp:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: FakeResp())
    token = fetch_l3_bearer(client_id="id", client_secret="secret", l3_url="http://l3")
    assert token == "jwt-from-l3"
