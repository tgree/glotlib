import math

import numpy as np

import glotlib


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


class Window(glotlib.Window):
    def __init__(self):
        super().__init__(900, 700, msaa=4)

        self.plot = self.add_plot(limits=(0, DY - 1, 2 * math.pi, DY + 1))

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


def main():
    Window()
    glotlib.animate()


if __name__ == '__main__':
    main()
