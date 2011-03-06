#!/usr/bin/env python
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
from __future__ import division

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt
import sys, os

image = "/home/pops/prog/img/IMGP0333.JPG"
### plugin infos #######################################################
NAME = "redimmensionner"
MOD_NAME = "plugin_resize"
DESCRIPTION = "redimmensionne les images"
AUTHOR = "pops"
VERSION = 0.1
EXEC_CLASS = "ResizeDialog"#(images, args)

class ResizeDialog(QtGui.QDialog):
    def __init__(self, images, args=None, code="", parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.codeBefore = code
        
        ### liste des images ###
        self.im = QtGui.QImage()
        self.imW = QtGui.QComboBox(self)
        self.imW.setCurrentIndex(0)
        self.imW.activated[str].connect(self.im_changed)
        
        self.images = []
        for i, v in enumerate(images):
            f = os.path.split(v)[1]
            self.imW.addItem(f)
            self.images.append(v)
        self.image = self.images[0]
        
        ### info sur l'image originale ###
        self.imOriInfo = QtGui.QLabel("")
        self.im_changed()
        
        ### ratio ###
        self.ratio = "set size"
        self.ratioW = QtGui.QComboBox(self)
        self.ratioW.addItem("set size")
        self.ratioW.addItem("fit to width")
        self.ratioW.addItem("fit to height")
        self.ratioW.setCurrentIndex(0)
        self.ratioW.activated[str].connect(self.ratio_changed)
        
        self.wL = QtGui.QLabel("width")
        self.wW = QtGui.QLineEdit(self)
        self.wW.setValidator(QtGui.QIntValidator(self.wW))
        self.wW.setText(str(self.im.width()))
        self.wW.textChanged[str].connect(self.w_changed)

        self.hL = QtGui.QLabel("height")
        self.hW = QtGui.QLineEdit(self)
        self.hW.setValidator(QtGui.QIntValidator(self.hW))
        self.hW.setText(str(self.im.height()))
        self.hW.textChanged[str].connect(self.h_changed)
        
        ### appliquer ###
        self.okW = QtGui.QPushButton('appliquer', self)
        self.okW.clicked.connect(self.ok_clicked)
        
        ### annuler ###
        self.undoW = QtGui.QPushButton('annuler', self)
        self.undoW.clicked.connect(self.undo_clicked)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(2)
        grid.addWidget(self.imW, 0, 1)
        grid.addWidget(self.imOriInfo, 0, 2)
        grid.addWidget(self.ratioW, 1, 1)
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
        
    def im_changed(self, text=None):
        self.im.load(self.images[self.imW.currentIndex()])
        print self.images[self.imW.currentIndex()]
        code = self.codeBefore.replace("$i", "self.im")
        exec code
        self.imOriInfo.setText("%s / %s"%(self.im.height(),self.im.width()))
        
        
    def ratio_changed(self, text):
        self.ratio = text
        if text == "set size":
            self.hW.setDisabled(False)
            self.wW.setDisabled(False)
        elif text == "fit to width":
            self.hW.setDisabled(True)
            self.wW.setDisabled(False)
            self.w_changed(self.wW.text())
        elif text == "fit to height":
            self.hW.setDisabled(False)
            self.wW.setDisabled(True)
            self.h_changed(self.hW.text())
    
    def w_changed(self, text):
        if self.ratio == "fit to width" and text > 0:
            h = int((self.im.height() * int(text)) / self.im.width())
            self.hW.setText(str(h))
            
    def h_changed(self, text):
        if self.ratio == "fit to height" and text > 0:
            w = int((self.im.width() * int(text)) / self.im.height())
            self.wW.setText(str(w))
    
    def ok_clicked(self):
        self.accept()
    def undo_clicked(self):
        self.reject()
        
    def get_return(self):
        w = self.wW.text()
        h = self.hW.text()
        if self.result() and w > 0 and h > 0:
            
            if self.ratio == "set size":
                code = "$i = $i.scaled(%s, %s, QtCh = %sore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)" %(w, h)
                desc = "w = %s h = %s" %(w, h)
            elif self.ratio == "fit to width":
                code = "$i = $i.scaledToWidth(%s, QtCore.Qt.SmoothTransformation)" %(w,)
                desc = "fit to width (%spx)" %(w,)
            elif self.ratio == "fit to height":
                code = "$i = $i.scaledToHeight(%s, QtCore.Qt.SmoothTransformation)" %(h,)
                desc = "fit to height (%spx)" %(h,)
            args = (w, h)
            return True , code, desc, args
        else:
            return False, None, None, None
    def apply_args(self, args):
        pass
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    win = ResizeDialog([image])
    app.exec_()
