import numpy as np


def ortho(l, r, b, t, n, f, dtype=np.float32):
    '''
    An orthographic projection that maps coordinates in the specified box to
    the unit cube.

    This matrix starts by translating the center point of each component to the
    origin and then scaling the resulting vector.
    '''
    return np.array(
        [[2 / (r - l), 0,           0,           (r + l) / (l - r)],
         [0,           2 / (t - b), 0,           (t + b) / (b - t)],
         [0,           0,           2 / (n - f), (f + n) / (n - f)],
         [0,           0,           0,           1],
         ], dtype=dtype)


def unortho(l, r, b, t, n, f, dtype=np.float32):
    '''
    The inverse of an orthographic projection that maps coordinates in the unit
    cube to the specified box.  The inverse of matrix.ortho().
    '''
    return np.array(
        [[(r - l) / 2, 0,           0,           (l + r) / 2],
         [0,           (t - b) / 2, 0,           (t + b) / 2],
         [0,           0,           (n - f) / 2, (n + f) / -2],
         [0,           0,           0,           1],
         ], dtype=dtype)


def translate(dx, dy, dz=0, dtype=np.float32):
    return np.array(
        [[1, 0, 0, dx],
         [0, 1, 0, dy],
         [0, 0, 1, dz],
         [0, 0, 0, 1],
         ], dtype=dtype)


def translate_in_place(a, dx, dy, dz=0):
    a[0, 3] += dx
    a[1, 3] += dy
    a[2, 3] += dz


def scale(rx, ry, rz=1, dtype=np.float32):
    return np.array(
        [[rx, 0,  0,  0],
         [0,  ry, 0,  0],
         [0,  0,  rz, 0],
         [0,  0,  0,  1],
         ], dtype=dtype)


def rotate(theta, dtype=np.float32):
    '''
    Rotate theta radians about the Z-axis.
    '''
    s = np.sin(theta)
    c = np.cos(theta)
    return np.array(
        [[c, -s, 0, 0],
         [s, c,  0, 0],
         [0, 0,  1, 0],
         [0, 0,  0, 1],
         ], dtype=dtype)
