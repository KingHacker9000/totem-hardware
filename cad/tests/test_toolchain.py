from __future__ import annotations

from pathlib import Path

import pytest

from toolchain import (
    CadInputError,
    axis_aligned_clearance_mm,
    build_smoke_parts,
    collision_volume,
    resolve_build_inputs,
    translated_box,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "cad" / "fixtures" / "synthetic-layout.json"


def test_synthetic_fixture_resolves_existing_measurement_contract() -> None:
    inputs, fixture = resolve_build_inputs(FIXTURE)
    assert fixture["non_production"] is True
    assert inputs.width_mm == pytest.approx(100.0)
    assert inputs.height_mm == pytest.approx(50.0)
    assert inputs.hole_diameter_mm == pytest.approx(3.0)


def test_smoke_parts_have_expected_abstract_envelopes() -> None:
    inputs, _ = resolve_build_inputs(FIXTURE)
    parts = build_smoke_parts(inputs)
    primary_box = parts["synthetic_primary"].val().BoundingBox()
    coupon_box = parts["synthetic_coupon"].val().BoundingBox()
    assert (primary_box.xlen, primary_box.ylen, primary_box.zlen) == pytest.approx((100.0, 50.0, 20.0))
    assert (coupon_box.xlen, coupon_box.ylen, coupon_box.zlen) == pytest.approx((30.0, 12.0, 3.0))


def test_collision_and_clearance_helpers_distinguish_cases() -> None:
    _, fixture = resolve_build_inputs(FIXTURE)
    probe = fixture["clearance_probe"]
    a = translated_box(probe["size_mm"], probe["offset_a_mm"])
    clear = translated_box(probe["size_mm"], probe["offset_b_clear_mm"])
    collision = translated_box(probe["size_mm"], probe["offset_b_collision_mm"])

    assert collision_volume(a, clear) == pytest.approx(0.0)
    assert axis_aligned_clearance_mm(a, clear) == pytest.approx(4.0)
    assert collision_volume(a, collision) > 0.0
    assert axis_aligned_clearance_mm(a, collision) == pytest.approx(0.0)


def test_t919_rejects_unmarked_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "bad.json"
    fixture.write_text('{"fixture_kind":"totem.synthetic-cad/v1","non_production":false}', encoding="utf-8")
    with pytest.raises(CadInputError, match="non-production synthetic"):
        resolve_build_inputs(fixture)
