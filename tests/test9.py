import math

import numpy as np

import glotlib


NVERTICES = 50000
dX        = 2 * math.pi / (NVERTICES - 1)
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

        self.series  = [self.plot.add_lines(X=[], Y=[], width=1, point_width=1)
                        for _ in AMP_RATES[:-1]]
        self.series += [self.plot.add_steps(X=[], Y=[], width=1, point_width=1)
                        for _ in AMP_RATES[-1:]]
        self.index = 0

    def update_geometry(self, t):
        for s, ar, tr in zip(self.series, AMP_RATES, THICK_RATES):
            s.append_x_y_data([dX * self.index * 100],
                              [math.sin(dX * self.index * 100 + ar) + DY])

            r = 2 * (np.sin(2 * math.pi * tr * t) + 1) + 1
            s.width = r
            s.point_width = r

        self.index += 1

        return True


def main():
    Window()
    glotlib.animate()


if __name__ == '__main__':
    main()
