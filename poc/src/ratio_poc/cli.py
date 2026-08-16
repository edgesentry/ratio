"""Minimal Ratio PoC pipeline: thin TD file → local raw → shareable product → SHACL → ODS stub."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pyshacl import validate as shacl_validate
from rdflib import Graph

from ratio_poc.ods import handoff
from ratio_poc import queue as product_queue

# poc/src/ratio_poc/cli.py → repo root
ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schemas"
TD_DIR = ROOT / "examples" / "td"
CONTEXT_PATH = SCHEMA_DIR / "shareable-product.context.jsonld"
SHACL_PATH = SCHEMA_DIR / "shareable-product.shacl.ttl"
DATA_RAW = ROOT / "data" / "raw"
DATA_OUT = ROOT / "data" / "out"

SCENARIOS = {
    "K1": {
        "domain": "kitakyushu_factory",
        "source_device": "did:example:kitakyushu-factory-robot-01",
        "produced_by": "urn:ratio:node:kitakyushu-poc-01",
        "td_path": TD_DIR / "k1-robot.td.json",
        "physical_context": {"motorRPM": 1450, "temperatureCelsius": 42.5},
        "raw_prefix": "raw_wave",
    },
    "S1": {
        "domain": "setouchi_maritime",
        "source_device": "did:example:setouchi-vessel-engine-vib-01",
        "produced_by": "urn:ratio:node:setouchi-poc-01",
        "td_path": TD_DIR / "s-engine-vib.td.json",
        "physical_context": {"shaftRPM": 98, "temperatureCelsius": 61.2},
        "raw_prefix": "raw_shaft",
    },
    "S2": {
        "domain": "setouchi_maritime",
        "source_device": "did:example:setouchi-vessel-engine-vib-01",
        "produced_by": "urn:ratio:node:setouchi-poc-01",
        "td_path": TD_DIR / "s-engine-vib.td.json",
        "physical_context": {"shaftRPM": 98, "temperatureCelsius": 61.2},
        "raw_prefix": "raw_shaft",
        "queue": True,
    },
}


def load_td(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"TD file not found: {path}")
    td = json.loads(path.read_text(encoding="utf-8"))
    for key in ("id", "title"):
        if key not in td:
            raise SystemExit(f"TD missing required field '{key}': {path}")
    return td


def load_context() -> dict:
    return json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))["@context"]


def write_raw(scenario: str, cfg: dict, stamp: str) -> tuple[Path, str]:
    raw_dir = DATA_RAW / scenario
    raw_dir.mkdir(parents=True, exist_ok=True)
    name = f"{cfg['raw_prefix']}_{stamp}.bin"
    path = raw_dir / name
    path.write_bytes(b"RATIO_RAW_STUB\n" + stamp.encode() + b"\n")
    pointer = f"local://storage/{scenario}/{name}"
    return path, pointer


def build_product(
    scenario: str,
    cfg: dict,
    product_id: str,
    ts: str,
    raw_pointer: str,
    *,
    use_queue: bool = False,
) -> dict:
    product = {
        "@context": load_context(),
        "@type": ["ShareableProduct"],
        "id": product_id,
        "sourceDevice": cfg["source_device"],
        "timestamp": ts,
        "domain": cfg["domain"],
        "scenario": scenario,
        "inference": {
            "task": "anomaly_detection",
            "result": "vibration_abnormal",
            "confidence": 0.96 if scenario == "K1" else 0.91,
            "physicalContext": cfg["physical_context"],
        },
        "dataGovernance": {
            "policyRef": "urn:odrl:policy:internal-only-rawdata",
            "rawDataPointer": raw_pointer,
        },
        "provenance": {"producedBy": cfg["produced_by"]},
    }
    if use_queue:
        product["provenance"]["firstBufferedAt"] = ts
    return product


def run_shacl(product: dict) -> tuple[bool, str]:
    data = Graph()
    data.parse(data=json.dumps(product), format="json-ld")
    shapes = Graph()
    shapes.parse(SHACL_PATH, format="turtle")
    conforms, _, report_text = shacl_validate(
        data,
        shacl_graph=shapes,
        inference="rdfs",
        abort_on_first=False,
        meta_shacl=False,
        advanced=True,
        inplace=False,
    )
    return bool(conforms), report_text


def _write_out(product: dict, stem: str) -> Path:
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    path = DATA_OUT / f"{stem}.jsonld"
    path.write_text(
        json.dumps(product, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


def _attempt_handoff(
    product: dict,
    product_path: Path,
    conforms: bool,
    ods_mode: str,
    ods_url: str | None,
    stem: str,
) -> tuple[bool, Path]:
    result = handoff(
        mode=ods_mode,
        product=product,
        product_path=product_path,
        conforms=conforms,
        root=ROOT,
        ods_url=ods_url,
    )
    receipt_path = DATA_OUT / f"{stem}.ods-{result.mode}.json"
    receipt_path.write_text(
        json.dumps(result.receipt, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"[5] ODS handoff mode={result.mode} ok={result.ok} → {receipt_path.relative_to(ROOT)}"
    )
    return result.ok, receipt_path


def flush_queue(ods_mode: str, ods_url: str | None) -> int:
    pending = product_queue.list_queued(ROOT)
    if not pending:
        print("OK: queue empty")
        return 0
    print(f"[flush] {len(pending)} queued product(s)")
    failures = 0
    for qpath in pending:
        stem = qpath.stem
        product = product_queue.load_queued(qpath)
        product_path = _write_out(product, stem)
        conforms = bool((product.get("dataGovernance") or {}).get("shaclConforms", True))
        print(f"[flush] {stem} …")
        ok, _ = _attempt_handoff(product, product_path, conforms, ods_mode, ods_url, stem)
        if ok:
            product_queue.dequeue(ROOT, stem)
            print(f"[flush] dequeued {stem}")
        else:
            failures += 1
            print(f"[flush] still queued {stem}", file=sys.stderr)
    product_queue.refresh_depths(ROOT)
    if failures:
        print(f"FAIL: {failures} still queued (link down or industry error)", file=sys.stderr)
        return 2
    print("OK: queue flushed; raw stayed local")
    return 0


def run(
    scenario: str,
    ods_mode: str = "stub",
    ods_url: str | None = None,
    *,
    offline: bool = False,
    td_path: Path | None = None,
) -> int:
    if scenario not in SCENARIOS:
        raise SystemExit(f"unknown scenario: {scenario}")
    cfg = SCENARIOS[scenario]
    path = Path(td_path) if td_path else Path(cfg["td_path"])
    td = load_td(path)
    use_queue = bool(cfg.get("queue"))
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = now.strftime("%Y%m%d_%H%M%S")
    product_id = f"urn:uuid:{uuid.uuid4()}"
    stem = f"{scenario.lower()}-{product_id.split(':')[-1][:8]}"

    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        rel = path
    print(f"[1] thin TD: {td['id']} — {td['title']} ← {rel}")
    raw_path, pointer = write_raw(scenario, cfg, stamp)
    print(f"[2] raw custody: {raw_path.relative_to(ROOT)} ({pointer})")

    product = build_product(
        scenario, cfg, product_id, ts, pointer, use_queue=use_queue
    )
    product_path = _write_out(product, stem)
    print(f"[3] shareable product: {product_path.relative_to(ROOT)}")

    conforms, report = run_shacl(product)
    report_path = DATA_OUT / f"{stem}.shacl.txt"
    report_path.write_text(report, encoding="utf-8")
    product["dataGovernance"]["shaclConforms"] = conforms
    product_path.write_text(
        json.dumps(product, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[4] SHACL conforms={conforms} → {report_path.relative_to(ROOT)}")

    if not conforms:
        print("FAIL: shareable product did not conform to SHACL", file=sys.stderr)
        return 1

    if use_queue:
        qpath = product_queue.enqueue(ROOT, product, stem)
        product = product_queue.load_queued(qpath)
        product_path.write_text(
            json.dumps(product, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(
            f"[4b] queued → {qpath.relative_to(ROOT)} "
            f"(depth={product['provenance'].get('queueDepth')})"
        )

    if use_queue and (offline or ods_mode == "stub"):
        # S2: buffering onboard is success; flush when link returns.
        print("OK: buffered onboard (store-and-forward); raw stayed local")
        print("     later: uv run ratio-poc --flush-queue --ods http")
        return 0

    if offline:
        print("OK: offline mode; product kept local; raw stayed local")
        return 0

    ok, _ = _attempt_handoff(product, product_path, conforms, ods_mode, ods_url, stem)

    if use_queue:
        if ok:
            product_queue.dequeue(ROOT, stem)
            product_queue.refresh_depths(ROOT)
            print("OK: forwarded from queue; raw stayed local")
            return 0
        print(
            "OK: link/industry unavailable — kept in queue (store-and-forward)",
            file=sys.stderr,
        )
        print("     later: uv run ratio-poc --flush-queue --ods http")
        return 0  # buffering is success for S2

    if not ok:
        print("FAIL: ODS/industry handoff failed", file=sys.stderr)
        return 2
    print("OK: raw stayed local; shareable product handed off")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Ratio minimal PoC pipeline")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS),
        default="K1",
        help="PoC scenario (default K1)",
    )
    parser.add_argument(
        "--ods",
        choices=("stub", "http"),
        default="stub",
        help="ODS handoff mode: stub (default) or http industry URL",
    )
    parser.add_argument(
        "--ods-url",
        default=None,
        help="Industry base URL for --ods http (default http://127.0.0.1:8787 or RATIO_ODS_URL)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Do not attempt handoff (S2: enqueue only)",
    )
    parser.add_argument(
        "--td",
        type=Path,
        default=None,
        help="Override thin WoT TD JSON path (default: examples/td per scenario)",
    )
    parser.add_argument(
        "--flush-queue",
        action="store_true",
        help="Publish all queued shareable products (S2 store-and-forward)",
    )
    args = parser.parse_args()
    if args.flush_queue:
        raise SystemExit(flush_queue(args.ods, args.ods_url))
    raise SystemExit(
        run(
            args.scenario,
            ods_mode=args.ods,
            ods_url=args.ods_url,
            offline=args.offline,
            td_path=args.td,
        )
    )


if __name__ == "__main__":
    main()
