import time
import threading

from OpenGL import GL

from . import programs
from . import fonts


INITED          = False
FONTS_INITED    = False
CONTEXTS        = set()
TASKS           = set()
FRAME           = 0
T0              = 0
FPS             = 0
SHOULD_INTERACT = False


def init(): # initialization is done in the widget itself might be redundant
    global INITED
    # if INITED:
    #     return

    # # TODO: This is where maybe you can init the external framework?
    # # glfw.init()
    INITED = True


def init_fonts():
    global FONTS_INITED

    assert INITED

    if FONTS_INITED:
        return

    fonts.load()
    FONTS_INITED = True


def add_context(w):
    init()
    CONTEXTS.add(w)


def draw_contexts(t):
    updated = False

    for w in CONTEXTS:
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

    draw_contexts(0)
    while True:
        # TODO: This is where we were polling for events.
        # glfw.poll_events()

        del_ws = [w for w in CONTEXTS if w.should_close()]
        for w in del_ws:
            w._destroy()
            CONTEXTS.remove(w)
        if not CONTEXTS:
            break

        t = time.time()
        if not draw_contexts(t - T0):
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

    # TODO: This is where we shut down glfw.
    # glfw.terminate()


def interact():
    global T0
    global SHOULD_INTERACT

    programs.load()
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    T0 = time.time()

    SHOULD_INTERACT = True
    draw_contexts(0)
    while SHOULD_INTERACT:
        # TODO: Get a HID event from glfw.
        # glfw.wait_events()

        del_ws = [w for w in CONTEXTS if w.should_close()]
        for w in del_ws:
            w._destroy()
            CONTEXTS.remove(w)
        if not CONTEXTS:
            break

        t = time.time()
        draw_contexts(t - T0)


def wakeup():
    # TODO: This is where we signaled the interact() thread to check its event
    # queue.
    # glfw.post_empty_event()
    pass

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
