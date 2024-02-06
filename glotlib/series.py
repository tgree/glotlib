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


class Series:
    '''
    Hardware representation of a data series.  This encodes the vertices into
    hardware buffers using float32 representation and binds the various buffers
    to a single VAO for efficient drawing.

    Setters are provided so that the underlying vertices can be updated
    dynamically by the client.
    '''
    MIN_LEN = None

    def __init__(self, plot, vertices, color=None, width=1,
                 point_width=None):
        self.plot        = plot
        self.vertices    = vertices
        self.color       = color
        self.width       = width
        self.point_width = point_width

        self.line_vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.line_vao)

        self.vert_vbo = vbo.VBO(vertices)
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

        self.point_vao = GL.glGenVertexArrays(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vert_vbo.vbo)
        GL.glBindVertexArray(self.point_vao)
        self.vert_vbo._attrib_pointer(0)
        GL.glEnableVertexAttribArray(0)

        GL.glBindVertexArray(0)

    def renormalize(self):
        '''
        Recompute the normalization of the data, using the plot's
        renormalization matrix.  Called to notify us of a change to the matrix
        without any change to the original vertex data.

        This performs the normalization math in float64 format and then
        converts it down to float32 when assigning to the VBO.
        '''
        if len(self.vertices) == 0:
            return

        X  = self.vertices[:, 0] * self.plot.rmatrix[0][0]
        X += self.plot.rmatrix[0][3]
        Y  = self.vertices[:, 1] * self.plot.rmatrix[1][1]
        Y += self.plot.rmatrix[1][3]
        self.vert_vbo.set_x_y_data(X, Y)

    def set_x_data(self, X):
        '''
        Replace the x coordinates of the original vertex data with the new X
        array and update the VBO data stored on the GPU with the normalized
        vertex data.
        '''
        X  = np.array(X, dtype=np.float64, copy=False)
        V  = X * self.plot.rmatrix[0][0]
        V += self.plot.rmatrix[0][3]
        self.vertices[:, 0] = X
        self.vert_vbo.set_x_data(V)

    def set_y_data(self, Y):
        '''
        Replace the y coordinates of the original vertex data with the new Y
        array and update the VBO data stored on the GPU with the normalized
        vertex data.
        '''
        Y  = np.array(Y, dtype=np.float64, copy=False)
        V  = Y * self.plot.rmatrix[1][1]
        V += self.plot.rmatrix[1][3]
        self.vertices[:, 1] = Y
        self.vert_vbo.set_y_data(V)

    def set_x_y_data(self, X, Y):
        X = np.array(X, dtype=np.float64, copy=False)
        Y = np.array(Y, dtype=np.float64, copy=False)
        self.vertices = np.column_stack((X, Y))

        X  = X * self.plot.rmatrix[0][0]
        X += self.plot.rmatrix[0][3]
        Y  = Y * self.plot.rmatrix[1][1]
        Y += self.plot.rmatrix[1][3]
        self.vert_vbo.set_x_y_data(X, Y)

    def sub_x_y_data(self, index, X, Y):
        if len(X) == 0:
            return

        X = np.array(X, dtype=np.float64, copy=False)
        Y = np.array(Y, dtype=np.float64, copy=False)
        V = np.column_stack((X, Y))
        overlap_v = V[:len(self.vertices) - index]
        new_v     = V[len(self.vertices) - index:]
        if len(overlap_v):
            self.vertices[-len(overlap_v):] = overlap_v
        self.vertices = np.concatenate((self.vertices, new_v))

        X  = X * self.plot.rmatrix[0][0]
        X += self.plot.rmatrix[0][3]
        Y  = Y * self.plot.rmatrix[1][1]
        Y += self.plot.rmatrix[1][3]
        self.vert_vbo.sub_x_y_data(index, X, Y)

    def append_x_y_data(self, X, Y):
        self.sub_x_y_data(len(self.vertices), X, Y)

    def draw(self, _t, z, mvp, resolution):
        if self.width and len(self.vert_vbo) >= 2:
            GL.glBindVertexArray(self.line_vao)
            programs.square_line.use(self.width, z, mvp, color=self.color,
                                     resolution=resolution)
            GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, len(INSTANCE_GEOMETRY),
                                     len(self.vert_vbo) - 1)

        if self.point_width and len(self.vert_vbo) >= 1:
            GL.glBindVertexArray(self.point_vao)
            programs.frag_points.use(z, mvp, color=self.color)
            GL.glPointSize(self.point_width * self.plot.window.r_w)
            GL.glDrawArrays(GL.GL_POINTS, 0, len(self.vert_vbo))
