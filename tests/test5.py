import glotlib
import glotlib.glfw


VERTICES = [
    (11.5, 11.5),
    (11.5, 91.5),
    (51.5, 91.5),
    (71.5, 51.5),
]


class Delegate(glotlib.GLContextDelegate):
    def __init__(self, ctx):
        self.ctx = ctx
        self.plot = ctx.add_plot(limits=(0, 0, 100, 100))
        self.plot.add_lines(VERTICES, color=(0, 0.8, 0.2, 0), width=20,
                            point_width=20)
        self.label = ctx.add_label((0.01, 0.01), '')

        glotlib.glfw.periodic(1, self.update_periodic)

    def update_geometry(self, t):
        return self.label.set_text('Time: %.1f' % t)

    def update_periodic(self, _t):
        self.ctx.mark_dirty()


def main():
    w = glotlib.glfw.Window(900, 700, msaa=None)
    w.gl_context.delegate = Delegate(w.gl_context)
    glotlib.glfw.interact()


if __name__ == '__main__':
    main()
