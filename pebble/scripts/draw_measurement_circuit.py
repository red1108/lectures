"""Draw the register-level ghosting and phase-correction circuit."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle

OUTPUT = Path(__file__).resolve().parents[1] / 'public' / 'figures'
OUTPUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'mathtext.fontset': 'stix', 'svg.fonttype': 'path'})
fig, ax = plt.subplots(figsize=(14, 4.8))
fig.patch.set_facecolor('white')
ax.set(xlim=(0, 1400), ylim=(480, 0), aspect='equal')
ax.axis('off')
ink = '#284b48'
muted = '#71877e'
green = '#3d7770'
rust = '#a45f3e'


def wire(x1, x2, y):
    ax.plot([x1, x2], [y, y], color=ink, lw=1.8, zorder=1)


def label(x, y, text, size=19, color=ink, ha='center'):
    ax.text(x, y, text, fontsize=size, color=color, ha=ha, va='center', zorder=4)


def gate(x, y, width, height, text):
    ax.add_patch(Rectangle((x-width/2, y-height/2), width, height,
                           facecolor='#eef5ef', edgecolor=green, lw=1.8, zorder=3))
    label(x, y, text, 24)


label(300, 32, 'Ghosting', 20)
label(995, 32, 'Correction', 20)
ax.plot([125, 450], [58, 58], color='#b9c9bc', lw=1.2)
ax.plot([710, 1210], [58, 58], color='#b9c9bc', lw=1.2)

# Each wire is a register bus. The input register is retained throughout.
label(55, 140, r'$|x\rangle$', 25)
label(55, 280, r'$|f(x)\rangle$', 25)
wire(115, 1280, 140)
wire(115, 420, 280)
wire(680, 1280, 280)
for x, y in [(160, 140), (160, 280), (695, 280)]:
    ax.plot([x-5, x+5], [y+7, y-7], color=ink, lw=1.5)
label(140, 330, r'$k$ qubits', 15, muted)
label(1330, 140, r'$|x\rangle$', 25)
label(1330, 280, r'$|0^k\rangle$', 25)

gate(245, 280, 105, 72, r'$H^{\otimes k}$')
# Computational-basis measurement after H is an X-basis measurement.
ax.add_patch(Rectangle((345, 244), 80, 72, facecolor='white', edgecolor=ink, lw=1.8, zorder=3))
ax.add_patch(Arc((385, 290), 52, 52, theta1=180, theta2=360, color=ink, lw=1.5, zorder=4))
ax.annotate('', xy=(404, 260), xytext=(383, 292),
            arrowprops={'arrowstyle': '-|>', 'color': ink, 'lw': 1.5}, zorder=4)
label(300, 372, 'X-basis measurement', 16, muted)

# No quantum wire crosses the released-register interval.
ax.add_patch(Circle((525, 244), 25, facecolor='#f4e6d7', edgecolor=rust,
                    lw=1.5, linestyle=(0, (4, 3))))
label(525, 244, 'G', 22, rust)
label(525, 295, 'released', 16, muted)
label(640, 280, r'$|0^k\rangle$', 25)
label(640, 320, 'fresh', 15, muted)

# Store all k outcome bits and feed them forward to the phase correction.
for offset in (-2.5, 2.5):
    ax.plot([425, 450+offset, 450+offset, 970+offset, 970+offset],
            [280+offset, 280+offset, 420+offset, 420+offset, 316],
            color=rust, lw=1.35, zorder=2)
label(705, 448, r'$m\in\{0,1\}^k$  (classical)', 18, rust)

gate(785, 210, 110, 212, r'$U_f$')
gate(970, 280, 115, 72, r'$Z(m)$')
gate(1155, 210, 110, 212, r'$U_f^\dagger$')
label(785, 80, 'Recompute', 16, muted)
label(970, 200, 'Correct', 16, muted)
label(1155, 80, 'Uncompute', 16, muted)

fig.subplots_adjust(left=.01, right=.99, bottom=.01, top=.99)
svg_path = OUTPUT / 'measurement-correction.svg'
fig.savefig(svg_path, facecolor='white')
svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines()) + '\n')
fig.savefig(OUTPUT / 'measurement-correction.png', dpi=200, facecolor='white')
plt.close(fig)
