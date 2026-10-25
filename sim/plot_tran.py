#!/usr/bin/env python3
"""Plot three_states_tran.txt (ngspice wrdata) -> three_states_tran.png"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src = sys.argv[1] if len(sys.argv) > 1 else "three_states_tran.txt"
out = sys.argv[2] if len(sys.argv) > 2 else "three_states_tran.png"
cols = [[float(v) for v in line.split()] for line in open(src) if line.strip()]
t = [r[0] * 1000 for r in cols]
hdd = [r[1] > 2.5 for r in cols]
tb = [r[3] > 2.5 for r in cols]
g, b, r = ([row[i] * 1000 for row in cols] for i in (5, 7, 9))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True, gridspec_kw={"height_ratios": [1, 2.4]})
ax1.step(t, [1.2 + h for h in hdd], where="post", color="#1565c0", label="HDD- active")
ax1.step(t, tb, where="post", color="#c62828", label="TURBO- active")
ax1.set_yticks([0.5, 1.7], ["TURBO", "HDD"])
ax1.set_ylim(-0.2, 2.4)
ax1.set_title("XT-AT-PC-RGB-LED v1 - ngspice transient (board resistor 330 ohm)")
ax2.plot(t, g, color="#1a9a2e", lw=2, label="green (power)")
ax2.plot(t, r, color="#c62828", lw=2, label="red (turbo)")
ax2.plot(t, b, color="#1565c0", lw=2, label="blue (HDD)")
ax2.set_ylabel("LED current / mA")
ax2.set_xlabel("time / ms")
ax2.set_ylim(-0.3, 7.8)
ax2.legend(loc="upper right", ncol=3)
ax2.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(out, dpi=130)
