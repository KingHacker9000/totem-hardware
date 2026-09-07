#!/usr/bin/env python3
"""Validate Totem measurement datasets without third-party dependencies.

This is intentionally conservative: it checks the invariants T909/T910 rely on and
refuses production/measured datasets containing unresolved CAD-driving values.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_COMPONENT_IDS = {
    "raspberry_pi_5",
    "active_cooler",
    "touch_display_2_5in",
    "respeaker_lite",
    "speaker",
    "led_ring",
    "momentary_buttons",
    "privacy_switch",
    "power_and_service_cables",
    "fasteners_and_inserts",
}
VALID_STATUS = {"template", "synthetic", "measured"}
VALID_SOURCE = {"unmeasured", "measured", "reference", "derived"}


def fail(message: str) -> None:
    raise ValueError(message)


def check_measurement(m: dict, path: str, dataset_status: str) -> None:
    for key in ("name", "value_mm", "source", "cad_driving"):
        if key not in m:
            fail(f"{path}: missing {key}")
    if m["source"] not in VALID_SOURCE:
        fail(f"{path}: invalid source {m['source']!r}")
    value = m["value_mm"]
    if value is not None and not isinstance(value, (int, float)):
        fail(f"{path}: value_mm must be numeric or null")
    if not isinstance(m["cad_driving"], bool):
        fail(f"{path}: cad_driving must be boolean")
    if m["source"] == "measured" and not m.get("method"):
        fail(f"{path}: measured values must record method")
    if dataset_status == "measured" and m["cad_driving"]:
        if m["source"] != "measured":
            fail(f"{path}: measured dataset has CAD-driving value not sourced from a physical measurement")
        if value is None:
            fail(f"{path}: measured dataset has unresolved CAD-driving null")


def validate(data: dict) -> None:
    if data.get("schema_version") != "totem.measurements/v1":
        fail("schema_version must be totem.measurements/v1")
    status = data.get("dataset_status")
    if status not in VALID_STATUS:
        fail(f"dataset_status must be one of {sorted(VALID_STATUS)}")
    if data.get("prototype") != "prototype-v1":
        fail("prototype must be prototype-v1")
    if data.get("units") != "mm":
        fail("units must be mm")
    if status in {"template", "synthetic"} and data.get("non_production") is not True:
        fail(f"{status} datasets must set non_production=true")
    if status == "measured" and data.get("non_production") is True:
        fail("measured datasets must not be marked non_production")

    datum = data.get("datum_convention")
    if not isinstance(datum, dict) or not datum.get("origin") or not datum.get("orientation_rule"):
        fail("datum_convention must define origin and orientation_rule")
    axes = datum.get("axes") if isinstance(datum, dict) else None
    if not isinstance(axes, dict) or set(axes) != {"x", "y", "z"}:
        fail("datum_convention.axes must define exactly x, y, z")

    components = data.get("components")
    if not isinstance(components, list) or not components:
        fail("components must be a non-empty array")
    ids = set()
    for i, component in enumerate(components):
        path = f"components[{i}]"
        cid = component.get("id")
        if not isinstance(cid, str) or not cid:
            fail(f"{path}: missing id")
        if cid in ids:
            fail(f"{path}: duplicate id {cid}")
        ids.add(cid)
        if not component.get("selected_part") or not component.get("orientation"):
            fail(f"{path}: selected_part and orientation are required")
        for j, m in enumerate(component.get("measurements", [])):
            check_measurement(m, f"{path}.measurements[{j}]", status)
        features = component.get("features", [])
        if not isinstance(features, list):
            fail(f"{path}.features must be an array")
        for j, feature in enumerate(features):
            fpath = f"{path}.features[{j}]"
            if not feature.get("name") or not feature.get("kind"):
                fail(f"{fpath}: name and kind are required")
            for k, m in enumerate(feature.get("measurements", [])):
                check_measurement(m, f"{fpath}.measurements[{k}]", status)

    if status in {"template", "measured"}:
        missing = REQUIRED_COMPONENT_IDS - ids
        if missing:
            fail(f"dataset is missing prototype-v1 component templates: {sorted(missing)}")

    coupons = data.get("fit_coupons")
    if not isinstance(coupons, list):
        fail("fit_coupons must be an array")
    for i, coupon in enumerate(coupons):
        for key in ("id", "purpose", "nominal_mm", "measured_mm", "result"):
            if key not in coupon:
                fail(f"fit_coupons[{i}]: missing {key}")
        if status == "measured" and coupon["result"] == "not_tested":
            fail(f"fit_coupons[{i}]: measured dataset cannot retain not_tested coupon")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: measurements/validate.py DATASET.json [DATASET.json ...]", file=sys.stderr)
        return 2
    for raw in sys.argv[1:]:
        path = Path(raw)
        try:
            validate(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            return 1
        print(f"PASS {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
