import math, sys
import pcbnew
from boards import BOARDS
import json, os
UUIDS = json.load(open('/tmp/uuids-%s.json' % sys.argv[1]))
LOCAL = os.path.dirname(os.path.abspath(__file__)) + '/../lib/'

FP = '/usr/share/kicad/footprints/'
MM = pcbnew.FromMM
OUT = sys.argv[2]

B = BOARDS[sys.argv[1]]
PLACE = B['place']
BOARD = B['board']
PARTS = B['parts']

b = pcbnew.BOARD()
b.SetCopperLayerCount(2)
ds = b.GetDesignSettings()
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetTrackWidth(MM(0.3))
nc.SetClearance(MM(0.2))
nc.SetViaDrill(MM(0.4))
nc.SetViaDiameter(MM(0.8))
ds.m_TrackMinWidth = MM(0.2)

nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(b, name if name in ('GND', '+5V') else '/' + name)
        b.Add(n)
        nets[name] = n
    return nets[name]

def pad(f, num):
    return [p for p in f.Pads() if p.GetNumber() == num][0]

def pos(p):
    v = p.GetPosition()
    return pcbnew.ToMM(v.x), pcbnew.ToMM(v.y)

for ref, (lib_id, value, fpid, _, conn) in PARTS.items():
    lib, name = fpid.split(':')
    f = pcbnew.FootprintLoad(FP + lib + '.pretty', name)
    f.SetFPID(pcbnew.LIB_ID(lib, name))
    f.SetReference(ref)
    f.SetPath(pcbnew.KIID_PATH('/' + UUIDS[ref]))
    f.SetValue(value)
    b.Add(f)
    kind = PLACE[ref]
    f.SetPosition(pcbnew.VECTOR2I(MM(100), MM(100)))
    if kind[0] == 'origin':
        f.SetOrientationDegrees(kind[2])
        p1 = (100, 100)
        tx, ty = kind[1]
    elif kind[0] == 'at':
        f.SetOrientationDegrees(kind[2])
        p1 = pos(pad(f, '1'))
        tx, ty = kind[1]
    else:
        (x1, y1), (x2, y2) = kind[1], kind[2]
        f.SetOrientationDegrees(0)
        a1, a2 = pos(pad(f, '1')), pos(pad(f, '2'))
        base = math.degrees(math.atan2(-(a2[1] - a1[1]), a2[0] - a1[0]))
        want = math.degrees(math.atan2(-(y2 - y1), x2 - x1))
        f.SetOrientationDegrees(round(want - base) % 360)
        p1 = pos(pad(f, '1'))
        tx, ty = x1, y1
    f.Move(pcbnew.VECTOR2I(MM(tx - p1[0]), MM(ty - p1[1])))
    for p in f.Pads():
        n = conn.get(p.GetNumber())
        if n:
            p.SetNet(net(n))
    if kind[0] == 'pads':
        got = pos(pad(f, '2'))
        assert abs(got[0] - kind[2][0]) < 0.05 and abs(got[1] - kind[2][1]) < 0.05, (ref, got, kind)
    if ref[0] in 'RD' and kind[0] == 'pads':
        # Flat resistors/diodes: reference inside the body outline, along the part.
        (x1, y1), (x2, y2) = kind[1], kind[2]
        t = f.Reference()
        t.SetTextSize(pcbnew.VECTOR2I(MM(1.0), MM(1.0)))
        t.SetTextThickness(MM(0.15))
        t.SetPosition(pcbnew.VECTOR2I(MM((x1 + x2) / 2), MM((y1 + y2) / 2)))
        # KiCad 7 stores footprint text relative to the footprint orientation.
        t.SetTextAngleDegrees(((90 if abs(x2 - x1) < 0.01 else 0) - f.GetOrientationDegrees()) % 360)

x0, y0, x1, y1 = BOARD
# Mounting rule for all boards: two M3 holes on the long axis, centred, 3.5 mm from the short edges.
for i, hx in enumerate((x0 + 3.5, x1 - 3.5)):
    h = pcbnew.FootprintLoad(FP + 'MountingHole.pretty', 'MountingHole_3.2mm_M3')
    h.SetFPID(pcbnew.LIB_ID('MountingHole', 'MountingHole_3.2mm_M3'))
    h.SetReference('H%d' % (i + 1))
    h.SetValue('M3')
    h.SetPosition(pcbnew.VECTOR2I(MM(hx), MM((y0 + y1) / 2)))
    h.Reference().SetVisible(False)
    b.Add(h)
pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
for i in range(4):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.1))
    s.SetStart(pcbnew.VECTOR2I(MM(pts[i][0]), MM(pts[i][1])))
    s.SetEnd(pcbnew.VECTOR2I(MM(pts[(i + 1) % 4][0]), MM(pts[(i + 1) % 4][1])))
    b.Add(s)

def text(t, x, y, size=1.0, layer=pcbnew.F_SilkS, rot=0):
    s = pcbnew.PCB_TEXT(b)
    s.SetText(t)
    s.SetLayer(layer)
    s.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    s.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    s.SetTextThickness(MM(size * 0.15))
    s.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        s.SetMirrored(True)
    b.Add(s)

for t, x, y, sz in B['texts']:
    text(t, x, y, sz)
for t, x, y, sz in B['btexts']:
    s = text(t, x, y, sz, pcbnew.B_SilkS)

def zone(layer):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNet(net('GND'))
    z.SetLocalClearance(MM(0.3))
    z.SetMinThickness(MM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    ol = z.Outline()
    ol.NewOutline()
    m = 0.5
    for x, y in [(x0 + m, y0 + m), (x1 - m, y0 + m), (x1 - m, y1 - m), (x0 + m, y1 - m)]:
        ol.Append(MM(x), MM(y))
    b.Add(z)

if '--zones' in sys.argv:
    zone(pcbnew.F_Cu)
    zone(pcbnew.B_Cu)
b.Save(OUT)
print('saved', OUT)
