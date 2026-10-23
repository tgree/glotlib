from OpenGL import GL

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtOpenGLWidgets import QOpenGLWidget


gl_format = QSurfaceFormat()
gl_format.setVersion(3, 3)
gl_format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
gl_format.setDepthBufferSize(24)
QSurfaceFormat.setDefaultFormat(gl_format)


class MyWidget(QOpenGLWidget):
    def initializeGL(self):
        # 1. Get the current active context format
        actual_format = self.context().format()
        
        # 2. Extract version details
        major = actual_format.majorVersion()
        minor = actual_format.minorVersion()
        
        # 3. Extract the profile type
        profile = actual_format.profile()
        if profile == QSurfaceFormat.OpenGLContextProfile.CoreProfile:
            profile_str = "Core Profile"
        elif profile == QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile:
            profile_str = "Compatibility Profile"
        else:
            profile_str = "No Profile (Legacy/Fallback)"

        print("\n=== GRANTED OPENGL SURFACE DETAILS ===")
        print(f"Version: {major}.{minor}")
        print(f"Profile: {profile_str}")
        print("======================================\n")

        # Your original clear color setting
        GL.glClearColor(1.0, 0.0, 0.0, 1.0)

    def resizeGL(self, w, h):
        pass

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)


app = QApplication()
window = QWidget()
layout = QVBoxLayout(window)

my_widget = MyWidget()
my_widget.setFormat(gl_format)

layout.addWidget(MyWidget())

window.resize(300, 300)
window.show()

app.exec()
