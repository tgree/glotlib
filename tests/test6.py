import glotlib
import glotlib.glfw


w = glotlib.glfw.Window(900, 700, msaa=4)
p = w.ctx.add_plot(bounds=(0.1, 0.1, 0.9, 0.9), limits=(-200, -50, 200, 50))
p.add_points([(0, 0)], width=10)

glotlib.glfw.animate()
