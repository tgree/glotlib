import math

import numpy as np

import glotlib


NVERTICES = 500

BOUNDS = [312, 313]
COLORS = [
    (0.8, 0.2, 0, 1),
    (0.8, 0, 0.2, 1),
]
AMP_RATES = [3.5, 0.35]

Xi = np.arange(NVERTICES) * 2 * math.pi / (NVERTICES - 1)
Xs = [ar * Xi for ar in AMP_RATES]


w = glotlib.Window(900, 650, msaa=4)

# Draw a circle in the top plot.
p = w.add_plot(311, limits=(-1, -1, 1, 1), aspect=glotlib.ASPECT_SQUARE)
T = np.linspace(0, 2 * math.pi, num=NVERTICES, endpoint=False)
p.add_hline(0, color=(0.5, 0.75, 0.5, 1))
p.add_hline(1, color=(0.5, 0.75, 0.5, 1))
p.add_hline(-1, color=(0.5, 0.75, 0.5, 1))
p.add_vline(0, color=(0.5, 0.75, 0.5, 1))
p.add_vline(1, color=(0.5, 0.75, 0.5, 1))
p.add_vline(-1, color=(0.5, 0.75, 0.5, 1))
p.add_lines(X=np.cos(T), Y=np.sin(T), color=(0, 0.8, 0.2, 1), width=1,
            point_width=3)

# Draw sine waves in the next two plots.
for bounds, color, X in zip(BOUNDS, COLORS, Xs):
    p = w.add_plot(bounds, limits=(0, -1, 2 * math.pi, 1))
    p.add_lines(X=Xi, Y=np.sin(X), color=color, width=1, point_width=3)

glotlib.animate()
