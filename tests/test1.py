import math

import numpy as np

import glotlib
import glotlib.glfw


NVERTICES = 501


w = glotlib.glfw.Window(900, 650, msaa=4)
ctx = w.gl_context

p = ctx.add_plot(limits=(0, -1, math.pi * 2, 1))
X = np.linspace(0, math.pi * 2, NVERTICES)
Y = np.sin(X)
p.add_steps(X=X, Y=Y)
p.set_x_label('X label goes here')
p.set_y_label('Y label goes here')

glotlib.glfw.interact()
