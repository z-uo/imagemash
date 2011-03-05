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

import os, sys
import imp
import re
import string
from PyQt4 import QtGui
from PyQt4 import QtCore

from subclass import *


### import des plugins #################################################
pluginpath = os.path.join(os.path.dirname(imp.find_module("mainwindow")[1]), "plugins/")
pluginfiles = [fname[:-3] for fname in os.listdir(pluginpath) if fname.endswith(".py") and fname.startswith("plugin_")]
if not pluginpath in sys.path:
    sys.path[:0] = [pluginpath]
imported_modules = []
for i in pluginfiles:
    imported_modules.append(__import__(i))
    exec("%s = sys.modules[i]"%(i,))

# TODO: gerer l'encodage des noms de fichiers



class ImgTab(QtGui.QWidget):
    """ Classe ou sont gérées les images à traiter
        peut prendre une liste d'url en argument """
    def __init__(self, parent=None, images=[]):
        QtGui.QWidget.__init__(self, parent)
        self.title = "images"
        
        ### modele ou sont enregistré les images ###
        self.modImgList = QtGui.QStandardItemModel(0,1)
        
        ### listview ou sont affichées les images ###
        self.imgList = DragDropListWidget()
        self.imgList.setModel(self.modImgList)
        self.imgList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.imgList.selectionModel().selectionChanged.connect(self.insert_miniature)
        self.imgList.dropped.connect(self.insert_image)
        self.insert_image(images)

        ### Apercu d'une image ###
        self.dicoImg = {}
        self.apercu = QtGui.QLabel()
        
        ### ajout et supression d'images ###
        self.imgAdd = QtGui.QPushButton("add")
        self.imgAdd.clicked.connect(self.add_image)
        self.imgRemove = QtGui.QPushButton("remove")
        self.imgRemove.clicked.connect(self.remove_image)
        self.checkApercu = QtGui.QCheckBox("apercu")
        self.checkApercu.clicked.connect(self.check_apercu)
        self.insert_miniature()
        
        ### layout ###
        self.imgBox = QtGui.QHBoxLayout()
        self.imgBox.addWidget(self.imgList)
        self.imgBox.addWidget(self.apercu)
        self.toolBox = QtGui.QHBoxLayout()
        self.toolBox.addWidget(self.imgAdd)
        self.toolBox.addWidget(self.imgRemove)
        self.toolBox.addWidget(self.checkApercu)
        self.toolBox.addStretch(0)
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addLayout(self.imgBox)
        self.layout.addLayout(self.toolBox)
    
    def add_image(self):
        """ boite de dialogue d'ajout d'images """
        url = QtGui.QFileDialog.getOpenFileNames(self, 
                "Ajouter des images", "", 
                "Images (*.png *.jpeg *.jpg *.gif *.tiff *.tif *.PNG *.JPEG *.JPG *.GIF *.TIFF *.TIF);;Tous les fichiers (*)")
        self.insert_image(url)
            
    def insert_image(self, url=[]):
        """ ajoute une image au modele """
        li = []
        for i in url:
            li.append(unicode(str(i)))
        img = self.verif_images(li)
        for i in img:
            self.modImgList.appendRow(Item(i))
        
    def remove_image(self):
        """ suprimme les images selectionnées du modele 
            ainsi que les miniatures enregistrées """
        sel = self.imgList.selectionModel().selectedIndexes()
        for i in sel:
            if self.dicoImg.has_key(i.data().toString()):
                del self.dicoImg[i.data().toString()]
            self.modImgList.removeRow(i.row())
    
    def check_apercu(self):
        if self.checkApercu.isChecked():
            self.insert_miniature()
        else:
            self.apercu.clear()
             
    def create_thumbnail(self, chemin="alpha"):
        """ renvoi ou cré une miniature de l'image
            les miniatures sont enregistrées dans self.dicoImg """
        if self.dicoImg.has_key(chemin):
            return self.dicoImg[chemin]
        else:
            if chemin == "alpha":
                img = QtGui.QPixmap(200,200)
                img.fill(QtGui.QColor(0,0,0,0))
            else:
                img = QtGui.QPixmap(chemin).scaledToWidth(200)
            self.dicoImg[chemin] = img
            return img
            
    def insert_miniature(self):
        """ insere la premiere image sélectionnée en miniature """
        if self.checkApercu.isChecked():
            sel = self.imgList.selectionModel().selectedIndexes()
            if sel:
                img = sel[0].data().toString()
                self.apercu.setPixmap(self.create_thumbnail(img))
            else:
                self.apercu.setPixmap(self.create_thumbnail("alpha"))
    
    def verif_images(self, li):
        """ verifie que le chemin existe et que le fichier est une image """
        images = []
        for i in li:
            ext = os.path.splitext(i) [1]
            if (os.path.isfile(i) and 
               (ext == ".png" or ext == ".PNG" or 
                ext == ".gif" or ext == ".GIF" or 
                ext == ".jpg" or ext == ".JPG" or 
                ext == ".jpeg" or ext == ".JPEG" or
                ext == ".tif" or ext == ".TIF" or
                ext == ".tiff" or ext == ".TIFF" )):
                images.append(i)  
        images.sort()
        return images
    
    def return_imgs(self):
        """ renvoi la liste des images"""
        nb = self.modImgList.rowCount()
        images = []
        for i in range(nb):
            images.append(str(self.modImgList.item(i).text()))
        return images
            
    
class ActionTab(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.title = "action"
        
        ### action disponibles ###
        self.actionAvailableListLabel = QtGui.QLabel("actions disponibles")
        self.modActionAvailableList = QtGui.QStandardItemModel(0,1)
        self.import_plugins()
        
        self.actionAvailableList = QtGui.QListView()
        self.actionAvailableList.setModel(self.modActionAvailableList)
        self.actionAvailableList.doubleClicked.connect(self.add_action)
        
        ### ajout et supression d'actions ###
        self.actionAdd = QtGui.QPushButton("add")
        self.actionAdd.clicked.connect(self.add_action)
        self.actionRemove = QtGui.QPushButton("remove")
        self.actionRemove.clicked.connect(self.remove_action)
        
        ### action ###
        self.actionListLabel = QtGui.QLabel("actions")
        self.modActionList = QtGui.QStandardItemModel(0,1)
        self.actionList = QtGui.QListView()
        self.actionList.setModel(self.modActionList)
        self.actionList.selectionModel().selectionChanged.connect(self.selAction)
        self.actionList.doubleClicked.connect(self.edit_action)
        
        ### description action ###
        self.labelDesc = QtGui.QLabel("description:                 ")
        self.labelPluginDesc = QtGui.QLabel("")
        self.labelActionDesc = QtGui.QLabel("")
        
        ### layout ###
        self.toolBox = QtGui.QVBoxLayout()
        self.toolBox.addWidget(self.actionAdd)
        self.toolBox.addWidget(self.actionRemove)
        self.toolBox.addStretch(0)
        self.descBox = QtGui.QVBoxLayout()
        self.descBox.addWidget(self.labelDesc)
        self.descBox.addWidget(self.labelPluginDesc)
        self.descBox.addWidget(self.labelActionDesc)
        self.descBox.addStretch(0)
        self.layout = QtGui.QGridLayout(self)
        self.layout.addWidget(self.actionAvailableListLabel, 1, 1)
        self.layout.addWidget(self.actionAvailableList, 2, 1)
        self.layout.addLayout(self.toolBox, 2, 2)
        self.layout.addWidget(self.actionListLabel, 1, 3)
        self.layout.addWidget(self.actionList, 2, 3)
        self.layout.addLayout(self.descBox, 2, 4)
            
    def import_plugins(self):
        for i in imported_modules:
            info = {"name": i.NAME,
                    "modname": i.MOD_NAME,
                    "description": i.DESCRIPTION,
                    "author": i.AUTHOR,
                    "version": i.VERSION,
                    "exec": i.EXEC_CLASS}
            self.modActionAvailableList.appendRow(Item(i.NAME, info)) 
        
    def add_action(self):
        sel = self.actionAvailableList.selectionModel().selectedIndexes()[0]
        name = sel.data().toString()
        if sel:
            item = self.modActionAvailableList.itemFromIndex(sel)
            info = item.info
            test = Item(name, info)
            self.modActionList.appendRow(test)
            
    def remove_action(self):
        sel = self.actionList.selectionModel().selectedIndexes()
        for i in sel:
            self.modActionList.removeRow(i.row())
            
    def selAction(self):
        sel = self.actionList.selectionModel().selectedIndexes()[0]
        item = self.modActionList.itemFromIndex(sel)
        self.labelPluginDesc.setText(item.info["description"])
        if item.getDesc():
            self.labelActionDesc.setText(item.getDesc())
        else:
            self.labelActionDesc.setText("")
        self.return_code_before_sel()
        
    def edit_action(self, text):
        sel = self.actionList.selectionModel().selectedIndexes()[0]
        item = self.modActionList.itemFromIndex(sel)
        exec("ok, code, desc, args = %s.%s(self.parent.imgTab.return_imgs(), item.getArgs(), self.return_code_before_sel(), self).getReturn()" 
                                     %(item.info["modname"], item.info["exec"]))
        if ok:
            item.setCode(code)
            item.setDesc(desc)
            item.setArgs(args)
        self.selAction()
        
    def return_code(self):
        nb = self.modActionList.rowCount()
        code = ""
        for i in range(nb):
            code = """%s
%s"""%(code, self.modActionList.item(i).getCode())
        print code
        return code
        
    def return_code_before_sel(self):
        # item selected
        sel = self.actionList.selectionModel().selectedIndexes()[0]
        item = self.modActionList.itemFromIndex(sel)
        # QModelIndex.row
        row = self.modActionList.indexFromItem(item).row()
        code = ""
        for i in range(row):
            print i
            code = """%s
%s"""%(code, self.modActionList.item(i).getCode())
        print code
        return code
        
        
class SaveTab(QtGui.QWidget):
    def __init__(self, parent=None, dossier=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.title = "save"
        
        # nouveau dossier
        self.dossier = dossier
        self.dossierLabel = QtGui.QLabel('nouveau dossier')
        #text edit
        self.dossierEdit = QtGui.QLineEdit(self)
        self.dossierEdit.setText(self.dossier)
        self.dossierEdit.textChanged[str].connect(self.dir_changed)
        #self.connect(self.edit_nd, QtCore.SIGNAL('textChanged(QString)'), self.onChanged)
        self.dossierChooser = QtGui.QPushButton("choose")
        self.dossierChooser.clicked.connect(self.change_dir)

        #nom de fichier
        self.filename = "%F%E"
        self.filenameLabel = QtGui.QLabel('nom des fichiers')
        #text edit
        self.filenameEdit = QtGui.QLineEdit(self)
        self.filenameEdit.setText("%F%E")
        self.filenameEdit.textChanged[str].connect(self.filename_changed)
        #self.connect(self.edit_fn, QtCore.SIGNAL('textChanged(QString)'), self.onChanged)
        # label nom de fichier
        self.oriFilename = QtGui.QLabel()
        self.newFilename = QtGui.QLabel()
        self.filename_changed()
        
        ### doc ###
        self.doc = """%F: nom du fichier original
%E: extention originale
%I: incrementation (10 chiffres)"""
        self.docLabel = QtGui.QLabel(self.doc)
        
        ### code ###
        self.codeEditButton = QtGui.QPushButton("code")
        self.codeEditButton.clicked.connect(self.edit_code)

        ### appliquer ###
        self.okW = QtGui.QPushButton("appliquer", self)
        self.okW.clicked.connect(self.ok_clicked)

        ### annuler ###
        self.undoW = QtGui.QPushButton("fermer", self)
        self.undoW.clicked.connect(self.undo_clicked)
        
        ### layout ###
        self.fileGrid = QtGui.QGridLayout()
        self.fileGrid.addWidget(self.dossierLabel,0, 0)
        self.fileGrid.addWidget(self.dossierEdit, 0, 1, 1, 2)
        self.fileGrid.addWidget(self.dossierChooser, 0, 3)
        self.fileGrid.addWidget(self.filenameLabel, 2, 0)
        self.fileGrid.addWidget(self.filenameEdit, 2, 1)
        self.fileGrid.addWidget(self.oriFilename, 1, 2)
        self.fileGrid.addWidget(self.newFilename, 2, 2)
        self.fileGrid.addWidget(self.docLabel, 3, 1)
        self.fileGrid.addWidget(self.codeEditButton, 4, 0)
        
        self.okBox = QtGui.QHBoxLayout()
        self.okBox.addStretch(0)
        self.okBox.addWidget(self.okW)
        self.okBox.addWidget(self.undoW)
        
        self.layout = QtGui.QVBoxLayout(self)
        #~ self.layout.addLayout(self.dirBox)
        self.layout.addLayout(self.fileGrid)
        self.layout.addStretch(0)
        self.layout.addLayout(self.okBox)
        #self.setLayout(self.layout)
    def dir_changed(self):
        self.dossier = self.dossierEdit.text()
    def change_dir(self):
        """ boite de dialogue changement dossier enregistrement """
        url = QtGui.QFileDialog.getExistingDirectory(self, "Choisir le dossier sauvegarde", self.dossier)
        if url:
            self.dossierEdit.setText(self.dossier)
            
    def filename_changed(self):
        orifn = os.path.split(self.parent.imgList[1]) [ 1 ]
        fn = str(self.filenameEdit.text())
        fn = self.return_new_filename(orifn, fn)
        self.oriFilename.setText(orifn)
        self.newFilename.setText(fn)
        
    def return_new_filename(self, orifn, fn, incr=1):
        base = os.path.splitext(orifn) [ 0 ]
        ext = os.path.splitext(orifn) [ 1 ]
        fn = fn.replace('%F', base)
        fn = fn.replace('%E', ext)
        rechaine = ''
        for i in xrange(1, 10):
            pattern = '%I{' + str(i) + '}'
            if re.search(pattern, fn):
                nbincr = i
                rechaine = '%'
        if rechaine:
            for i in range(nbincr):
                rechaine = rechaine + 'I'
            fn = fn.replace(rechaine, string.zfill(incr, nbincr))
        return fn
        
    def edit_code(self):
        ok, self.parent.codeStr = TextEditDialog(self, self.parent.codeStr).getReturn()
        print self.parent.codeStr

    def ok_clicked(self):
        rep = str(self.dossier)
        if not os.path.isdir(rep):
            os.mkdir(rep)
        images = self.parent.imgList
        print images
        n = 0
        for i in images:
            n = n+1
            fn = self.return_new_filename(os.path.split(i)[1], str(self.filenameEdit.text()), n)
            fn = os.path.join(rep, fn)
            print fn
            im = QtGui.QImage()
            im.load(i)
            code = self.parent.codeStr.replace("$i", "im")
            exec code
            ok = im.save(fn)
            print ok
        
    def undo_clicked(self):
        self.parent.reject()
        
class MainDialog(QtGui.QDialog):
    def __init__(self, images, dossier, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.imgList = images
        self.codeList = ""
        
        self.imgTab = ImgTab(self, images)
        self.actionTab = ActionTab(self)
        self.saveTab = SaveTab(self, dossier)
        
        self.tab = QtGui.QTabWidget()
        self.tab.addTab(self.imgTab, self.imgTab.title)
        self.tab.addTab(self.actionTab, self.actionTab.title)
        self.tab.addTab(self.saveTab, self.saveTab.title)
        self.tab.currentChanged[int].connect(self.tab_changed)
        self.vBox = QtGui.QVBoxLayout()
        self.vBox.addWidget(self.tab)
        self.setLayout(self.vBox)
        self.show()
        
    def tab_changed(self, tab):
        if tab == 0:
            print "image tab"
        if tab == 1:
            print "action tab"
            self.imgList = self.imgTab.return_imgs()
        if tab == 2:
            print "save tab"
            self.imgList = self.imgTab.return_imgs()
            self.codeStr = self.actionTab.return_code()
        

if __name__=="__main__":
    if len(sys.argv) == 1:
        sys.argv.append("/home/pops/prog/img")
    fichiers = []
    if os.path.isdir(sys.argv[1]):
        for i in os.listdir(sys.argv[1]):
            fichiers.append(os.path.join(sys.argv[1], i))
        dossier = sys.argv[1]
    else:
        for i in sys.argv[1:]:
            if os.path.isfile(i):
                fichiers.append(i)
        dossier = os.path.dirname(sys.argv[1])
    app = QtGui.QApplication(sys.argv)
    win=MainDialog(fichiers, dossier)
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
                app, QtCore.SLOT("quit()"))
    app.exec_()
            
