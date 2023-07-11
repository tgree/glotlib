import numpy as np

from OpenGL import GL

from . import programs


class MiterLines:
    def __init__(self, vertices):
        self.vertices  = None
        self.vao       = GL.glGenVertexArrays(1)
        self.buffer    = GL.glGenBuffers(1)
        self.texture   = GL.glGenTextures(1)
        self.bind_unit = None
        self._update(vertices)

    def bind(self, unit):
        GL.glBindVertexArray(self.vao)
        GL.glActiveTexture(GL.GL_TEXTURE0 + unit)
        GL.glBindTexture(GL.GL_TEXTURE_BUFFER, self.texture)
        GL.glTexBuffer(GL.GL_TEXTURE_BUFFER, GL.GL_RG32F, self.buffer)
        self.bind_unit = unit

    def use_program(self, width, z, mvp, color, resolution):
        programs.miter_line.use(width, z, self, mvp, color=color,
                                resolution=resolution)

    def draw(self):
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6 * (len(self.vertices) - 3))

    def _update(self, vertices):
        self.vertices = vertices
        GL.glBindBuffer(GL.GL_TEXTURE_BUFFER, self.buffer)
        GL.glBufferData(GL.GL_TEXTURE_BUFFER, vertices, GL.GL_DYNAMIC_DRAW)

    def update_points(self, xy_tuples):
        self._update(vertices_from_points(xy_tuples))

    def update_lists(self, X, Y):
        self._update(vertices_from_lists(X, Y))


def vertices_from_points(xy_tuples):
    # Extend the first and last segments to get the endpoint miters.
    v0 = (2 * xy_tuples[0][0] - xy_tuples[1][0],
          2 * xy_tuples[0][1] - xy_tuples[1][1])
    vN = (2 * xy_tuples[-1][0] - xy_tuples[-2][0],
          2 * xy_tuples[-1][1] - xy_tuples[-2][1])

    # Generate the array.
    vs            = np.empty((len(xy_tuples) + 2, 2), dtype=np.float32)
    vs[0]         = v0
    vs[1:-1, 0:2] = xy_tuples
    vs[-1]        = vN
    return vs


def vertices_from_poly_points(xy_tuples):
    vs            = np.empty((len(xy_tuples) + 3, 2), dtype=np.float32)
    vs[0]         = xy_tuples[-1]
    vs[1:-2, 0:2] = xy_tuples
    vs[-2]        = xy_tuples[0]
    vs[-1]        = xy_tuples[1]
    return vs


def vertices_from_lists(X, Y):
    # Extend the first and last segments to get the endpoint miters.
    v0 = (2 * X[0] - X[1], 2 * Y[0] - Y[1])
    vN = (2 * X[-1] - X[-2], 2 * Y[-1] - Y[-2])

    # Generate the array.
    vs          = np.empty((len(X) + 2, 2), dtype=np.float32)
    vs[0]       = v0
    vs[1:-1, 0] = X
    vs[1:-1, 1] = Y
    vs[-1]      = vN
    return vs


def from_points(xy_tuples):
    return MiterLines(vertices_from_points(xy_tuples))


def from_lists(X, Y):
    vs       = np.empty((len(X), 2), dtype=np.float32)
    vs[:, 0] = X
    vs[:, 1] = Y
    return MiterLines(vs)


def from_poly_points(xy_tuples):
    return MiterLines(vertices_from_poly_points(xy_tuples))
