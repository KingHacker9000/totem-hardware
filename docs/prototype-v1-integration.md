# Totem prototype v1 integration plan

Status: **assembly plan for T911**

This document turns `bom/prototype-v1.md` into a bench- and enclosure-integration plan for the first generic Totem prototype. It is intentionally generic and contains no Portal/franchise-specific geometry.

The plan is conservative: it prefers known-good Raspberry Pi interfaces, keeps high-current loads bounded, makes privacy behavior physically observable, and requires bench validation before anything is enclosed.

## 1. Architecture summary

Prototype v1 uses these primary paths:

- Raspberry Pi 5 is the compute and GPIO controller.
- Raspberry Pi Touch Display 2 (5-inch) uses the supplied Pi-5 DSI cable for video/touch and the supplied GPIO power lead.
- reSpeaker Lite uses USB Audio Class over USB-C for capture/playback and drives the single 4-ohm speaker from its onboard speaker output.
- the 24-pixel WS2812B/SK6812 ring is driven from one Pi GPIO through a 74AHCT125-class 3.3 V -> 5 V logic buffer.
- two momentary panel buttons are direct active-low GPIO inputs using internal pull-ups.
- the maintained privacy switch has two independent functions: one pole provides a hard physical mute command to the reSpeaker mute circuit where the purchased board exposes a practical contact point; the other pole exposes the latched mute state to the Pi. If the purchased board cannot accept a safe external hard-mute contact, the switch must instead interrupt only the microphone-capture path through a separately verified hardware method before T912. Do **not** cut the entire reSpeaker USB supply as the default mute design because that also removes playback/AEC and causes USB churn.
- the official Pi 5 Active Cooler remains on the dedicated Pi fan header.
- the official 27 W Pi USB-C PSU remains the only mains-connected supply in the baseline prototype. No mains wiring is brought inside the enclosure.

The first enclosure should therefore have one low-voltage USB-C power entry, plus service access for Ethernet/USB. Do not design any internal AC mains distribution.

## 2. Power budget and distribution

### 2.1 Baseline decision

Use the official Raspberry Pi 27 W USB-C PSU directly into the Pi 5. Power the display from its official Pi GPIO lead, reSpeaker from Pi USB, and the LED branch from the Pi 5 V rail **only with a strict software brightness/current ceiling and an inline branch fuse/polyfuse**.

This is acceptable for first-prototype bring-up because the official supply exposes the Pi 5's intended high-current 5.1 V / 5 A operating profile and avoids an unverified splitter or internal mains PSU. It is **not** permission to operate every downstream load at its theoretical maximum simultaneously.

If measured current or undervoltage telemetry shows insufficient margin during T912, split the LED branch onto a separately regulated 5 V accessory supply or redesign around a single certified higher-power DC architecture. Do not improvise a Y-cable on the USB-C input.

### 2.2 Planning current envelope

| Load | Planning allowance | Notes |
| --- | ---: | --- |
| Pi 5 compute + storage + interfaces | 2.5 A at 5 V transient planning envelope | Actual workload current must be measured during burn-in; this is a budget reservation, not a claimed board maximum. |
| Touch Display 2, 5-inch | 0.5 A budget | Powered by official GPIO lead. Measure actual draw/rail behavior in T912. |
| Active Cooler | 0.25 A budget | Dedicated fan header; measure peak startup and sustained draw. |
| reSpeaker Lite + normal capture DSP | 0.30 A budget | USB-powered; measure with final firmware. |
| Speaker playback through reSpeaker | 0.60 A incremental peak budget | Speech playback is intermittent. Validate actual USB/current behavior at chosen loudness before enclosure use. |
| 24-pixel LED ring | **0.40 A enforced ceiling** | Treat unrestricted full-white as a fault/test-only condition. 24 x 60 mA theoretical worst case is ~1.44 A, so firmware must limit aggregate brightness. |
| GPIO/buttons/level shifter | <0.05 A | Negligible relative to main loads. |
| Reserved margin | ~0.4 A or more under normal profile | Final acceptance is based on measured rail stability/telemetry, not this table alone. |

The normal operating profile must target **well below 5 A total**. During bench validation, log Pi undervoltage/throttling flags while simultaneously running CPU load, display at expected brightness, speech playback/capture and the configured LED ceiling.

### 2.3 Distribution rules

1. Official 27 W PSU -> Pi USB-C directly.
2. Touch Display 2 -> supplied GPIO cable on Pi physical pins 2/4/6 as designed by Raspberry Pi; red 5 V lead at pin 2, black ground at pin 6 when using the supplied three-pin connector orientation.
3. reSpeaker Lite -> Pi USB 3/USB 2 host port via short, serviceable USB cable. Do not use an unpowered internal hub for v1.
4. LED 5 V branch -> Pi 5 V rail through a dedicated locking connector and **0.75-1.0 A resettable fuse or appropriately sized replaceable fuse** near the source. Final fuse choice follows measured normal/peak current and wire gauge.
5. All low-voltage branches share common ground at the Pi-side distribution point. Avoid chaining LED return current through microphone/audio ground wiring.
6. Use separate paired power/ground conductors for LED and audio branches. Do not use a solderless breadboard as permanent power distribution.
7. Use locking JST-style connectors for removable internal subassemblies. Dupont jumpers are bench-only.

## 3. Raspberry Pi GPIO allocation

Use BCM numbering in software and document physical pin numbers on harness labels.

| Function | BCM GPIO | Physical pin | Electrical rule |
| --- | ---: | ---: | --- |
| LED data | GPIO12 | 32 | 3.3 V output -> 74AHCT125 input; 5 V-buffered output -> LED DIN. Keeps GPIO18/19/21 free for a possible future I2S amplifier fallback. |
| Wake/action button | GPIO5 | 29 | Active-low input with internal pull-up. Switch shorts GPIO to GND when pressed. |
| Secondary/service button | GPIO6 | 31 | Active-low input with internal pull-up. Switch shorts GPIO to GND when pressed. |
| Physical mute state sense | GPIO16 | 36 | Active-low input with internal pull-up from the second pole of the maintained privacy switch. Never apply 5 V to this GPIO. |
| Reserved I2S fallback | GPIO18/19/21 | 12/35/40 | Do not consume in v1 unless MAX98357A fallback becomes necessary. |
| Ground for controls | GND | 34 or another nearby GND | Use a local control-harness ground, not the LED high-current return lead. |

GPIO outputs and inputs are 3.3 V logic. Do not connect 5 V logic directly to GPIO pins.

## 4. LED ring wiring

### 4.1 Signal chain

`Pi GPIO12 -> 74AHCT125 input -> 74AHCT125 output -> 220-470 ohm series resistor -> LED DIN`

Power the 74AHCT125 from the same 5 V/GND domain as the LED ring so the buffered high level tracks LED VDD. Tie the selected channel's active-low output-enable permanently low. Terminate unused inputs to defined logic levels rather than leaving them floating.

At the ring:

- use a locking 3-pin connector: `+5V / DATA / GND`;
- place a bulk capacitor across 5 V/GND near the ring (nominally about 1000 uF, >=6.3 V, low-ESR is suitable for prototype work);
- keep the data run short and routed away from the reSpeaker microphone traces/cable;
- connect ground before 5 V during bench work and avoid hot-plugging the LED connector;
- enforce an aggregate brightness/current limit in software; the documented v1 ceiling is 0.40 A until measurements justify another value.

The diffuser must form a light-tight optical path around the display bezel. Add an opaque barrier between the LED cavity and LCD/glass edges so status lighting does not bleed under the circular mask.

## 5. Buttons and privacy switch

### 5.1 Momentary controls

Each 16 mm momentary NO button is wired between its assigned GPIO and GND. Configure the input with an internal pull-up and debounce in software. Do not place 5 V on the switch contacts.

Harness labels:

- `BTN1_WAKE`: GPIO5 / GND
- `BTN2_SERVICE`: GPIO6 / GND

### 5.2 Maintained microphone privacy switch

The physical privacy control must be latched and visually/mechanically obvious. Use a DPST/DPDT maintained switch if possible so privacy state and Pi sensing remain electrically separate.

Preferred implementation:

- **Pole A — hard mute control:** parallel or extend the reSpeaker Lite's onboard mute-button contact using a verified isolated contact interface, *only after continuity/schematic verification on the purchased board*. The reSpeaker documentation states that its onboard mute button mutes audio input; T912 must verify that this still blocks captured microphone samples at the host, not merely a UI indicator.
- **Pole B — state sense:** GPIO16 to GND when muted; Pi internal pull-up gives `0 = physically muted`, `1 = unmuted`.

Software must treat the physical state as authoritative: when GPIO16 reports mute, Totem must not reopen capture. A software mute may additionally disable capture when the switch is unmuted.

If continuity/schematic validation shows that the onboard mute switch cannot safely be paralleled as a maintained contact, T912 must choose a verified hardware alternative. Acceptable alternatives are limited to methods that disable microphone capture without putting 5 V on Pi GPIO and without defeating speaker playback unintentionally. Cutting the entire reSpeaker USB VBUS is a **diagnostic fallback only**, not the target design.

Bench acceptance for the privacy control:

1. start a raw host recording from the reSpeaker capture endpoint;
2. speak continuously and toggle the physical switch;
3. confirm recorded microphone content becomes silent/disabled while muted;
4. confirm Totem's UI/state changes to muted from GPIO16;
5. reboot with the switch already muted and confirm capture remains blocked after boot;
6. verify speaker playback still works if the selected hard-mute implementation is intended to preserve it.

## 6. reSpeaker and speaker integration

Use reSpeaker Lite in its default USB-audio firmware for v1. The board provides the dual-microphone front end, AEC/noise processing and the speaker connector, so do not add the MAX98357A fallback unless bench tests demonstrate a concrete reason.

Speaker wiring:

- reSpeaker speaker output -> locking 2-pin speaker connector -> one 4-ohm 3-5 W enclosed speaker;
- preserve output polarity through the harness even though v1 is mono;
- never connect either amplified speaker terminal to Pi ground unless the reSpeaker schematic explicitly defines that output as single-ended. Treat it as a two-wire amplifier output.

Placement rules:

- microphones belong near an exterior acoustic opening and as far from the speaker diaphragm/vent as the compact enclosure permits;
- do not put the microphones in the Active Cooler exhaust stream;
- mount the speaker to a gasket/foam interface so basket vibration does not couple directly into the mic PCB or display frame;
- give the speaker a deliberate front acoustic path and avoid venting it into the same open cavity used by the microphones;
- use a partial internal acoustic divider between speaker cavity and microphone region;
- keep USB/audio wiring away from LED power/data where practical.

Initial software/audio settings should favor intelligible assistant speech over loudness. Increase speaker level only after AEC and feedback testing.

## 7. Cooling and airflow

The official Pi 5 Active Cooler remains the thermal solution for v1.

Mechanical routing rules:

- keep the blower intake unobstructed;
- provide a short, low-restriction exhaust route to exterior vents;
- do not exhaust directly onto the reSpeaker microphones;
- keep FFC, USB and LED wiring outside the fan intake plane and secure cables so they cannot migrate into the blower;
- make the vent/dust path externally cleanable without removing the display;
- leave service clearance for the cooler fan connector and its cable.

Thermal validation during T912 should record idle and sustained-load CPU temperature, throttling/undervoltage flags and fan behavior with the enclosure assembled.

## 8. Cable routing and service zones

Create three logical harness zones:

1. **display zone:** DSI FFC + display GPIO power cable; minimum bends, no sharp fold at connector latch;
2. **quiet/audio zone:** reSpeaker USB, mute harness and speaker pair; keep away from fan exhaust and LED high-current return path;
3. **lighting/control zone:** LED +5V/data/GND, buttons and GPIO control harnesses.

Rear/service access must expose or make reachable without a full teardown:

- Pi USB-C power input;
- Ethernet;
- at least one USB host port for external HDD/service use;
- microSD access or an explicit service procedure if physically hidden;
- fasteners for removing the rear shell;
- internal locking connectors with enough slack to unplug after opening the shell.

Do not force tight right-angle bends directly at USB-C, Ethernet, DSI or speaker connectors. T909 provides the real plug-shell and bend-envelope dimensions used by CAD.

## 9. Connector and harness naming

Use these logical names in wiring drawings, labels and future CAD:

| Harness | End A | End B | Minimum conductors |
| --- | --- | --- | ---: |
| `H-DISP-PWR` | Pi GPIO pins 2/4/6 | Touch Display 2 J1 | supplied 3-pin assembly |
| `H-DISP-DSI` | Pi DISP connector | Touch Display 2 DSI | supplied 22-to-15 FFC |
| `H-AUDIO-USB` | Pi USB host | reSpeaker USB-C | USB cable |
| `H-SPK` | reSpeaker speaker output | mono speaker | 2 |
| `H-LED` | fused 5 V + level-shifted data + GND | LED ring | 3 |
| `H-BTN1` | GPIO5/GND | wake button | 2 |
| `H-BTN2` | GPIO6/GND | service button | 2 |
| `H-MUTE-SENSE` | GPIO16/GND | privacy switch pole B | 2 |
| `H-MUTE-HARD` | verified reSpeaker mute contact | privacy switch pole A | 2 isolated contact wires |

Use keyed/locking connectors where polarity reversal could damage electronics. Label both ends of every removable harness.

## 10. Bench-test sequence

Do **not** install electronics in the enclosure until this sequence passes.

### Stage A — visual and continuity

1. Verify PSU, Pi, display and reSpeaker are disconnected from power.
2. Inspect all harness polarity and connector keying.
3. Continuity-test GND distribution and confirm no 5 V-to-GND short.
4. Confirm buttons and privacy-switch poles have the intended NO/NC behavior.
5. Confirm LED DIN, not DOUT, is connected to the level shifter.

### Stage B — Pi + display baseline

1. Connect only Pi 5, Active Cooler and Touch Display 2.
2. Boot from the known-good Totem image/deployment.
3. Verify display, touch orientation, touchscreen edge behavior and fan operation.
4. Capture idle voltage/undervoltage/throttling state.

### Stage C — audio subsystem

1. Add reSpeaker over USB without the speaker connected.
2. Confirm enumeration, capture and playback endpoints.
3. Record near-field and ~1 m speech samples.
4. Add the speaker at low volume; confirm clean playback and no abnormal heating.
5. Exercise simultaneous playback/capture and verify AEC behavior.
6. Validate the physical privacy switch using the test in section 5.2.

### Stage D — controls

1. Add wake and service buttons.
2. Verify active-low state and debounce.
3. Reboot while holding each button and confirm no unsafe boot side effect.
4. Verify physical mute state is read correctly before Totem enables capture.

### Stage E — LEDs

1. Connect the level shifter with LED power disconnected and verify 3.3 V input / 5 V logic-supply wiring.
2. Add the fused LED branch and one low-brightness color test.
3. Test all pixels, color order and data direction.
4. Apply the 0.40 A software ceiling and verify it remains enforced across animation patterns.
5. Test CPU + display + audio + LEDs together while monitoring Pi voltage/throttling state.

### Stage F — pre-enclosure burn-in

Run at least 30 minutes of the representative combined workload:

- Totem core/UI active;
- display at expected brightness;
- periodic speech capture and TTS playback;
- LED animations at configured ceiling;
- CPU workload sufficient to exercise the Active Cooler;
- external storage connected if it is part of the intended daily setup.

Pass criteria:

- no undervoltage event;
- no thermal throttling;
- no USB audio disconnect/re-enumeration;
- no LED-induced audio noise or microphone corruption;
- no stuck buttons/mute-state inversion;
- no connector or wire becomes abnormally warm;
- current remains within the validated supply/harness envelope.

Only after this passes should T912 place the assembly in the printed enclosure and repeat the thermal/acoustic tests.

## 11. Enclosure integration checklist

Before closing the shell:

- [ ] all T909 measured envelopes used by CAD are current;
- [ ] DSI cable is not pinched or sharply folded;
- [ ] fan intake/exhaust are unobstructed;
- [ ] microphone ports are clear and not in the fan exhaust path;
- [ ] speaker gasket/divider is installed;
- [ ] LED diffuser barrier prevents display-edge light bleed;
- [ ] LED branch fuse is accessible for service;
- [ ] privacy switch remains mechanically latched and clearly identifiable;
- [ ] USB-C power plug can be inserted/removed without stressing the Pi connector;
- [ ] Ethernet/USB service connectors have real plug/bend clearance;
- [ ] all harnesses have strain relief and cannot enter the fan;
- [ ] rear shell can be opened far enough to unplug harnesses without tearing wires out.

## 12. Fallback decisions

### If speaker playback through reSpeaker is inadequate

Only then add a MAX98357A-class I2S amplifier. The reserved GPIO18/19/21 pins are intentionally left free for this possibility. Recalculate 5 V current, grounding, speaker wiring and acoustic tests before integration.

### If LED load causes rail instability

First lower the enforced LED current ceiling. If the product requirement still needs more brightness, move LEDs to a separately regulated/fused 5 V accessory rail with common logic ground. Do not increase wire/fuse limits without validating the upstream source and connector ratings.

### If reSpeaker AEC/far-field capture is inadequate

Keep the software/device interfaces stable and move to the previously identified larger microphone-array candidate in a later mechanical revision. Do not distort the first chassis around an unmeasured substitute.

### If the hard-mute contact cannot be safely externalized

Keep T912 blocked on selecting and validating a real hardware capture-disable path. Do not silently downgrade privacy to software-only mute.

## 13. T912 evidence to record

The physical-integration task should attach or commit:

- measured idle/combined current and any relevant rail voltage data;
- `vcgencmd get_throttled` or equivalent Pi diagnostics before/after burn-in;
- CPU temperature/fan observations under sustained load;
- ALSA/PipeWire device identity for reSpeaker;
- a mute test demonstrating host capture suppression;
- LED ceiling used and worst observed current;
- speaker level used for feedback/AEC testing;
- photos of harness routing, acoustic divider/gasket and fan clearances;
- any changed pin assignments or connector choices.

## 14. References

- Raspberry Pi Touch Display 2 documentation: https://www.raspberrypi.com/documentation/accessories/touch-display-2.html
- Raspberry Pi GPIO documentation: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
- Seeed reSpeaker Lite documentation: https://wiki.seeedstudio.com/reSpeaker_usb_v3/
- Adafruit NeoPixel Raspberry Pi wiring/level shifting guidance: https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring
- Totem selected BOM: `../bom/prototype-v1.md`
