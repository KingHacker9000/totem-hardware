from __future__ import annotations

import json
from pathlib import Path

import pytest

from cad.package import create_package_manifest, verify_package_manifest, write_package_manifest


def _fixture_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    fixture = tmp_path / "synthetic-layout.json"
    fixture.write_text('{"fixture_kind":"totem.synthetic-cad/v1","non_production":true}\n', encoding="utf-8")
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("cadquery==2.5.2\n", encoding="utf-8")
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "part.step").write_text("STEP-SYNTHETIC\n", encoding="utf-8")
    (build_dir / "part.stl").write_text("STL-SYNTHETIC\n", encoding="utf-8")
    (build_dir / "manifest.json").write_text(
        json.dumps({"manifest_version": "totem.cad-build/v1", "non_production": True}) + "\n",
        encoding="utf-8",
    )
    return build_dir, fixture, requirements


def test_package_manifest_is_deterministic_for_fixed_inputs(tmp_path: Path) -> None:
    build_dir, fixture, requirements = _fixture_tree(tmp_path)
    kwargs = dict(
        build_dir=build_dir,
        fixture=fixture,
        source_revision="abc123",
        generated_at="2026-09-07T04:00:00Z",
        requirements=requirements,
    )
    first = create_package_manifest(**kwargs)
    second = create_package_manifest(**kwargs)
    assert first == second
    assert first["non_production"] is True
    assert first["measurement_input"]["kind"] == "totem.synthetic-cad/v1"
    assert {entry["path"] for entry in first["artifacts"]} == {"manifest.json", "part.step", "part.stl"}


def test_verifier_detects_tampered_artifact(tmp_path: Path) -> None:
    build_dir, fixture, requirements = _fixture_tree(tmp_path)
    write_package_manifest(
        build_dir,
        fixture,
        "abc123",
        "2026-09-07T04:00:00Z",
        requirements,
    )
    verify_package_manifest(build_dir, fixture, requirements)
    (build_dir / "part.stl").write_text("TAMPERED\n", encoding="utf-8")
    with pytest.raises(ValueError, match="artifact set/hash mismatch"):
        verify_package_manifest(build_dir, fixture, requirements)


def test_verifier_detects_stale_measurement_input(tmp_path: Path) -> None:
    build_dir, fixture, requirements = _fixture_tree(tmp_path)
    write_package_manifest(
        build_dir,
        fixture,
        "abc123",
        "2026-09-07T04:00:00Z",
        requirements,
    )
    fixture.write_text('{"fixture_kind":"totem.synthetic-cad/v1","non_production":true,"changed":true}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="measurement input hash mismatch"):
        verify_package_manifest(build_dir, fixture, requirements)
