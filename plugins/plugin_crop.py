#!/usr/bin/env python3
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

from plugsubclass import Viewer
from plugsubclass import Painting
from plugsubclass import Rect

### plugin infos #######################################################
NAME = "recadrage"
MOD_NAME = "plugin_crop"
DESCRIPTION = "recadre les images"
AUTHOR = "pops"
VERSION = 0.1


########################################################################
class ExecDialog(QtGui.QDialog):
    def __init__(self, images, args=None, code="", parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("crop")
        self.parent = parent
        self.codeBefore = code

        ### widget #####################################################
        ### image ###
        self.imW = QtGui.QComboBox(self)
        self.images = []
        for i, v in enumerate(images):
            f = os.path.split(v)[1]
            self.imW.addItem(f)
            self.images.append(v)

        ### effacer ###
        self.eraseW = QtGui.QToolButton(self)
        self.eraseW.setAutoRaise(True)
        self.eraseW.setIcon(QtGui.QIcon(QtGui.QPixmap('icons/black_eraser.svg')))

        ### couleur ###
        if args:
            self.color = args[4]
        else:
            self.color = QtGui.QColor(0, 0, 0)
        self.colorIcon = QtGui.QPixmap(22, 22)
        self.colorIcon.fill(self.color)

        self.colorW = QtGui.QToolButton(self)
        self.colorW.setAutoRaise(True)
        self.colorW.setIcon(QtGui.QIcon(self.colorIcon))

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

        ### labels info ###
        self.oriL = QtGui.QLabel("original size")
        self.oriWL = QtGui.QLabel("")
        self.oriHL = QtGui.QLabel("")
        self.newL = QtGui.QLabel("new size")
        self.newWL = QtGui.QLabel("")
        self.newHL = QtGui.QLabel("")

        ### action ###
        self.actionL = QtGui.QLabel("action")
        self.actionW = QtGui.QComboBox(self)
        self.actionW.addItem("ignore aspect ratio")
        self.actionW.addItem("keep aspect ratio")
        self.actionW.addItem("keep aspect ratio and resize")
        self.actionW.addItem("define width and height")

        ### w ###
        self.wL = QtGui.QLabel("width : ")
        self.wW = QtGui.QLineEdit("0")
        self.wW.setValidator(QtGui.QIntValidator(self.wW))

        ### h ###
        self.hL = QtGui.QLabel("height : ")
        self.hW = QtGui.QLineEdit("0")
        self.hW.setValidator(QtGui.QIntValidator(self.hW))

        ### edit ###
        self.editW = QtGui.QPushButton('edit', self)

        ### viewer ###
        self.painting = Painting(self)
        if args:
            self.painting.set_fig(Rect(self.painting, args[5]), self.color)
        else:
            self.painting.set_fig(Rect(self.painting, args), self.color)
        self.viewer = Viewer(self)
        self.viewer.setWidget(self.painting)

        ### apply, undo ###
        self.okW = QtGui.QPushButton('apply', self)
        self.undoW = QtGui.QPushButton('undo', self)

        ### function ###################################################
        self.im_changed(self.images[0])
        self.rect_changed()

        ### connexion ##################################################
        self.imW.activated[str].connect(self.im_changed)
        self.eraseW.clicked.connect(self.painting.fig.erase)
        self.colorW.clicked.connect(self.color_clicked)

        self.actionW.activated[str].connect(self.action_changed)
        self.wW.textChanged.connect(self.action_changed)
        self.hW.textChanged.connect(self.action_changed)
        self.editW.clicked.connect(self.edit_clicked)
        self.painting.fig.figChanged.connect(self.rect_changed)

        self.okW.clicked.connect(self.ok_clicked)
        self.undoW.clicked.connect(self.undo_clicked)

        self.zoomInW.clicked.connect(self.zoom_in)
        self.viewer.zoomIn.connect(self.zoom_in)
        self.zoomOutW.clicked.connect(self.zoom_out)
        self.viewer.zoomOut.connect(self.zoom_out)
        self.zoomOneW.clicked.connect(self.zoom_one)

        ### args #######################################################
        if args:
            self.wW.setText(str(args[1]))
            self.hW.setText(str(args[2]))
            self.actionW.setCurrentIndex(int(args[0]))
            self.painting.zoom(args[3])
        else:
            self.wW.setText(str(self.painting.imW))
            self.hW.setText(str(self.painting.imH))

        ### layout #####################################################
        toolBox = QtGui.QHBoxLayout()
        toolBox.addWidget(self.zoomInW)
        toolBox.addWidget(self.zoomOutW)
        toolBox.addWidget(self.zoomOneW)
        toolBox.addWidget(self.eraseW)
        toolBox.addWidget(self.colorW)
        toolBox.addStretch(0)

        grid = QtGui.QGridLayout()
        grid.setSpacing(2)
        grid.setColumnMinimumWidth(1, 10)
        grid.setColumnMinimumWidth(5, 10)
        grid.setColumnMinimumWidth(6, 100)
        grid.setColumnMinimumWidth(7, 100)

        grid.addWidget(self.imW, 0, 0)
        grid.addWidget(self.editW, 1, 0)
        grid.addLayout(toolBox, 2, 0)

        grid.addWidget(self.actionW, 0, 3, 1, 2)
        grid.addWidget(self.wL, 1, 3)
        grid.addWidget(self.hL, 2, 3)
        grid.addWidget(self.wW, 1, 4)
        grid.addWidget(self.hW, 2, 4)

        grid.addWidget(self.oriL, 0, 6)
        grid.addWidget(self.oriWL, 1, 6)
        grid.addWidget(self.oriHL, 2, 6)

        grid.addWidget(self.newL, 0, 7)
        grid.addWidget(self.newWL, 1, 7)
        grid.addWidget(self.newHL, 2, 7)

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
        self.color = QtGui.QColorDialog.getColor(self.color)
        if self.color.isValid():
            self.colorIcon.fill(self.color)
            self.colorW.setIcon(QtGui.QIcon(self.colorIcon))
            self.painting.color = self.color
        self.painting.draw()

    def action_changed(self, text=""):
        if self.hW.text() == "" or self.wW.text() == "":
            return
        #~ elif int(self.hW.text()) == 0 or int(self.wW.text()) == 0:
            #~ self.actionW.setCurrentIndex(0)
            #~ error = QtGui.QMessageBox(self)
            #~ error.setWindowTitle("error")
            #~ error.setText("The size must be greater than 0.")
            #~ error.setIcon(2)
            #~ error.exec()
            #~ return
        #~ if self.actionW.currentIndex() == 0:
            #~ self.wW.setDisabled(True)
            #~ self.hW.setDisabled(True)
        #~ else:
            #~ self.wW.setDisabled(False)
            #~ self.hW.setDisabled(False)
        if not self.painting.fig.action_changed(self.actionW.currentIndex(),
                                                    int(self.wW.text()),
                                                    int(self.hW.text())):
            self.actionW.setCurrentIndex(0)
            error = QtGui.QMessageBox(self)
            error.setWindowTitle("error")
            error.setText("The size must be greater than 0.")
            error.setIcon(2)
            error.exec()


    def edit_clicked(self):
        ok, x, y, w, h =  EditDialog(self, self.painting.fig.x,
                                           self.painting.fig.y,
                                           self.painting.fig.w,
                                           self.painting.fig.h).get_return()
        if ok:
            if w == "" or h == "":
                return
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)

            if w == 0 or h == 0:
                self.actionW.setCurrentIndex(0)
                error = QtGui.QMessageBox(self)
                error.setWindowTitle("error")
                error.setText("The size must be greater than 0.")
                error.setIcon(2)
                error.exec()
            else:
                self.actionW.setCurrentIndex(3)
                self.wW.setText(str(w))
                self.hW.setText(str(h))
                self.painting.fig.set_xywh(x, y, w, h)

    def rect_changed(self):
        self.oriWL.setText(str(self.painting.imW))
        self.oriHL.setText(str(self.painting.imH))
        if self.actionW.currentIndex() == 2: #keep aspect ratio and resize
            self.newWL.setText(self.wW.text())
            self.newHL.setText(self.hW.text())
        else:
            self.newWL.setText(str(self.painting.fig.w or ""))
            self.newHL.setText(str(self.painting.fig.h or ""))

    def ok_clicked(self):
        self.accept()

    def undo_clicked(self):
        self.reject()

    def get_return(self):
        if self.result():
            x = self.painting.fig.x
            y = self.painting.fig.y
            w = self.painting.fig.w
            h = self.painting.fig.h
            if self.painting.fig.exist:
                code = "$i = $i.copy(%s, %s, %s, %s)" %(x, y, w, h)
                desc = """x = %s y = %s
w = %s h = %s""" %(x, y, w, h)

            else:
                code = ""
                desc = ""
            # (windows args), (fig args)
            # (action, w, h, color, x, y, w, h, zoom)
            args = (self.actionW.currentIndex(),
                     int(self.wW.text()),
                     int(self.hW.text()),
                     self.painting.zoomN,
                     self.color,
                     (x, y, w, h))
            return True , code, desc, args
        else:
            return False, None, None, None

########################################################################
class EditDialog(QtGui.QDialog):
    def __init__(self, parent=None, x=0, y=0, w=1, h=1):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent

        self.xL = QtGui.QLabel("x")
        self.xW = QtGui.QLineEdit(self)
        self.xW.setValidator(QtGui.QIntValidator(self.xW))
        self.xW.setText(str(x))
        self.yL = QtGui.QLabel("y")
        self.yW = QtGui.QLineEdit(self)
        self.yW.setValidator(QtGui.QIntValidator(self.yW))
        self.yW.setText(str(y))
        self.wL = QtGui.QLabel("w")
        self.wW = QtGui.QLineEdit(self)
        self.wW.setValidator(QtGui.QIntValidator(self.wW))
        self.wW.setText(str(w))
        self.hL = QtGui.QLabel("h")
        self.hW = QtGui.QLineEdit(self)
        self.hW.setValidator(QtGui.QIntValidator(self.hW))
        self.hW.setText(str(h))

        ### appliquer ###
        self.okW = QtGui.QPushButton('apply', self)
        self.okW.clicked.connect(self.ok_clicked)
        ### annuler ###
        self.undoW = QtGui.QPushButton('undo', self)
        self.undoW.clicked.connect(self.undo_clicked)

        grid = QtGui.QGridLayout()
        grid.setSpacing(2)
        grid.addWidget(self.xL, 0, 0)
        grid.addWidget(self.xW, 0, 1)
        grid.addWidget(self.yL, 1, 0)
        grid.addWidget(self.yW, 1, 1)
        grid.addWidget(self.wL, 2, 0)
        grid.addWidget(self.wW, 2, 1)
        grid.addWidget(self.hL, 3, 0)
        grid.addWidget(self.hW, 3, 1)

        hBox = QtGui.QHBoxLayout()
        hBox.addWidget(self.okW)
        hBox.addWidget(self.undoW)

        grid.addLayout(hBox, 4, 0, 1, 2)
        self.setLayout(grid)
        self.exec_()

    def ok_clicked(self):
        self.accept()

    def undo_clicked(self):
        self.reject()

    def get_return(self):
        if self.result():
            x = self.xW.text()
            y = self.yW.text()
            w = self.wW.text()
            h = self.hW.text()
            return True, x, y, w, h
        else:
            return False, None, None, None, None


if __name__=="__main__":
    image = "/media/donnees/programation/imagemash/test/imgs/IMGP0333.JPG"
    app = QtGui.QApplication(sys.argv)
    win = ExecDialog([image])
