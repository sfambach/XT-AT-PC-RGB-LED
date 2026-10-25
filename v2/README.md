# Version 2 – microcontroller and addressable LED

Same idea as version 1 (green = power, red = turbo, blue = HDD with priority), but an ATtiny85 drives one **addressable RGB LED** (APA106 / PL9823, 5 mm through-hole, WS2812 protocol). Colours, brightness and behaviour come from a config file.

**Status: firmware written and compiled, not tested on hardware.** No PCB yet.

## Why

- **No measuring:** each header gets a load resistor between its two pins. A signal is active when the two pins differ, so it does not matter which pin is switched, whether the board switches low or high side, or which way round the cable is plugged in.
- **Free colours:** any colour per state, also yellow (mix mode), brightness, LED chains.
- **Short HDD pulses** are stretched to a minimum time so they stay visible.

## Pins (ATtiny85, DIP-8)

| Pin | Port | Function |
|---|---|---|
| 5 | PB0 | LED data (through 330 Ω) |
| 6 | PB1 | HDD header pin A |
| 7 | PB2 | HDD header pin B |
| 2 | PB3 | TURBO header pin A |
| 3 | PB4 | TURBO header pin B |
| 8 | VCC | +5 V |
| 4 | GND | GND |
| 1 | RESET | free (programming) |

## Wiring (concept)

- **Supply: clean +5 V**, not `PLED+` (that one sits behind the board's series resistor). Candidates: speaker header (usually pin 1 = +5 V) or a floppy power connector. To be checked per board.
- Per header (HDD, TURBO): **4.7 kΩ** between the two header pins (it takes the place of the original LED), each header pin through **1 kΩ** to its ATtiny pin. Internal pull-ups are on, so an unused header simply reads "inactive".
- 100 nF at the ATtiny, 100 nF + 330 Ω data resistor at the LED.
- `PLED` is not needed: when the PC has power, the LED is green.

## Parts (estimate, prices not checked)

| Part | Qty | approx. € |
|---|---|---|
| ATtiny85-20PU + DIP-8 socket | 1 | 1.50 |
| APA106 / PL9823 5 mm RGB LED | 1 | 0.25 |
| Resistors 4.7 kΩ ×2, 1 kΩ ×4, 330 Ω ×1 | 7 | 0.15 |
| Capacitors 100 nF | 2 | 0.10 |
| Pin headers / cable | – | 0.50 |
| Small PCB (5 pcs, without shipping) | 1 | 0.50 |
| **Total** | | **≈ 3 €** |

## Firmware

```
cd firmware
make size
```

| MCU | Clock | Flash | RAM |
|---|---|---|---|
| ATtiny85 | 8 MHz internal | 678 bytes (8 %) | 32 bytes |
| ATtiny13A | 9.6 MHz internal | 664 bytes (65 %) | 32 bytes |

The ATtiny13A is pin compatible and still fits, so it can replace the ATtiny85 later.
Fuses are listed in `firmware/Makefile`. The LED timing is generated in assembler (11 cycles per bit), interrupts are off while sending.

## Configuration

Edit [config.ini](config.ini), then

```
python3 tools/make_eeprom.py config.ini eeprom.hex
```

and write `firmware/build/*.hex` to flash and `eeprom.hex` to the EEPROM (e.g. XGecu T48). Without EEPROM data the firmware uses the defaults from `firmware/config.h` (WS2812B colour order GRB). For APA106 / PL9823 set `order = RGB`.

## License

- Hardware: CERN-OHL-S-2.0 ([../LICENSE](../LICENSE))
- Firmware and tools: PolyForm Noncommercial 1.0.0 ([LICENSE.md](LICENSE.md))
