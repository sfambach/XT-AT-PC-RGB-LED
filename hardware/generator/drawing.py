"""2D dimension drawing (top, front, side view) for a board, read from the KiCad PCB."""
import sys
import pcbnew
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

T = 1.6        # board thickness
H_TOP = 8.5    # pin headers, DIP socket and TO-92 above board (assumption)
H_BOT = 3.0    # pins / leads below board (assumption)

v = sys.argv[1]
b = pcbnew.LoadBoard(f"../{v}/xt-at-pc-rgb-led-{v}.kicad_pcb")
bb = b.GetBoardEdgesBoundingBox()
x0, y0 = pcbnew.ToMM(bb.GetX()) + 0.05, pcbnew.ToMM(bb.GetY()) + 0.05
W, H = round(pcbnew.ToMM(bb.GetWidth()) - 0.1, 2), round(pcbnew.ToMM(bb.GetHeight()) - 0.1, 2)
holes, parts = [], []
for f in b.GetFootprints():
    r = f.GetReference()
    p = f.GetPosition()
    x, y = round(pcbnew.ToMM(p.x) - x0, 2), round(pcbnew.ToMM(p.y) - y0, 2)
    if r.startswith("H"):
        holes.append((x, y))
    elif r.startswith(("J", "U")):
        fb = f.GetBoundingBox(False, False)
        parts.append((r, pcbnew.ToMM(fb.GetX()) - x0, pcbnew.ToMM(fb.GetY()) - y0,
                      pcbnew.ToMM(fb.GetWidth()), pcbnew.ToMM(fb.GetHeight())))
holes.sort()

def dim(ax, a, b, off, text, vertical=False):
    kw = dict(arrowprops=dict(arrowstyle="<->", lw=0.7), annotation_clip=False)
    if vertical:
        ax.annotate("", (off, a), (off, b), **kw)
        ax.text(off - 1, (a + b) / 2, text, rotation=90, ha="right", va="center", fontsize=7)
    else:
        ax.annotate("", (a, off), (b, off), **kw)
        up = -0.8 if ax.yaxis_inverted() else 0.8
        ax.text((a + b) / 2, off + up, text, ha="center", va="bottom", fontsize=7)

def mm(x):
    return f"{x:g}".replace(".", ",")

fig = plt.figure(figsize=(11, 7.5))
gs = fig.add_gridspec(2, 2, width_ratios=[W + 12, H + 12], height_ratios=[H + 10, H_TOP + H_BOT + 12], wspace=0.15, hspace=0.1)
top = fig.add_subplot(gs[0, 0]); front = fig.add_subplot(gs[1, 0]); side = fig.add_subplot(gs[1, 1]); note = fig.add_subplot(gs[0, 1])

# top view
top.add_patch(Rectangle((0, 0), W, H, fill=False, lw=1.2))
for r, x, y, w, h in parts:
    top.add_patch(Rectangle((x, y), w, h, fill=False, lw=0.5, ls="--", color="grey"))
    top.text(x + w / 2, y + h / 2, r, ha="center", va="center", fontsize=6, color="grey")
for x, y in holes:
    top.add_patch(Circle((x, y), 1.6, fill=False, lw=0.9))
    top.plot([x - 2.5, x + 2.5], [y, y], lw=0.4, color="k"); top.plot([x, x], [y - 2.5, y + 2.5], lw=0.4, color="k")
top.text(holes[0][0] + 3, holes[0][1] + 4.5, "2× Ø3,2 (M3)", ha="left", fontsize=7)
dim(top, 0, W, -4, mm(W))
dim(top, 0, holes[0][0], -1.2, mm(holes[0][0]))
dim(top, holes[0][0], holes[1][0], H + 3.5, mm(holes[1][0] - holes[0][0]))
dim(top, 0, H, -4.5, mm(H), vertical=True)
dim(top, 0, holes[0][1], -1.2, mm(holes[0][1]), vertical=True)
top.set_title("Draufsicht (Bestückungsseite)", fontsize=9)
top.set_xlim(-8, W + 4); top.set_ylim(H + 6, -7)

def elevation(ax, L, title):
    ax.add_patch(Rectangle((0, 0), L, T, color="#6a8f4e"))
    ax.add_patch(Rectangle((0, T), L, H_TOP, fill=False, lw=0.6, ls="--", color="grey"))
    ax.add_patch(Rectangle((0, -H_BOT), L, H_BOT, fill=False, lw=0.6, ls=":", color="grey"))
    ax.text(L / 2, T + H_TOP / 2, "Bauteile", ha="center", va="center", fontsize=6, color="grey")
    dim(ax, 0, L, -H_BOT - 2, mm(L))
    dim(ax, T, T + H_TOP, L + 4, "ca. " + mm(H_TOP), vertical=True)
    dim(ax, 0, T, -1.5, mm(T), vertical=True)
    ax.set_title(title, fontsize=9)
    ax.set_xlim(-6, L + 5); ax.set_ylim(-H_BOT - 5, T + H_TOP + 2)

elevation(front, W, "Vorderansicht")
elevation(side, H, "Seitenansicht (von rechts)")

note.axis("off")
note.text(0, 1, f"XT-AT-PC-RGB-LED {v}\nMaße in mm\n\n"
         "Platine 2-lagig, 1,6 mm\n"
         "M3-Regel: 2 Löcher auf der\nlangen Achse, mittig, 3,5 mm\nvon den kurzen Kanten\n\n"
         "Annahmen (nicht gemessen):\n"
         f"- oben ca. {mm(H_TOP)} mm (Stiftleisten,\n  R/D liegend)\n"
         f"- unten ca. {mm(H_BOT)} mm (Beinchen\n  gekürzt)\n"
         "- abgewinkelte Stiftleisten\n  ändern die Bauhöhe",
         fontsize=8, va="top", family="monospace", transform=note.transAxes)

for ax in (top, front, side):
    ax.set_aspect("equal"); ax.axis("off")
fig.savefig(f"../drawings/{v}-dimensions.png", dpi=150, bbox_inches="tight")
fig.savefig(f"../drawings/{v}-dimensions.svg", bbox_inches="tight")
print(v, W, H, holes)
