from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PACKAGE_VERSION = "totem.cad-package/v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def create_package_manifest(
    build_dir: Path,
    fixture: Path,
    source_revision: str,
    generated_at: str,
    requirements: Path,
) -> dict[str, object]:
    build_manifest_path = build_dir / "manifest.json"
    build_manifest = load_json(build_manifest_path)
    if build_manifest.get("manifest_version") != "totem.cad-build/v1":
        raise ValueError("unsupported CAD build manifest")
    if build_manifest.get("non_production") is not True:
        raise ValueError("T923 packaging only accepts explicitly non-production synthetic outputs")

    artifacts: list[dict[str, str]] = []
    for path in sorted(build_dir.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.name == "package-manifest.json":
            continue
        artifacts.append({"path": path.name, "sha256": sha256(path)})

    return {
        "package_version": PACKAGE_VERSION,
        "non_production": True,
        "source_revision": source_revision,
        "generated_at": generated_at,
        "measurement_input": {
            "path": fixture.as_posix(),
            "sha256": sha256(fixture),
            "kind": load_json(fixture).get("fixture_kind"),
        },
        "toolchain": {
            "requirements_path": requirements.as_posix(),
            "requirements_sha256": sha256(requirements),
        },
        "build_manifest": {
            "path": "manifest.json",
            "sha256": sha256(build_manifest_path),
        },
        "artifacts": artifacts,
    }


def write_package_manifest(
    build_dir: Path,
    fixture: Path,
    source_revision: str,
    generated_at: str,
    requirements: Path,
) -> Path:
    manifest = create_package_manifest(build_dir, fixture, source_revision, generated_at, requirements)
    target = build_dir / "package-manifest.json"
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def verify_package_manifest(build_dir: Path, fixture: Path, requirements: Path) -> None:
    path = build_dir / "package-manifest.json"
    manifest = load_json(path)
    if manifest.get("package_version") != PACKAGE_VERSION or manifest.get("non_production") is not True:
        raise ValueError("invalid CAD package manifest contract")

    measurement = manifest.get("measurement_input")
    toolchain = manifest.get("toolchain")
    build_manifest = manifest.get("build_manifest")
    artifacts = manifest.get("artifacts")
    if not isinstance(measurement, dict) or measurement.get("sha256") != sha256(fixture):
        raise ValueError("measurement input hash mismatch")
    if not isinstance(toolchain, dict) or toolchain.get("requirements_sha256") != sha256(requirements):
        raise ValueError("toolchain requirements hash mismatch")
    build_manifest_path = build_dir / "manifest.json"
    if not isinstance(build_manifest, dict) or build_manifest.get("sha256") != sha256(build_manifest_path):
        raise ValueError("build manifest hash mismatch")
    if not isinstance(artifacts, list):
        raise ValueError("artifacts must be a list")

    expected = {entry["path"]: entry["sha256"] for entry in artifacts if isinstance(entry, dict)}
    actual = {
        item.name: sha256(item)
        for item in build_dir.iterdir()
        if item.is_file() and item.name != "package-manifest.json"
    }
    if expected != actual:
        raise ValueError("artifact set/hash mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description="Package or verify reproducible Totem CAD provenance")
    parser.add_argument("--build-dir", type=Path, default=Path("cad/build"))
    parser.add_argument("--fixture", type=Path, default=Path("cad/fixtures/synthetic-layout.json"))
    parser.add_argument("--requirements", type=Path, default=Path("cad/requirements.txt"))
    parser.add_argument("--source-revision")
    parser.add_argument("--generated-at")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        verify_package_manifest(args.build_dir, args.fixture, args.requirements)
        return 0
    if not args.source_revision or not args.generated_at:
        parser.error("--source-revision and --generated-at are required when creating a package manifest")
    write_package_manifest(args.build_dir, args.fixture, args.source_revision, args.generated_at, args.requirements)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
