import time
import threading

import glfw
from OpenGL import GL

from . import programs
from . import fonts


INITED          = False
FONTS_INITED    = False
WINDOWS         = set()
TASKS           = set()
FRAME           = 0
T0              = 0
FPS             = 0
SHOULD_INTERACT = False


def init():
    global INITED
    if INITED:
        return

    glfw.init()
    INITED = True


def init_fonts():
    global FONTS_INITED

    assert INITED

    if FONTS_INITED:
        return

    fonts.load()
    FONTS_INITED = True


def add_window(w):
    init()
    WINDOWS.add(w)


def draw_windows(t):
    updated = False

    for w in WINDOWS:
        updated = updated or w._draw(t)

    return updated


def get_frame_time():
    return time.time() - T0


def get_fps():
    return FPS


def animate():
    global FRAME
    global FPS
    global T0

    programs.load()
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    T0     = time.time()
    fps_f0 = FRAME
    fps_t0 = T0
    del_ws = []

    # glfw.swap_interval(1)
    # GL.glClearDepth(1.)
    # GL.glEnable(GL.GL_DEPTH_TEST)
    # GL.glDepthFunc(GL.GL_LESS)
    # GL.glEnable(GL.GL_BLEND)

    draw_windows(0)
    while True:
        # GL.glFinish()
        glfw.poll_events()

        del_ws = [w for w in WINDOWS if w.should_close()]
        for w in del_ws:
            w._destroy()
            WINDOWS.remove(w)
        if not WINDOWS:
            break

        t = time.time()
        if not draw_windows(t - T0):
            time.sleep(0.005)
        FRAME += 1

        fps_dt = t - fps_t0
        if fps_dt < 0.2:
            continue

        fps_df = FRAME - fps_f0
        FPS    = fps_df / fps_dt
        # print('FPS: %.1f' % FPS)

        fps_f0 = FRAME
        fps_t0 = t

    glfw.terminate()


def interact():
    global T0
    global SHOULD_INTERACT

    programs.load()
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    T0 = time.time()

    SHOULD_INTERACT = True
    draw_windows(0)
    while SHOULD_INTERACT:
        glfw.wait_events()

        del_ws = [w for w in WINDOWS if w.should_close()]
        for w in del_ws:
            w._destroy()
            WINDOWS.remove(w)
        if not WINDOWS:
            break

        t = time.time()
        draw_windows(t - T0)


def wakeup():
    glfw.post_empty_event()


def stop():
    global SHOULD_INTERACT
    SHOULD_INTERACT = False
    wakeup()


def _periodic_thread_func(dt, callback):
    t_target = time.time() + dt
    while True:
        t = time.time()
        while t >= t_target:
            callback(t_target)
            t_target += dt
        sleep_len = t_target - time.time()
        time.sleep(max(sleep_len, 0))


def periodic(dt, callback):
    t = threading.Thread(target=_periodic_thread_func, args=(dt, callback),
                         daemon=True)
    TASKS.add(t)
    t.start()
