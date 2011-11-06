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

from PyQt4 import QtGui
from PyQt4 import QtCore

### plugin infos #######################################################
NAME = "flip / rotate"
MOD_NAME = "plugin_flip"
DESCRIPTION = "flip / rotate"
AUTHOR = "pops"
VERSION = 0.1


########################################################################
class ExecDialog(QtGui.QDialog):
    def __init__(self, images=[], args=None, code="", parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle("flip / rotate")

        ### flip ###
        self.flipL = QtGui.QLabel("flip")
        self.flipW = QtGui.QComboBox(self)
        self.flipW.addItem("no flip")
        self.flipW.addItem("flip horizontally")
        self.flipW.addItem("flip vertically")
        self.flipW.addItem("flip horizontally and vertically")

        ### rotate ###
        self.rotateL = QtGui.QLabel("rotate")
        self.rotateW = QtGui.QComboBox(self)
        self.rotateW.addItem("no rotation")
        self.rotateW.addItem("rotate by 90°")
        self.rotateW.addItem("rotate by -90°")
        self.rotateW.addItem("rotate 180°")

        ### args ###
        if args:
            self.flipW.setCurrentIndex(args[0])
            self.rotateW.setCurrentIndex(args[1])

        ### apply, undo ###
        self.okW = QtGui.QPushButton('apply', self)
        self.okW.clicked.connect(self.ok_clicked)
        self.undoW = QtGui.QPushButton('undo', self)
        self.undoW.clicked.connect(self.undo_clicked)

        ### layout ###
        grid = QtGui.QGridLayout()
        grid.setSpacing(3)
        grid.addWidget(self.flipL, 0, 0)
        grid.addWidget(self.flipW, 0, 1)
        grid.addWidget(self.rotateL, 1, 0)
        grid.addWidget(self.rotateW, 1, 1)

        okBox = QtGui.QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.okW)
        okBox.addWidget(self.undoW)

        vBox = QtGui.QVBoxLayout()
        vBox.addLayout(grid)
        vBox.addStretch(0)
        vBox.addLayout(okBox)

        self.setLayout(vBox)
        self.exec_()

    def ok_clicked(self):
        self.accept()

    def undo_clicked(self):
        self.reject()

    def get_return(self):
        if self.result():
            if self.flipW.currentIndex() == 0: # horizontal
                code = ""
                desc = "no flip"
            if self.flipW.currentIndex() == 1: # horizontal
                code = "$i = $i.mirrored(True, False)"
                desc = "flip horizontally"
            elif self.flipW.currentIndex() == 2: # vertical
                code = "$i = $i.mirrored(False, True)"
                desc = "flip vertically"
            elif self.flipW.currentIndex() == 3: # horizontal and vertical
                code = "$i = $i.mirrored(True, True)"
                desc = "flip horizontally and vertically"

            if self.rotateW.currentIndex() == 0:
                desc = """%s
no rotation""" %(desc)
            elif self.rotateW.currentIndex() == 1: # 90°
                code = """%s
transform = QtGui.QTransform()
transform.rotate(90)
$i = $i.transformed(transform, QtCore.Qt.SmoothTransformation)""" %(code,)
                desc = """%s
rotate by 90°""" %(desc)
            elif self.rotateW.currentIndex() == 2: # -90°
                code = """%s
transform = QtGui.QTransform()
transform.rotate(-90)
$i = $i.transformed(transform, QtCore.Qt.SmoothTransformation)""" %(code,)
                desc = """%s
rotate by -90°""" %(desc)
            elif self.rotateW.currentIndex() == 3: # 180°
                code = """%s
transform = QtGui.QTransform()
transform.rotate(180)
$i = $i.transformed(transform, QtCore.Qt.SmoothTransformation)""" %(code,)
                desc = """%s
rotate by 180°""" %(desc)

            args = (self.flipW.currentIndex(), self.rotateW.currentIndex())
            return True , code, desc, args
        else:
            return False, None, None, None

if __name__=="__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = ExecDialog()
