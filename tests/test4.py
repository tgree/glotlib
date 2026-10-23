import math

import numpy as np

import glotlib
import glotlib.glfw


NVERTICES = 500000
X         = np.arange(NVERTICES) * 2 * math.pi / (NVERTICES - 1)
DY        = 30000

AMP_RATES = [
    1.0,
    0.5,
    0.35,
]
THICK_RATES = [
    0.1,
    0.2,
    0.5,
]


class App(glotlib.GLContextDelegate):
    def __init__(self):
        w = glotlib.glfw.Window(900, 700, msaa=4, delegate=self)

        self.plot = w.ctx.add_plot(limits=(0, DY - 1, 2 * math.pi, DY + 1))

        print('DX: %f' % (X[1] - X[0]))
        Ys = [np.sin(X + ar) + DY for ar in AMP_RATES]
        self.series = [self.plot.add_lines(X=X, Y=Y, width=1, point_width=1)
                       for Y in Ys]

    def update_geometry(self, t):
        for s, ar, tr in zip(self.series, AMP_RATES, THICK_RATES):
            Y = np.sin(X + ar * t) + DY
            s.set_y_data(Y)

            r = 2 * (np.sin(2 * math.pi * tr * t) + 1) + 1
            s.width = r
            s.point_width = r

        return True

    def run(self):
        glotlib.glfw.animate()


def main():
    App().run()


if __name__ == '__main__':
    main()
