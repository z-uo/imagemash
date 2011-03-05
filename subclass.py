#!/usr/bin/env python
#-*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore

class Item(QtGui.QStandardItem):
    codeChanged = QtCore.pyqtSignal(str)
    descChanged = QtCore.pyqtSignal(str)
    argsChanged = QtCore.pyqtSignal(str)
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
        #self.codeChanged.emit(text)
    def getCode(self):
        return self.code
        
    def setDesc(self, text):
        self.desc = text
        #self.descChanged.emit(text)
    def getDesc(self):
        return self.desc
        
    def setArgs(self, text):
        self.args = text
        #self.argsChanged.emit(text)
    def getArgs(self):
        return self.args
        
class DragDropListWidget(QtGui.QListView):
    """ QListView acceptant un fichier en drop """
    dropped = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        QtGui.QListView.__init__(self, parent)
        self.setAcceptDrops(True)
        
        #self.dropped = QtCore.pyqtSignal()
        self.dropped.connect(self.test)
    def test(self):
        print "test reussi"
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
        
        self.codeEdit = QtGui.QTextEdit()
        self.codeEdit.setText(code)
        
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
