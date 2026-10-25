# Concept

Goal: replace the power, turbo and HDD LEDs of a retro PC case with one RGB LED.

| HDD- | TURBO- | Colour |
|---|---|---|
| idle | idle | green |
| idle | active | red |
| active | any | blue |

As few parts as possible, through-hole, no extra supply.

## Mainboard headers (assumptions)

| Header | Typical behaviour |
|---|---|
| `PLED+` | +5 V through a series resistor on the board (usually 330 Ω to 1 kΩ). Some AT boards give plain +5 V, then R0 is needed. |
| `PLED-` | GND |
| `HDD+` / `TURBO+` | +5 V through a series resistor (not used) |
| `HDD-` / `TURBO-` | open collector to GND, low while active |

Check with a multimeter before connecting. Boards that switch an LED on the high side (`-` pin is GND) are not covered.

## Why discrete and not an IC

The only supply at the front panel is `PLED+`, which already sits behind the board's series resistor and drops to the LED voltage under load. A logic IC or a small microcontroller would need its own clean 5 V (extra cable to a drive power connector) and would still need driver transistors for the LED. Two transistors do the job with the existing current source.

## Circuit

- Common anode → `PLED+` (current limited by the board).
- Blue cathode → `HDD-`.
- Green cathode → Q1 → D4 → GND. R1 (10 kΩ) from the anode keeps Q1 on. D1 to `HDD-` and D2 to `TURBO-` pull the base node to about 0.9 V; with D4 in the emitter Q1 needs about 1.3 V, so it turns off.
- Red cathode → Q2 → D5 → `TURBO-`. Red only has a path while `TURBO-` is low. R2 keeps Q2 on, D3 to `HDD-` turns it off on HDD activity (D5 lifts the threshold as for Q1).
- The diodes block any path from one input to the other. Without turbo: leave out Q2, R2, D3, D5 (D2 can stay or go).

## Simulation (ngspice, `sim/three_states.cir`)

Board resistor 330 Ω, InGaN green and blue, standard red:

| HDD- | TURBO- | Green | Blue | Red |
|---|---|---|---|---|
| idle | idle | 3.7 mA | 0 | 0 |
| idle | active | 0.3 µA | 0 | 6.0 mA |
| active | idle | 0.3 µA | 5.2 mA | 0 |
| active | active | 0.05 µA | 5.2 mA | 0.2 µA |

With a 1 kΩ board resistor: green 1.3 mA, red 2.0 mA, blue 1.6 mA. Enough for a diffused indicator LED, but dimmer.
LED models are rough fits, not datasheet models.

## Variants considered

| Variant | Parts | Result |
|---|---|---|
| A – one diode in series with green (power + HDD only) | 1 | works only with InGaN green, fails with classic GaP green |
| B – 1 NPN + 2 resistors (power + HDD only) | 3 | works, faint blue leak (≈ 5 µA) while idle |
| B + red through a resistor to `TURBO-` | 4 | red only mixes in (yellow/magenta), no clean red |
| **C – 2 NPN + 5 diodes + 2 resistors (this design)** | 9 | clean green/red/blue, HDD has priority, no leakage |
| C with base dividers instead of D4/D5 | 11 | about 50 % brighter green, two more parts |
| Logic IC / microcontroller | – | needs its own 5 V supply, rejected |

## Build

Small enough to solder freely onto the LED legs and cover with heat shrink, or a tiny strip-board. Wires: `PLED+`, `PLED-`, `HDD-`, `TURBO-`.
