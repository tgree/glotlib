import glfw

import glotlib

from .gl_context import GLContext
from . import main


MOUSE_ACTIONS = {
    glfw.PRESS      : glotlib.constants.MOUSE_BUTTON_PRESS,
    glfw.RELEASE    : glotlib.constants.MOUSE_BUTTON_RELEASE,
}

MOUSE_BUTTONS = {
    glfw.MOUSE_BUTTON_LEFT   : glotlib.constants.MOUSE_BUTTON_LEFT,
    glfw.MOUSE_BUTTON_RIGHT  : glotlib.constants.MOUSE_BUTTON_RIGHT,
    glfw.MOUSE_BUTTON_MIDDLE : glotlib.constants.MOUSE_BUTTON_MIDDLE,
}

KEY_ACTIONS = {
    glfw.PRESS      : glotlib.constants.KEY_PRESS,
    glfw.RELEASE    : glotlib.constants.KEY_RELEASE,
}

GLFW_KEYMAP_TO_GLOTLIB = {
    glfw.KEY_ESCAPE         : glotlib.constants.KEY_ESCAPE,
    glfw.KEY_SPACE          : ' ',
    glfw.KEY_LEFT_SHIFT     : glotlib.constants.KEY_LEFT_SHIFT,
    glfw.KEY_RIGHT_SHIFT    : glotlib.constants.KEY_RIGHT_SHIFT,
    glfw.KEY_LEFT_ALT       : glotlib.constants.KEY_LEFT_ALT,
    glfw.KEY_RIGHT_ALT      : glotlib.constants.KEY_RIGHT_ALT,
}

GLOTLIB_KEYMAP_TO_GLFW = {v: k for k, v in GLFW_KEYMAP_TO_GLOTLIB.items()}


class Window:
    def __init__(self, w, h, x=100, y=100, name='', msaa=None, **kwargs):
        main.add_window(self)

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        if msaa is not None:
            glfw.window_hint(glfw.SAMPLES, 4)
        self.window = glfw.create_window(w, h, name, None, None)

        glfw.set_window_pos(self.window, x, y)
        glfw.set_window_size_limits(self.window, 16, 16,
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
        glfw.set_window_iconify_callback(self.window,
                                         self._handle_window_iconified)
        glfw.make_context_current(self.window)

        self._iconified = False

        w_w, w_h = glfw.get_window_size(self.window)
        fb_w, fb_h = glfw.get_framebuffer_size(self.window)
        self.gl_context = GLContext(self, w_w, w_h, fb_w, fb_h, msaa, **kwargs)

    def _destroy(self):
        glfw.destroy_window(self.window)

    def _is_key_down(self, key):
        key = GLOTLIB_KEYMAP_TO_GLFW.get(key)
        if key is None:
            return False
        return glfw.get_key(self.window, key) == glfw.PRESS

    def _handle_window_size_changed(self, _window, w, h):
        if not self._iconified:
            self.gl_context._handle_context_size_changed(w, h)

    def _handle_framebuffer_size_changed(self, _window, w, h):
        if not self._iconified:
            self.gl_context._handle_framebuffer_size_changed(w, h)

    def _handle_window_iconified(self, _window, iconified):
        self._iconified = iconified

    def _handle_window_refresh(self, _window):
        self.gl_context._dirty = True
        self.gl_context._draw(main.get_frame_time())

    def _handle_mouse_button_callback(self, _window, button, action, mods):
        mb = MOUSE_BUTTONS.get(button)
        if mb is None:
            return

        action = MOUSE_ACTIONS.get(action)
        if action is None:
            return

        self.gl_context._handle_mouse_button_callback(mb, action, mods)

    def _handle_mouse_moved(self, _window, x, y):
        y = self.gl_context.ctx_h - y
        self.gl_context._handle_mouse_moved(x, y)

    def _handle_mouse_scrolled(self, _window, dx, dy):
        self.gl_context._handle_mouse_scrolled(dx, dy)

    def _handle_key_event(self, _window, key, _scancode, action, _mods):
        action = KEY_ACTIONS.get(action)
        if action is None:
            return

        key = GLFW_KEYMAP_TO_GLOTLIB.get(key)
        if key is None:
            return

        self.gl_context._handle_key_event(key, action)

    def resize(self, w, h):
        glfw.set_window_size(self.window, w, h)

    def close(self):
        glfw.set_window_should_close(self.window, glfw.TRUE)

    def should_close(self):
        return glfw.window_should_close(self.window)
