import glotlib


VERTICES = [
    (11.5, 11.5),
    (11.5, 91.5),
    (51.5, 91.5),
    (71.5, 51.5),
]


class Window(glotlib.Window):
    def __init__(self):
        super().__init__(900, 700, msaa=None)

        self.plot = self.add_plot(limits=(0, 0, 100, 100))
        self.plot.add_lines(VERTICES, color=(0, 0.8, 0.2, 0), width=20,
                            point_width=20)
        self.label = self.add_label((0.01, 0.01), '')

        glotlib.periodic(1, self.update_periodic)

    def update_geometry(self, t):
        return self.label.set_text('Time: %.1f' % t)

    def update_periodic(self, _t):
        self.mark_dirty()


def main():
    Window()
    glotlib.interact()


if __name__ == '__main__':
    main()
