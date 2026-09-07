from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import cadquery as cq

from cad.toolchain import build_smoke_parts, resolve_build_inputs


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _shape_metrics(part: cq.Workplane) -> dict[str, object]:
    shape = part.val()
    box = shape.BoundingBox()
    return {
        "volume_mm3": round(shape.Volume(), 6),
        "bbox_mm": [
            round(box.xlen, 6),
            round(box.ylen, 6),
            round(box.zlen, 6),
        ],
    }


def build(fixture: Path, output: Path) -> dict[str, object]:
    inputs, fixture_data = resolve_build_inputs(fixture)
    parts = build_smoke_parts(inputs)

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    manifest: dict[str, object] = {
        "manifest_version": "totem.cad-build/v1",
        "non_production": True,
        "fixture_kind": fixture_data["fixture_kind"],
        "source_fixture": fixture.as_posix(),
        "exports": {},
    }

    exports: dict[str, object] = {}
    for name, part in sorted(parts.items()):
        step_path = output / f"{name}.step"
        stl_path = output / f"{name}.stl"
        cq.exporters.export(part, str(step_path))
        cq.exporters.export(part, str(stl_path), tolerance=0.01, angularTolerance=0.1)
        exports[name] = {
            "metrics": _shape_metrics(part),
            "step": {"path": step_path.name, "sha256": _sha256(step_path)},
            "stl": {"path": stl_path.name, "sha256": _sha256(stl_path)},
        }

    manifest["exports"] = exports
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def verify_round_trip(output: Path, manifest: dict[str, object]) -> None:
    exports = manifest["exports"]
    assert isinstance(exports, dict)
    for name, entry in exports.items():
        assert isinstance(entry, dict)
        metrics = entry["metrics"]
        assert isinstance(metrics, dict)
        imported = cq.importers.importStep(str(output / entry["step"]["path"]))
        imported_metrics = _shape_metrics(imported)
        if imported_metrics != metrics:
            raise RuntimeError(f"STEP round-trip changed geometry metrics for {name}: {imported_metrics} != {metrics}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build non-production T919 CAD smoke geometry")
    parser.add_argument("--fixture", type=Path, default=Path("cad/fixtures/synthetic-layout.json"))
    parser.add_argument("--output", type=Path, default=Path("cad/build"))
    parser.add_argument("--verify-round-trip", action="store_true")
    args = parser.parse_args()

    manifest = build(args.fixture, args.output)
    if args.verify_round_trip:
        verify_round_trip(args.output, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
