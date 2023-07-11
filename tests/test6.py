import glotlib


w = glotlib.Window(900, 700, msaa=4)
p = w.add_plot(bounds=(0.1, 0.1, 0.9, 0.9), limits=(-200, -50, 200, 50))
p.add_points([(0, 0)], width=10)

glotlib.animate()
