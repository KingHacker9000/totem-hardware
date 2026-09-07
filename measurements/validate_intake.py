#!/usr/bin/env python3
"""Validate Totem prototype part-intake manifests without third-party dependencies."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCHEMA = "totem.part-intake/v1"
MATCH = {"unverified", "match", "substitution"}
RECEIPT = {"pending", "received", "missing", "rejected"}
IDENTITY_FIELDS = (
    "component_id", "manufacturer", "ordered_sku", "received_sku",
    "revision_or_pcb_marking", "serial_or_lot", "supplier",
)


def fingerprint(item: dict) -> str:
    payload = {key: item.get(key) for key in IDENTITY_FIELDS}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate(path: Path, require_ready: bool) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read JSON: {exc}"]

    errors: list[str] = []
    if data.get("schema_version") != SCHEMA:
        errors.append(f"schema_version must be {SCHEMA!r}")
    if data.get("prototype") != "prototype-v1":
        errors.append("prototype must be 'prototype-v1'")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        return errors + ["items must be a non-empty array"]

    seen: set[str] = set()
    for index, item in enumerate(items):
        where = f"items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        cid = item.get("component_id")
        if not isinstance(cid, str) or not cid:
            errors.append(f"{where}.component_id must be non-empty")
            continue
        if cid in seen:
            errors.append(f"duplicate component_id {cid!r}")
        seen.add(cid)
        state = item.get("receipt_state")
        match = item.get("bom_match")
        if state not in RECEIPT:
            errors.append(f"{cid}: receipt_state must be one of {sorted(RECEIPT)}")
        if match not in MATCH:
            errors.append(f"{cid}: bom_match must be one of {sorted(MATCH)}")
        if match == "substitution" and not item.get("substitution_reason"):
            errors.append(f"{cid}: substitution requires substitution_reason")
        photos = item.get("evidence_photos")
        if not isinstance(photos, list):
            errors.append(f"{cid}: evidence_photos must be an array")
        blockers = item.get("measurement_blockers")
        if not isinstance(blockers, list):
            errors.append(f"{cid}: measurement_blockers must be an array")
            blockers = []
        ready = item.get("measurement_ready") is True
        if ready:
            if state != "received":
                errors.append(f"{cid}: measurement_ready requires receipt_state='received'")
            if match not in {"match", "substitution"}:
                errors.append(f"{cid}: measurement_ready requires resolved bom_match")
            if blockers:
                errors.append(f"{cid}: measurement_ready requires no measurement_blockers")
            if not item.get("received_sku") and not item.get("revision_or_pcb_marking") and not item.get("serial_or_lot"):
                errors.append(f"{cid}: measurement_ready requires at least one received identity discriminator")
            expected = fingerprint(item)
            if item.get("identity_lock") != expected:
                errors.append(f"{cid}: identity_lock mismatch; expected {expected}")
        elif item.get("identity_lock") is not None:
            errors.append(f"{cid}: identity_lock is only valid for measurement-ready received items")
        if require_ready and not ready:
            errors.append(f"{cid}: not measurement-ready")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--require-ready", action="store_true", help="require every item to be ready for T909")
    parser.add_argument("--fingerprints", action="store_true", help="print computed identity fingerprints")
    args = parser.parse_args()
    errors = validate(args.manifest, args.require_ready)
    if args.fingerprints:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        for item in data.get("items", []):
            print(f"{item.get('component_id')}: {fingerprint(item)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {args.manifest} conforms to {SCHEMA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
