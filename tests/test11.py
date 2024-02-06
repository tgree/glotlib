import math

import numpy as np

import glotlib


NPOINTS = 5000000


w = glotlib.Window(512, 512, msaa=4)
p = w.add_plot(limits=(-6, -6, 6, 6))
X = np.random.normal(0, 1, NPOINTS)
Y = np.random.normal(0, 1, NPOINTS)
p.add_points(X=X, Y=Y)

glotlib.interact()
