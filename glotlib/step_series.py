import numpy as np

from . import series


class StepSeries(series.Series):
    def __init__(self, plot, vertices, **kwargs):
        vertices = self._expand_vertices_left(vertices)
        super().__init__(plot, vertices, **kwargs)

    @staticmethod
    def _expand_vertices_left(vertices):
        if len(vertices) == 0:
            return vertices

        vs          = np.empty((len(vertices) * 2 - 1, 2), dtype=vertices.dtype)
        vs[0::2]    = vertices
        vs[1::2, 0] = vertices[0:len(vertices) - 1, 0]
        vs[1::2, 1] = vertices[1:len(vertices), 1]
        return vs

    def set_x_data(self, X):
        vX       = np.empty(len(X) * 2 - 1, dtype=np.float64)
        vX[0::2] = X
        vX[1::2] = X[0:len(X) - 1]
        super().set_x_data(vX)

    def set_y_data(self, Y):
        vY       = np.empty(len(Y) * 2 - 1, dtype=np.float64)
        vY[0::2] = Y
        vY[1::2] = Y[1:len(Y)]
        super().set_y_data(vY)

    def set_x_y_data(self, X, Y):
        if len(X) == 0:
            super().set_x_y_data(X, Y)
            return

        vX       = np.empty(len(X) * 2 - 1, dtype=np.float64)
        vX[0::2] = X
        vX[1::2] = X[0:len(X) - 1]

        vY       = np.empty(len(Y) * 2 - 1, dtype=np.float64)
        vY[0::2] = Y
        vY[1::2] = Y[1:len(Y)]

        super().set_x_y_data(vX, vY)

    def append_x_y_data(self, X, Y):
        # Append data with a step change on the left side:
        #
        #   *               *---*
        #   |         or    |
        #   *---*           *
        if len(X) == 0:
            return

        if len(self.vertices) != 0:
            super().append_x_y_data([self.vertices[-1][0]], [Y[0]])

        # Vertices 0, 2, 4, 8 are at X[0], X[1], X[2], X[3], ...
        # Vertices 1, 3, 5, 7 are at X[0], X[1], X[2], ...
        vX       = np.empty(len(X) * 2 - 1, dtype=np.float64)
        vX[0::2] = X
        vX[1::2] = X[0:len(X) - 1]

        # Vertices 0, 2, 4, 8 are at Y[0], Y[1], Y[2], Y[3], ...
        # Vertices 1, 3, 5, 7 are at Y[1], Y[2], Y[3], ...
        vY       = np.empty(len(Y) * 2 - 1, dtype=np.float64)
        vY[0::2] = Y
        vY[1::2] = Y[1:len(Y)]

        super().append_x_y_data(vX, vY)
