from ctypes import c_void_p
from enum import IntEnum

from OpenGL import GL

from . import matrix
from . import programs


class HAlign(IntEnum):
    LEFT    = 0
    MIDDLE  = 1
    RIGHT   = 2


class VAlign(IntEnum):
    BOTTOM  = 0
    MIDDLE  = 1
    TOP     = 2


ALIGNMENTS = {
    'N'     : (HAlign.MIDDLE,   VAlign.TOP),
    'NE'    : (HAlign.RIGHT,    VAlign.TOP),
    'E'     : (HAlign.RIGHT,    VAlign.MIDDLE),
    'SE'    : (HAlign.RIGHT,    VAlign.BOTTOM),
    'S'     : (HAlign.MIDDLE,   VAlign.BOTTOM),
    'SW'    : (HAlign.LEFT,     VAlign.BOTTOM),
    'W'     : (HAlign.LEFT,     VAlign.MIDDLE),
    'NW'    : (HAlign.LEFT,     VAlign.TOP),
    'C'     : (HAlign.MIDDLE,   VAlign.MIDDLE),
}


class Label:
    def __init__(self, pos, text, font=None, theta=0, anchor='SW',
                 visible=True):
        assert font

        self.font      = font
        self.pos       = (round(pos[0]), round(pos[1]))
        self.theta     = theta
        self.visible   = visible
        self.text      = None
        self.mvp       = None
        alignment      = ALIGNMENTS[anchor]
        self.halign    = alignment[0]
        self.valign    = alignment[1]
        self.width     = 0
        self.nvertices = 0

        self.vao      = GL.glGenVertexArrays(1)
        self.geom_vbo = GL.glGenBuffers(1)
        self.tex_vbo  = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.geom_vbo)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, c_void_p(0))
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.tex_vbo)
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, c_void_p(0))
        GL.glEnableVertexAttribArray(1)

        self.set_text(text)

    def _update_mvp(self):
        dx         = round(self.width * self.halign / 2)
        dy         = round(self.font.ascender * self.valign / 2)
        anchor_pos = (self.pos[0] - dx, self.pos[1] - dy)
        self.mvp = matrix.translate(*anchor_pos) @ matrix.rotate(self.theta)

    def set_text(self, text):
        if text == self.text:
            return False

        vertices, tex_coords, width, _ = self.font.gen_vertices_left(text)

        self.text      = text
        self.nvertices = len(vertices)
        self.width     = width
        if self.nvertices:
            GL.glBindVertexArray(self.vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.geom_vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices, GL.GL_STATIC_DRAW)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.tex_vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, tex_coords, GL.GL_STATIC_DRAW)

        self._update_mvp()
        return True

    def set_pos(self, pos):
        self.pos = (int(pos[0]), int(pos[1]))
        self._update_mvp()

    def set_theta(self, theta):
        self.theta = theta
        self._update_mvp()

    def draw(self, mvp, color=(0, 0, 0, 1)):
        if not self.nvertices:
            return

        mvp = mvp @ self.mvp
        GL.glBindVertexArray(self.vao)
        self.font.bind(0)
        programs.text.use(0, mvp, self.font, color=color)
        GL.glEnable(GL.GL_BLEND)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.nvertices)
        GL.glDisable(GL.GL_BLEND)

    def draw_batched(self, mvp):
        if not self.nvertices:
            return

        mvp = mvp @ self.mvp
        programs.text.uniformMatrix4fv('u_mvp', mvp)
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.nvertices)


class FlexLabel(Label):
    def __init__(self, window, pos, *args, **kwargs):
        self.window   = window
        self.flex_pos = pos
        pos           = (pos[0] * window.w_w, pos[1] * window.w_h)
        super().__init__(pos, *args, **kwargs)

    def _handle_resize(self):
        pos = (self.flex_pos[0] * self.window.w_w,
               self.flex_pos[1] * self.window.w_h)
        super().set_pos(pos)

    def set_pos(self, pos):
        self.flex_pos = pos
        pos           = (pos[0] * self.window.w_w,
                         pos[1] * self.window.w_h)
        super().set_pos(pos)

    def show(self):
        self.visible = True
        self.window.mark_dirty()

    def hide(self):
        self.visible = False
        self.window.mark_dirty()
