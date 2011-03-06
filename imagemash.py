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


class ImgTab(QtGui.QWidget):
    """ Classe ou sont gérées les images à traiter
        peut prendre une liste d'url en argument """
    def __init__(self, parent=None, images=[]):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.title = "images"
        
        ### modele ou sont enregistré les images ###
        self.modImgList = QtGui.QStandardItemModel(0,1)
        self.add_images(images)
        
        ### listview ou sont affichées les images ###
        self.imgList = DragDropListWidget()
        self.imgList.setModel(self.modImgList)
        self.imgList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.imgList.selectionModel().selectionChanged.connect(self.insert_thumbnail)
        self.imgList.dropped.connect(self.add_images)

        ### Apercu d'une image ###
        self.dicoImg = {}
        self.apercu = QtGui.QLabel()
        self.checkApercu = QtGui.QCheckBox("apercu")
        self.checkApercu.clicked.connect(self.check_apercu)
        self.insert_thumbnail()
        
        ### ajout et supression d'images ###
        self.imgAdd = QtGui.QPushButton("add")
        self.imgAdd.clicked.connect(self.add_images_clicked)
        self.imgRemove = QtGui.QPushButton("remove")
        self.imgRemove.clicked.connect(self.remove_images_clicked)
        
        ### layout ###
        imgBox = QtGui.QHBoxLayout()
        imgBox.addWidget(self.imgList)
        imgBox.addWidget(self.apercu)
        toolBox = QtGui.QHBoxLayout()
        toolBox.addWidget(self.imgAdd)
        toolBox.addWidget(self.imgRemove)
        toolBox.addWidget(self.checkApercu)
        toolBox.addStretch(0)
        layout = QtGui.QVBoxLayout(self)
        layout.addLayout(imgBox)
        layout.addLayout(toolBox)
    
    def add_images_clicked(self):
        """ boite de dialogue d'ajout d'images """
        url = QtGui.QFileDialog.getOpenFileNames(self, 
                "Ajouter des images", "", 
                "Images (*.png *.jpeg *.jpg *.gif *.tiff *.tif *.PNG *.JPEG *.JPG *.GIF *.TIFF *.TIF);;Tous les fichiers (*)")
        self.add_images(url)
            
    def remove_images_clicked(self):
        """ suprimme les images selectionnées du modele 
            ainsi que les miniatures enregistrées """
        sel = self.imgList.selectionModel().selectedIndexes()
        for i in sel:
            self.delete_thumbnail(i.data().toString())
            self.modImgList.removeRow(i.row())
            
    def add_images(self, url=[]):
        """ ajoute une image au modele """
        li = []
        for i in url:
            li.append(unicode(str(i)))
        img = self.verif_images(li)
        for i in img:
            self.modImgList.appendRow(Item(i))
        
    def verif_images(self, url):
        """ verifie que le chemin existe et que le fichier est une image """
        images = []
        for i in url:
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
        
    def check_apercu(self):
        if self.checkApercu.isChecked():
            self.insert_thumbnail()
        else:
            self.apercu.clear()
             
    def insert_thumbnail(self):
        """ insere la premiere image sélectionnée en miniature """
        if self.checkApercu.isChecked():
            sel = self.imgList.selectionModel().selectedIndexes()
            if sel:
                img = sel[0].data().toString()
                self.apercu.setPixmap(self.create_thumbnail(img))
            else:
                self.apercu.setPixmap(self.create_thumbnail("alpha"))
                
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
            
    def delete_thumbnail(self, image):
        """ suprime la miniature de l'image du dictionnaire """
        if self.dicoImg.has_key(image):
            del self.dicoImg[image]
            

class ActionTab(QtGui.QWidget):
    """ classe ou sont géré les action """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.title = "action"
        self.imgs = self.parent.imgTab.return_imgs()
        
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
        self.actionList.selectionModel().selectionChanged.connect(self.sel_action)
        self.actionList.doubleClicked.connect(self.edit_action)
        
        ### description action ###
        self.labelDesc = QtGui.QLabel("description:                 ")
        self.labelPluginDesc = QtGui.QLabel("")
        self.labelActionDesc = QtGui.QLabel("")
        
        ### layout ###
        toolBox = QtGui.QVBoxLayout()
        toolBox.addWidget(self.actionAdd)
        toolBox.addWidget(self.actionRemove)
        toolBox.addStretch(0)
        descBox = QtGui.QVBoxLayout()
        descBox.addWidget(self.labelDesc)
        descBox.addWidget(self.labelPluginDesc)
        descBox.addWidget(self.labelActionDesc)
        descBox.addStretch(0)
        layout = QtGui.QGridLayout(self)
        layout.addWidget(self.actionAvailableListLabel, 1, 1)
        layout.addWidget(self.actionAvailableList, 2, 1)
        layout.addLayout(toolBox, 2, 2)
        layout.addWidget(self.actionListLabel, 1, 3)
        layout.addWidget(self.actionList, 2, 3)
        layout.addLayout(descBox, 2, 4)
            
    def import_plugins(self):
        """ insere les plugin importé au lancement de l'aplication 
            dans la liste des action disponibles"""
        for i in importedModules:
            info = {"name": i.NAME,
                    "modname": i.MOD_NAME,
                    "description": i.DESCRIPTION,
                    "author": i.AUTHOR,
                    "version": i.VERSION,
                    "exec": i.EXEC_CLASS}
            self.modActionAvailableList.appendRow(Item(i.NAME, info)) 
        
    def add_action(self):
        """ ajoute une action dans la liste des action a effectuer sur les images """
        sel = self.actionAvailableList.selectionModel().selectedIndexes()[0]
        if sel:
            item = self.modActionAvailableList.itemFromIndex(sel)
            nItem = Item(sel.data().toString(), item.info)
            self.modActionList.appendRow(nItem)
            
    def remove_action(self):
        """ suprime une action de la liste des action a effectuer sur les images """
        sel = self.actionList.selectionModel().selectedIndexes()
        for i in sel:
            self.modActionList.removeRow(i.row())
            
    def sel_action(self):
        """ affiche la description de l'action selectionnée """
        sel = self.actionList.selectionModel().selectedIndexes()[0]
        item = self.modActionList.itemFromIndex(sel)
        self.labelPluginDesc.setText(item.info["description"])
        if item.getDesc():
            self.labelActionDesc.setText(item.getDesc())
        else:
            self.labelActionDesc.setText("")
        
    def edit_action(self, text):
        """ lance le plugin selectionné
            et enregistre le retour"""
        sel = self.actionList.selectionModel().selectedIndexes()[0]
        item = self.modActionList.itemFromIndex(sel)
        exec("ok, code, desc, args = %s.%s(self.parent.imgTab.return_imgs(), item.getArgs(), self.return_code(True), self).get_return()" 
                                     %(item.info["modname"], item.info["exec"]))
        if ok:
            item.setCode(code)
            item.setDesc(desc)
            item.setArgs(args)
        self.sel_action()
        
    def return_code(self, beforeSel=False):
        """ retourne le code des actions
            tout le code si beforeSel==False
            ou le code avant l'element selectionné si beforeSel==True"""
        if beforeSel:
            sel = self.actionList.selectionModel().selectedIndexes()[0]
            item = self.modActionList.itemFromIndex(sel)
            nb = self.modActionList.indexFromItem(item).row()
        else:
            nb = self.modActionList.rowCount()
        code = ""
        for i in range(nb):
            code = """%s
%s"""%(code, self.modActionList.item(i).getCode())
        return code
        
        
class SaveTab(QtGui.QWidget):
    """classe ou est gérée l'enregistrement des images"""
    def __init__(self, parent=None, dossier=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.title = "save"
        self.imgs = self.parent.imgTab.return_imgs()
        self.code = self.parent.actionTab.return_code()
        
        ### dossier d'enregistrement ###
        self.dossier = dossier
        self.dossierLabel = QtGui.QLabel('nouveau dossier')
        self.dossierEdit = QtGui.QLineEdit(self)
        self.dossierEdit.setText(self.dossier)
        self.dossierEdit.textChanged[str].connect(self.dir_changed)
        self.dossierChooser = QtGui.QPushButton("choose")
        self.dossierChooser.clicked.connect(self.change_dir)

        ### nom de fichier ###
        self.oriFn = os.path.split(self.imgs[1]) [1]
        self.filenameLabel = QtGui.QLabel('nom des fichiers')
        self.filenameEdit = QtGui.QLineEdit(self)
        self.filenameEdit.setText("%F%E")
        self.filenameEdit.textChanged[str].connect(self.filename_changed)
        self.oriFilename = QtGui.QLabel(self.oriFn)
        self.newFilename = QtGui.QLabel(self.oriFn)
        
        ### doc nom de fichier ###
        self.doc = """%F: nom du fichier original
%E: extention originale
%I: incrementation (10 chiffres)"""
        self.docLabel = QtGui.QLabel(self.doc)
        
        ### code ###
        self.codeEditButton = QtGui.QPushButton("code")
        self.codeEditButton.clicked.connect(self.edit_code)

        ### appliquer ###
        self.applyW = QtGui.QPushButton("appliquer")
        self.applyW.clicked.connect(self.apply_clicked)

        ### info ###
        self.infoLabel = QtGui.QLabel("")
        
        ### layout ###
        fileGrid = QtGui.QGridLayout()
        fileGrid.addWidget(self.dossierLabel,0, 0)
        fileGrid.addWidget(self.dossierEdit, 0, 1, 1, 2)
        fileGrid.addWidget(self.dossierChooser, 0, 3)
        fileGrid.addWidget(self.filenameLabel, 2, 0)
        fileGrid.addWidget(self.filenameEdit, 2, 1)
        fileGrid.addWidget(self.oriFilename, 1, 2)
        fileGrid.addWidget(self.newFilename, 2, 2)
        fileGrid.addWidget(self.docLabel, 3, 1)
        fileGrid.addWidget(self.codeEditButton, 4, 0)
        
        okBox = QtGui.QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.infoLabel)
        okBox.addWidget(self.applyW)
        
        layout = QtGui.QVBoxLayout(self)
        layout.addLayout(fileGrid)
        layout.addStretch(0)
        layout.addLayout(okBox)
        
    def dir_changed(self):
        """ modification du dossier d'enregistrement """
        self.dossier = self.dossierEdit.text()
    def change_dir(self):
        """ boite de dialogue changement dossier enregistrement """
        url = QtGui.QFileDialog.getExistingDirectory(self, "Choisir le dossier de sauvegarde", self.dossier)
        if url:
            self.dossierEdit.setText(url)
            
    def filename_changed(self):
        """ change le label du nom de fichier en fonction des modifications """
        fn = str(self.filenameEdit.text())
        fn = self.return_new_filename(self.oriFn, fn)
        self.newFilename.setText(fn)
        
    def return_new_filename(self, orifn, fn, incr=1):
        """ renvoi les nom de fichier
            remplace %F par le nom de base du fichier original
            remplace %E par l'extention du fichier original
            remplace %III par une incrémentation """
        base = os.path.splitext(orifn) [0]
        ext = os.path.splitext(orifn) [1]
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
        """ ouvre une boite de dialogue pour voir et éditer
            le code qui sera appliqué aux images """
        ok, self.code = TextEditDialog(self, self.code).getReturn()

    def apply_clicked(self):
        """ applique le tout """
        rep = str(self.dossier)
        if not os.path.isdir(rep):
            os.mkdir(rep)
        images = self.imgs
        print images
        n = 0
        for i in images:
            self.infoLabel.setText(i)
            n = n+1
            fn = self.return_new_filename(os.path.split(i)[1], str(self.filenameEdit.text()), n)
            fn = os.path.join(rep, fn)
            print fn
            im = QtGui.QImage()
            im.load(i)
            code = self.code.replace("$i", "im")
            exec code
            ok = im.save(fn)
            print ok
        self.infoLabel.setText("toutes les images ont été traitées ou pas")
        
class MainDialog(QtGui.QDialog):
    """ fenetre principale de l'application """
    def __init__(self, images, dossier, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.imgTab = ImgTab(self, images)
        self.actionTab = ActionTab(self)
        self.saveTab = SaveTab(self, dossier)
        
        self.tab = QtGui.QTabWidget()
        self.tab.addTab(self.imgTab, self.imgTab.title)
        self.tab.addTab(self.actionTab, self.actionTab.title)
        self.tab.addTab(self.saveTab, self.saveTab.title)
        self.tab.currentChanged[int].connect(self.tab_changed)
        
        vBox = QtGui.QVBoxLayout()
        vBox.addWidget(self.tab)
        self.setLayout(vBox)
        self.show()
        
    def tab_changed(self, tab):
        """ envoi des données au onglets au moment de leur ouverture """
        if tab == 1:
            self.actionTab.imgs = self.imgTab.return_imgs()
        elif tab == 2:
            self.saveTab.imgs = self.imgTab.return_imgs()
            self.saveTab.code = self.actionTab.return_code()
        

if __name__=="__main__":
    ### import des images ##############################################
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
    
    ### import des plugins #############################################
    pluginPath = os.path.join(os.path.dirname(imp.find_module("imagemash")[1]), "plugins/")
    pluginFiles = [fname[:-3] for fname in os.listdir(pluginPath) if fname.endswith(".py") and fname.startswith("plugin_")]
    if not pluginPath in sys.path:
        sys.path[:0] = [pluginPath]
    importedModules = []
    for i in pluginFiles:
        importedModules.append(__import__(i))
        exec("%s = sys.modules[i]"%(i,))
    
    ### demarage de l'interface ########################################
    app = QtGui.QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    win = MainDialog(fichiers, dossier)
    app.exec_()
            
