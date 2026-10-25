#!/bin/sh
# Gerber ZIP, schematic PDF and top/bottom renders for one board: sh outputs.sh v1|v2
set -e
cd "$(dirname "$0")/.."
B=${1:?board}
N=$B/xt-at-pc-rgb-led-$B
mkdir -p "$B/gerber"
kicad-cli pcb export gerbers -o "$B/gerber/" "$N.kicad_pcb" >/dev/null
kicad-cli pcb export drill -o "$B/gerber/" "$N.kicad_pcb" >/dev/null
rm -f "$N-gerber.zip"
(cd "$B/gerber" && zip -q "../xt-at-pc-rgb-led-$B-gerber.zip" ./*)
rm -r "$B/gerber"
kicad-cli sch export pdf -o "$N-schematic.pdf" "$N.kicad_sch" >/dev/null
sh generator/render.sh "$B" "$B"
rm "$B/$B-top.svg" "$B/$B-bottom.svg"
