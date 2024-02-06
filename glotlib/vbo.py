import math
from ctypes import c_void_p

import numpy as np
from OpenGL import GL


def ceil_pow2(v):
    return (1 << math.ceil(math.log2(v)))


class VBO:
    '''
    This class holds a set of vertices in float32 format, bound to a hardware
    VBO.  This class does not store the original vertices at all; the vertices
    field in the VBO stores renormalized data while the Series object contains
    the original data.  The VBO remains bound to GL_ARRAY_BUFFER after
    initialization.
    '''
    def __init__(self, vertices=None, ncomponents=None,
                 gl_type=GL.GL_DYNAMIC_DRAW):
        self.vertices = None
        self.gl_type  = gl_type
        self.vbo      = GL.glGenBuffers(1)
        self.capacity = 0

        if vertices is not None and ncomponents:
            assert len(vertices[0]) == ncomponents
            self.ncomponents = ncomponents
            self.set_data(vertices)
        elif ncomponents:
            self.ncomponents = ncomponents
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        elif len(vertices) == 0:
            self.ncomponents = 2
            self.set_data(vertices)
        else:
            self.ncomponents = len(vertices[0])
            self.set_data(vertices)

    def __len__(self):
        return len(self.vertices)

    def _sub_vbo_tail(self, N):
        '''
        Writes the last N values of self.vertices to the VBO, enlarging the
        VBO buffer if necessary.
        '''
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

        # Enlarge the VBO and copy it all in if necessary.
        if self.capacity < len(self.vertices):
            self.capacity = ceil_pow2(len(self.vertices))
            GL.glBufferData(GL.GL_ARRAY_BUFFER,
                            4 * self.ncomponents * self.capacity,
                            None, self.gl_type)
            N = len(self.vertices)

        # Sub in the new data.
        offset = 4 * self.ncomponents * (len(self.vertices) - N)
        size   = 4 * self.ncomponents * N
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, offset, size, self.vertices[-N:])

    def _update_vbo(self):
        self._sub_vbo_tail(len(self.vertices))

    def _attrib_pointer(self, unit, offset=0):
        GL.glVertexAttribPointer(unit, self.ncomponents, GL.GL_FLOAT,
                                 GL.GL_FALSE, 0, c_void_p(offset))

    def set_data(self, vertices):
        '''
        Replace all data in the VBO with the new vertices, which must have the
        same number of components as the original data.
        '''
        vertices = np.array(vertices, dtype=np.float32)
        if len(vertices):
            assert self.ncomponents == vertices.shape[1]

        self.vertices = vertices
        self._update_vbo()

    def set_component_data(self, index, V):
        '''
        Replace a single component of the VBO with the new series of values,
        which must have the same number of entries as there are in the current
        list of vertices.
        '''
        self.vertices[:, index] = V
        self._update_vbo()

    def set_x_data(self, X):
        '''
        Replaces the first component of all vertices with the specified X
        values, which must have as many elements as the length of the current
        vertices list.
        '''
        self.set_component_data(0, X)

    def set_y_data(self, Y):
        '''
        Replaces the seconds component of all vertices with the specified Y
        values, which must have as many elements as the length of the current
        vertices list.
        '''
        self.set_component_data(1, Y)

    def set_x_y_data(self, X, Y):
        '''
        Replaces the first and second components of all vertices with the
        specifeid X and Y values, which must both be the same length and match
        the number of entries in the current vertices list, unless the current
        vertices list is only comprised of (x, y) vertices in which case it can
        simply replace them all.
        '''
        if self.ncomponents == 2:
            self.set_data(np.column_stack((X, Y)).astype(np.float32,
                                                         copy=False))
        else:
            self.vertices[:, 0] = X
            self.vertices[:, 1] = Y
            self._update_vbo()

    def sub_x_y_data(self, index, X, Y):
        '''
        Substitutes X and Y components starting at the specified index.  The
        data will be extended if the data to be substituted in goes past the
        end of the existing data.
        '''
        assert len(X) == len(Y)
        assert index <= len(self.vertices)
        sub_data     = np.column_stack((X, Y)).astype(np.float32, copy=False)
        overlap_data = sub_data[:len(self.vertices) - index]
        new_data     = sub_data[len(self.vertices) - index:]
        if len(overlap_data):
            self.vertices[-len(overlap_data):] = overlap_data
        self.vertices = np.concatenate((self.vertices, new_data))
        self._sub_vbo_tail(len(X))


class StaticVBO(VBO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, gl_type=GL.GL_STATIC_DRAW, **kwargs)


class DynamicVBO(VBO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, gl_type=GL.GL_DYNAMIC_DRAW, **kwargs)
