# CAD toolchain (T919 prep)

This directory is infrastructure for the future **measured** T910 CAD lane. It intentionally does **not** contain the Totem enclosure or any BOM-derived final geometry.

## Environment

The prep toolchain uses CadQuery with Python 3.11. Dependencies are pinned in `requirements.txt` so a fresh checkout and CI use the same major geometry stack.

```bash
python -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r cad/requirements.txt
```

## Input boundary

`toolchain.py` reads the versioned `totem.measurements/v1` contract created by T917. The T919 smoke path accepts only a `dataset_status: synthetic` measurement dataset and requires `non_production: true`. The fixture in `cad/fixtures/synthetic-layout.json` points at `measurements/examples/synthetic.json` and maps measurement names into abstract geometry parameters.

T910 should reuse `load_measurements()` and the component/feature lookup boundary, but replace the synthetic fixture with T909's completed measured dataset. T910 must not copy dimensions from vendor pages or this synthetic fixture.

## Build and test

From the repository root:

```bash
python cad/build.py --verify-round-trip
python -m pytest cad/tests -q
```

The build clears `cad/build/`, emits STEP and STL for two deliberately abstract smoke parts, then writes `manifest.json` containing geometry metrics and SHA-256 hashes of the produced files. STEP is re-imported and its bounding box/volume metrics are checked against the source shape. This validates transforms, booleans, serialization, and reconstruction without asserting any real Totem fit.

CadQuery's STEP/STL exporters are the supported deterministic-from-source outputs for this prep lane. 3MF is deliberately not promised by this pinned path; T910 may add it only if the selected exporter is validated rather than generating an unverified file.

## Clearance/collision helpers

`collision_volume()` uses solid intersection volume. `axis_aligned_clearance_mm()` returns the smallest positive AABB separation and returns zero for collision/contact. The tests exercise both a known-clear and known-colliding synthetic pair. These helpers are scaffolding, not a substitute for later measured-part clearance checks.

## Guardrails

- Everything in `cad/fixtures/` for T919 is synthetic and non-production.
- No Raspberry Pi, display, audio board, LED, cooler, connector, or chassis dimension is encoded here.
- Generated `cad/build/` output is disposable and should not become source of truth.
- T909 remains the authority for physical dimensions; T910 remains blocked until those measurements exist.
- T910 should use small measured fit coupons before committing to large enclosure prints.
