import glotlib
import glotlib.glfw
from glotlib import fonts


class Delegate(glotlib.GLContextDelegate):
    def __init__(self, ctx):
        self.label = ctx.add_label(
            (0.5, 0.5),
            '.Woven silk pyjamas\nexchanged\nfor blue quartz.',
            font=fonts.vera(20, 1),
            anchor='C',
            )
        ctx.add_label((0.5, 0.5), '.', font=fonts.vera(20, 1))

    def update_geometry(self, t):
        self.label.set_theta(t / 4)
        return True


def main():
    w = glotlib.glfw.Window(512, 512, msaa=4)
    w.gl_context.delegate = Delegate(w.gl_context)
    glotlib.glfw.animate()


if __name__ == '__main__':
    main()
