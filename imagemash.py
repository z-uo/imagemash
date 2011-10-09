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
import imp
import gettext
from PyQt4 import QtGui
from PyQt4 import QtCore

from subclass import Item
from subclass import DragDropListWidget
from subclass import TextEditDialog
from subclass import ApplyDialog
from preview import PrevDialog
from funct import verif_images
from funct import return_new_filename


class ImgTab(QtGui.QWidget):
    """ manages the images to be processed
        can take a list of url as argument """
    def __init__(self, parent=None, images=[]):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.title = _("images")

        ### model to store images ###
        self.modImgList = QtGui.QStandardItemModel(0, 1)
        self.add_images(images)

        ### listview to display images ###
        self.imgList = DragDropListWidget()
        self.imgList.setModel(self.modImgList)
        self.imgList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.imgList.selectionModel().selectionChanged.connect(self.insert_thumbnail)
        self.imgList.dropped.connect(self.add_images)

        ### preview thumbnail are stored in a dic ###
        self.thumbnailDic = {}
        self.previewW = QtGui.QLabel()
        self.checkPreviewW = QtGui.QCheckBox(_("preview"))
        self.checkPreviewW.clicked.connect(self.check_preview)
        self.insert_thumbnail()

        ### adding and deleting images ###
        self.imgAdd = QtGui.QPushButton(_("add"))
        self.imgAdd.clicked.connect(self.add_images_clicked)
        self.imgRemove = QtGui.QPushButton(_("remove"))
        self.imgRemove.clicked.connect(self.remove_images_clicked)

        ### layout ###
        imgBox = QtGui.QHBoxLayout()
        imgBox.addWidget(self.imgList)
        imgBox.addWidget(self.previewW)
        toolBox = QtGui.QHBoxLayout()
        toolBox.addWidget(self.imgAdd)
        toolBox.addWidget(self.imgRemove)
        toolBox.addWidget(self.checkPreviewW)
        toolBox.addStretch(0)
        layout = QtGui.QVBoxLayout(self)
        layout.addLayout(imgBox)
        layout.addLayout(toolBox)

    def add_images_clicked(self):
        """ dialog for adding images """
        url = QtGui.QFileDialog.getOpenFileNames(self, _("add images"),
                "", _("""Images (*.png *.jpeg *.jpg *.gif *.tiff *.tif
                                 *.PNG *.JPEG *.JPG *.GIF *.TIFF *.TIF)
                                 ;;All files (*)"""))
        self.add_images(url)

    def remove_images_clicked(self):
        """ delete selected images from the model
            and the thumbnail from dic """
        sel = self.imgList.selectionModel().selectedIndexes()
        for i in sel:
            self.delete_thumbnail(i.data())
            self.modImgList.removeRow(i.row())

    def add_images(self, url=[]):
        """ add an image in the model """
        li = []
        for i in url:
            li.append(str(i))
        img = verif_images(li)
        for i in img:
            self.modImgList.appendRow(Item(i))

    def return_imgs(self):
        """ return a list containning all images's url """
        nb = self.modImgList.rowCount()
        images = []
        for i in range(nb):
            images.append(str(self.modImgList.item(i).text()))
        return images

    def check_preview(self):
        """ show or hide thumdnail """
        if self.checkPreviewW.isChecked():
            self.insert_thumbnail()
        else:
            self.previewW.clear()

    def insert_thumbnail(self):
        """ insert the first selected image thumbnail """
        if self.checkPreviewW.isChecked():
            sel = self.imgList.selectionModel().selectedIndexes()
            if sel:
                img = sel[0].data()
                self.previewW.setPixmap(self.create_thumbnail(img))
            else:
                self.previewW.setPixmap(self.create_thumbnail("alpha"))

    def create_thumbnail(self, url="alpha"):
        """ return or create thumbnail from url
            thumbnail are stored in self.thumbnailDic """
        if url in self.thumbnailDic:
            return self.thumbnailDic[url]
        else:
            if url == "alpha":
                img = QtGui.QPixmap(200, 200)
                img.fill(QtGui.QColor(0, 0, 0, 0))
            else:
                img = QtGui.QPixmap(url).scaledToWidth(200)
            self.thumbnailDic[url] = img
            return img

    def delete_thumbnail(self, image):
        """ delete thumbnail from self.thumbnailDic """
        if image in self.thumbnailDic:
            del self.thumbnailDic[image]


class ActionTab(QtGui.QWidget):
    """ manage action that will be applied on images"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.title = _("actions")
        self.imgs = self.parent.imgTab.return_imgs()

        ### available actions ###
        self.actionAvailableListLabel = QtGui.QLabel(_("available actions"))
        self.modActionAvailableList = QtGui.QStandardItemModel(0, 1)
        self.import_plugins()

        self.actionAvailableList = QtGui.QListView()
        self.actionAvailableList.setModel(self.modActionAvailableList)
        self.actionAvailableList.doubleClicked.connect(self.add_action)

        ### adding and deleting actions ###
        self.actionAdd = QtGui.QPushButton(_("add"))
        self.actionAdd.clicked.connect(self.add_action)
        self.actionRemove = QtGui.QPushButton(_("remove"))
        self.actionRemove.clicked.connect(self.remove_action)
        self.actionEdit = QtGui.QPushButton(_("edit"))
        self.actionEdit.clicked.connect(self.edit_action)

        ### action ###
        self.actionListLabel = QtGui.QLabel(_("actions"))
        self.modActionList = QtGui.QStandardItemModel(0, 1)
        self.actionList = QtGui.QListView()
        self.actionList.setModel(self.modActionList)
        self.actionList.selectionModel().selectionChanged.connect(self.sel_action)
        self.actionList.doubleClicked.connect(self.edit_action)

        ### preview ###
        self.previewW = QtGui.QPushButton(_("preview"))
        self.previewW.clicked.connect(self.preview)

        ### description of the selected action ###
        self.labelDesc = QtGui.QLabel(_("description"))
        self.labelPluginDesc = QtGui.QLabel("")
        self.labelActionDesc = QtGui.QLabel("")

        ### layout ###
        toolBox = QtGui.QVBoxLayout()
        toolBox.addWidget(self.actionAdd)
        toolBox.addWidget(self.actionRemove)
        toolBox.addStretch(0)

        descBox = QtGui.QVBoxLayout()
        descBox.addWidget(self.labelPluginDesc)
        descBox.addWidget(self.labelActionDesc)
        descBox.addStretch(0)
        descBox.addWidget(self.actionEdit)

        layout = QtGui.QGridLayout(self)
        layout.setColumnMinimumWidth(4, 200)
        layout.addWidget(self.actionAvailableListLabel, 1, 1)
        layout.addWidget(self.actionAvailableList, 2, 1, 2, 1)

        layout.addLayout(toolBox, 2, 2, 2, 1)

        layout.addWidget(self.actionListLabel, 1, 3)
        layout.addWidget(self.actionList, 2, 3)
        layout.addWidget(self.previewW, 3, 3)

        layout.addWidget(self.labelDesc, 1, 4)
        layout.addLayout(descBox, 2, 4, 2, 1)

    def import_plugins(self):
        """ plug-in are imported at launch
            this function insert them in the action available list"""
        for i in importedModules:
            info = {"name": i.NAME,
                    "modname": i.MOD_NAME,
                    "description": i.DESCRIPTION,
                    "author": i.AUTHOR,
                    "version": i.VERSION}
            self.modActionAvailableList.appendRow(Item(i.NAME, info))

    def add_action(self):
        """ add an action in the list of action that will applyed on image """
        sel = self.actionAvailableList.selectionModel().selectedIndexes()[0]
        if sel:
            # add item to the action list
            item = self.modActionAvailableList.itemFromIndex(sel)
            nItem = Item(sel.data(), item.info)
            self.modActionList.appendRow(nItem)
            # select and edit item
            self.actionList.setCurrentIndex(self.modActionList.index(self.modActionList.rowCount()-1, 0))
            self.edit_action()

    def remove_action(self):
        """ delete an action from the list of action that will applyed on image """
        sel = self.actionList.selectionModel().selectedIndexes()
        for i in sel:
            self.modActionList.removeRow(i.row())

    def sel_action(self):
        """ display the description of the selected action """
        sel = self.actionList.selectionModel().selectedIndexes()[0]
        item = self.modActionList.itemFromIndex(sel)
        self.labelPluginDesc.setText(item.info["description"])
        if item.getDesc():
            self.labelActionDesc.setText(item.getDesc())
        else:
            self.labelActionDesc.setText("")

    def edit_action(self, text=""):
        """ launch selected plugin
            and save what it return"""
        sel = self.actionList.selectionModel().selectedIndexes()[0]
        item = self.modActionList.itemFromIndex(sel)
        exec("""ok, code, desc, args = %s.ExecDialog(self.parent.imgTab.return_imgs(),
                                                     item.getArgs(),
                                                     self.return_code(True),
                                                     self).get_return()"""
                                       %(item.info["modname"], ))

        if locals()['ok']:
            item.setCode(locals()['code']) # code
            item.setDesc(locals()['desc']) # description
            item.setArgs(locals()['args']) # arguments
        self.sel_action()

    def return_code(self, beforeSel=False):
        """ return the code from actions
            all actions if beforeSel==False
            or actions before selected action beforeSel==True"""
        if beforeSel:
            sel = self.actionList.selectionModel().selectedIndexes()[0]
            item = self.modActionList.itemFromIndex(sel)
            nb = self.modActionList.indexFromItem(item).row()
        else:
            nb = self.modActionList.rowCount()
        code = ""
        for i in range(nb):
            code = """%s
%s""" %(code, self.modActionList.item(i).getCode())
        return code

    def preview(self):
        """ display a preview of an image after processing """
        PrevDialog(self.parent.imgTab.return_imgs(),
                                self.return_code(), self)


class SaveTab(QtGui.QWidget):
    """ manage the saving of the images """
    def __init__(self, parent=None, folder=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.title = _("save")
        self.imgs = self.parent.imgTab.return_imgs()
        self.code = self.parent.actionTab.return_code()

        ### saving folder ###
        self.folder = folder
        self.folderLabel = QtGui.QLabel(_("new dir"))
        self.folderEdit = QtGui.QLineEdit(self)
        self.folderEdit.setText(self.folder)
        self.folderEdit.textChanged[str].connect(self.dir_changed)
        self.folderChooser = QtGui.QPushButton(_("choose"))
        self.folderChooser.clicked.connect(self.change_dir)

        ### filename ###
        self.filenameLabel = QtGui.QLabel(_("filenames"))
        self.filenameEdit = QtGui.QLineEdit(self)
        self.filenameEdit.setText("%F%E")
        self.filenameEdit.textChanged[str].connect(self.filename_changed)

        self.oriFilenameLabel = QtGui.QLabel(_("original filename:"))
        self.oriFilename = QtGui.QLabel()

        self.newFilenameLabel = QtGui.QLabel(_("new filename:"))
        self.newFilename = QtGui.QLabel()
        self.tab_enter()
        self.parent.save_enter.connect(self.tab_enter)

        ### filename documentation ###
        self.doc = _( """%F : original filename
%E : original extension
%I to %IIIIIIIIII : increment (1 to 10 digits)""")
        self.docLabel = QtGui.QLabel(self.doc)

        ### code verification###
        self.codeEditButton = QtGui.QPushButton(_("code"))
        self.codeEditButton.clicked.connect(self.edit_code)

        ### apply ###
        self.applyW = QtGui.QPushButton(_("apply"))
        self.applyW.clicked.connect(self.apply_clicked)

        ### info ###
        self.infoLabel = QtGui.QLabel("")

        ### layout ###
        fileGrid = QtGui.QGridLayout()
        fileGrid.addWidget(self.folderLabel, 0, 0)
        fileGrid.addWidget(self.folderEdit, 0, 1, 1, 3)
        fileGrid.addWidget(self.folderChooser, 0, 4)
        fileGrid.addWidget(self.filenameLabel, 2, 0)
        fileGrid.addWidget(self.filenameEdit, 2, 1)

        fileGrid.addWidget(self.oriFilenameLabel, 1, 2)
        fileGrid.addWidget(self.oriFilename, 1, 3)
        fileGrid.addWidget(self.newFilenameLabel, 2, 2)
        fileGrid.addWidget(self.newFilename, 2, 3)
        fileGrid.addWidget(self.docLabel, 3, 1)
        fileGrid.addWidget(self.codeEditButton, 4, 1)

        okBox = QtGui.QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.infoLabel)
        okBox.addWidget(self.applyW)

        layout = QtGui.QVBoxLayout(self)
        layout.addLayout(fileGrid)
        layout.addStretch(0)
        layout.addLayout(okBox)

    def tab_enter (self):
        """change filename exemple depending of new images"""
        if len(self.imgs) > 0:
            self.oriFn = os.path.split(self.imgs[0]) [1]
        else:
            self.oriFn = ""
        self.oriFilename.setText(self.oriFn)
        self.filename_changed()

    def dir_changed(self):
        """ modify the saving folder """
        self.folder = self.folderEdit.text()

    def change_dir(self):
        """ dialog to change saving folder """
        url = QtGui.QFileDialog.getExistingDirectory(self,
                    _("Select the saving folder"), self.folder)
        if url:
            self.folderEdit.setText(url)
        print(self.folder)

    def filename_changed(self):
        """ change filename label depending of filename edit """
        fn = str(self.filenameEdit.text())
        fn = return_new_filename(self.oriFn, fn)
        self.newFilename.setText(fn)

    def edit_code(self):
        """ open a dialog to see and edit
            the code that will be applied to images """
        ok, self.code = TextEditDialog(self, self.code).getReturn()

    def apply_clicked(self):
        """ open the dialog that process images"""
        fn = str(self.filenameEdit.text())
        ApplyDialog(self.folder, fn, self.code, self.imgs, self)


class MainDialog(QtGui.QDialog):
    """ main windows of the application
        include the 3 class above as tab"""
    img_enter = QtCore.pyqtSignal()
    action_enter = QtCore.pyqtSignal()
    save_enter = QtCore.pyqtSignal()

    def __init__(self, images, dossier, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(_("imagemash"))

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
        """ send data to tab at opening """
        if tab == 0:
            self.img_enter.emit()
        elif tab == 1:
            self.actionTab.imgs = self.imgTab.return_imgs()
            self.action_enter.emit()
        elif tab == 2:
            self.saveTab.imgs = self.imgTab.return_imgs()
            self.saveTab.code = self.actionTab.return_code()
            self.save_enter.emit()


if __name__ == "__main__":
    ### import of the images ##############################################
    if len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]):
            fichiers = [os.path.join(sys.argv[1], i)
                        for i in os.listdir(sys.argv[1])]
            dossier = sys.argv[1]
        else:
            fichiers = [i for i in sys.argv[1:] if os.path.isfile(i)]
            dossier = os.path.dirname(sys.argv[1])
    else:
        fichiers = []
        dossier = ""

    ### import of the plugins #############################################
    pluginPath = os.path.join(os.path.dirname(
                           imp.find_module("imagemash")[1]), "plugins/")
    pluginFiles = [fname[:-3] for fname in os.listdir(pluginPath)
                   if fname.endswith(".py")
                   and fname.startswith("plugin_")]
    if not pluginPath in sys.path:
        sys.path[:0] = [pluginPath]
    importedModules = []
    for i in pluginFiles:
        importedModules.append(__import__(i))
        exec("%s = sys.modules[i]"%(i,))

    ### traduction #####################################################
    localesPath = os.path.join(os.path.dirname(
                           imp.find_module("imagemash")[1]), "locale/")
    gettext.install("imagemash", os.path.join(localesPath, "fr"))
    presLan_fr = gettext.translation("imagemash", localesPath,
                                     languages=['fr'])
    presLan_fr.install()

    ### starting the interface ########################################
    app = QtGui.QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    win = MainDialog(fichiers, dossier)
    app.exec_()
