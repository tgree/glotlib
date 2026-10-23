from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from .gl_context import GLWidget


class Window:
    def __init__(self, w, h, x=100, y=100, name='', msaa=None, parent=None,
                 **kwargs):
        self.window_widget = QWidget()

        layout = QHBoxLayout(self.window_widget)
        # layout.setContentsMargins(0, 0, 0, 0)

        self.gl_widget = GLWidget(self, msaa, parent=self.window_widget)
        self.ctx = None

        layout.addWidget(self.gl_widget)

        self.window_widget.setWindowTitle(name)
        self.window_widget.resize(w, h)
        self.window_widget.move(x, y)

    def show(self):
        self.window_widget.show()
