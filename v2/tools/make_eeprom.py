#!/usr/bin/env python3
# XT-AT-PC-RGB-LED v2 - build the EEPROM image from config.ini
# Copyright (C) 2026 Stefan Fambach (SteFam), https://www.fambach.net
# License: PolyForm Noncommercial 1.0.0, see ../LICENSE.md
"""Usage: make_eeprom.py config.ini eeprom.hex  (layout: firmware/config.h)"""
import configparser
import sys

MAGIC, VERSION = 0xA5, 1


def colour(text):
    text = text.strip()
    if text.startswith("#"):
        return [int(text[i:i + 2], 16) for i in (1, 3, 5)]
    values = [int(v) for v in text.split(",")]
    if len(values) != 3 or not all(0 <= v <= 255 for v in values):
        raise ValueError(f"colour needs three values 0..255: {text}")
    return values


def byte(value, name):
    if not 0 <= value <= 255:
        raise ValueError(f"{name} out of range 0..255: {value}")
    return value


def build(ini):
    order = {"GRB": 0, "RGB": 1}[ini.get("led", "order").strip().upper()]
    mode = {"replace": 0, "mix": 1}[ini.get("behaviour", "turbo_mode").strip().lower()]
    data = [
        MAGIC, VERSION, order,
        byte(ini.getint("led", "count"), "count") or 1,
        byte(ini.getint("led", "brightness"), "brightness"),
        byte(round(ini.getint("behaviour", "hdd_hold_ms") / 10), "hdd_hold_ms / 10"),
        mode,
    ]
    for name in ("power", "turbo", "hdd"):
        data += colour(ini.get("colours", name))
    return data


def intel_hex(data):
    lines = []
    for offset in range(0, len(data), 16):
        chunk = data[offset:offset + 16]
        record = [len(chunk), offset >> 8, offset & 0xFF, 0] + chunk
        lines.append(":" + "".join(f"{b:02X}" for b in record) + f"{-sum(record) & 0xFF:02X}")
    lines.append(":00000001FF")
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    ini = configparser.ConfigParser(inline_comment_prefixes=(";",))
    ini.read(sys.argv[1], encoding="utf-8")
    data = build(ini)
    with open(sys.argv[2], "w", encoding="ascii") as out:
        out.write(intel_hex(data))
    print(f"{len(data)} bytes: " + " ".join(f"{b:02X}" for b in data))


if __name__ == "__main__":
    main()
