import glotlib
import glotlib.glfw


VERTICES = [
    (11.5, 11.5),
    (11.5, 91.5),
    (51.5, 91.5),
    (71.5, 51.5),
]


class App(glotlib.GLContextDelegate):
    def __init__(self):
        w = glotlib.glfw.Window(900, 700, msaa=None, delegate=self)

        self.ctx = w.ctx
        self.plot = w.ctx.add_plot(limits=(0, 0, 100, 100))
        self.plot.add_lines(VERTICES, color=(0, 0.8, 0.2, 0), width=20,
                            point_width=20)
        self.label = w.ctx.add_label((0.01, 0.01), '')

        glotlib.glfw.periodic(1, self.update_periodic)

    def update_geometry(self, t):
        return self.label.set_text('Time: %.1f' % t)

    def update_periodic(self, _t):
        self.ctx.mark_dirty()

    def run(self):
        glotlib.glfw.interact()


def main():
    App().run()


if __name__ == '__main__':
    main()
