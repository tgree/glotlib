import glotlib
from glotlib import fonts


class Window(glotlib.Window):
    def __init__(self):
        super().__init__(512, 512, msaa=4)

        self.label = self.add_label(
            (0.5, 0.5),
            '.Woven silk pyjamas\nexchanged\nfor blue quartz.',
            font=fonts.vera(20, 1),
            anchor='C',
            )
        self.add_label((0.5, 0.5), '.', font=fonts.vera(20, 1))

    def update_geometry(self, t):
        self.label.set_theta(t / 4)
        return True


def main():
    Window()
    glotlib.animate()


if __name__ == '__main__':
    main()
