from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cadquery as cq


MEASUREMENT_SCHEMA = "totem.measurements/v1"
SYNTHETIC_FIXTURE_KIND = "totem.synthetic-cad/v1"


class CadInputError(ValueError):
    pass


@dataclass(frozen=True)
class BuildInputs:
    width_mm: float
    height_mm: float
    depth_mm: float
    hole_diameter_mm: float
    coupon_width_mm: float
    coupon_height_mm: float
    coupon_depth_mm: float
    coupon_slot_width_mm: float


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_measurements(path: Path) -> dict[str, Any]:
    data = _load_json(path)
    if data.get("schema_version") != MEASUREMENT_SCHEMA:
        raise CadInputError(f"unsupported measurement schema: {data.get('schema_version')!r}")
    if data.get("units") != "mm":
        raise CadInputError("CAD input must use millimetres")
    status = data.get("dataset_status")
    if status not in {"synthetic", "measured"}:
        raise CadInputError(f"unsupported dataset_status: {status!r}")
    if status == "synthetic" and data.get("non_production") is not True:
        raise CadInputError("synthetic measurement data must declare non_production=true")
    return data


def _component(data: dict[str, Any], component_id: str) -> dict[str, Any]:
    for component in data.get("components", []):
        if component.get("id") == component_id:
            return component
    raise CadInputError(f"missing component {component_id!r}")


def _measurement(items: list[dict[str, Any]], name: str) -> float:
    for item in items:
        if item.get("name") == name:
            value = item.get("value_mm")
            if not isinstance(value, (int, float)) or value <= 0:
                raise CadInputError(f"measurement {name!r} must be a positive number")
            return float(value)
    raise CadInputError(f"missing measurement {name!r}")


def resolve_build_inputs(fixture_path: Path) -> tuple[BuildInputs, dict[str, Any]]:
    fixture = _load_json(fixture_path)
    if fixture.get("fixture_kind") != SYNTHETIC_FIXTURE_KIND or fixture.get("non_production") is not True:
        raise CadInputError("T919 fixture must be explicitly marked non-production synthetic data")

    measurement_path = (fixture_path.parent / fixture["measurement_dataset"]).resolve()
    measurements = load_measurements(measurement_path)
    if measurements.get("dataset_status") != "synthetic":
        raise CadInputError("T919 smoke geometry only accepts synthetic measurement datasets")

    primary = fixture["primary"]
    component = _component(measurements, primary["component_id"])
    width = _measurement(component.get("measurements", []), primary["width_measurement"])
    height = _measurement(component.get("measurements", []), primary["height_measurement"])

    feature = next((f for f in component.get("features", []) if f.get("name") == primary["hole_feature"]), None)
    if feature is None:
        raise CadInputError(f"missing feature {primary['hole_feature']!r}")
    hole_diameter = _measurement(feature.get("measurements", []), primary["hole_measurement"])

    coupon = fixture["coupon"]
    inputs = BuildInputs(
        width_mm=width,
        height_mm=height,
        depth_mm=float(primary["depth_mm"]),
        hole_diameter_mm=hole_diameter,
        coupon_width_mm=float(coupon["width_mm"]),
        coupon_height_mm=float(coupon["height_mm"]),
        coupon_depth_mm=float(coupon["depth_mm"]),
        coupon_slot_width_mm=float(coupon["slot_width_mm"]),
    )
    return inputs, fixture


def build_smoke_parts(inputs: BuildInputs) -> dict[str, cq.Workplane]:
    primary = (
        cq.Workplane("XY")
        .box(inputs.width_mm, inputs.height_mm, inputs.depth_mm)
        .faces(">Z")
        .workplane()
        .hole(inputs.hole_diameter_mm)
    )
    coupon = (
        cq.Workplane("XY")
        .box(inputs.coupon_width_mm, inputs.coupon_height_mm, inputs.coupon_depth_mm)
        .faces(">Z")
        .workplane()
        .rect(inputs.coupon_slot_width_mm, inputs.coupon_height_mm * 0.55)
        .cutThruAll()
    )
    return {"synthetic_primary": primary, "synthetic_coupon": coupon}


def collision_volume(a: cq.Shape, b: cq.Shape) -> float:
    return a.intersect(b).Volume()


def axis_aligned_clearance_mm(a: cq.Shape, b: cq.Shape) -> float:
    aa = a.BoundingBox()
    bb = b.BoundingBox()
    gaps = [
        max(bb.xmin - aa.xmax, aa.xmin - bb.xmax, 0.0),
        max(bb.ymin - aa.ymax, aa.ymin - bb.ymax, 0.0),
        max(bb.zmin - aa.zmax, aa.zmin - bb.zmax, 0.0),
    ]
    if collision_volume(a, b) > 1e-9:
        return 0.0
    positive = [gap for gap in gaps if gap > 0.0]
    return min(positive) if positive else 0.0


def translated_box(size_mm: list[float], offset_mm: list[float]) -> cq.Shape:
    shape = cq.Workplane("XY").box(*map(float, size_mm)).val()
    return shape.moved(cq.Location(cq.Vector(*map(float, offset_mm))))
