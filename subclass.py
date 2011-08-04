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
                l.append(url.toLocalFile())
            self.dropped.emit(l)
        else:
            event.ignore()
            


class TextEditDialog(QtGui.QDialog):
    def __init__(self, parent=None, code=""):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("edit code")
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


class ApplyDialog(QtGui.QDialog):
    def __init__(self, rep, fn, code, images, parent=None):
        super(ApplyDialog, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle(_("apply code"))
        self.quit = False
        self.fin = False
        
        ### progress bar
        self.barre = QtGui.QProgressBar(self)
        self.barre.setRange(0, len(images))
        self.barre.setValue(0)

        ### stop ###
        self.stopW = QtGui.QPushButton(_("stop"), self)
        self.stopW.clicked.connect(self.stopClicked)
        ### quit ###
        self.quitW = QtGui.QPushButton(_("quit"), self)
        self.quitW.clicked.connect(self.quitClicked)
        
        ### text edit ###
        self.errorW = QtGui.QTextEdit()
        self.errorW.setReadOnly(True)
        
        ### thread ###
        self.applyThread = Apply(rep, fn, code, images)
        self.applyThread.infoBatch.connect(self.infoBatch)
        self.applyThread.finBatch.connect(self.finBatch)
        self.applyThread.start()
        
        ### layout ###
        toolBox = QtGui.QHBoxLayout()
        toolBox.addStretch(0)
        toolBox.addWidget(self.stopW)
        toolBox.addWidget(self.quitW)
        vBox = QtGui.QVBoxLayout()
        vBox.addWidget(self.barre)
        vBox.addWidget(self.errorW)
        vBox.addLayout(toolBox)
        self.setLayout(vBox)
        self.exec_()
        
    def stopClicked(self):
        self.applyThread.stop = True
        self.stopW.setDisabled(True)
        
    def infoBatch(self, info):
        self.barre.setValue(info[0])
        self.errorW.setText(info[1])
        
    def finBatch(self, truc):
        if self.quit:
            self.applyThread.quit()
            self.accept()
        else:
            self.applyThread.quit()
            self.fin = True
            self.stopW.setDisabled(True)

    def quitClicked(self):
        if self.fin:
            self.applyThread.quit()
            self.accept()
        else:
            self.applyThread.stop = True
            self.quit = True
            
    def closeEvent(self, event):
        if self.fin:
            self.applyThread.quit()
            event.accept()
        else:
            self.applyThread.stop = True
            self.quit = True
            event.ignore()


class Apply(QtCore.QThread):
    """ TODO: pouvoir stopper le thread a n'importe quel moment proprement
    """
    infoBatch = QtCore.pyqtSignal(tuple)
    finBatch = QtCore.pyqtSignal(bool)
    def __init__(self, rep, fn, code, images, parent=None):
        super(Apply, self).__init__(parent)
        self.rep = rep
        self.fn = fn
        self.code = code.replace("$i", "im")
        self.images = images
        self.error = ""
        self.stop = False
        
    def run(self):
        if not os.path.isdir(self.rep):
            try:
                os.mkdir(self.rep)
            except:
                self.error = "%sle repertoire(%s) n'as pas pu etre créé\n" %(self.error, rep)
                self.infoBatch.emit((0, self.error))
                return
                
        n = 0   
        im = QtGui.QImage()
        for i in self.images:
            n = n + 1
            fn = return_new_filename(os.path.split(i)[1], self.fn, n)
            fn = os.path.join(self.rep, fn)
            # verifie que le fichier n'existe pas déja
            # a modifier pour permettre d'ecraser les fichiers
            if os.path.isfile(fn):
                self.error = "%sle fichier (%s) existe deja\n" %(self.error, fn)
                self.infoBatch.emit((n, self.error))
            else:
                ### ouverture de l'image ###
                if not self.stop:
                    if im.load(i):
                        pass
                    else:
                        self.error = "%simage illisible\n" %(self.error,)
                        self.infoBatch.emit((n-1, self.error))
                        continue
                else: break
                    
                ### execution du code ###
                if not self.stop:
                    try:
                        exec(self.code)
                    except:
                        self.error = "%scode incorrect\n" %(self.error,)
                        self.infoBatch.emit((n-1, self.error))
                        continue
                else: break
                
                ### enregistrement de l'image ###
                if not self.stop:
                    if im.save(fn):
                        self.error = "%s%s\n" %(self.error, i)
                        self.infoBatch.emit((n, self.error))
                    else:
                        self.error = "%sl'image ne peut pas etre enregistree\n" %(self.error,)
                        self.infoBatch.emit((n-1, self.error))
                else: break
        self.finBatch.emit(True)
