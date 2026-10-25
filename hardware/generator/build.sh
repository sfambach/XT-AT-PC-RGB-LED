#!/bin/sh
# Builds schematic, board (Freerouting) and DRC report for one board: sh build.sh v1|v2
# Needs KiCad 7 (pcbnew Python), Java, xvfb-run and the Freerouting jar ($FREEROUTING).
set -e
export KICAD7_FOOTPRINT_DIR=${KICAD7_FOOTPRINT_DIR:-/usr/share/kicad/footprints}
export KICAD7_SYMBOL_DIR=${KICAD7_SYMBOL_DIR:-/usr/share/kicad/symbols}
cd "$(dirname "$0")"
B=$1
H=$(cd .. && pwd)/$B
T=${TMPDIR:-/tmp}/rgbled-$B
mkdir -p $H $T
N=xt-at-pc-rgb-led-$B
python3 mksch.py $B $H/$N.kicad_sch
kicad-cli sch export netlist -o $T/net.net $H/$N.kicad_sch >/dev/null
python3 verify.py $B $T/net.net
rm -f $T/route.kicad_pro $H/$N.kicad_pro
python3 mkpcb.py $B $T/route.kicad_pcb
python3 -c "import pcbnew;b=pcbnew.LoadBoard('$T/route.kicad_pcb');pcbnew.ExportSpecctraDSN(b,'$T/route.dsn')"
rm -f $T/route.ses
(cd $T && timeout 1200 xvfb-run -a java -jar ${FREEROUTING:-freerouting.jar} -de $T/route.dsn -do $T/route.ses -mp ${PASSES:-60} 2>&1 | grep -E "completed|unrouted|incomplete" | tail -3)
python3 finish.py $B $T/route.kicad_pcb $T/route.ses $H/$N.kicad_pcb
python3 -c "import pcbnew;b=pcbnew.LoadBoard('$H/$N.kicad_pcb');pcbnew.WriteDRCReport(b,'$H/drc-report.txt',pcbnew.EDA_UNITS_MILLIMETRES,True)"
grep -E "^\[" $H/drc-report.txt | sed 's/\]:.*/]/' | sort | uniq -c || true
grep -E "unconnected pads" $H/drc-report.txt
