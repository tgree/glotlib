from OpenGL import GL

import glotlib.plot
import glotlib.main
from . import matrix
from . import constants
from . import fonts
from . import label


# This is the padding on each side of the flexible window area.  Note that
# this amount of padding exists on the left and right sides and on the top and
# bottom sides, so the total padding is double these values.
PAD_H = 0.05
PAD_V = 0.05


def _bounds_hwp(h, w, p):
    '''
    Given a grid of height h and width w, returns the bounds (l, b, r, t) of
    the grid cell p, with coordinates as percentages of the total grid.  The
    value p is specified by numbering the grid cells as follows:

        1, 2, 3, 4,
        5, 6, 7, 8,
        ...

    Note that the first cell is numbered 1.
    '''
    p -= 1
    y  = h - (p // w) - 1
    x  = p % w

    return (x / w, y / h, (x + 1) / w, (y + 1) / h)


def _bounds_hwr(h, w, r):
    '''
    Given a grid of height h and width w, and a tuple r (p0, p1), returns the
    bounds (l, b, r, t) of the smallest rectangle fully enclosing both p0 and
    p1, with coordinates as percentages of the total grid.  The values p0 and
    p1 arespecified by numbering the grid cells as follows:

        1, 2, 3, 4,
        5, 6, 7, 8,
        ...

    Note that the first cell is numbered 1.  In the example above, the range
    (2, 7) and (7, 2) would specify the same rectangle, covering all of cells
    2, 3, 6 and 7.
    '''
    b0 = _bounds_hwp(h, w, r[0])
    b1 = _bounds_hwp(h, w, r[1])
    return (min(b0[0], b1[0]), min(b0[1], b1[1]),
            max(b0[2], b1[2]), max(b0[3], b1[3]))


def _bounds_int(b):
    '''
    Given the value b, in the range 111 to 999, interpret the value as thought
    the first digit were the height of the grid, the second digit were the
    width of the grid and the third digit was the position p in the grid, and
    then use _boudns_hwp() to compute the coordinates.
    '''
    assert 111 <= b <= 999
    h = b // 100
    w = (b % 100) // 10
    p = (b % 10)
    return _bounds_hwp(h, w, p)


def _bounds(b, pad_l=PAD_H, pad_r=PAD_H, pad_b=PAD_V, pad_t=PAD_V):
    if isinstance(b, int):
        c = _bounds_int(b)
    elif isinstance(b, tuple) and len(b) == 3 and isinstance(b[2], int):
        c = _bounds_hwp(*b)
    elif isinstance(b, tuple) and len(b) == 3 and isinstance(b[2], tuple):
        c = _bounds_hwr(*b)
    elif isinstance(b, tuple) and len(b) == 4:
        c = b
    else:
        return None

    return (pad_l + (1 - (pad_l + pad_r))*c[0],
            pad_b + (1 - (pad_b + pad_t))*c[1],
            pad_l + (1 - (pad_l + pad_r))*c[2],
            pad_b + (1 - (pad_b + pad_t))*c[3])


class MouseButtonState:
    def __init__(self, plot, button, x, y, mods):
        self.plot    = plot
        self.button  = button
        self.click_x = x
        self.click_y = y
        self.mods    = mods


class GLContextDelegate:
    def handle_mouse_moved(self, x, y):
        pass

    def handle_key_press(self, key):
        pass

    def update_geometry(self, _t):
        return False

    def draw(self, t):
        pass


class GLContext:
    def __init__(self, ctx_w, ctx_h, fb_w, fb_h, msaa, clear_color=(1, 1, 1),
                 delegate=None):
        self.ctx_w, self.ctx_h = ctx_w, ctx_h
        self.fb_w, self.fb_h = fb_w, fb_h
        self.delegate = delegate or GLContextDelegate()
        self.r_w = self.r_h = 0
        self.mvp = matrix.ortho(0, self.ctx_w, 0, self.ctx_h, -1, 1)
        self._update_ratios()

        glotlib.init_fonts()

        GL.glClearColor(*clear_color, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        if msaa is not None:
            GL.glEnable(GL.GL_MULTISAMPLE)

        self.mouse_button_state = {}

        self.plots      = []
        self.labels     = []
        self._dirty     = True

    def _is_key_down(self, key):
        raise NotImplementedError

    def _get_cursor_pos(self):
        raise NotImplementedError

    def _swap_buffers(self):
        raise NotImplementedError

    def _notify_dirty(self):
        raise NotImplementedError

    def _update_ratios(self):
        # print('Context dimensions %u x %u.  Framebuffer dimensions %u x %u.' %
        #       (self.ctx_w, self.ctx_h, self.fb_w, self.fb_h))
        self.r_w = self.fb_w / self.ctx_w if self.ctx_w else 0
        self.r_h = self.fb_h / self.ctx_h if self.ctx_h else 0

    def _handle_context_size_changed(self, ctx_w, ctx_h):
        self.ctx_w, self.ctx_h = ctx_w, ctx_h
        self.mvp = matrix.ortho(0, self.ctx_w, 0, self.ctx_h, -1, 1)
        self._update_ratios()
        for p in self.plots:
            p._handle_resize()
        for l in self.labels:
            l._handle_resize()

    def _handle_framebuffer_size_changed(self, fb_w, fb_h):
        self.fb_w, self.fb_h = fb_w, fb_h
        self._update_ratios()

    def _handle_mouse_button_callback(self, button, action, mods):
        if action == constants.MOUSE_BUTTON_PRESS:
            x, y = self._get_cursor_pos()
            plot = self.find_plot(x, y)
            if plot:
                mbs = MouseButtonState(plot, button, x, y, mods)
                self.mouse_button_state[button] = mbs
                plot.handle_mouse_down(mbs)
        elif action == constants.MOUSE_BUTTON_RELEASE:
            mbs = self.mouse_button_state.get(button)
            if mbs:
                mbs.plot.handle_mouse_up(mbs)
                self.mouse_button_state[button] = None

    def _handle_mouse_moved(self, x, y):
        for p in self.plots:
            p.handle_mouse_moved(x, y)
        self.delegate.handle_mouse_moved(x, y)

    def _handle_mouse_scrolled(self, dx, dy):
        x, y = self._get_cursor_pos()
        plot = self.find_plot(x, y)
        if plot:
            ls = self._is_key_down(constants.KEY_LEFT_SHIFT)
            rs = self._is_key_down(constants.KEY_RIGHT_SHIFT)
            la = self._is_key_down(constants.KEY_LEFT_ALT)
            ra = self._is_key_down(constants.KEY_RIGHT_ALT)
            plot.handle_mouse_scrolled(x, y, dx, dy, ls or rs, la or ra)

    def _handle_key_event(self, key, action):
        if action != constants.KEY_PRESS:
            return
        if key == ' ':
            x, y = self._get_cursor_pos()
            p    = self.find_plot(x, y)
            if p:
                p.snap_bounds()
        else:
            self.delegate.handle_key_press(key)

    def _draw(self, t):
        if not self.delegate.update_geometry(t) and not self._dirty:
            return False
        self._dirty = False

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        for p in self.plots:
            if p.visible:
                p.draw(t)

        GL.glViewport(0, 0, self.fb_w, self.fb_h)
        for l in self.labels:
            if l.visible:
                l.draw(self.mvp)

        self.delegate.draw(t)

        self._swap_buffers()

        return True

    def mark_dirty(self):
        if not self._dirty:
            self._dirty = True
            self._notify_dirty()

    def add_plot(self, bounds=111, **kwargs):
        '''
        Adds a rectangular plot to the window.  The bounds value selects the
        position of the plot and can have one of the following formats:

            HWP - a set of 3 integers encoded either as a 3-digit decimal
                  number with H, W, P in the hundreds, tens and ones positions,
                  respectively, or as a 3-tuple (H, W, P).  H and W divide the
                  window space into a grid of height H and width W and P
                  selects the grid cell numbered from 1 to H*W left-to-right
                  and then top-to-bottom.

            HWR - a 3-tuple (H, W, (r0, r1)) where the H and W values are the
                  same as HWP format but the plot rectangle will have the
                  bounds of the smallest rectangle that fully encloses both the
                  grid cells at positions r0 and r1.

            (x0, y0, x1, y1) - a 4-tuple specifying the bottom-left and top-
                  right positions of the bounding rectangle, expressed as a
                  fraction from 0 to 1 which scaled with the dimensions of the
                  enclosing window.

        The limits 4-tuple can be used to specify the (x0, y0, x1, y1) data
        limits that the plot will initially be looking at.

        The colors parameter can specify a list of (R, G, B, A) colors to cycle
        through for each new curve added to the plot, as floating-point values
        from 0 to 1.

        The max_h_ticks and max_v_ticks parameters can be used to specify the
        maximum number of ticks to display on the plot, which can be useful to
        limit spam on smaller plots.

        The aspect parameter can be either Plot.ASPECT_NONE or
        Plot.ASPECT_SQUARE, the latter which enforces the plot's data view
        edges so that squares in the data space are rendered as squares in the
        screen space.
        '''
        p = glotlib.plot.Plot(self, bounds=_bounds(bounds), **kwargs)
        self.plots.append(p)
        return p

    def set_plot_bounds(self, plot, bounds, **kwargs):
        plot.bounds = _bounds(bounds, **kwargs)
        plot._handle_resize()

    def add_label(self, *args, font=None, **kwargs):
        font = font or fonts.vera(12, 0)
        l    = label.FlexLabel(self, *args, font=font, **kwargs)
        self.labels.append(l)
        return l

    def find_plot(self, x, y):
        for p in self.plots:
            if p.visible and p.x <= x < p.x + p.w and p.y <= y < p.y + p.h:
                return p
        return None

    def get_mouse_pos(self):
        '''
        Returns a tuple:

            (window_x, window_y, plot, data_x, data_y)

        If the mouse is not over a plot then the last three elements will be
        None.
        '''
        x, y = self._get_cursor_pos()
        p    = self.find_plot(x, y)
        if p is not None:
            px, py = p._window_to_data(x, y)
            return (x, y, p, px, py)
        return (x, y, None, None, None)
