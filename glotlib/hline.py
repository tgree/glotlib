import numpy as np
from OpenGL import GL

from . import vbo
from . import programs


INSTANCE_GEOMETRY = np.array(
    [[0, -0.5],
     [1, -0.5],
     [1,  0.5],
     [0, -0.5],
     [1,  0.5],
     [0,  0.5],
     ], dtype=np.float32)


class HLine:
    def __init__(self, plot, y, color=None, width=1):
        self.plot     = plot
        self.y        = y
        self.color    = color
        self.width    = width
        self.vertices = [(-1, y), (1, y)]

        self.line_vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.line_vao)

        self.vert_vbo = vbo.VBO(self.vertices)
        self.vert_vbo._attrib_pointer(0)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribDivisor(0, 1)

        self.vert_vbo._attrib_pointer(1, 8)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribDivisor(1, 1)

        self.geom_vbo = vbo.StaticVBO(INSTANCE_GEOMETRY)
        self.geom_vbo._attrib_pointer(2)
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribDivisor(2, 0)

        GL.glBindVertexArray(0)

    def renormalize(self):
        y = self.y * self.plot.rmatrix[1][1] + self.plot.rmatrix[1][3]
        self.vert_vbo.vertices[:, 1] = y

    def draw(self, _t, z, mvp, resolution):
        if not self.width:
            return

        l = self.plot.mvpi[0][3] - self.plot.mvpi[0][0]
        r = self.plot.mvpi[0][3] + self.plot.mvpi[0][0]
        self.vert_vbo.vertices[0][0] = l
        self.vert_vbo.vertices[1][0] = r
        self.vert_vbo._update_vbo()

        GL.glBindVertexArray(self.line_vao)
        programs.square_line.use(self.width, z, mvp, color=self.color,
                                 resolution=resolution)
        GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, len(INSTANCE_GEOMETRY), 1)
