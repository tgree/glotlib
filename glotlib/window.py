import glfw
from OpenGL import GL

import glotlib.plot
import glotlib.main
from . import matrix
from . import constants
from . import fonts
from . import label

# The window is divided up into multiple regions.  On the edge of the window,
# we have a fixed-width (in window pixels) buffer, which can be 0.  Then we
# have a flexible-width (in percentage of window minus the fixed region)
# buffer, which can also be zero.  The flexible buffer grows and shrinks as the
# window resizes, while the fixed buffer is always a constant-sized buffer,
# suitable for things like a fixed-size status panel on the bottom of the
# window.  Then we have the content region.  The content region is the part
# where plot objects are flexibly rendered; the region and the plots grow/
# shrink dynamically as the window is resized.  It all comes together something
# like this:
#
#     +-----------------------------------+
#     |            Fixed buffer           |
#     |  +-----------------------------+  |
#     |  |       Flexible buffer       |  |
#     |  |  +-----------------------+  |  |
#     |  |  |                       |  |  |
#     |  |  |                       |  |  |
#     |  |  |        Flexible       |  |  |
#     |  |  |        content        |  |  |
#     |  |  |                       |  |  |
#     |  |  |                       |  |  |
#     |  |  +-----------------------+  |  |
#     |  |                             |  |
#     |  +-----------------------------+  |
#     |                                   |
#     +-----------------------------------+
#
# The fixed and flexible buffer sizes can be individually specified for all 4
# sides of the window.

# This is the padding on each side of the fixed window area.
FIXED_L = 0
FIXED_R = 10
FIXED_B = 0
FIXED_T = 10


# This is the padding on each side of the flexible window area.
FLEX_L = 0
FLEX_R = 0
FLEX_B = 0
FLEX_T = 0


MOUSE_BUTTONS = {
    glfw.MOUSE_BUTTON_LEFT   : constants.MOUSE_BUTTON_LEFT,
    glfw.MOUSE_BUTTON_RIGHT  : constants.MOUSE_BUTTON_RIGHT,
    glfw.MOUSE_BUTTON_MIDDLE : constants.MOUSE_BUTTON_MIDDLE,
}


class MouseButtonState:
    def __init__(self, plot, button, x, y, mods):
        self.plot    = plot
        self.button  = button
        self.click_x = x
        self.click_y = y
        self.mods    = mods


class Window:
    def __init__(self, w, h, x=100, y=100, name='', msaa=None,
                 clear_color=(1, 1, 1),
                 flex_pad=(FLEX_L, FLEX_B, FLEX_R, FLEX_T),
                 fixed_pad=(FIXED_L, FIXED_B, FIXED_R, FIXED_T)):
        glotlib.main.add_window(self)

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        if msaa is not None:
            glfw.window_hint(glfw.SAMPLES, 4)
        self.window = glfw.create_window(w, h, name, None, None)

        min_w = fixed_pad[0] + fixed_pad[2] + 8
        min_h = fixed_pad[1] + fixed_pad[3] + 8
        glfw.set_window_pos(self.window, x, y)
        glfw.set_window_size_limits(self.window, min_w, min_h,
                                    glfw.DONT_CARE, glfw.DONT_CARE)
        glfw.set_window_size_callback(
            self.window, self._handle_window_size_changed)
        glfw.set_framebuffer_size_callback(
            self.window, self._handle_framebuffer_size_changed)
        glfw.set_mouse_button_callback(
            self.window, self._handle_mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self._handle_mouse_moved)
        glfw.set_scroll_callback(self.window, self._handle_mouse_scrolled)
        glfw.set_key_callback(self.window, self._handle_key_event)
        glfw.set_window_refresh_callback(self.window,
                                         self._handle_window_refresh)
        glfw.make_context_current(self.window)

        self.w_w, self.w_h   = glfw.get_window_size(self.window)
        self.fb_w, self.fb_h = glfw.get_framebuffer_size(self.window)
        self.r_w, self.r_h   = 0, 0
        self.mvp             = matrix.ortho(0, self.w_w, 0, self.w_h, -1, 1)
        self.flex_pad        = flex_pad
        self.fixed_pad       = fixed_pad
        self._update_ratios()

        glotlib.init_fonts()

        GL.glClearColor(*clear_color, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        if msaa is not None:
            GL.glEnable(GL.GL_MULTISAMPLE)
            self.msaa_samples = GL.glGetIntegerv(GL.GL_SAMPLES)
        else:
            self.msaa_samples = None

        self.mouse_button_state = [None] * (glfw.MOUSE_BUTTON_LAST + 1)

        self.plots  = []
        self.labels = []
        self._dirty = True

    def _destroy(self):
        glfw.destroy_window(self.window)

    def _update_ratios(self):
        # print('Screen dimensions %u x %u.  Framebuffer dimensions %u x %u.' %
        #       (self.w_w, self.w_h, self.fb_w, self.fb_h))
        self.r_w = self.fb_w / self.w_w if self.w_w else 0
        self.r_h = self.fb_h / self.w_h if self.w_h else 0

    def _handle_window_size_changed(self, _window, w, h):
        self.w_w, self.w_h = w, h
        self.mvp = matrix.ortho(0, self.w_w, 0, self.w_h, -1, 1)
        self._update_ratios()
        for p in self.plots:
            p._handle_resize()
        for l in self.labels:
            l._handle_resize()
        self.handle_window_size_changed()

    def _handle_framebuffer_size_changed(self, _window, w, h):
        self.fb_w, self.fb_h = w, h
        self._update_ratios()
        self.handle_framebuffer_size_changed()

    def handle_window_size_changed(self):
        pass

    def handle_framebuffer_size_changed(self):
        pass

    def handle_mouse_moved(self, x, y):
        pass

    def handle_key_press(self, key):
        pass

    def _handle_window_refresh(self, _window):
        self._dirty = True
        self._draw(glotlib.get_frame_time())

    def _handle_mouse_button_callback(self, _window, button, action, mods):
        mb = MOUSE_BUTTONS.get(button)
        if mb is None:
            return

        if action == glfw.PRESS:
            x, y = glfw.get_cursor_pos(self.window)
            y    = self.w_h - y
            plot = self.find_plot(x, y)
            if plot:
                mbs = MouseButtonState(plot, MOUSE_BUTTONS[button], x, y, mods)
                self.mouse_button_state[button] = mbs
                plot.handle_mouse_down(mbs)
        elif action == glfw.RELEASE:
            mbs = self.mouse_button_state[button]
            if mbs:
                mbs.plot.handle_mouse_up(mbs)
                self.mouse_button_state[button] = None

    def _handle_mouse_moved(self, _window, x, y):
        y = self.w_h - y
        for p in self.plots:
            p.handle_mouse_moved(x, y)
        self.handle_mouse_moved(x, y)

    def _handle_mouse_scrolled(self, _window, dx, dy):
        x, y = glfw.get_cursor_pos(self.window)
        y    = self.w_h - y
        plot = self.find_plot(x, y)
        if plot:
            ls = (glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS)
            rs = (glfw.get_key(self.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS)
            la = (glfw.get_key(self.window, glfw.KEY_LEFT_ALT) == glfw.PRESS)
            ra = (glfw.get_key(self.window, glfw.KEY_RIGHT_ALT) == glfw.PRESS)
            plot.handle_mouse_scrolled(x, y, dx, dy, ls or rs, la or ra)

    def _handle_key_event(self, _window, key, _scancode, action, _mods):
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_SPACE:
            x, y = glfw.get_cursor_pos(self.window)
            y    = self.w_h - y
            p    = self.find_plot(x, y)
            if p:
                p.snap_bounds()
        else:
            self.handle_key_press(key)

    def _draw(self, t):
        if not self.update_geometry(t) and not self._dirty:
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

        self.draw(t)

        self.swap_buffers()

        return True

    def resize(self, w, h):
        glfw.set_window_size(self.window, w, h)

    def mark_dirty(self):
        if not self._dirty:
            self._dirty = True
            glotlib.wakeup()

    def update_geometry(self, _t):
        return False

    def draw(self, t):
        pass

    def add_plot(self, bounds=(0, 0, 1, 1), **kwargs):
        p = glotlib.plot.Plot(self, bounds=bounds, **kwargs)
        self.plots.append(p)
        return p

    def flex_bounds_to_abs_bounds(self, bounds):
        '''
        Given flexible bounds as percentages of the flexible content area,
        return the absolute bounds in window pixels.
        '''
        flex_l, flex_b, flex_r, flex_t = self.flex_pad
        fix_l, fix_b, fix_r, fix_t = self.fixed_pad
        w_w = self.w_w - fix_l - fix_r
        w_h = self.w_h - fix_t - fix_b
        return (
            fix_l + int((flex_l + (1 - (flex_l + flex_r)) * bounds[0]) * w_w),
            fix_b + int((flex_b + (1 - (flex_b + flex_t)) * bounds[1]) * w_h),
            fix_l + int((flex_l + (1 - (flex_l + flex_r)) * bounds[2]) * w_w),
            fix_b + int((flex_b + (1 - (flex_b + flex_t)) * bounds[3]) * w_h))

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
        glfw.set_window_should_close(self.window, glfw.TRUE)

    def should_close(self):
        return glfw.window_should_close(self.window)

    def swap_buffers(self):
        glfw.swap_buffers(self.window)

    def get_mouse_pos(self):
        '''
        Returns a tuple:

            (window_x, window_y, plot, data_x, data_y)

        If the mouse is not over a plot then the last three elements will be
        None.
        '''
        x, y = glfw.get_cursor_pos(self.window)
        y    = self.w_h - y
        p    = self.find_plot(x, y)
        if p is not None:
            px, py = p._window_to_data(x, y)
            return (x, y, p, px, py)
        return (x, y, None, None, None)
