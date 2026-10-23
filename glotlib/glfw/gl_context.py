from OpenGL import GL

import glfw

from .. import gl_context
from . import main


class GLContext(gl_context.GLContext):
    def __init__(self, window, *args, **kwargs):
        self._glfw_window = window
        super().__init__(*args, **kwargs)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def _is_key_down(self, key):
        return self._glfw_window._is_key_down(key)

    def _get_cursor_pos(self):
        x, y = glfw.get_cursor_pos(self._glfw_window.window)
        return x, self.ctx_h - y

    def _swap_buffers(self):
        glfw.swap_buffers(self._glfw_window.window)

    def _notify_dirty(self):
        main.wakeup()

    def _draw(self, t):
        if self._glfw_window._iconified:
            return False
        return super()._draw(t)
