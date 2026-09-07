# Prototype v1 measurement capture kit

This document is the T917 handoff into T909. It defines how to turn the actual purchased prototype parts into CAD-driving data without substituting vendor dimensions.

## Ground rules

- Start from `measurements/prototype-v1.template.json`; do not edit the synthetic fixture into production data.
- Keep `dataset_status: template` and `non_production: true` until every CAD-driving field required by the selected build is physically measured.
- Vendor dimensions may be copied only as `source: reference` and must use `cad_driving: false` until confirmed physically.
- Physical values use `source: measured`, a non-null `method`, and the tool used (for example `digital caliper`, `steel rule`, or `fit coupon`).
- Derived values must name their basis in `notes`; a derived value must not replace an available physical measurement for critical fit.
- All dimensions are millimetres. Record uncertainty when it affects fit.
- Preserve each component's declared datum/orientation. Never silently mirror coordinates to match the enclosure.

## Capture equipment

Bring the following to one measurement session so parts do not need repeated disassembly:

1. digital calipers with depth rod;
2. steel rule for cable/bend envelopes beyond caliper range;
3. small square or flat reference plate;
4. camera/phone for datum-labelled photos;
5. actual cables/plugs that will be installed, including strain reliefs;
6. the intended screws, nuts, washers, heat-set inserts and printer profile information;
7. painter's tape or removable labels for component IDs and datum arrows.

For every component, take at least one photo showing the nominated primary face and +X/+Y directions. Add photo paths to the dataset when storing them in the repository.

## One-pass capture order

### 1. Loose parts before assembly

Measure parts that become hard to access after stacking:

- momentary buttons: panel cutout, bezel OD, retainer/thread stack, rear terminal envelope;
- maintained privacy switch: cutout, body/bezel envelope, rear depth, terminal/wire envelope;
- heat-set inserts and screw heads;
- LED ring OD/ID/thickness, pad locations and wire exit;
- speaker enclosure, mounting holes, front/rear clearance and wire exit;
- reSpeaker Lite PCB, max component height, microphone acoustic centres, connector positions and control access.

### 2. Raspberry Pi 5 bare board

With the Pi unstacked, capture:

- PCB X/Y/thickness;
- each mounting-hole X/Y centre and diameter from the declared lower-left datum;
- USB/Ethernet/USB-C/micro-HDMI connector positions and metalwork projection;
- microSD removal path;
- fan-header position.

Then insert the actual Ethernet, USB service and USB-C power plugs and capture plug body plus strain-relief/bend envelopes. Board connector metalwork alone is not sufficient for enclosure openings.

### 3. Pi + Active Cooler installed

Install the exact cooler and record:

- installed height above PCB;
- footprint in the Pi coordinate frame;
- intake and exhaust keep-outs;
- fan cable/connector sweep.

Do not infer installed height by adding vendor part dimensions.

### 4. Touch Display 2

Measure before fastening it into any prototype frame:

- outer glass/PCB outline and total stack depth;
- active/visible area origin and width/height relative to the glass datum;
- mounting-hole centres, diameters and standoff/screw stack;
- DSI and power connector positions;
- actual FFC and power-wire bend/service envelopes.

Separately test touch response around the planned circular-mask boundary. Record the smallest mask opening that does not create unusable edge touch targets; this is a functional measurement, not just a geometric one.

### 5. Cable and service envelopes

Using the actual installed cable set, capture the largest required envelope for:

- USB-C power entry;
- Ethernet plug latch and strain relief;
- external USB HDD/service USB;
- DSI FFC bend;
- reSpeaker USB and speaker leads;
- LED harness;
- privacy/button terminals.

Service envelopes should include enough room to insert/remove a plug without disassembling unrelated modules when T911 requires service access.

### 6. Printer fit coupons

Before T910 produces full enclosure parts, print a small coupon set using the intended material/profile. At minimum exercise:

- M2.5 clearance;
- M3 clearance;
- chosen heat-set insert pocket;
- one representative press/slip-fit interface if the design uses one.

Record nominal geometry, actual printed/measured geometry, printer profile and qualitative result (`loose`, `acceptable`, `tight`, `failed`). Only measured coupon results may become final tolerance compensation.

## Expanding compact template entries

Some template feature rows use one placeholder measurement such as `hole_centers_and_diameters` to keep the blank file readable. During T909, replace these compact placeholders with one scalar record per datum, for example:

```json
{"name":"hole_a_x","value_mm":12.34,"source":"measured","cad_driving":true,"method":"caliper from X datum","tool":"digital caliper","uncertainty_mm":0.05,"reference":null,"notes":null}
```

Repeat for `hole_a_y`, `hole_a_diameter`, then each additional hole. Do the same for connector origins and envelope dimensions. Scalar, named values are preferred over encoded coordinate strings because T910 can consume them deterministically.

## Promotion from template to measured

T909 may change the dataset to `dataset_status: measured` and `non_production: false` only after:

- all CAD-driving values needed by the chosen prototype are non-null physical measurements;
- every measured value records its method;
- all selected BOM components/interfaces are represented;
- printer coupons required for final fit are no longer `not_tested`;
- missing physical data is resolved or the affected geometry is explicitly removed from the selected prototype scope.

Run:

```bash
python3 measurements/validate.py measurements/prototype-v1.template.json measurements/examples/synthetic.json
```

For the real T909 dataset, run the same validator against its file. A measured dataset fails validation if any CAD-driving value remains unmeasured, reference-only, or null.

## Handoff to T910

T910 must consume the measured dataset through a documented parameter-loading layer. CAD code may transform coordinates, add explicit design clearances, and derive enclosure parameters, but it must retain traceability back to named measured fields and fit-coupon outcomes. Synthetic fixtures are only for toolchain tests and never establish real component geometry.
