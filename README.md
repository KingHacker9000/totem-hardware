# Totem Hardware

Generic reference hardware, enclosure engineering, CAD, electronics, and print documentation for Totem.

## Current phase

Totem is **software-first**. This repository is initialized now so hardware requirements are recorded, but detailed CAD work intentionally starts later, after the PC software stack and Pi deployment requirements are understood.

When hardware work begins, the enclosure will be designed as a **parametric, modular system**, not as one monolithic STL.

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

## Physical design requirements already known

The future design must account for:

- Raspberry Pi 5 and active cooling
- inexpensive rectangular/square touchscreen hidden behind a configurable circular bezel/mask
- touch access and cable clearance
- speaker, amplifier/DAC, acoustic chamber, grille, and vibration isolation
- microphone hardware/array, acoustic openings, and separation from speaker/fan
- addressable LEDs, diffusion, hotspot control, and light-bleed prevention
- airflow, intake/exhaust, fan noise, heatsink clearance, and serviceability
- rear I/O for power, Ethernet, external USB HDD, spare USB, and service access
- cable bend radii and connector access
- threaded inserts/screws/snap fits and realistic 3D-print tolerances
- removable subassemblies so a screen or Pi change does not require redesigning the whole enclosure

## CAD workflow

The final enclosure will be derived from **real measurements** of selected components. CadQuery or another code-friendly parametric CAD approach is preferred so dimensions can be updated reproducibly.

Codex/other coding agents are expected to be used heavily during the hardware phase for parametric CAD generation, variant exploration, geometry checks, documentation, and parallel engineering analysis. The first physical prints should be small fit/tolerance coupons before full enclosure prototypes.

## Generic vs private themed hardware

This repository contains generic, redistributable mechanical designs. The user's character/franchise-specific cosmetic enclosure work lives separately in the private `KingHacker9000/totem-portal-hardware` repository. That private repository may reuse the generic chassis interfaces defined here, but it is not a dependency of Totem and proprietary/themed geometry must not be copied back into this public repository.

## Milestone order

1. finish software architecture and PC simulator
2. validate software requirements
3. deploy to Pi 5
4. select low-cost hardware components
5. measure actual parts with calipers
6. generate parametric CAD
7. print fit coupons
8. prototype chassis/enclosure
9. test thermals, acoustics, lighting, touch, and serviceability
10. publish generic production-ready hardware files
