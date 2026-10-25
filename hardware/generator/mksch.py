import copy, uuid, sys, os
from sexpr import parse, dump, Sym, find, first
import re
from boards import BOARDS
B = BOARDS[sys.argv[1]]
POWER = set(B['power'])
PARTS = B['parts']

LIBDIR = '/usr/share/kicad/symbols/'
PROJECT = B['name']
ROOT = str(uuid.uuid4())
_cache = {}

def U():
    return str(uuid.uuid4())

def lib_symbols(lib):
    if lib not in _cache:
        path = LIBDIR + lib + '.kicad_sym'
        tree = parse(open(path).read())[0]
        _cache[lib] = {x[1]: x for x in find(tree, 'symbol')}
    return _cache[lib]

def flat(lib, name):
    syms = lib_symbols(lib)
    s = copy.deepcopy(syms[name])
    ext = first(s, 'extends')
    if not ext:
        return s
    base = flat(lib, ext[1])
    pname = ext[1]
    out = [Sym('symbol'), name]
    child_props = {p[1]: p for p in find(s, 'property')}
    for x in base[2:]:
        if isinstance(x, list) and x[0] == 'property':
            out.append(child_props.pop(x[1], x))
        elif isinstance(x, list) and x[0] == 'symbol':
            y = copy.deepcopy(x)
            y[1] = name + y[1][len(pname):]
            out.append(y)
        else:
            out.append(x)
    out[2:2] = []
    for p in child_props.values():
        out.insert(3, p)
    return out

def pins(sym):
    res = {}
    for sub in find(sym, 'symbol'):
        parts = sub[1].rsplit('_', 2)
        unit = int(parts[-2])
        if unit not in (0, 1):
            continue
        for p in find(sub, 'pin'):
            at = first(p, 'at')
            num = first(p, 'number')[1]
            res[num] = (float(at[1]), float(at[2]), int(float(at[3])) if len(at) > 3 else 0, p[1])
    return res

def eff(hide=False, justify=None):
    e = [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]]]
    if justify:
        e.append([Sym('justify'), Sym(justify)])
    if hide:
        e.append(Sym('hide'))
    return e

def prop(k, v, x, y, hide=False, rot=0):
    return [Sym('property'), k, v, [Sym('at'), x, y, rot], eff(hide)]

items, libs = [], {}
UUIDS = {}

def props(ref, value, x, y, away=90):
    if ref.startswith('#'):
        import math
        d = 5 if ref.startswith('#PWR') else -4
        a = math.radians(away)
        vx, vy = round(x + d * math.cos(a), 2), round(y - d * math.sin(a), 2)
        return [prop('Reference', ref, x, y, hide=True), prop('Value', value, vx, vy)]
    if ref[0] in 'RC':
        r = [Sym('property'), 'Reference', ref, [Sym('at'), x + 2.5, y - 1.3, 0], eff(justify='left')]
        v = [Sym('property'), 'Value', value, [Sym('at'), x + 2.5, y + 1.3, 0], eff(justify='left')]
        return [r, v]
    d = {'U1': 22, 'J8': 9}.get(ref, 9)
    return [prop('Reference', ref, x, y - d), prop('Value', value, x, y + d)]

pwr_n = [0]

def place(lib_id, ref, value, fp, x, y, rot=0, pinnums=(), in_bom=True, away=90):
    lib, name = lib_id.split(':')
    if lib_id not in libs:
        s = flat(lib, name)
        s[1] = lib_id
        libs[lib_id] = s
    e = [Sym('symbol'), [Sym('lib_id'), lib_id], [Sym('at'), x, y, rot], [Sym('unit'), 1],
         [Sym('in_bom'), Sym('yes' if in_bom else 'no')], [Sym('on_board'), Sym('yes')], [Sym('dnp'), Sym('no')],
         [Sym('uuid'), UUIDS.setdefault(ref, U())],
         *props(ref, value, x, y, away),
         prop('Footprint', fp, x, y, hide=True),
         prop('Datasheet', '~', x, y, hide=True)]
    for n in pinnums:
        e.append([Sym('pin'), n, [Sym('uuid'), U()]])
    e.append([Sym('instances'), [Sym('project'), PROJECT, [Sym('path'), '/' + ROOT, [Sym('reference'), ref], [Sym('unit'), 1]]]])
    items.append(e)

def power(net, x, y, away):
    pwr_n[0] += 1
    base = 270 if net == 'GND' else 90
    rot = (base - away) % 360
    place('power:' + net, '#PWR%02d' % pwr_n[0], net, '', x, y, rot, ['1'], in_bom=False, away=away)

for ref, (lib_id, value, fp, (x, y), conn) in PARTS.items():
    lib, name = lib_id.split(':')
    sym = flat(lib, name)
    pp = pins(sym)
    assert set(pp) == set(conn), (ref, sorted(set(pp) ^ set(conn)))
    place(lib_id, ref, value, fp, x, y, 0, sorted(pp, key=lambda n: [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', n)]))
    for num, (px, py, ang, ptype) in pp.items():
        ax, ay = round(x + px, 2), round(y - py, 2)
        away = (ang + 180) % 360
        net = conn[num]
        if net is None:
            items.append([Sym('no_connect'), [Sym('at'), ax, ay], [Sym('uuid'), U()]])
        elif net in POWER:
            power(net, ax, ay, away)
        else:
            just = 'left' if away in (0, 90) else 'right'
            items.append([Sym('label'), net, [Sym('at'), ax, ay, away], eff(justify=just), [Sym('uuid'), U()]])

for i, net in enumerate(B['power']):
    x = 30 + i * 20
    pwr_n[0] += 1
    place('power:PWR_FLAG', '#FLG%02d' % (i + 1), 'PWR_FLAG', '', x, 15, 0, ['1'], in_bom=False)
    power(net, x, 15, 270 if net == 'GND' else 90)

texts = [[Sym('text'), B['note'], [Sym('at'), 30, 185, 0], eff(justify='left'), [Sym('uuid'), U()]]]

sch = [Sym('kicad_sch'), [Sym('version'), 20230121], [Sym('generator'), Sym('eeschema')], [Sym('uuid'), ROOT],
       [Sym('paper'), 'A4'],
       [Sym('title_block'), [Sym('title'), B['title']], [Sym('date'), '2026-10-25'], [Sym('rev'), '1.0'], [Sym('company'), 'fambach.net']],
       [Sym('lib_symbols')] + list(libs.values())] + items + texts + [
       [Sym('sheet_instances'), [Sym('path'), '/', [Sym('page'), '1']]]]
open(sys.argv[2], 'w').write(dump(sch) + '\n')
import json
json.dump(UUIDS, open('/tmp/uuids-%s.json' % sys.argv[1], 'w'))
print('ok', len(items))
