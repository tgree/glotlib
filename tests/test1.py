import math

import numpy as np

import glotlib


NVERTICES = 501


w = glotlib.Window(900, 650, msaa=4)
p = w.add_plot(limits=(0, -1, math.pi * 2, 1))
X = np.linspace(0, math.pi * 2, NVERTICES)
Y = np.sin(X)
p.add_steps(X=X, Y=Y)

glotlib.interact()
