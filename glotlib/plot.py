import math

import numpy as np
from OpenGL import GL

import glotlib.miter_lines
from . import matrix
from . import constants
from . import ticker
from . import fonts
from . import programs
from . import colors
from .label import Label
from .series import Series
from .hline import HLine
from .vline import VLine
from .step_series import StepSeries


PAD_L       = 0.05
PAD_B       = 0.025
MAX_H_TICKS = 10
MAX_V_TICKS = 7


class DragState:
    def __init__(self, plot, mbs):
        self.plot            = plot
        self.mbs             = mbs
        self.click_fb_point  = plot._window_to_data(mbs.click_x, mbs.click_y)

    def handle_mouse_moved(self, x, y):
        self.plot._gen_mvp_from_point(self.click_fb_point, (x, y))
        self.plot._gen_ticks()
        self.plot._update_shared_axes()


class NoAspect:
    @staticmethod
    def apply(wh, _window_wh):
        return wh

    @staticmethod
    def adjust_vert(wh, _window_wh):
        return wh

    @staticmethod
    def adjust_horiz(wh, _window_wh):
        return wh


class SquareAspect:
    @staticmethod
    def apply(wh, window_wh):
        '''
        Grow the dimension of the smaller axis until a square aspect ratio is
        achieved.
        '''
        window_aspect = window_wh[0] / window_wh[1]
        wh_aspect     = wh[0] / wh[1]
        if window_aspect < wh_aspect:
            return (wh[0], wh[0] / window_aspect)
        return (wh[1] * window_aspect, wh[1])

    @staticmethod
    def adjust_vert(wh, window_wh):
        '''
        Adjust the vertical dimension to achieve a square aspect ratio.
        '''
        window_aspect = window_wh[1] / window_wh[0]
        return (wh[0], wh[0] * window_aspect)

    @staticmethod
    def adjust_horiz(wh, window_wh):
        '''
        Adjust the horizontal dimension to achieve a square aspect ratio.
        '''
        window_aspect = window_wh[0] / window_wh[1]
        return (wh[1] * window_aspect, wh[1])


class Plot:
    ASPECT_MAP = {
        constants.ASPECT_NONE   : NoAspect,
        constants.ASPECT_SQUARE : SquareAspect,
    }

    def __init__(self, window, bounds=(0, 0, 1, 1), limits=None, _colors=None,
                 max_h_ticks=MAX_H_TICKS, max_v_ticks=MAX_V_TICKS,
                 aspect=constants.ASPECT_NONE, sharex=None, sharey=None,
                 visible=True):
        l, b, r, t = limits if limits else (-1, -1, 1, 1)

        self.window         = window
        self.bounds         = bounds
        self.color_iter     = (colors.cycle(_colors)
                               if _colors else colors.cycle(colors.tab10))
        self.max_h_ticks    = max_h_ticks
        self.max_v_ticks    = max_v_ticks
        self.aspect         = Plot.ASPECT_MAP[aspect]
        self.sharex         = sharex.sharex if sharex else set()
        self.sharey         = sharey.sharey if sharey else set()
        self.visible        = visible
        self.x              = None
        self.y              = None
        self.w              = None
        self.h              = None
        self.fb_x           = None
        self.fb_y           = None
        self.fb_w           = None
        self.fb_h           = None
        self.rmatrix        = None
        self.rmatrixi       = None
        self.mvp            = None
        self.mvpi           = None
        self.mvp32          = None
        self.mouse_state    = None
        self.series         = []
        self.graph_artists  = []
        self.border_lines   = glotlib.miter_lines.from_points([(0, 0)] * 6)
        self.h_ticks        = []
        self.v_ticks        = []

        self.sharex.add(self)
        self.sharey.add(self)

        for _ in range(max_h_ticks):
            self.h_ticks.append(Label((0, 0), '', fonts.vera(12, 0),
                                      anchor='N'))
        for _ in range(max_v_ticks):
            self.v_ticks.append(Label((0, 0), '', fonts.vera(12, 0),
                                      anchor='E'))

        self._gen_bounds()
        l, r, b, t = self._adjust_lrbt(l, r, b, t)
        self._renormalize(l, r, b, t)
        self._gen_ticks()
        self._update_shared_axes()

    def _get_data_bounds(self):
        l = self.mvpi[0][3] - self.mvpi[0][0]
        r = self.mvpi[0][3] + self.mvpi[0][0]
        b = self.mvpi[1][3] - self.mvpi[1][1]
        t = self.mvpi[1][3] + self.mvpi[1][1]
        l, b, _, _ = self.rmatrixi @ (l, b, 0, 1)
        r, t, _, _ = self.rmatrixi @ (r, t, 0, 1)
        return l, r, b, t

    def _update_shared_axes(self):
        l, r, b, t = self._get_data_bounds()
        for p in self.sharex:
            if p is not self:
                p._set_x_lim(l, r)
        for p in self.sharey:
            if p is not self:
                p._set_y_lim(b, t)

    def _adjust_lrbt(self, l, r, b, t, rx=1, ry=1):
        '''
        Given l, r, b, t bounds, adjust them so that the center point of the
        rectangle is maintained but the edges grow/shrink as necessary to
        maintain the plot's data space aspect ratio.
        '''
        w    = (r - l) * rx
        h    = (t - b) * ry
        w, h = self.aspect.apply((w, h), (self.w, self.h))
        xc   = (l + r) / 2
        yc   = (b + t) / 2
        l    = xc - w / 2
        r    = xc + w / 2
        b    = yc - h / 2
        t    = yc + h / 2
        return l, r, b, t

    def _handle_resize(self):
        p_w    = self.w
        p_h    = self.h
        xc, yc = self._window_to_data(self.x + self.w / 2, self.y + self.h / 2)

        self._gen_bounds()

        if self.aspect == SquareAspect:
            n_w = self.w
            n_h = self.h
            self._gen_mvp_from_point((xc, yc),
                                     (self.x + n_w / 2, self.y + n_h / 2),
                                     rx=(n_w / p_w), ry=(n_h / p_h))

        self._gen_ticks()

    def _gen_bounds(self):
        x = self.x = int((self.bounds[0] + PAD_L) * self.window.w_w)
        y = self.y = int((self.bounds[1] + PAD_B) * self.window.w_h)
        w = self.w = (int((self.bounds[2] - self.bounds[0] - PAD_L) *
                      self.window.w_w))
        h = self.h = (int((self.bounds[3] - self.bounds[1] - PAD_B) *
                      self.window.w_h))

        x += 0.5
        y += 0.5
        ps = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        vs = glotlib.miter_lines.vertices_from_poly_points(ps)
        self.border_lines._update(vs)

        x += 0.5
        y += 0.5
        w -= 1
        h -= 1
        self.fb_x  = round(x * self.window.fb_w / self.window.w_w)
        self.fb_y  = round(y * self.window.fb_h / self.window.w_h)
        self.fb_w  = round(w * self.window.fb_w / self.window.w_w)
        self.fb_h  = round(h * self.window.fb_h / self.window.w_h)

    def _renormalize(self, l, r, b, t):
        self.rmatrix  = matrix.ortho(l, r, b, t, -1, 1, dtype=np.float64)
        self.rmatrixi = matrix.unortho(l, r, b, t, -1, 1, dtype=np.float64)
        self.mvp      = matrix.ortho(-1, 1, -1, 1, -1, 1, dtype=np.float64)
        self.mvpi     = matrix.unortho(-1, 1, -1, 1, -1, 1, dtype=np.float64)
        self.mvp32    = np.array(self.mvp, dtype=np.float32)
        for ga in self.graph_artists:
            ga.renormalize()

    def _gen_ticks(self):
        l, r, b, t = self._get_data_bounds()

        ticks, texts = ticker.gen_ticks_and_texts(l, r, Nmax=self.max_h_ticks)
        for i, h_t in enumerate(self.h_ticks):
            if i < len(ticks):
                x = (ticks[i] - l) * self.w / (r - l)
                h_t.set_pos((self.x + x, self.y))
                h_t.set_text(texts[i])
            else:
                h_t.pos = (0, 0)
                h_t.set_text('')

        ticks, texts = ticker.gen_ticks_and_texts(b, t, Nmax=self.max_v_ticks)
        for i, v_t in enumerate(self.v_ticks):
            if i < len(ticks):
                y = int((ticks[i] - b) * self.h / (t - b))
                v_t.set_pos((self.x - 2, self.y + y + 2))
                v_t.set_text(texts[i])
            else:
                v_t.pos = (0, 0)
                v_t.set_text('')

    def _gen_mvp_from_limits(self, l, r, b, t):
        '''
        Generates mvp and mvpi such that we will be viewing the specified
        rectangle of data dimensions.  This is a simple orthographic
        projection.
        '''
        ml, mb, _, _ = self.rmatrix @ (l, b, 0, 1)
        mr, mt, _, _ = self.rmatrix @ (r, t, 0, 1)
        self.mvp   = matrix.ortho(ml, mr, mb, mt, -1, 1, dtype=np.float64)
        self.mvpi  = matrix.unortho(ml, mr, mb, mt, -1, 1, dtype=np.float64)
        self.mvp32 = np.array(self.mvp, dtype=np.float32)
        self.window.mark_dirty()

        K        = 2**(23 - 2)
        window_w = self.w
        window_h = self.h
        mvp_w    = 2 * self.mvpi[0][0]
        mvp_h    = 2 * self.mvpi[1][1]
        max_x    = max(abs(ml), abs(mr))
        max_y    = max(abs(mb), abs(mt))
        renorm_x = (max_x > mvp_w * K / window_w)
        renorm_y = (max_y > mvp_h * K / window_h)
        if renorm_x or renorm_y:
            self._renormalize(l, r, b, t)

    def _gen_mvp_from_dimensions_and_point(self, w, h, d_point, p_point):
        '''
        Generates mvp and mvpi such that we will be viewing a rectangle of
        data dimensions w x h with the (x, y) data point d_point locked to the
        center of the (x, y) plot pixel p_point.
        '''
        p_x_ratio  = (p_point[0] - self.x) / self.w
        p_y_ratio  = (p_point[1] - self.y) / self.h
        l          = d_point[0] - p_x_ratio * w
        r          = l + w
        b          = d_point[1] - p_y_ratio * h
        t          = b + h
        self._gen_mvp_from_limits(l, r, b, t)

    def _gen_mvp_from_point(self, d_point, p_point, rx=1, ry=1):
        '''
        Generates mvp and mvpi such that the current dimensions are unchanged
        (or optionally multiplied by rx and ry) but data point d_point will
        appear under the plot pixel p_point.
        '''
        w = rx * 2 * self.mvpi[0][0] * self.rmatrixi[0][0]
        h = ry * 2 * self.mvpi[1][1] * self.rmatrixi[1][1]
        self._gen_mvp_from_dimensions_and_point(w, h, d_point, p_point)

    def _window_to_data(self, x, y):
        '''
        Converts a window coordinate to a data coordinate.
        '''
        x = 2 * (x - self.x) / self.w - 1
        y = 2 * (y - self.y) / self.h - 1
        v = self.rmatrixi @ self.mvpi @ (x, y, 0, 1)
        return v[0], v[1]

    def _data_to_window(self, x, y):
        '''
        Converts a data coordinate to a window coordinate.
        '''
        x, y, _, _ = self.mvp @ self.rmatrix @ (x, y, 0, 1)
        y = (y + 1) * self.h / 2 + self.y
        x = (x + 1) * self.w / 2 + self.x
        return x, y

    def handle_mouse_down(self, mbs):
        if self.mouse_state:
            return

        if mbs.button == constants.MOUSE_BUTTON_LEFT:
            self.mouse_state = DragState(self, mbs)

    def handle_mouse_moved(self, x, y):
        # print('%f x %f -> %.20f x %.20f' %
        #       (x, y, *self._window_to_data(x, y)))
        if self.mouse_state:
            self.mouse_state.handle_mouse_moved(x, y)

    def handle_mouse_up(self, mbs):
        if not self.mouse_state:
            return
        if mbs.button != self.mouse_state.mbs.button:
            return

        self.mouse_state = None

    def handle_mouse_scrolled(self, x, y, dx, dy, shift, alt):
        dx = max(dx, -99)
        dx = min(dx, 99)
        dy = max(dy, -99)
        dy = min(dy, 99)
        if self.aspect == SquareAspect:
            rx = ry = 1 - dy / 100
        elif shift:
            rx = 1 + dx / 100
            ry = 1 - dy / 100
        elif alt:
            rx = 1
            ry = 1 - dy / 100
        else:
            rx = ry = 1 - dy / 100

        fx, fy = self._window_to_data(x, y)
        self._gen_mvp_from_point((fx, fy), (x, y), rx=rx, ry=ry)
        self._gen_ticks()
        self._update_shared_axes()

    def _add_series(self, cls, points=None, X=None, Y=None, color=None,
                    **kwargs):
        color = colors.make(color, self.color_iter)

        if points is not None:
            vs = np.array(points, dtype=np.float64)
        else:
            vs = np.column_stack((X, Y)).astype(np.float64, copy=False)

        s = cls(self, vs, color=color, **kwargs)
        s.renormalize()
        self.series.append(s)
        self.graph_artists.append(s)
        return s

    def add_lines(self, points=None, **kwargs):
        '''
        Adds a set of Lines joining all the specified points.  The points can
        be encoded in a list of (x, y) tuples using the points keyword argument,
        or they can be encoded as separate lists of X and Y coordinates using
        the X and Y keyword arguments.
        '''
        return self._add_series(Series, points=points, **kwargs)

    def add_points(self, points=None, width=1, **kwargs):
        '''
        Adds a set of Points at the specified points.  The points can be
        encoded in a list of (x, y) tuples using the points keyword argument,
        or they can be encoded as separate lists of X and Y coordinates using
        the X and Y keyword arguments.
        '''
        return self._add_series(Series, points=points, width=None,
                                point_width=width, **kwargs)

    def add_steps(self, points=None, **kwargs):
        '''
        Adds a set of steps between the specified points.
        '''
        return self._add_series(StepSeries, points=points, **kwargs)

    def add_hline(self, y, color=None, **kwargs):
        '''
        Adds a horizontal line at the specified y coordinate.
        '''
        color = colors.make(color, self.color_iter)
        hl    = HLine(self, y, color=color, **kwargs)
        hl.renormalize()
        self.graph_artists.append(hl)
        return hl

    def add_vline(self, x, color=None, **kwargs):
        '''
        Adds a vertical line at the specified x coordinate.
        '''
        color = colors.make(color, self.color_iter)
        vl    = VLine(self, x, color=color, **kwargs)
        vl.renormalize()
        self.graph_artists.append(vl)
        return vl

    def snap_bounds(self):
        l = b = math.inf
        r = t = -math.inf
        for s in self.series:
            if len(s.vertices) == 0:
                continue

            sl, sb = s.vertices.min(axis=0)
            sr, st = s.vertices.max(axis=0)
            l = min(l, sl)
            b = min(b, sb)
            r = max(r, sr)
            t = max(t, st)
        if l == r:
            l -= 0.5
            r += 0.5
        if b == t:
            b -= 0.5
            t += 0.5
        if l >= r or b >= t:
            return

        l, r, b, t = self._adjust_lrbt(l, r, b, t, 1.05, 1.05)
        self._gen_mvp_from_limits(l, r, b, t)
        self._gen_ticks()
        self._update_shared_axes()

    def _set_x_lim(self, l, r):
        _, _, b, t = self._get_data_bounds()
        _, h = self.aspect.adjust_vert((r - l, t - b), (self.w, self.h))
        b    = (b + t - h) / 2
        t    = (b + t + h) / 2
        self._gen_mvp_from_limits(l, r, b, t)
        self._gen_ticks()

    def _set_y_lim(self, b, t):
        l, r, _, _ = self._get_data_bounds()
        w, _ = self.aspect.adjust_horiz((r - l, t - b), (self.w, self.h))
        l    = (l + r - w) / 2
        r    = (l + r + w) / 2
        self._gen_mvp_from_limits(l, r, b, t)
        self._gen_ticks()

    def show(self):
        self.visible = True
        self.window.mark_dirty()

    def hide(self):
        self.visible = False
        self.window.mark_dirty()

    def set_bounds(self, bounds, **kwargs):
        self.window.set_plot_bounds(self, bounds, **kwargs)

    def draw(self, t):
        GL.glViewport(0, 0, self.window.fb_w, self.window.fb_h)
        self.border_lines.bind(0)
        self.border_lines.use_program(1, 0, self.window.mvp, (0, 0, 0, 1),
                                      (self.window.w_w, self.window.w_h))
        self.border_lines.draw()

        fonts.vera(12, 0).bind(0)
        programs.text.useProgram()
        programs.text.uniform1f('u_z', 0)
        programs.text.uniform4f('u_color', 0, 0, 0, 1)
        programs.text.uniform1i('u_sampler', 0)
        GL.glEnable(GL.GL_BLEND)
        for h_t in self.h_ticks:
            h_t.draw_batched(self.window.mvp)
        for v_t in self.v_ticks:
            v_t.draw_batched(self.window.mvp)
        GL.glDisable(GL.GL_BLEND)

        GL.glViewport(self.fb_x, self.fb_y, self.fb_w, self.fb_h)
        for ga in self.graph_artists:
            # TODO: I feel like this is where self.mvp32 goes.
            ga.draw(t, 0, self.mvp, (self.w, self.h))
