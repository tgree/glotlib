import importlib.resources
import sys

from OpenGL import GL
from OpenGL.GL import shaders


class Program:
    def __init__(self, v_text, f_text, uniforms=None):
        self.v_shader = shaders.compileShader(v_text, GL.GL_VERTEX_SHADER)
        self.f_shader = shaders.compileShader(f_text, GL.GL_FRAGMENT_SHADER)
        self.shader   = shaders.compileProgram(self.v_shader, self.f_shader,
                                               validate=False)
        if uniforms:
            self.uniforms = {u : GL.glGetUniformLocation(self.shader, u)
                             for u in uniforms}
        else:
            self.uniforms = {}

    @staticmethod
    def from_resource(anchor, v_path, f_path, **kwargs):
        if sys.version_info < (3, 9):
            v_text = importlib.resources.read_text(anchor, v_path)
            f_text = importlib.resources.read_text(anchor, f_path)
        else:
            files  = importlib.resources.files(anchor)
            v_text = files.joinpath(v_path).read_text()
            f_text = files.joinpath(f_path).read_text()
        return Program(v_text, f_text, **kwargs)

    @staticmethod
    def from_builtin(v_path, f_path, **kwargs):
        return Program.from_resource('glotlib.shaders', v_path, f_path,
                                     **kwargs)

    def useProgram(self):
        GL.glUseProgram(self.shader)

    def uniform1i(self, u, i):
        GL.glUniform1i(self.uniforms[u], i)

    def uniform1f(self, u, f):
        GL.glUniform1f(self.uniforms[u], f)

    def uniform2f(self, u, f0, f1):
        GL.glUniform2f(self.uniforms[u], f0, f1)

    def uniform4f(self, u, f0, f1, f2, f3):
        GL.glUniform4f(self.uniforms[u], f0, f1, f2, f3)

    def uniformMatrix4fv(self, u, m):
        GL.glUniformMatrix4fv(self.uniforms[u], 1, GL.GL_TRUE, m)

    def attrib_location(self, name):
        return GL.glGetAttribLocation(self.shader, name)


class BuiltinProgram(Program):
    def __init__(self, v_path, f_path, **kwargs):
        if sys.version_info < (3, 9):
            v_text = importlib.resources.read_text('glotlib.shaders', v_path)
            f_text = importlib.resources.read_text('glotlib.shaders', f_path)
        else:
            files  = importlib.resources.files('glotlib.shaders')
            v_text = files.joinpath(v_path).read_text()
            f_text = files.joinpath(f_path).read_text()
        super().__init__(v_text, f_text, **kwargs)
