import glotlib
from glotlib import fonts


class Window(glotlib.Window):
    def __init__(self):
        super().__init__(1024, 256, msaa=4)

        self.label = self.add_label(
            (0.1, 0.1),
            '.Woven silk pyjamas\nexchanged\nfor blue quartz.',
            font=fonts.vera(20, 1))

    def update_geometry(self, t):
        self.label.set_theta(t / 4)
        return True


def main():
    Window()
    glotlib.animate()


if __name__ == '__main__':
    main()
