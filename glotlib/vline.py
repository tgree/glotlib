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


class VLine:
    def __init__(self, plot, x, color=None, width=1):
        self.plot     = plot
        self.x        = x
        self.color    = color
        self.width    = width
        self.vertices = [(x, -1), (x, 1)]

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
        x = self.x * self.plot.rmatrix[0][0] + self.plot.rmatrix[0][3]
        self.vert_vbo.vertices[:, 0] = x

    def draw(self, _t, z, mvp, resolution):
        if not self.width:
            return

        b = self.plot.mvpi[1][3] - self.plot.mvpi[1][1]
        t = self.plot.mvpi[1][3] + self.plot.mvpi[1][1]
        self.vert_vbo.vertices[0][1] = b
        self.vert_vbo.vertices[1][1] = t
        self.vert_vbo._update_vbo()

        GL.glBindVertexArray(self.line_vao)
        programs.square_line.use(self.width, z, mvp, color=self.color,
                                 resolution=resolution)
        GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, len(INSTANCE_GEOMETRY), 1)

    def set_x_data(self, x):
        self.x = x
        self.renormalize()
