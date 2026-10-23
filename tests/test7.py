import math
from enum import Enum

import numpy as np

import glotlib
import glotlib.glfw


NVERTICES = 500000
Xi        = np.arange(NVERTICES) * 2 * math.pi / (NVERTICES - 1)

H_BOUNDS = [311, 312, 313]
V_BOUNDS = [131, 132, 133]
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


class ViewMode(Enum):
    HORIZONTAL  = 1
    VERTICAL    = 2


class App(glotlib.GLContextDelegate):
    def __init__(self):
        w = glotlib.glfw.Window(900, 650, msaa=4, delegate=self)

        self.ctx       = w.ctx
        self.series    = []
        self.view_mode = ViewMode.HORIZONTAL

        for bounds, color, X in zip(H_BOUNDS, COLORS, Xs):
            p = w.ctx.add_plot(bounds, limits=(0, -1, 2 * math.pi, 1))

            Y = np.sin(X)
            self.series.append(p.add_lines(X=Xi, Y=Y, color=color, width=1))

        w.ctx.add_label((.1, 12.1 / 13), 'tcdc_6_2000014_n4.csv')
        self.fps_label = w.ctx.add_label((0.01, 0.01), '')

    def _set_mode_vertical(self):
        if self.view_mode == ViewMode.VERTICAL:
            return

        for bounds, p in zip(V_BOUNDS, self.ctx.plots):
            p.set_bounds(bounds)
        self.view_mode = ViewMode.VERTICAL

    def _set_mode_horizontal(self):
        if self.view_mode == ViewMode.HORIZONTAL:
            return

        for bounds, p in zip(H_BOUNDS, self.ctx.plots):
            p.set_bounds(bounds)
        self.view_mode = ViewMode.HORIZONTAL

    def handle_key_press(self, key):
        if key == glotlib.constants.KEY_ESCAPE:
            if self.view_mode == ViewMode.HORIZONTAL:
                self._set_mode_vertical()
            else:
                self._set_mode_horizontal()
            self.ctx.mark_dirty()

    def update_geometry(self, t):
        for s, tr, X in zip(self.series, THICK_RATES, Xs):
            Y = np.sin(X + t)
            s.set_y_data(Y)
            s.width = 2 * (np.sin(2 * math.pi * tr * t) + 1) + 1

        fps = glotlib.glfw.get_fps()
        if fps is not None:
            self.fps_label.set_text('FPS: %.1f' % fps)
        else:
            self.fps_label.set_text('FPS: Unknown')

        return True

    def run(self):
        glotlib.glfw.animate()


def main():
    App().run()


if __name__ == '__main__':
    main()
