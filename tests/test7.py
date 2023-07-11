import math

import numpy as np

import glotlib


NVERTICES = 500000
Xi        = np.arange(NVERTICES) * 2 * math.pi / (NVERTICES - 1)

BOUNDS = [311, 312, 313]
COLORS = [
    (0, 0.8, 0.2, 1),
    (0.8, 0.2, 0, 1),
    (0.8, 0, 0.2, 1),
]
AMP_RATES = [
    1.0,
    3.5,
    0.35,
]
THICK_RATES = [
    0.1,
    0.2,
    0.5,
]
Xs = [ar * Xi for ar in AMP_RATES]


class Window(glotlib.Window):
    def __init__(self):
        super().__init__(900, 650, msaa=4)

        self.series = []

        for bounds, color, X in zip(BOUNDS, COLORS, Xs):
            p = self.add_plot(bounds, limits=(0, -1, 2 * math.pi, 1))

            Y = np.sin(X)
            self.series.append(p.add_lines(X=Xi, Y=Y, color=color, width=1))

        self.add_label((.1, 12.1 / 13), 'tcdc_6_2000014_n4.csv')
        self.fps_label = self.add_label((0.01, 0.01), '')

    def update_geometry(self, t):
        for s, tr, X in zip(self.series, THICK_RATES, Xs):
            Y = np.sin(X + t)
            s.set_y_data(Y)
            s.width = 2 * (np.sin(2 * math.pi * tr * t) + 1) + 1

        fps = glotlib.get_fps()
        if fps is not None:
            self.fps_label.set_text('FPS: %.1f' % fps)
        else:
            self.fps_label.set_text('FPS: Unknown')

        return True


def main():
    Window()
    glotlib.animate()


if __name__ == '__main__':
    main()
