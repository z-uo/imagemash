#!/usr/bin/python3
#-*- coding: utf-8 -*-
#
#Copyright pops (pops451@gmail.com), 2010-2011
#
#This file is part of imagemash.
#
#    imagemash is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    imagemash is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with imagemash.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
import math

from plugsubclass import Viewer
from plugsubclass import Painting
from plugsubclass import Line

### plugin infos #######################################################
NAME = "rotation"
MOD_NAME = "plugin_rotate"
DESCRIPTION = "rotation libre"
AUTHOR = "pops"
VERSION = 0.1


########################################################################
class ExecDialog(QtGui.QDialog):
    def __init__(self, images, args=None, code="", parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("rotation")
        self.parent = parent
        self.codeBefore = code

        ### widget #####################################################
        ### image ###
        self.imW = QtGui.QComboBox(self)
        self.images = []
        if images:
            for i, v in enumerate(images):
                f = os.path.split(v)[1]
                self.imW.addItem(f)
                self.images.append(v)

        ### zoom buttons ###
        self.zoomInW = QtGui.QToolButton()
        self.zoomInW.setAutoRaise(True)
        self.zoomInW.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/black_zoom_in.svg")))
        self.zoomOutW = QtGui.QToolButton()
        self.zoomOutW.setAutoRaise(True)
        self.zoomOutW.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/black_zoom_out.svg")))
        self.zoomOneW = QtGui.QToolButton()
        self.zoomOneW.setAutoRaise(True)
        self.zoomOneW.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/black_zoom_one.svg")))

        ### couleur ###
        if args:
            self.color = args["color"]
        else:
            self.color = QtGui.QColor(0, 0, 0)
        self.colorIcon = QtGui.QPixmap(22, 22)
        self.colorIcon.fill(self.color)

        self.colorW = QtGui.QToolButton(self)
        self.colorW.setAutoRaise(True)
        self.colorW.setIcon(QtGui.QIcon(self.colorIcon))

        ### action ###
        self.actionW = QtGui.QComboBox(self)
        self.actionW.addItem("tracer horizontal")
        self.actionW.addItem("tracer vertical")
        self.actionW.addItem("entrer angle")

        ### rotate 90, 180, 370 ###
        self.rotate90W = QtGui.QToolButton()
        self.rotate90W.setAutoRaise(True)
        self.rotate90W.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/90.svg")))
        self.rotate270W = QtGui.QToolButton()
        self.rotate270W.setAutoRaise(True)
        self.rotate270W.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/-90.svg")))
        self.rotate180W = QtGui.QToolButton()
        self.rotate180W.setAutoRaise(True)
        self.rotate180W.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/180.svg")))

        ### labels info ###
        self.angle = 0
        self.degreL = QtGui.QLabel("angle :")
        self.degreW = QtGui.QLineEdit("0")
        self.degreW.setValidator(QtGui.QIntValidator(self.degreW))
        self.degreW.setDisabled(True)

        ### reset ###
        self.resetW = QtGui.QPushButton("reset")

        ### apercu ###
        self.apercuW = QtGui.QPushButton("apercu")

        ### viewer ###
        self.painting = Painting(self)
        self.painting.set_fig(Line(self.painting), self.color)
        self.viewer = Viewer(self)
        self.viewer.setWidget(self.painting)

        ### apply, undo ###
        self.okW = QtGui.QPushButton('apply', self)
        self.undoW = QtGui.QPushButton('undo', self)

        ### function ###################################################
        if images:
            self.im_changed(self.images[0])

        ### connexion ##################################################
        self.imW.activated[str].connect(self.im_changed)

        self.rotate90W.clicked.connect(self.rot90)
        self.rotate180W.clicked.connect(self.rot180)
        self.rotate270W.clicked.connect(self.rot270)
        self.colorW.clicked.connect(self.color_clicked)

        self.actionW.activated[str].connect(self.action_changed)
        self.degreW.textChanged.connect(self.degre_changed)
        self.apercuW.clicked.connect(self.apercu_clicked)
        self.resetW.clicked.connect(self.reset_clicked)

        self.okW.clicked.connect(self.ok_clicked)
        self.undoW.clicked.connect(self.undo_clicked)

        self.zoomInW.clicked.connect(self.zoom_in)
        self.viewer.zoomIn.connect(self.zoom_in)
        self.zoomOutW.clicked.connect(self.zoom_out)
        self.viewer.zoomOut.connect(self.zoom_out)
        self.zoomOneW.clicked.connect(self.zoom_one)

        ### args #######################################################
        if args:
            self.actionW.setCurrentIndex(args["action"])
            self.action_changed()
            self.painting.zoomN = args["zoom"]
            self.angle = args["angle"]
            self.apercu_clicked(self.angle)
        else:
            pass

        ### layout #####################################################
        toolBox = QtGui.QHBoxLayout()
        toolBox.addWidget(self.zoomInW)
        toolBox.addWidget(self.zoomOutW)
        toolBox.addWidget(self.zoomOneW)
        toolBox.addWidget(self.colorW)
        toolBox.addWidget(self.rotate90W)
        toolBox.addWidget(self.rotate270W)
        toolBox.addWidget(self.rotate180W)
        toolBox.addStretch(0)

        grid = QtGui.QGridLayout()
        grid.setSpacing(2)
        grid.addWidget(self.imW, 0, 0)
        grid.addLayout(toolBox, 1, 0, 1, 2)
        grid.addWidget(self.actionW, 0, 1)
        grid.addWidget(self.degreL, 0, 2)
        grid.addWidget(self.degreW, 0, 3)
        grid.addWidget(self.apercuW, 1, 3)
        grid.addWidget(self.resetW, 1, 2)

        ### ok, undo ###
        okBox = QtGui.QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.okW)
        okBox.addWidget(self.undoW)

        ### layout ###
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(2)
        layout.addLayout(grid)
        layout.addWidget(self.viewer)
        layout.addLayout(okBox)

        self.setLayout(layout)
        self.exec_()

    def zoom_in(self):
        self.painting.zoom(2.0)

    def zoom_out(self):
        self.painting.zoom(0.5)

    def zoom_one(self):
        self.painting.zoom(0)

    def im_changed(self, text):
        im = self.images[self.imW.currentIndex()]
        self.painting.change_image(im, self.codeBefore)

    def color_clicked(self):
        color = QtGui.QColorDialog.getColor(self.color)
        if color.isValid():
            self.color = color
            self.colorIcon.fill(self.color)
            self.colorW.setIcon(QtGui.QIcon(self.colorIcon))
            self.painting.color = self.color
        self.painting.draw()

    def rot90(self):
        self.apercu_clicked(self.angle + 90)

    def rot180(self):
        self.apercu_clicked(self.angle + 180)

    def rot270(self):
        self.apercu_clicked(self.angle + 270)

    def action_changed(self, text=None):
        if self.actionW.currentIndex() == 0:
            self.degreW.setDisabled(True)
            self.painting.fig.setDisabled(False)
        elif self.actionW.currentIndex() == 1:
            self.degreW.setDisabled(True)
            self.painting.fig.setDisabled(False)
        elif self.actionW.currentIndex() == 2:
            self.degreW.setDisabled(False)
            self.painting.fig.setDisabled(True)
        self.painting.draw()

    def apercu_clicked(self, angle=False):
        angle = angle or self.return_angle()
        self.angle = self.display_deg(angle)
        self.degreW.setText(str(self.angle))
        self.rotate()

    def return_angle(self):
        angle = self.angle
        if self.actionW.currentIndex() == 0 and self.painting.fig.visible:
                x1, x2 = self.painting.fig.x1, self.painting.fig.x2
                y1, y2 = self.painting.fig.y1, self.painting.fig.y2
                hypotenuse = math.sqrt(((x2 - x1)*(x2 - x1)) + ((y1 - y2)*(y1 - y2)))
                cos = (x2 - x1) / hypotenuse
                angle = math.degrees(math.acos(cos))
                if y2 < y1 :
                    angle = -angle
                if x2 < x1 :
                    angle = angle - 180
                angle = self.angle - angle

        elif self.actionW.currentIndex() == 1 and self.painting.fig.visible:
            if self.painting.fig.visible:
                x1, x2 = self.painting.fig.x1, self.painting.fig.x2
                y1, y2 = self.painting.fig.y1, self.painting.fig.y2
                hypotenuse = math.sqrt(((x2 - x1)*(x2 - x1)) + ((y1 - y2)*(y1 - y2)))
                cos = (y2 - y1) / hypotenuse
                angle = math.degrees(math.acos(cos))
                if x1 < x2 :
                    angle = -angle
                if y2 < y1 :
                    angle = angle - 180
                angle = self.angle - angle

        elif self.actionW.currentIndex() == 2:
            angle = float(self.degreW.text())
        return angle

    def rotate(self):
        if self.angle != 0:
            code = """
matrix = QtGui.QMatrix()
matrix.rotate(%s)
$i = $i.transformed(matrix, QtCore.Qt.FastTransformation)""" %(self.angle,)
            self.painting.fig.hide()
            self.painting.apply_rotation(code)
        else:
            self.painting.reset()

    def reset_clicked(self):
        self.painting.reset()
        self.degreW.setText("0")
        self.angle = 0

    def display_deg(self, angle=0):
        while angle >= 360:
            angle -= 360
        while angle <= -360:
            angle += 360
        return angle

    def degre_changed(self):
        pass

    def ok_clicked(self):
        self.accept()

    def undo_clicked(self):
        self.reject()

    def get_return(self):
        if self.result():
            self.angle = self.display_deg(self.return_angle())
            if self.angle != 0:
                code = """
matrix = QtGui.QMatrix()
matrix.rotate(%s)
$i = $i.transformed(matrix, QtCore.Qt.SmoothTransformation)""" %(self.angle,)
            else:
                code = ""
            desc = "angle = %s" %(self.angle,)
            args = {"action": self.actionW.currentIndex(),
                    "color": self.color,
                    "zoom": self.painting.zoomN,
                    "angle": self.angle,}
            return True , code, desc, args
        else:
            return False, None, None, None

if __name__=="__main__":
    image = "../test/imgs/IMGP0333.JPG"
    app = QtGui.QApplication(sys.argv)
    win = ExecDialog([image])
