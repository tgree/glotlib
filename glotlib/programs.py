from .program import BuiltinProgram


miter_line  = None
square_line = None
frag_points = None
text        = None


class MiterLineProgram(BuiltinProgram):
    UNIFORMS = [
        'u_line_vertices',
        'u_mvp',
        'u_resolution',
        'u_width',
        'u_z',
        'u_color',
    ]

    def __init__(self):
        super().__init__('miter_line.vert', 'frag.frag', uniforms=self.UNIFORMS)

    def use(self, width, z, lines, mvp, color=(0, 0, 0, 1), resolution=None):
        self.useProgram()
        self.uniform1f('u_width', width)
        self.uniform1f('u_z', z)
        self.uniform1i('u_line_vertices', lines.bind_unit)
        self.uniform4f('u_color', *color)
        self.uniformMatrix4fv('u_mvp', mvp)
        self.uniform2f('u_resolution', *resolution)


class SquareLineProgram(BuiltinProgram):
    UNIFORMS = [
        'u_mvp',
        'u_width',
        'u_resolution',
        'u_z',
        'u_color',
    ]

    def __init__(self):
        super().__init__('square_instanced_line.vert', 'frag.frag',
                         uniforms=self.UNIFORMS)

    def use(self, width, z, mvp, color=(0, 0, 0, 1), resolution=None):
        self.useProgram()
        self.uniform1f('u_width', width)
        self.uniform1f('u_z', z)
        self.uniform4f('u_color', *color)
        self.uniformMatrix4fv('u_mvp', mvp)
        self.uniform2f('u_resolution', *resolution)


class FragPointsProgram(BuiltinProgram):
    UNIFORMS = [
        'u_mvp',
        'u_z',
        'u_color',
    ]

    def __init__(self):
        super().__init__('mvp_z.vert', 'points.frag', uniforms=self.UNIFORMS)

    def use(self, z, mvp, color=(0, 0, 0, 1)):
        self.useProgram()
        self.uniform1f('u_z', z)
        self.uniform4f('u_color', *color)
        self.uniformMatrix4fv('u_mvp', mvp)


class TextProgram(BuiltinProgram):
    UNIFORMS = [
        'u_mvp',
        'u_z',
        'u_color',
        'u_sampler',
    ]

    def __init__(self):
        super().__init__('text.vert', 'text.frag', uniforms=self.UNIFORMS)

    def use(self, z, mvp, font, color=(0, 0, 0, 1)):
        self.useProgram()
        self.uniform1f('u_z', z)
        self.uniform4f('u_color', *color)
        self.uniformMatrix4fv('u_mvp', mvp)
        self.uniform1i('u_sampler', font.bind_unit)


def load():
    global miter_line
    global square_line
    global frag_points
    global text

    miter_line  = MiterLineProgram()
    square_line = SquareLineProgram()
    frag_points = FragPointsProgram()
    text        = TextProgram()
