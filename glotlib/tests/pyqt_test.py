# Copyright (c) 2023 by Phase Advanced Sensor Systems, Inc.
# All rights reserved.
import threading
import argparse
import math
import time
import sys
import glotlib

import xtalx.p_sensor
from xtalx.tools.math import XYSeries
from OpenGL import GL
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QSurfaceFormat
from PyQt5 import QtCore, QtGui, QtWidgets


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")

        self.setMaximumSize(900,825)
        self.setMinimumSize(900, 825)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 900, 825))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.tabWidget.setFont(font)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setObjectName("tabWidget")
        self.plots = QtWidgets.QWidget()
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        self.plots.setFont(font)
        self.plots.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.plots.setAcceptDrops(False)
        self.plots.setObjectName("plots")
        self.glotlibWidget = glotlibglotlib_context()
        self.glotlibWidget.setGeometry(QtCore.QRect(0, 35, 900, 700))
        self.glotlibWidget.setParent(self.plots)
        self.glotlibWidget.setObjectName("glotlibWidget")
        self.saveButton = QtWidgets.QPushButton(self.plots)
        self.saveButton.setGeometry(QtCore.QRect(725, 748, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        self.saveButton.setFont(font)
        self.saveButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.saveButton.setStyleSheet("")
        icon = QtGui.QIcon.fromTheme("QIcon::ThemeIcon::DocumentSave")
        self.saveButton.setIcon(icon)
        self.saveButton.setIconSize(QtCore.QSize(20, 20))
        self.saveButton.setObjectName("saveButton")
        self.serialNum = QtWidgets.QLabel(self.plots)
        self.serialNum.setGeometry(QtCore.QRect(10, 6, 100, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.serialNum.setFont(font)
        self.serialNum.setObjectName("serialNum")
        self.serialPlace = QtWidgets.QLabel(self.plots)
        self.serialPlace.setGeometry(QtCore.QRect(120, 6, 141, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        self.serialPlace.setFont(font)
        self.serialPlace.setObjectName("serialPlace")
        self.tabWidget.addTab(self.plots, "")
        self.about = QtWidgets.QWidget()
        self.about.setObjectName("about")
        self.tabWidget.addTab(self.about, "")
        self.settings = QtWidgets.QWidget()
        self.settings.setObjectName("settings")
        self.tabWidget.addTab(self.settings, "")
        self.setCentralWidget(self.centralwidget)
        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)
        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "xtalx"))
        self.saveButton.setText(_translate("MainWindow", "Save as CSV File"))
        self.serialNum.setText(_translate("MainWindow", "Serial Number:"))
        self.serialPlace.setText(_translate("MainWindow", "Place Holder"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.plots), _translate("MainWindow", "Plots"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.about), _translate("MainWindow", "Settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settings), _translate("MainWindow", "About"))

LINE_WIDTH = 1


class glotlibglotlib_context(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.width           = 900
        self.height          = 700
        self.msaa            = 2
        self.t0              = None

        # Manually sets OpenGl version to 3.3
        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QSurfaceFormat.CoreProfile)
        QSurfaceFormat.setDefaultFormat(fmt)
        self.setFormat(fmt)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(0)  # Update approximately every 16ms (~60 FPS)

    def update_geometry(self, t):
        for s, ar, tr in zip(self.series, AMP_RATES, THICK_RATES):
            Y = np.sin(X + ar * t) + DY
            s.set_y_data(Y)

            r = 2 * (np.sin(2 * math.pi * tr * t) + 1) + 1
            s.width = r
            s.point_width = r

    def initializeGL(self):
        GL.glClearColor(1,1,1,0)
        glotlib.programs.load()
        self.makeCurrent()
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        
        self.glotlib_context = glotlib.Context(self.width,self.height,
                                               msaa=self.msaa) 

        self.plot = self.add_plot(limits=(0, DY - 1, 2 * math.pi, DY + 1))

        print('DX: %f' % (X[1] - X[0]))
        Ys = [np.sin(X + ar) + DY for ar in AMP_RATES]
        self.series = [self.plot.add_lines(X=X, Y=Y, width=1, point_width=1)
                       for Y in Ys]

    def paintGL(self):
        if self.t0 is None:
            self.t0 = time.time()
        self.update_geometry(time.time() - self.t0)

        # Mandatory Field 
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self._dirty = True
        self.makeCurrent()
        glotlib.main.draw_contexts(0)

    def resizeGL(self, w, h):
        GL.glViewport(0,0,w,h)
    

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


def _main():
    main()


if __name__ == '__main__':
    _main()
