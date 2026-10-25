# Version 2 – microcontroller board

Same idea as version 1 (green = power, red = turbo, blue = HDD with priority), but a small ATtiny board drives the LED. Colours, brightness and behaviour come from a config file, and the header polarity does not need to be measured.

**Status: concept + firmware compiled, not tested on hardware.** No PCB yet.

## Two LED outputs

The board drives both kinds of RGB LED at the same time, so the user picks what fits the case:

| Output | For | Parts on the board |
|---|---|---|
| **J_ADDR** (5 V, DATA, GND) | addressable LED: APA106 / PL9823 5 mm, WS2812B, LED chains | 330 Ω data resistor |
| **J_RGB** (common, R, G, B) | plain RGB LED or **RGB push button / switch**, common anode or common cathode | 3 series resistors (R_R, R_G, R_B), fitted only when used |

`J_RGB` uses three hardware PWM pins of the ATtiny84. The LED type is set in the config (`rgb_output = common_anode | common_cathode | none`), the common pin of `J_RGB` is jumpered to +5 V (anode) or GND (cathode). Series resistors for 5 V: about 150 Ω (red) and 100 Ω (green, blue) for ≈ 15–20 mA, more for a dimmer LED. Many metal buttons come as 12/24 V versions with built-in resistors – take the 3–6 V version (or bridge the resistors and check the brightness).

## Button or switch

The contacts of an illuminated button have nothing to do with its LED. They are **not** wired through the electronics; the board only offers a pass-through header (`J_SW_IN` → `J_SW_OUT`) so the cable can be tidy.

| Setup | Needs | Why |
|---|---|---|
| ATX mainboard | **momentary push button** to `PWR_SW` | the board's soft-power logic wants a short pulse; holding a latching switch for 4 s forces power off |
| ATX power supply on an AT board (ATX-to-AT adapter) | **latching switch** on the adapter (PS_ON to GND) | there is no soft-power logic, PS_ON must stay low while the PC runs |
| Classic AT power supply | **not with this board** | the AT power switch carries mains voltage (230 V) |

## Pins

ATtiny84 (DIP-14, main board, both outputs):

| Pin | Port | Function |
|---|---|---|
| 13 | PA0 | HDD header pin A |
| 12 | PA1 | HDD header pin B |
| 11 | PA2 | TURBO header pin A |
| 10 | PA3 | TURBO header pin B |
| 2 | PB0 | J_ADDR data |
| 5 | PB2 (OC0A) | J_RGB red |
| 6 | PA7 (OC0B) | J_RGB green |
| 7 | PA6 (OC1A) | J_RGB blue |
| 1 / 14 | VCC / GND | +5 V / GND |
| 3, 9, 8, 4 | PB1, PA4, PA5, RESET | free (PA4–PA6 + RESET also ISP) |

ATtiny85 / ATtiny13A (DIP-8, addressable output only): PB0 data, PB1/PB2 HDD, PB3/PB4 TURBO.

## Inputs

- Per header (HDD, TURBO): **4.7 kΩ** between the two header pins (it takes the place of the original LED), each header pin through **1 kΩ** to its ATtiny pin. Internal pull-ups are on.
- A signal is active when the two pins differ. It does not matter which pin is switched, whether the board switches low or high side, or which way round the cable is plugged in. An unused header reads "inactive".
- `PLED` is not needed: when the PC has power, the LED shows the power colour.

## Supply

Clean +5 V, not `PLED+` (that one sits behind the board's series resistor). Candidates: speaker header (usually pin 1 = +5 V) or a floppy power connector. To be checked per board (see the measurement table in the blog post). 100 nF at the ATtiny, 100 nF at the LED.

## Parts (estimate, prices not checked)

| Part | Qty | approx. € |
|---|---|---|
| ATtiny84A-PU + DIP-14 socket | 1 | 2.00 |
| Resistors 4.7 kΩ ×2, 1 kΩ ×4, 330 Ω ×1 | 7 | 0.15 |
| Resistors for J_RGB (optional) | 3 | 0.05 |
| Capacitors 100 nF | 2 | 0.10 |
| Pin headers, jumper | – | 0.50 |
| Small PCB (5 pcs, without shipping) | 1 | 0.50 |
| LED: APA106 5 mm, or RGB button | 1 | 0.25 / 2–5 |
| **Total without button** | | **≈ 3.50 €** |

## Firmware

```
cd firmware
make size
```

| MCU | Clock | Flash | RAM | Outputs |
|---|---|---|---|---|
| ATtiny84 | 8 MHz internal | 826 bytes (10 %) | 35 bytes | J_ADDR + J_RGB |
| ATtiny85 | 8 MHz internal | 680 bytes (8 %) | 35 bytes | J_ADDR |
| ATtiny13A | 9.6 MHz internal | 666 bytes (65 %) | 35 bytes | J_ADDR |

Fuses are listed in `firmware/Makefile`. The LED data timing is generated in assembler (11 cycles per bit), interrupts are off while sending. `J_RGB` uses hardware PWM at about 3.9 kHz; a colour channel at 0 is switched off completely.

## Configuration

Edit [config.ini](config.ini), then

```
python3 tools/make_eeprom.py config.ini eeprom.hex
```

and write `firmware/build/*.hex` to flash and `eeprom.hex` to the EEPROM (e.g. XGecu T48). Without EEPROM data the firmware uses the defaults from `firmware/config.h` (WS2812B colour order GRB, J_RGB common anode). For APA106 / PL9823 set `order = RGB`.

## Open points

- Measure the front panel headers and the +5 V source on real boards.
- Schematic and PCB (KiCad), through-hole.
- Test the LED timing with APA106 and WS2812B.

## License

- Hardware: CERN-OHL-S-2.0 ([../LICENSE](../LICENSE))
- Firmware and tools: PolyForm Noncommercial 1.0.0 ([LICENSE.md](LICENSE.md))
