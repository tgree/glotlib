import glotlib
import glotlib.glfw
from glotlib import fonts


class App(glotlib.GLContextDelegate):
    def __init__(self):
        w = glotlib.glfw.Window(512, 512, msaa=4, delegate=self)

        self.label = w.ctx.add_label(
            (0.5, 0.5),
            '.Woven silk pyjamas\nexchanged\nfor blue quartz.',
            font=fonts.vera(20, 1),
            anchor='C',
            )
        w.ctx.add_label((0.5, 0.5), '.', font=fonts.vera(20, 1))

    def update_geometry(self, t):
        self.label.set_theta(t / 4)
        return True

    def run(self):
        glotlib.glfw.animate()


def main():
    App().run()


if __name__ == '__main__':
    main()
