import time
import random
import math

import numpy as np
from OpenGL.GL import *
import glfw


NVERTICES      = 100000
TS             = np.array([(i / NVERTICES) * 2 * math.pi
                           for i in range(NVERTICES)])
VERTICES       = np.array([0.0] * NVERTICES * 3, dtype=np.float32)
VERTICES[0::3] = [2 * i / NVERTICES - 1 for i in range(NVERTICES)]


def gen_vertices(t):
    global VERTICES
    VERTICES[1::3] = np.sin(TS + t)


def main():
    global VERTICES

    glfw.init()

    # glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(900, 700, "PyOpenGL Triangle", None, None)
    glfw.set_window_pos(window, 100, 100)
    glfw.make_context_current(window)

    glEnableClientState(GL_VERTEX_ARRAY)

    glVertexPointer(3, GL_FLOAT, 0, VERTICES)

    glClearColor(255/255, 180/255, 0, 0)

    glColor(0, 0, 0, 0)
    glLineWidth(3)

    t      = time.time()
    t0     = 0
    dt     = 1 / 60
    frames = 0
    while not glfw.window_should_close(window):
        glfw.poll_events()
        rt = t - time.time()
        if rt > 0:
            time.sleep(rt)
            continue

        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_LINE_STRIP, 0, 3*NVERTICES//4)
        gen_vertices(t)
        glfw.swap_buffers(window)

        t      += dt
        frames += 1

        t1 = time.time()
        if t1 - t0 < 1:
            continue

        print('FPS: %.1f' % (frames / (t1 - t0)))
        frames = 0
        t0     = t1

    glfw.terminate()


if __name__ == '__main__':
    main()
