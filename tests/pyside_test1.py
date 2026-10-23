import math
import sys

import numpy as np

from PySide6.QtWidgets import QApplication

import glotlib.pyside6


NVERTICES = 501


glotlib.pyside6.init_backend()

app = QApplication(sys.argv)

w = glotlib.pyside6.Window(900, 650, msaa=None)
w.show()

p = w.ctx.add_plot(limits=(0, -1, math.pi * 2, 1))
X = np.linspace(0, math.pi * 2, NVERTICES)
Y = np.sin(X)
p.add_steps(X=X, Y=Y)
p.set_x_label('X label goes here')
p.set_y_label('Y label goes here')

app.exec()
