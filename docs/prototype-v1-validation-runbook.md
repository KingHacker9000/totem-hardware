# Totem prototype v1 assembly and validation runbook

Status: **pre-physical execution harness for T912**

This runbook turns the T911 integration plan and T918 device-present validation seams into one ordered, evidence-oriented physical-validation sequence. It deliberately records **no physical result in advance** and contains **no enclosure dimensions**. Final fit and geometry remain gated by T909 real measurements and T910 measured CAD.

## Evidence rules

Create one evidence bundle per stage/iteration with:

```bash
python3 validation/capture.py --stage <stage> --totem-repo /path/to/totem
```

The command writes a timestamped bundle under `validation/evidence/` containing an `evidence.json` record plus host/Pi diagnostic outputs when the corresponding commands exist. Missing utilities are recorded as skipped rather than fabricated. Copy photos/audio/video/measurement files into the same bundle, add them to `artifacts`, and record operator observations in `results` using `validation/evidence.schema.json`.

Use artifact names that are immutable and comparable: `<run-id>-<check-id>.<ext>`. Do not overwrite evidence from a previous iteration. `overall_status` remains `IN_PROGRESS` until all required checks for the stage are explicitly resolved.

Allowed statuses are `PASS`, `FAIL`, `BLOCKED`, and `SKIP`. `SKIP` requires a reason; it is not equivalent to PASS. `BLOCKED` identifies a prerequisite that prevented the check from running. Any failure that can damage hardware or invalidate safety/privacy guarantees stops progression to the next stage.

## Public/private boundary

The generic chassis, electrical integration, measurements, thermal/acoustic evidence, and generic validation results belong in this public repository. Portal/franchise cosmetic shell appearance, proprietary geometry, and cosmetic-only checks stay in the private hardware repository. A private cosmetic observation may reference the generic chassis revision, but proprietary geometry or media must not be copied into this public evidence tree.

## Stage 0 — intake gates

Do not begin powered assembly until:

- T909 has actual purchased-part measurement records derived from the exact received parts;
- T910 has produced measured generic CAD and fit coupons;
- printed fit coupons needed for risky interfaces have been physically checked;
- the T911 harness/power decisions still match the delivered component revisions;
- no unresolved measurement or substitution blocker is being papered over with vendor dimensions.

Record the exact hardware revision, measurement record, CAD revision, Totem revision, and operator in the evidence record.

## Stage 1 — pre-power / loose hardware

Stage value: `pre-power`.

Required checks:

1. **Visual condition** — no cracked PCB, bent connector, damaged cable, pinched insulation, foreign conductive debris, or suspect printed part.
2. **Harness identity** — both ends of each removable harness use the T911 names (`H-DISP-PWR`, `H-DISP-DSI`, `H-AUDIO-USB`, `H-SPK`, `H-LED`, `H-BTN1`, `H-BTN2`, `H-MUTE-SENSE`, `H-MUTE-HARD`).
3. **Polarity/keying** — verify all 5 V/GND and LED DIN orientation before connection.
4. **Continuity** — with power disconnected, verify common ground where intended and no low-resistance 5 V-to-GND short.
5. **Privacy switch topology** — verify the physical switch poles and the chosen hard-mute contact behavior before connecting it to the reSpeaker/Pi.
6. **Fuse/current ceiling** — verify the LED branch fuse/current-limiting plan and that permanent assembly does not use a solderless breadboard.

Hard-stop FAIL conditions: suspected short, polarity ambiguity, exposed conductor likely to short, 5 V path into a Pi GPIO input, unsafe privacy-switch wiring, or a delivered-part revision that invalidates the T909/T910 interface record.

## Stage 2 — Pi/display baseline

Stage value: `bench-display`.

Connect only Pi 5, Active Cooler, storage, and Touch Display 2 using the T911 wiring plan.

Record:

- boot success and Totem service state;
- display detection/native orientation;
- touch registration, orientation, edge/corner behavior, and absence of dead areas relevant to the intended UI;
- idle CPU temperature and throttling/undervoltage telemetry;
- fan startup/operation;
- `pnpm validate:pi` output from the checked-out Totem revision when practical.

FAIL if the display/touch path is unreliable, there is sustained undervoltage/throttling at idle, the cooler is not functioning, or the software reports a hardware capability as available when the device is absent/unusable.

## Stage 3 — audio and privacy bench

Stage value: `bench-audio`.

Add the reSpeaker over USB first without the speaker, then add the speaker at low level.

Record:

- capture/playback endpoint enumeration;
- near-field and approximately 1 m speech samples;
- low-level playback quality and unexpected heating/noise;
- simultaneous playback/capture behavior and AEC observations;
- microphone privacy behavior with the physical switch;
- reboot while physically muted, then confirm capture remains fail-closed after boot;
- whether speaker playback remains available if the selected mute design is intended to preserve playback;
- Totem hardware-capability/privacy state during each transition.

Privacy is an immediate FAIL if host microphone samples remain intelligible while the hard physical mute is asserted, Totem reports unmuted while the authoritative hardware state is muted, capture reopens after reboot in the muted position, or an unknown hardware mute state is treated as safe-to-record.

Audio FAIL conditions include recurring USB disconnect/re-enumeration, severe playback distortion at the intended speech level, obvious feedback that prevents wake/STT use, or abnormal component heating.

## Stage 4 — controls

Stage value: `bench-controls`.

Add wake/service buttons and the mute-state GPIO sense path.

Record:

- active-low state transitions;
- debounce behavior;
- button behavior during normal Totem operation;
- reboot while each control is held;
- authoritative mute-state synchronization before speech capture initializes.

FAIL if a control can short a supply, causes an unsafe boot mode, sticks/repeats uncontrollably under normal use, or the mute-state signal is inverted/ambiguous.

## Stage 5 — LEDs and combined power load

Stage value: `bench-led`.

Add the level shifter and fused LED branch only after low-voltage logic/power wiring has been checked.

Record:

- first low-brightness pixel test;
- pixel count, order, color order, and data direction;
- enforcement of the T911 0.40 A prototype software ceiling;
- CPU + display + audio + LED combined operation;
- Pi throttling/undervoltage telemetry during the combined load;
- audible microphone/speaker noise correlated with LED activity.

FAIL on repeated undervoltage, thermal throttling caused by normal combined use, LED-current ceiling bypass, LED-induced microphone corruption/noise that compromises speech use, abnormal connector/wire heating, or data/power instability.

## Stage 6 — pre-enclosure burn-in

Stage value: `pre-enclosure-burnin`.

Run at least 30 minutes of representative combined workload before installing electronics in the chassis:

- Totem core/UI active;
- display at intended brightness;
- periodic speech capture and TTS playback;
- LED animations at the configured ceiling;
- enough CPU load to exercise the Active Cooler;
- intended external storage connected if it is part of daily operation.

Capture beginning/end temperatures, any peak temperature available, throttling/undervoltage state, Totem service logs, audio disconnects, control state, and operator notes on heat/noise/instability.

Do not continue to enclosure installation if this stage FAILs.

## Stage 7 — enclosure fit and serviceability

Stage value: `enclosure-fit`.

Use only T910 measured CAD/prints. Record real fit outcomes; never edit the evidence template with a guessed clearance to make an interface appear acceptable.

Check:

- display bezel/mask alignment and unobstructed touch area;
- Pi/cooler clearance and airflow path;
- speaker gasket/chamber mounting and microphone acoustic opening;
- LED diffuser alignment and light isolation;
- connector insertion/removal without destructive disassembly;
- cable bend/service slack at DSI, USB-C, Ethernet, speaker, LED, and internal locking connectors;
- microSD/service access according to the documented service procedure;
- no cable can migrate into the fan;
- rear shell can be removed and internal connectors unplugged without stressing wires;
- no private Portal cosmetic geometry is required to make the generic chassis mechanically valid.

Mechanical FAIL means the affected interface returns to measured-data/CAD correction; do not file down, force, or conceal a mismatch without recording it.

## Stage 8 — enclosed burn-in and thermal/acoustic validation

Stage value: `enclosure-burnin`.

Repeat the representative combined workload with the chassis fully assembled. Record:

- idle, sustained-load, and post-load CPU temperatures;
- throttling/undervoltage telemetry;
- fan behavior and any recirculation/hotspot observation;
- near-field and ~1 m speech capture with TTS/LED activity;
- barge-in behavior and practical wake/push-to-talk usability;
- audio feedback/AEC behavior;
- light bleed under/around the display mask;
- enclosure vibration/rattle;
- accessible surface/connector temperatures where observed with an appropriate instrument;
- service access after burn-in.

FAIL if normal use causes thermal throttling, persistent undervoltage, unacceptable audio feedback, privacy regression, light bleed that compromises the display presentation, enclosure vibration that disrupts speech, or any connector/wire/part becomes abnormally hot.

## Stage 9 — final T912 acceptance

Stage value: `final`.

A final PASS requires explicit evidence for all of the following:

- Totem boots and remains healthy on the real Pi in the assembled prototype;
- display and touch work through the intended generic device path;
- microphone capture, TTS playback, and barge-in are usable in the assembled enclosure;
- physical privacy behavior is fail-closed and survives reboot;
- buttons and LEDs work through generic driver contracts;
- no unacceptable thermal throttling/undervoltage/audio feedback/light bleed/fit blocker remains;
- service access is practical for power, Ethernet, intended USB storage, rear-shell removal, and documented storage servicing;
- corrections and reprints are linked to their evidence/measurement/CAD revisions;
- public evidence contains only generic hardware information.

If any item is unresolved, the final record is `FAIL` or `BLOCKED`, not PASS. T912 should close only after the evidence set supports the checked acceptance criteria.

## Result-record examples

A measured thermal result:

```json
{
  "id": "thermal-load-peak",
  "category": "thermal",
  "status": "PASS",
  "observed_at": "2026-09-07T12:00:00Z",
  "summary": "Peak CPU temperature during enclosed representative load",
  "measurement": {"value": 71.2, "unit": "degC", "method": "vcgencmd measure_temp"},
  "artifacts": ["vcgencmd-temperature.txt"],
  "notes": null
}
```

A blocked fit check:

```json
{
  "id": "rear-usb-service-clearance",
  "category": "serviceability",
  "status": "BLOCKED",
  "observed_at": "2026-09-07T12:10:00Z",
  "summary": "Cannot validate until corrected T910 rear-I/O print exists",
  "measurement": null,
  "artifacts": [],
  "notes": "Do not infer clearance from vendor connector dimensions."
}
```
