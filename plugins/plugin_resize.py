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

### plugin infos #######################################################
NAME = "redimmensionner"
MOD_NAME = "plugin_resize"
DESCRIPTION = "redimmensionne les images"
AUTHOR = "pops"
VERSION = 0.1


########################################################################
class ExecDialog(QtGui.QDialog):
    def __init__(self, images=[], args=None, code="", parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle("resize")
        self.codeBefore = code
        
        ### liste des images ###
        self.im = QtGui.QImage()
        self.imW = QtGui.QComboBox(self)
        self.images = []
        for i, v in enumerate(images):
            f = os.path.split(v)[1]
            self.imW.addItem(f)
            self.images.append(v)
        
        ### ratio ###
        self.ratioIndex = ["keep aspect ratio",
                           "keep aspect ratio by extending",
                           "ignore aspect ratio",
                           "fit to width",
                           "fit to height"]
        self.ratioW = QtGui.QComboBox(self)
        for i in self.ratioIndex:
            self.ratioW.addItem(i)
        
        ### width ###
        self.wL = QtGui.QLabel("width")
        self.wW = QtGui.QLineEdit(self)
        self.wW.setValidator(QtGui.QIntValidator(self.wW))
        
        ### height ###
        self.hL = QtGui.QLabel("height")
        self.hW = QtGui.QLineEdit(self)
        self.hW.setValidator(QtGui.QIntValidator(self.hW))
        
        ### info labels ###
        self.oriL = QtGui.QLabel("original size")
        self.oriWL = QtGui.QLabel("")
        self.oriHL = QtGui.QLabel("")
        
        self.newL = QtGui.QLabel("new size")
        self.newWL = QtGui.QLabel("")
        self.newHL = QtGui.QLabel("")
        
        ### apply, undo ###
        self.okW = QtGui.QPushButton('apply', self)
        self.undoW = QtGui.QPushButton('undo', self)
        
        ### initialise le ratio et l'image courante ###
        self.im_changed(False)
        if args:
            self.ratioW.setCurrentIndex(self.ratioIndex.index(args[2]))
            self.wW.setText(str(args[0]))
            self.hW.setText(str(args[1]))
        else:
            self.wW.setText(str(self.im.width()))
            self.hW.setText(str(self.im.height()))
        self.ratio_changed()
        
        ### connecte tout le bordel ###
        self.imW.activated.connect(self.im_changed)
        self.ratioW.activated.connect(self.ratio_changed)
        self.wW.textChanged.connect(self.maj)
        self.hW.textChanged.connect(self.maj)
        self.okW.clicked.connect(self.ok_clicked)
        self.undoW.clicked.connect(self.undo_clicked)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(3)
        grid.setColumnMinimumWidth(0, 50)
        grid.setColumnMinimumWidth(1, 50)
        grid.setColumnMinimumWidth(2, 100)
        grid.setColumnMinimumWidth(3, 100)

        grid.addWidget(self.imW, 0, 1)
        grid.addWidget(self.ratioW, 1, 1, 1, 3)
        
        grid.addWidget(self.wL, 3, 0)
        grid.addWidget(self.hL, 4, 0)
        
        grid.addWidget(self.wW, 3, 1)
        grid.addWidget(self.hW, 4, 1)
        
        grid.addWidget(self.oriL, 2, 2)
        grid.addWidget(self.oriWL, 3, 2)
        grid.addWidget(self.oriHL, 4, 2)
        
        grid.addWidget(self.newL, 2, 3)
        grid.addWidget(self.newWL, 3, 3)
        grid.addWidget(self.newHL, 4, 3)
        
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
        
    def im_changed(self, maj=True):
        if self.images:
            self.im.load(self.images[self.imW.currentIndex()])
            code = self.codeBefore.replace("$i", "self.im")
            exec(code)
            self.oriWL.setText("%s"%(self.im.width(),))
            self.oriHL.setText("%s"%(self.im.height(),))
            if maj:
                self.maj()
        
    def ratio_changed(self):
        ratio = str(self.ratioW.currentText())
        if ratio == "fit to width":
            self.hW.setDisabled(True)
            self.wW.setDisabled(False)
        elif ratio == "fit to height":
            self.hW.setDisabled(False)
            self.wW.setDisabled(True)
        else:
            self.hW.setDisabled(False)
            self.wW.setDisabled(False)
        self.maj()
            
    def maj(self):
        w = int(self.wW.text()) or 0
        h = int(self.hW.text()) or 0
        if self.images:
            oriW = int(self.im.width())
            oriH = int(self.im.height())
            ratio = str(self.ratioW.currentText())
            if ratio == "keep aspect ratio" and w > 0 and h > 0:
                oriRatio = oriW / oriH 
                newRatio = w / h
                if oriRatio >= newRatio:
                    h = int((oriH * w) / oriW)
                elif oriRatio < newRatio:
                    w = int((oriW * h) / oriH)
                    
            elif ratio == "keep aspect ratio by extending" and w > 0 and h > 0:
                oriRatio = oriW / oriH 
                newRatio = w / h
                if oriRatio <= newRatio:
                    h = int((oriH * w) / oriW)
                elif oriRatio > newRatio:
                    w = int((oriW * h) / oriH)
            elif ratio == "ignore aspect ratio" and w > 0 and h > 0:
                pass
            elif ratio == "fit to width" and w > 0:
                    h = int((oriH * w) / oriW)
            elif ratio == "fit to height" and h > 0:
                    w = int((oriW * h) / oriH)
            else:
                w = oriW
                h = oriH
        self.newWL.setText(str(w))
        self.newHL.setText(str(h))
    
    def ok_clicked(self):
        self.accept()
        
    def undo_clicked(self):
        self.reject()
        
    def get_return(self):
        if self.result():
            w = int(self.wW.text())
            h = int(self.hW.text())
            ratio = str(self.ratioW.currentText())
            transform = "QtCore.Qt.SmoothTransformation"
            
            if ratio == "keep aspect ratio" and w > 0 and h > 0:
                code = "$i = $i.scaled(%s, %s, QtCore.Qt.KeepAspectRatio, %s)" %(w, h, transform)
                desc = """keep aspect ratio
w = %spx
h = %spx""" %(w, h)
            elif ratio == "keep aspect ratio by extending" and w > 0 and h > 0:
                code = "$i = $i.scaled(%s, %s, QtCore.Qt.KeepAspectRatioByExpanding, %s)" %(w, h, transform)
                desc = """keep aspect ratio by extending
w = %spx
h = %spx""" %(w, h)
            elif ratio == "ignore aspect ratio" and w > 0 and h > 0:
                code = "$i = $i.scaled(%s, %s, QtCore.Qt.IgnoreAspectRatio, %s)" %(w, h, transform)
                desc = """ignore aspect ratio
w = %spx
h = %spx""" %(w, h)
            elif ratio == "fit to width" and w > 0:
                code = "$i = $i.scaledToWidth(%s, %s)" %(w, transform)
                desc = """fit to width
w = %spx""" %(w,)
            elif ratio == "fit to height" and h > 0:
                code = "$i = $i.scaledToHeight(%s, %s)" %(h, transform)
                desc = """fit to height
h = %spx""" %(h,)
            else:
                code = ""
                desc = ""
            args = (w, h, ratio)
            return True , code, desc, args
        else:
            return False, None, None, None
        
if __name__=="__main__":
    image = "media/donees/programation/imagemash/test/imgs/IMGP0333.JPG"
    app = QtGui.QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    win = ExecDialog()
    app.exec_()
