# Totem generic prototype v1 BOM

Status: **selected for measurement/prototyping** (T908)

This is the first generic public Totem hardware candidate set. It intentionally avoids Portal/franchise-specific cosmetic geometry. Final CAD dimensions must come from the actual purchased parts and T909 measurements, not only the vendor dimensions below.

## Recommended prototype BOM

| Function | Selected candidate | Planning facts | Why selected |
| --- | --- | --- | --- |
| Compute | Raspberry Pi 5 already used by Totem | Keep the real-Pi software target validated in T907. | Avoid changing the validated compute target before the first physical prototype. |
| Touch display | **Raspberry Pi Touch Display 2, 5-inch** | 720×1280, 5-point capacitive touch; 91.5×143.5×16 mm outline; ~62×110.5 mm active area; DSI + GPIO power; Pi 5 cable included. List price US$40. | Official Raspberry Pi OS support, no USB/HDMI dongles, low cost, predictable DSI/touch behavior, and compact enough for a circular-mask face. |
| Microphone / audio front end | **Seeed reSpeaker Lite (XU316)** | 2 digital mics, up to 3 m pickup; AEC/IC/noise suppression/VNR/AGC; USB Audio Class 2.0 with Raspberry Pi; USB or external 5 V; 35×86 mm; speaker connector + 3.5 mm output; supports a 5 W amplified speaker path. Current listed price US$26.99. | Much stronger voice-assistant fit than a bare USB mic while remaining far cheaper/smaller than a 4-mic array. USB keeps first-prototype Linux integration simple and its AEC is valuable with an enclosed speaker. |
| Speaker | **4 Ω, 3–5 W enclosed speaker, one unit for v1**; initial reference: Adafruit 3 W 4 Ω enclosed speaker | Reference unit 30×70×17 mm, 4 Ω / 3 W, with mounting holes. | Mono is sufficient for assistant speech, reduces enclosure volume and acoustic feedback paths, and is compatible with the selected reSpeaker's amplified speaker class. A 4 Ω / 5 W unit is acceptable if the exact reSpeaker output contract and current budget are verified before use. |
| Amplifier / DAC | **Use reSpeaker Lite audio output for v1; no separate amplifier by default** | reSpeaker Lite exposes an amplified speaker connector and a headphone output. | Eliminates another PCB, I2S bus conflict, power load and cable path. Keep a MAX98357A breakout as a fallback if reSpeaker playback proves unsuitable. |
| LED status light | **Adafruit-compatible 24-pixel WS2812B/SK6812 ring geometry** | 65.5 mm OD, ~52.3 mm ID, ~3.2 mm PCB thickness. | Cheap, well-understood one-wire addressable lighting; ring geometry works naturally around/behind a circular diffuser. Use brightness limiting in software; do not size power for 100% white as the normal operating point. |
| Cooling | **Official Raspberry Pi 5 Active Cooler** | Pi-5-specific anodised heatsink + PWM/tach blower; 5 V from dedicated Pi fan header; 1.09 CFM maximum airflow. | Known-good Pi 5 thermal solution, keeps GPIO more available, and gives a stable CAD target. |
| Main power | **Official Raspberry Pi 27 W USB-C PSU for bench/first prototype** | 5.1 V / 5 A main profile (25.5 W), plus USB-PD profiles; 1.2 m cable. | Correct Pi 5 high-current negotiation and low-risk bring-up. T911 must decide whether the enclosed prototype remains externally USB-C powered or receives a dedicated internal distribution rail. |
| User input | **2 × 16 mm panel-mount momentary normally-open buttons** | Representative body ~18×18×29.4 mm; shaft ~14.9×15.6×18.7 mm. | Simple, inexpensive, easy to replace, and mechanically measurable. Suggested roles: wake/action and secondary/service. |
| Privacy control | **1 × maintained two-position panel switch for microphone mute** | Select an electrically maintained SPST/SPDT switch rated comfortably above logic-level current. Exact candidate to be purchased/measured in T909. | A latched physical state is preferable to a software-only mute. T911 should wire it so capture is electrically disabled where practical and also expose state to software. |
| Internal connectors | **JST-PH / locking JST-style low-voltage connectors where supported; Dupont only for bench bring-up** | Exact series/pin count follows the selected modules and current. | Reduces accidental disconnects inside the enclosure; avoids treating loose breadboard jumpers as production wiring. |
| Fasteners | **M2.5 for Pi/display ecosystem plus M3 for generic printed chassis joints; heat-set inserts where repeated service is expected** | Final lengths and insert OD depend on printed wall thickness and measured stack-ups. | Matches Raspberry Pi hardware conventions while keeping generic enclosure joints robust and serviceable. |

## Display geometry strategy

The generic enclosure should continue using a **rectangular panel hidden behind a configurable circular bezel/mask**. The 5-inch Touch Display 2 has an active width of about 62 mm, so a circular visible region around 58–60 mm diameter is a sensible first CAD parameter while preserving a small masking margin. This is not a final dimension: T909 must measure the actual panel, visible-area alignment, glass edge, mounting bosses and touch behavior near the mask before T910 freezes geometry.

The screen mount must remain modular. A future 7-inch variant (120×189.5×15 mm; ~87×154.5 mm active area) can trade a substantially larger circular face for a larger chassis. The original 7-inch Raspberry Pi Touch Display is not preferred because Touch Display 2 is newer, higher resolution, simpler to cable to Pi 5, and has a known production horizon.

## Audio alternatives and trade-offs

### Selected: reSpeaker Lite

The two-mic XU316 board is the best v1 cost/complexity balance: USB Audio Class operation on Raspberry Pi, on-board AEC/noise processing, 3 m advertised pickup, compact 35×86 mm geometry, and a speaker-output path. Keep the microphones near an enclosure edge with clear acoustic ports, mechanically isolate the speaker, and avoid placing the Pi blower exhaust directly across the microphone apertures.

### Upgrade: reSpeaker XVF3800 4-mic array

Use this if v1 shows weak far-field pickup, poor directionality, or difficult speaker echo. The current USB XVF3800 board is roughly US$60.99 and provides a circular 4-mic array, 360-degree pickup to 5 m, AEC, AGC, DoA, VAD, dereverberation, noise suppression and multi-beamforming. It is a much better acoustics platform but costs more and consumes substantially more front-panel/enclosure area. Treat it as a v2 upgrade, not a v1 dependency.

### Lowest-cost diagnostic fallback: USB mini microphone

A class-compliant mini USB microphone is useful only as a debugging fallback. The Adafruit reference unit is 22.2×18.3×7 mm, US$5.95, and explicitly works with Raspberry Pi. It lacks the far-field/AEC features wanted for an enclosed assistant, so it is not the recommended prototype microphone.

## Amplifier alternatives

The selected build first uses the reSpeaker Lite playback/speaker path. If that path cannot meet playback quality or driver requirements, use a MAX98357A I2S Class-D board as the fallback. A current Adafruit stereo MAX98357A board accepts 2.5–5.5 V, needs no MCLK, supports 8–96 kHz I2S, and can deliver about 3.2 W/channel into 4 Ω at 5 V (10% THD). The board is 25.5×19×11.8 mm. This fallback must not be added until T911 confirms Pi GPIO/I2S pin use and the power budget.

## Planning-level compatibility review

### Interfaces

- Touch Display 2 uses DSI for video/touch and GPIO 5 V power; the Pi 5 cable is supplied.
- reSpeaker Lite should use USB for the first physical prototype. This avoids relying on a custom Pi HAT driver and keeps I2S free as a fallback.
- The Pi Active Cooler uses its dedicated four-pin fan header.
- WS2812/SK6812 LEDs need one data GPIO plus 5 V/GND. T911 should add level shifting if required by the chosen LED batch/cable length and should reserve a GPIO not consumed by buttons or future hardware.
- Two momentary buttons need GPIO inputs with pull-ups/pull-downs. The maintained mic-mute control should be treated separately from ordinary UI buttons.

### Power

The official 27 W Pi 5 PSU supplies 5.1 V at up to 5 A. That is appropriate for bench bring-up, but the enclosure should **not yet assume** every accessory can be powered indefinitely from the Pi header at maximum simultaneous CPU, display, speaker and LED load. The speaker and LED ring are the dominant variable accessory loads. T911 must create a current budget from measured/confirmed loads and decide whether to:

1. keep one official USB-C supply and distribute its 5 V rail safely;
2. add a separately fused/regulator-fed 5 V accessory rail; or
3. reduce speaker/LED peak power.

Do not run a 24-pixel ring at unrestricted full-white brightness from a small GPIO/header wiring path. Firmware should impose a current/brightness ceiling even if the final supply has ample capacity.

### Thermal / acoustics

- Keep the official Active Cooler exhaust path clear and provide intake/exhaust openings with serviceable dust access.
- Put microphones away from fan exhaust and speaker pressure vents.
- Use a gasket/foam or flexible mounting treatment around the speaker to reduce vibration transfer into the microphone board and chassis.
- Give the speaker a defined front acoustic path and avoid a large shared open cavity with the microphones.
- The circular LED diffuser should be optically isolated from the display edges to prevent light bleed.

## Alternatives considered

| Area | Alternative | When to choose it | Trade-off |
| --- | --- | --- | --- |
| Display | Touch Display 2 7-inch | Larger face/readability is more important than compact size. | Larger 120×189.5 mm envelope and larger enclosure; US$60 list. |
| Display | Third-party HDMI/USB 5-inch panel | Only if circular geometry needs a panel unavailable in the official line. | More cables, USB consumption and vendor-specific touch/EDID behavior. |
| Mic | reSpeaker XVF3800 4-mic USB | Far-field/AEC performance is insufficient with the Lite board. | ~US$61 vs ~US$27 and larger geometry. |
| Mic | Mini USB microphone | Software/audio debugging or absolute minimum-cost bench test. | No dedicated AEC/beamforming/front-end DSP. |
| Audio | Separate MAX98357A I2S amp | reSpeaker playback path is unsuitable. | Extra board, GPIO/I2S wiring and power integration. |
| LED | Short WS2812/SK6812 strip | Ring cannot fit the final bezel geometry. | More custom mounting/diffuser work but easier diameter tuning. |
| Cooling | Large third-party tower cooler | Sustained thermal testing shows official cooler insufficient. | Consumes more enclosure volume and can complicate airflow/acoustics. |

## Parts/data T909 must physically measure

T909 should create a measured record for every actual purchased part. At minimum capture:

1. **Raspberry Pi 5** — PCB X/Y/Z, mounting-hole coordinates/diameters, USB/Ethernet/USB-C/micro-HDMI connector protrusions, microSD access, fan-header cable envelope and standoff stack.
2. **Official Active Cooler** — installed height above Pi, full X/Y footprint, blower intake/exhaust clearances, cable/connector sweep.
3. **5-inch Touch Display 2** — PCB/glass outline, total stack depth, active/visible area position relative to edges, mounting-hole coordinates, screw/standoff stack, DSI and power connector positions, FFC bend envelope, glass/bezel edge thickness, and touch response near the intended circular mask.
4. **reSpeaker Lite** — true PCB outline/thickness, mounting holes if present, microphone acoustic-center coordinates, USB connector envelope, speaker/JST and 3.5 mm connector positions, mute/control access and required keep-out above components.
5. **Selected speaker** — basket/enclosure outline, actual depth, mounting holes, diaphragm/front clearance, rear vent/opening, wire exit and minimum acoustic-chamber clearance.
6. **LED ring or strip** — exact OD/ID/thickness (or strip pitch), solder-pad locations, connector/wire exit, diffuser standoff needed to hide hotspots.
7. **Momentary buttons and maintained mute switch** — required panel cutout, bezel OD, thread/retainer depth, terminal clearance, travel and connector direction.
8. **Power entry** — if retaining direct USB-C, measure plug body and bend radius at the installed Pi; if using a panel extension, measure that exact extension/coupler.
9. **Ethernet/USB service openings** — measure real plug shells and strain-relief bend envelopes, not only PCB connector metalwork.
10. **Fasteners/inserts** — actual heat-set insert OD/length and screw-head diameters for the printer/process chosen.

Record advertised dimensions separately from measured dimensions. CAD-driving values should use measured values once the physical parts are available.

## Procurement order

To minimize wasted purchases, acquire/confirm in this order:

1. 5-inch Touch Display 2;
2. reSpeaker Lite;
3. one chosen 4 Ω 3–5 W speaker compatible with the reSpeaker output;
4. 24-pixel LED ring or equivalent strip segment;
5. official Active Cooler if not already installed;
6. two momentary buttons plus one maintained mute switch;
7. connectors, wire, M2.5/M3 screws and representative heat-set inserts.

The official Pi 27 W supply can remain the bench supply while T911 finishes the enclosed power architecture.

## Vendor references checked for T908

- Raspberry Pi Touch Display 2 product/documentation: https://www.raspberrypi.com/products/touch-display-2/ and https://www.raspberrypi.com/documentation/accessories/touch-display-2.html
- Raspberry Pi Active Cooler: https://www.raspberrypi.com/products/active-cooler/
- Raspberry Pi 27 W USB-C PSU: https://www.raspberrypi.com/products/27w-power-supply/
- Seeed reSpeaker Lite product/wiki: https://www.seeedstudio.com/ReSpeaker-Lite-p-5928.html and https://wiki.seeedstudio.com/reSpeaker_usb_v3/
- Seeed reSpeaker XVF3800 product family: https://www.seeedstudio.com/ReSpeaker-XVF3800-USB-Mic-Array-p-6488.html
- Adafruit 24-pixel NeoPixel ring: https://www.adafruit.com/product/1586
- Adafruit 3 W 4 Ω enclosed speaker reference: https://www.adafruit.com/product/3351
- Adafruit MAX98357A amplifier reference: https://www.adafruit.com/product/6513
- Adafruit mini USB microphone diagnostic fallback: https://www.adafruit.com/product/3367
- Adafruit 16 mm panel momentary button geometry reference: https://www.adafruit.com/product/1505

Prices and stock are planning snapshots, not purchasing guarantees. Re-check the user's local Canadian supplier before ordering.
