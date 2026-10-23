from PySide6.QtGui import QSurfaceFormat
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


def init_backend(msaa=None):
    """
    Initializes the global OpenGL format requirements for glotlib.
    Must be called at the very top of the client application 
    BEFORE instantiating the QApplication object.
    """
    gl_format = QSurfaceFormat()
    gl_format.setVersion(3, 3)
    gl_format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    gl_format.setDepthBufferSize(24)
    gl_format.setStencilBufferSize(8)
    
    if msaa is not None:
        gl_format.setSamples(msaa)
        
    # Lock this configuration in globally
    QSurfaceFormat.setDefaultFormat(gl_format)
    
    # Force Desktop Hardware rendering path across all platforms
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)
