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

class Item(QtGui.QStandardItem):
    def __init__(self, parent=None, copy=False):
        QtGui.QStandardItem.__init__(self, parent)
        self.setEditable(False)
        self.code = None
        self.desc = None
        self.args = None
        if copy:
            self.info = copy
        
    def setCode(self, text):
        self.code = text
    def getCode(self):
        return self.code
        
    def setDesc(self, text):
        self.desc = text
    def getDesc(self):
        return self.desc
        
    def setArgs(self, text):
        self.args = text
    def getArgs(self):
        return self.args
        
class DragDropListWidget(QtGui.QListView):
    """ QListView acceptant un fichier en drop """
    dropped = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        QtGui.QListView.__init__(self, parent)
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()
 
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
 
    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            l = []
            for url in event.mimeData().urls():
                l.append(unicode(url.toLocalFile()))
            self.dropped.emit(l)
        else:
            event.ignore()
            


class TextEditDialog(QtGui.QDialog):
    def __init__(self, parent=None, code=""):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        
        ### editeur de code ###
        self.codeEdit = QtGui.QTextEdit()
        self.codeEdit.setText(code)
        
        ### infos ###
        self.info = QtGui.QLabel("$i: QImage")
        ### appliquer ###
        self.okW = QtGui.QPushButton('appliquer', self)
        self.okW.clicked.connect(self.okClicked)
        ### annuler ###
        self.undoW = QtGui.QPushButton('annuler', self)
        self.undoW.clicked.connect(self.undoClicked)
        
        hBox = QtGui.QHBoxLayout()
        hBox.addWidget(self.okW)
        hBox.addWidget(self.undoW)
        
        vBox = QtGui.QVBoxLayout()
        vBox.addWidget(self.codeEdit)
        vBox.addWidget(self.info)
        vBox.addLayout(hBox)
        
        self.setLayout(vBox)
        self.exec_()
        
    def getReturn(self):
        if self.result():
            return True, str(self.codeEdit.toPlainText())
        else:
            return False, None
            
    def okClicked(self):
        self.accept()
    def undoClicked(self):
        self.reject()
