"""Local industry-service stub for Pull of shareable products only.

Simulates the provider-side industry API that ODS L2 (Web API Transfer)
would forward to. Serves JSON-LD from data/out — never data/raw.
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[3]
DATA_OUT = ROOT / "data" / "out"
DATA_RAW = ROOT / "data" / "raw"


def _catalog() -> list[dict]:
    items = []
    if not DATA_OUT.exists():
        return items
    for path in sorted(DATA_OUT.glob("*.jsonld")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        items.append(
            {
                "id": doc.get("id"),
                "scenario": doc.get("scenario"),
                "domain": doc.get("domain"),
                "file": path.name,
                "path": f"/products/{path.stem}",
            }
        )
    return items


def _load_product(stem: str) -> dict | None:
    path = DATA_OUT / f"{stem}.jsonld"
    if not path.is_file():
        # allow full uuid-ish stem match
        matches = list(DATA_OUT.glob(f"{stem}*.jsonld"))
        if len(matches) == 1:
            path = matches[0]
        else:
            return None
    return json.loads(path.read_text(encoding="utf-8"))


class Handler(BaseHTTPRequestHandler):
    server_version = "RatioIndustryStub/0.1"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[industry] {self.address_string()} - {fmt % args}")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Ratio-Raw-Exposed", "false")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, obj: object) -> None:
        body = json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path in ("/", "/health"):
            self._send_json(
                200,
                {
                    "service": "ratio-industry-stub",
                    "role": "provider industry API (L2 upstream stand-in)",
                    "raw_dir_exposed": False,
                    "products": len(_catalog()),
                },
            )
            return

        if path == "/products":
            self._send_json(200, {"products": _catalog()})
            return

        if path.startswith("/products/"):
            stem = path[len("/products/") :].rstrip("/")
            if ".." in stem or "/" in stem or stem.startswith("raw"):
                self._send_json(400, {"error": "invalid id"})
                return
            # Hard deny any attempt to reach raw store via this server.
            if DATA_RAW.exists() and (DATA_RAW / stem).exists():
                self._send_json(403, {"error": "raw custody is not served"})
                return
            doc = _load_product(stem)
            if doc is None:
                self._send_json(404, {"error": "not found"})
                return
            body = json.dumps(doc, indent=2, ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/ld+json; charset=utf-8")
            return

        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path.rstrip("/") != "/products":
            self._send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            doc = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid json"})
            return

        if "RATIO_RAW_STUB" in raw.decode("utf-8", errors="replace"):
            self._send_json(400, {"error": "raw payload refused"})
            return

        pointer = (doc.get("dataGovernance") or {}).get("rawDataPointer")
        if pointer and not str(pointer).startswith("local://"):
            self._send_json(400, {"error": "rawDataPointer must be local://"})
            return

        DATA_OUT.mkdir(parents=True, exist_ok=True)
        pid = str(doc.get("id", "unknown")).split(":")[-1][:8]
        scenario = str(doc.get("scenario", "xx")).lower()
        name = f"{scenario}-{pid}.jsonld"
        path_out = DATA_OUT / name
        path_out.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self._send_json(
            201,
            {
                "status": "accepted",
                "id": doc.get("id"),
                "pull": f"/products/{path_out.stem}",
                "raw_on_publish_path": False,
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ratio industry-service stub (shareable products only)"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(
        f"ratio-serve on http://{args.host}:{args.port} "
        f"(products from {DATA_OUT.relative_to(ROOT)}; raw never served)",
        flush=True,
    )
    httpd.serve_forever()


if __name__ == "__main__":
    main()
