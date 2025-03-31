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


class Context:
    def __init__(self, w, h, x=100, y=100, name='', msaa=None,
                 clear_color=(1, 1, 1)):
        glotlib.main.add_context(self)

        # TODO:
        # This code actually creates the window and makes the OpenGL context
        # current.  Instead, we should get the context passed in from somewhere
        # else so that we can extract parameters from it somehow.
        #
        # glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        # glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        # glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # if msaa is not None:
        #     glfw.window_hint(glfw.SAMPLES, 4)
        # self.window = glfw.create_window(w, h, name, None, None)
        #
        # glfw.make_context_current(self.window)
        #
        # self.w_w, self.w_h   = glfw.get_window_size(self.window)
        # self.fb_w, self.fb_h = glfw.get_framebuffer_size(self.window)

        self.w_w, self.w_h   = w, h
        self.fb_w, self.fb_h = (w*msaa), (h*msaa)

        self.r_w = self.r_h  = 0
        self.mvp = matrix.ortho(0, self.w_w, 0, self.w_h, -1, 1)
        self._update_ratios()

        glotlib.init_fonts()
        
        if msaa is not None:
            GL.glEnable(GL.GL_MULTISAMPLE)
            self.msaa_samples = GL.glGetIntegerv(GL.GL_SAMPLES)
        else:
            self.msaa_samples = None

        self.plots      = []
        self.labels     = []
        self._dirty     = True
        self._iconified = False

    def _destroy(self):
        pass

    def _update_ratios(self):
        # print('Screen dimensions %u x %u.  Framebuffer dimensions %u x %u.' %
        #       (self.w_w, self.w_h, self.fb_w, self.fb_h))
        self.r_w = self.fb_w / self.w_w if self.w_w else 0
        self.r_h = self.fb_h / self.w_h if self.w_h else 0

    def _handle_context_refresh(self, _context):
        self._dirty = True
        self._draw(glotlib.get_frame_time())

    def _draw(self, t):
        if not self.update_geometry(t) and not self._dirty:
            return False
        if self._iconified:
            return False
        self._dirty = False

        for p in self.plots:
            if p.visible:
                p.draw(t)

        GL.glViewport(0, 0, self.fb_w, self.fb_h)
        for l in self.labels:
            if l.visible:
                l.draw(self.mvp)

        self.draw(t)

        self.swap_buffers()

        return True

    def resize(self, w, h):
        raise Exception('resize() not supported')

    def mark_dirty(self):
        if not self._dirty:
            self._dirty = True
            glotlib.wakeup()

    def update_geometry(self, _t):
        return False

    def draw(self, t):
        pass

    def add_plot(self, bounds=111, **kwargs):
        '''
        Adds a rectangular plot to the context.  The bounds value selects the
        position of the plot and can have one of the following formats:

            HWP - a set of 3 integers encoded either as a 3-digit decimal
                  number with H, W, P in the hundreds, tens and ones positions,
                  respectively, or as a 3-tuple (H, W, P).  H and W divide the
                  context space into a grid of height H and width W and P
                  selects the grid cell numbered from 1 to H*W left-to-right
                  and then top-to-bottom.

            HWR - a 3-tuple (H, W, (r0, r1)) where the H and W values are the
                  same as HWP format but the plot rectangle will have the
                  bounds of the smallest rectangle that fully encloses both the
                  grid cells at positions r0 and r1.

            (x0, y0, x1, y1) - a 4-tuple specifying the bottom-left and top-
                  right positions of the bounding rectangle, expressed as a
                  fraction from 0 to 1 which scaled with the dimensions of the
                  enclosing context.

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

    def close(self):
        raise Exception('close() not supported')

    def should_close(self):
        raise Exception('should_close() not supported')

    def swap_buffers(self):
        # TODO: This code swaps the buffer being displayed on screen with the
        # buffer that was just rendered into, to display the newly-rendered
        # graphics.
        # glfw.swap_buffers(self.window)
        pass

    def get_mouse_pos(self):
        '''
        Returns a tuple:

            (context_x, context_y, plot, data_x, data_y)

        If the mouse is not over a plot then the last three elements will be
        None.
        '''
        return (0, 0, None, None, None)
