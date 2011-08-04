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

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt
import sys, os

from plugins.plugsubclass import Viewer
from plugins.plugsubclass import Painting

        
########################################################################
class PrevDialog(QtGui.QDialog):
    def __init__(self, images, code="", parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle("preview")
        self.codeBefore = code
        
        ### widget #####################################################
        ### image ###
        self.imW = QtGui.QComboBox(self)
        self.images = []
        for i, v in enumerate(images):
            f = os.path.split(v)[1]
            self.imW.addItem(f)
            self.images.append(v)

        ### zoom buttons ###
        self.zoomInW = QtGui.QToolButton()
        self.zoomInW.setAutoRaise(True)
        self.zoomInW.setIcon(QtGui.QIcon(
                             QtGui.QPixmap("icons/black_zoom_in.svg")))
        self.zoomOutW = QtGui.QToolButton()
        self.zoomOutW.setAutoRaise(True)
        self.zoomOutW.setIcon(QtGui.QIcon(
                              QtGui.QPixmap("icons/black_zoom_out.svg")))
        self.zoomOneW = QtGui.QToolButton()
        self.zoomOneW.setAutoRaise(True)
        self.zoomOneW.setIcon(QtGui.QIcon(
                              QtGui.QPixmap("icons/black_zoom_one.svg")))
        
        ### viewer ###
        self.painting = Painting(self)
        self.viewer = Viewer(self)
        self.viewer.setWidget(self.painting)
        
        ### apply, undo ###
        self.okW = QtGui.QPushButton('ok', self)
        
        ### function ###################################################
        self.im_changed(self.images[0])
        
        ### connexion ##################################################
        self.imW.activated[str].connect(self.im_changed)
        self.okW.clicked.connect(self.ok_clicked)
        
        self.zoomInW.clicked.connect(self.zoom_in)
        self.viewer.zoomIn.connect(self.zoom_in)
        self.zoomOutW.clicked.connect(self.zoom_out)
        self.viewer.zoomOut.connect(self.zoom_out)
        self.zoomOneW.clicked.connect(self.zoom_one)

        ### layout #####################################################
        toolBox = QtGui.QHBoxLayout()
        toolBox.setSpacing(2)
        toolBox.addWidget(self.imW)
        toolBox.addWidget(self.zoomInW)
        toolBox.addWidget(self.zoomOutW)
        toolBox.addWidget(self.zoomOneW)
        toolBox.addStretch(0)
        
        ### ok, undo ###
        okBox = QtGui.QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.okW)
        
        ### layout ###
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(2)
        layout.addLayout(toolBox)
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
                    
    def ok_clicked(self):
        self.accept()

if __name__=="__main__":
    image = "test/imgs/IMGP0333.JPG"
    app = QtGui.QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    win = PrevDialog([image])
    app.exec_()
