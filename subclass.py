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

import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from funct import return_new_filename

class Item(QtGui.QStandardItem):
    """ a QStandartItem that can contain:
        a piece of code, a description, and argument
        it is used to store the action to apply on images """
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
    """ QListView supporting a file drop """
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
    """ dialog with a text editor """
    def __init__(self, parent=None, code=""):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("edit code")
        self.parent = parent

        ### code edit ###
        self.codeEdit = QtGui.QTextEdit()
        self.codeEdit.setText(code)

        ### infos ###
        self.info = QtGui.QLabel("$i: QImage")
        ### apply ###
        self.okW = QtGui.QPushButton('apply', self)
        self.okW.clicked.connect(self.okClicked)
        ### annuler ###
        self.undoW = QtGui.QPushButton('undo', self)
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
    """ dialog with info and a progress bar
        used while applying the code on images"""
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
        self.applyThread.endBatch.connect(self.endBatch)
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

    def endBatch(self, truc):
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
    """ thread used to apply the code on images
    """
    infoBatch = QtCore.pyqtSignal(tuple)
    endBatch = QtCore.pyqtSignal(bool)
    def __init__(self, rep, fn, code, images, parent=None):
        super(Apply, self).__init__(parent)
        self.rep = rep
        self.fn = fn
        self.code = code.replace("$i", "self.im")
        self.images = images
        self.error = ""
        self.stop = False

    def run(self):
        if not os.path.isdir(self.rep):
            ### create folder ###
            try:
                os.mkdir(self.rep)
            except:
                self.error = "%sthe directory (% s) can not be created\n" %(self.error, self.rep)
                self.infoBatch.emit((0, self.error))
                return

        n = 0
        self.im = QtGui.QImage()
        for i in self.images:
            n = n + 1
            fn = return_new_filename(os.path.split(i)[1], self.fn, n)
            fn = os.path.join(self.rep, fn)
            # verifies that the file does not exist
            # to change to allow overwriting files
            if os.path.isfile(fn):
                self.error = "%sthe file (%s) already exists\n" %(self.error, fn)
                self.infoBatch.emit((n, self.error))
            else:
                ### open ###
                if not self.stop:
                    if self.im.load(i):
                        pass
                    else:
                        self.error = "%simage unreadable\n" %(self.error,)
                        self.infoBatch.emit((n-1, self.error))
                        continue
                else: break

                ### code ###
                if not self.stop:
                    try:
                        exec(self.code)
                    except:
                        self.error = "%sincorrect code\n" %(self.error,)
                        self.infoBatch.emit((n-1, self.error))
                        continue
                else: break

                ### save ###
                if not self.stop:
                    if self.im.save(fn):
                        self.error = "%s%s\n" %(self.error, i)
                        self.infoBatch.emit((n, self.error))
                    else:
                        self.error = "%sthe image can not be saved\n" %(self.error,)
                        self.infoBatch.emit((n-1, self.error))
                else: break
        self.endBatch.emit(True)
