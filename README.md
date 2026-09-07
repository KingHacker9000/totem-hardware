# Totem Hardware

Generic reference hardware, enclosure engineering, CAD, electronics, and print documentation for Totem.

## Current phase

The software platform and first prototype BOM are established. Hardware work is now progressing through **measured, gated physical integration**: selected components are documented, the wiring/power/acoustics plan is ready, and final CAD remains blocked until actual purchased parts are measured.

Current public prototype artifacts:

- [`bom/prototype-v1.md`](bom/prototype-v1.md) — selected generic prototype v1 components, alternatives, procurement order, and the physical data that must be measured before CAD.
- [`docs/prototype-v1-integration.md`](docs/prototype-v1-integration.md) — power budget, GPIO allocation, wiring/harness strategy, physical microphone privacy behavior, acoustics/cooling rules, service access, and bench-test sequence.

Final enclosure geometry must still be derived from **real measurements**, not vendor dimensions alone.

## Planned scope

```text
cad/
  enclosure/
  screen-mount/
  pi-mount/
  speaker-mount/
  microphone-mount/
  led-diffusers/
  cooling/
  rear-io/
exports/
  step/
  stl/
  3mf/
electronics/
  wiring/
  power/
  pinout/
bom/
measurements/
prototypes/
print-profiles/
docs/
```

## Physical design requirements

The design accounts for:

- Raspberry Pi 5 and active cooling
- inexpensive rectangular/square touchscreen hidden behind a configurable circular bezel/mask
- touch access and cable clearance
- speaker, amplifier/DAC, acoustic chamber, grille, and vibration isolation
- microphone hardware/array, acoustic openings, physical privacy control, and separation from speaker/fan
- addressable LEDs, diffusion, hotspot control, current limiting, and light-bleed prevention
- airflow, intake/exhaust, fan noise, heatsink clearance, and serviceability
- rear I/O for power, Ethernet, external USB HDD, spare USB, and service access
- cable bend radii and connector access
- threaded inserts/screws/snap fits and realistic 3D-print tolerances
- removable subassemblies so a screen or Pi change does not require redesigning the whole enclosure

## CAD workflow

The final enclosure will be derived from **real measurements** of selected components. CadQuery or another code-friendly parametric CAD approach is preferred so dimensions can be updated reproducibly.

The physical workflow is intentionally gated: prepare integration requirements, measure the actual components, then generate parametric CAD and small fit/tolerance coupons before full enclosure prints. Final CAD must not be generated from guessed dimensions.

## Generic vs private themed hardware

This repository contains generic, redistributable mechanical designs. The user's character/franchise-specific cosmetic enclosure work lives separately in the private `KingHacker9000/totem-portal-hardware` repository. That private repository may reuse the generic chassis interfaces defined here, but it is not a dependency of Totem and proprietary/themed geometry must not be copied back into this public repository.

## Milestone order

1. software architecture and PC simulator — complete
2. Pi software/deployment preparation — complete; real-device evidence is tracked separately
3. select low-cost prototype hardware components — complete
4. prepare wiring/power/acoustics/bench-integration plan — complete
5. measure actual purchased parts with calipers
6. generate parametric CAD from measured interfaces
7. print fit coupons
8. prototype chassis/enclosure
9. test thermals, acoustics, lighting, touch, privacy controls, and serviceability
10. publish generic production-ready hardware files
