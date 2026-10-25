#!/bin/sh
# Renders top and bottom view of a board to PNG: sh render.sh v1|v2 outdir
set -e
cd "$(dirname "$0")/.."
B=$1; O=$2; P=$B/xt-at-pc-rgb-led-$B.kicad_pcb
kicad-cli pcb export svg --page-size-mode 2 --exclude-drawing-sheet --layers F.Cu,F.SilkS,F.Mask,Edge.Cuts -o $O/$B-top.svg $P >/dev/null
kicad-cli pcb export svg --page-size-mode 2 --exclude-drawing-sheet --mirror --layers B.Cu,B.SilkS,B.Mask,Edge.Cuts -o $O/$B-bottom.svg $P >/dev/null
for s in top bottom; do python3 -c "import cairosvg;cairosvg.svg2png(url='$O/$B-$s.svg',write_to='$O/$B-$s.png',output_width=1400,background_color='white')"; done
