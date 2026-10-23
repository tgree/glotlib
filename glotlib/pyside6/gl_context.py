import os

from OpenGL import GL, platform

from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat

from .. import gl_context
from .. import programs


class GLContext(gl_context.GLContext):
    def __init__(self, widget, *args, **kwargs):
        self._gl_widget = widget
        super().__init__(*args, **kwargs)

    def _is_key_down(self, key):
        return False

    def _get_cursor_pos(self):
        return 0, 0

    def _swap_buffers(self):
        pass

    def _notify_dirty(self):
        pass

    def _draw(self, t):
        gl_context.GLContext._draw(self, t)


class GLWidget(QOpenGLWidget):
    def __init__(self, window, msaa, parent=None):
        super().__init__(parent)
        self._glotlib_window = window
        self._glotlib_msaa = msaa

    def initializeGL(self):
        actual_format = self.context().format()
        if (actual_format.profile() !=
                QSurfaceFormat.OpenGLContextProfile.CoreProfile):
            print('GLOTLIB WARNING: Failed to secure Core Profile. '
                  'Did you call glotlib.init_backend()?')
            os._exit(-1)

        programs.load()
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        ratio = self._glotlib_window.window_widget.devicePixelRatio()
        w_w   = self._glotlib_window.window_widget.width()
        w_h   = self._glotlib_window.window_widget.height()
        fb_w  = int(w_w * ratio)
        fb_h  = int(w_h * ratio)

        self._glotlib_window.ctx = GLContext(self, w_w, w_h, fb_w, fb_h,
                                             msaa=self._glotlib_msaa)

    def resizeGL(self, w, h):
        ratio = self._glotlib_window.window_widget.devicePixelRatio()
        w_w   = w
        w_h   = h
        fb_w  = int(w_w * ratio)
        fb_h  = int(w_h * ratio)

        self._glotlib_window.ctx._handle_framebuffer_size_changed(fb_w, fb_h)
        self._glotlib_window.ctx._handle_context_size_changed(w_w, w_h)

    def paintGL(self):
        self._glotlib_window.ctx._dirty = True
        self._glotlib_window.ctx._draw(0)
