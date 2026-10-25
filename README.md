# XT-AT-PC-RGB-LED

**One RGB LED instead of separate power, turbo and HDD LEDs for retro PCs (XT / AT)**

| State | Colour |
|---|---|
| Power on | green |
| Turbo on | red (instead of green) |
| HDD activity | blue, overrides green and red |

It plugs into the normal mainboard headers (power LED, HDD LED, turbo LED). Two NPN transistors, five small diodes and two resistors, through-hole parts only, powered from the power LED header.

**Status: concept, simulated (ngspice).** Not built or tested yet.

![Schematic](docs/schematic.png)

## How it works

- Common anode of the RGB LED is fed from `PLED+`. The mainboard's own series resistor sets the current (optional R0 if the board has none).
- Blue cathode goes straight to `HDD-`. The open-collector HDD driver pulls it low on activity, exactly like the original HDD LED.
- Green: Q1 switches the green cathode to GND. R1 keeps Q1 on. D1 (from `HDD-`) or D2 (from `TURBO-`) pull its base down and turn green off. D4 in the emitter lifts the turn-on threshold above that one diode drop.
- Red: Q2 switches the red cathode to `TURBO-`, so red can only light while turbo is active. D3 pulls its base down on HDD activity, D5 again lifts the threshold.
- The diodes keep the two inputs apart: no input leaks into the other colour.
- `HDD+` and `TURBO+` are not used. Without a turbo connection leave out Q2, R2, D3 and D5.

Details, variants and simulation results: [docs/concept.md](docs/concept.md)

## Versions

| Version | What | Status |
|---|---|---|
| **v1** | discrete, no microcontroller, through-hole board ([hardware/v1](hardware/v1)) | simulated, board designed |
| **v2** | ATtiny84 board for an addressable LED and/or a plain RGB LED or RGB button, colours from a config file, no measuring of the headers needed ([v2/](v2/README.md), [hardware/v2](hardware/v2)) | firmware compiled, board designed |
| v3 | full SMD version | planned |

Simulation (ngspice): [sim/](sim/), transient plot `sim/three_states_tran.png`.

## History and key points

The project started as "one RGB LED for power and HDD" and grew step by step:

1. **Power + HDD with one LED.** A single diode in series with green only works with InGaN green LEDs: with a common anode the colour with the lowest forward voltage wins. One transistor solves it.
2. **Turbo added (red).** Red has about 2 V forward voltage and pulls the common anode down, so mixing colours (yellow) does not work. Result: two transistors, five diodes, HDD has priority (v1).
3. **Unknown header polarity.** Which pin of the turbo header switches is not standardised. Instead of measuring every board, v2 uses a load resistor between the two pins and treats "pins differ" as active.
4. **Microcontroller (v2).** A logic IC was rejected for v1 because the front panel has no clean 5 V. v2 accepts an extra 5 V cable and gets colours from a config file.
5. **Addressable or plain RGB?** Addressable LEDs need no resistors and can be chained; illuminated RGB buttons only exist as plain RGB. v2 has both outputs, so the power button itself can be the indicator.
6. **Boards.** v1 and v2 through-hole with the common M3 hole rule; v3 (full SMD) is planned.

Open: measurement of the front panel headers, 5 V source for v2, building and testing.

## Parts

| Ref | Part | Note |
|---|---|---|
| R1, R2 | 10 kΩ, 1/4 W | base resistors |
| R0 | 330 Ω, 1/4 W | only if `PLED+` has no series resistor on the board, otherwise bridge |
| Q1, Q2 | BC547B (BC548, 2N3904 also fine) | |
| D1–D5 | 1N4148 | |
| LED1 | RGB LED 5 mm, common anode, diffused, 4 pins | 3 mm also fine |

## License

- Hardware: [CERN-OHL-S-2.0](LICENSE)
- Firmware and tools (v2): PolyForm Noncommercial 1.0.0, see [v2/LICENSE.md](v2/LICENSE.md)
- Documentation: CC BY-SA 4.0

## Authors

- **Stefan Fambach** (SteFam) – idea and concept, review and testing – https://www.fambach.net
- **Claude** (Anthropic AI) – implementation, via Claude Code

## AI disclosure

This project is built with AI assistance. Stefan Fambach had the idea, wrote the concept and reviews and tests every change; the implementation (schematics, simulation, firmware and documentation) is written largely by Claude (Anthropic) via Claude Code.
