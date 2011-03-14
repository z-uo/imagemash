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

from plugsubclass import *

image = "/home/pops/prog/img/IMGP0333.JPG"
### plugin infos #######################################################
NAME = "recadrage"
MOD_NAME = "plugin_crop"
DESCRIPTION = "recadre les images"
AUTHOR = "pops"
VERSION = 0.1
EXEC_CLASS = "CropDialog"#(images, args)

### plugin prefs #######################################################


class Fig(QtCore.QObject):
    """ classe représentant le rectangle défini pour recadrer l'image
        args = (x, y, w, h)
    """
    rectChanged = QtCore.pyqtSignal(dict)
    def __init__ (self, parent=None, args=None):
        QtCore.QObject.__init__(self, parent)
        self.parent = parent
        
        # coordonnées du rectangle
        # si le rectangle existe
        if args:
            self.x = args[0]
            self.y = args[1]
            self.w = args[2]
            self.h = args[3]
            self.exist = True
        else:
            self.x, self.y = 0, 0
            self.w, self.h = 0, 0
            self.exist = False
                 
        # ratio du rectangle
        self.keepRatio = False
        self.ratio = (0, 0)
        
        # rayon des poignées du rectangle
        self.pR = 5
        
        # hauteur et largeur de l'image en sortie
        # permet de redimmentionner en meme temp l'image
        self.outW = False
        self.outH = False
        
        # si on peut ou pas scaler le rectangle
        self.scale = True
        
        # voir clic
        self.action = "scale"
        self.diffX, self.diffY = 0, 0
        self.oppositeX, self.oppositeY = 0, 0
    
    def alendroit(self):
        """ remet le rectangle a l'endroit si besoin
        """
        if self.w < 0:
            self.x = self.x + self.w
            self.w = -self.w
        if self.h < 0:
            self.y = self.y + self.h
            self.h = -self.h
            
    def clic(self, mouseX, mouseY, zoom=1):
        """ fonction apelé au clic sur l'image
            recoit la position de la souris et le zoom
            defini l'action a effectuer et enregistre des variables temporaires
            scale: enregistre le coté opposé                      > oppositeX
            move: enregistre la différence x,y rect / x,y souris  > diffX
        """
        mouseX, mouseY = mouseX // zoom, mouseY // zoom
        if self.exist:
            self.alendroit()
            x, y, w, h = self.x, self.y, self.w, self.h
            pR = self.pR // zoom
            
            # verifie la poignée haut gauche
            if x-pR <= mouseX <= x+pR and y-pR <= mouseY <= y+pR:
                self.action = "scale"
                self.oppositeX = x + w
                self.oppositeY = y + h
                return None
            # verifie la poignée haut droit
            elif x+w-pR <= mouseX <= x+w+pR and y-pR <= mouseY <= y+pR:
                self.action = "scale"
                self.oppositeX = x
                self.oppositeY = y + h
                return None
            # verifie la poignée bas gauche
            elif x-pR <= mouseX <= x+pR and y+h-pR <= mouseY <= y+h+pR:
                self.action = "scale"
                self.oppositeX = x + w
                self.oppositeY = y
                return None
            # verifie la poignée bas droit    
            elif x+w-pR <= mouseX <= x+w+pR and y+h-pR <= mouseY <= y+h+pR:
                self.action = "scale"
                self.oppositeX = x
                self.oppositeY = y
                return None
            # verifie le rectangle
            elif x <= mouseX <= x+w and y <= mouseY <= y+h:
                self.action = "move"
                self.diffX = mouseX - x
                self.diffY = mouseY - y
                return None
            # sinon enregistre la position de la souris 
            # pour créer un nouveau rectangle au premier mouvement
            else:
                self.action = "scale"
                self.oppositeX = mouseX
                self.oppositeY = mouseY
                return None
        # sinon enregistre la position de la souris 
        # pour créer un nouveau rectangle au premier mouvement
        else:
            self.action = "scale"
            self.oppositeX = mouseX
            self.oppositeY = mouseY
            return None
            
            
    def move(self, mouseX, mouseY, zoom=1):
        """ fonction apelée par un clic mouvement sur l'image
            enregistre la position et taille du rectangle
            ou son déplacement
        """
        self.exist = True
        mouseX, mouseY = mouseX // zoom, mouseY // zoom
        
        if self.action == "scale":
            self.x = self.oppositeX
            self.y = self.oppositeY
            self.w = mouseX - self.oppositeX
            self.h = mouseY - self.oppositeY
            self.KeepRatio()
            self.alendroit()
            self.rectChanged.emit({"x":self.x, "y":self.y, "w":self.w, "h":self.h}) 
            
        elif self.action == "move":
            self.x = mouseX - self.diffX
            self.y = mouseY - self.diffY
        
    def KeepRatio(self, side="w"):
        if self.keepRatio:
            r = float(self.ratio[0]) / float(self.ratio[1])
            if side == "w":
                if self.h < 0 and self.w > 0:
                    self.h = int(self.w * -1 // r)
                elif self.h > 0 and self.w < 0:
                    self.h = int(self.w * -1 // r)
                else:
                    self.h = int(self.w // r)
            elif side == "h":
                if self.h < 0 and self.w > 0:
                    self.w = int(self.h * -1 * r)
                elif self.h > 0 and self.w < 0:
                    self.w = int(self.h * -1 * r)
                else:
                    self.w = int(self.h * r)
                            
    def toDraw(self, z, imW, imH):
        """ renvoi la liste des éléments à dessiner sur l'image
        """
        list = []
        if self.exist:
            x, y, w, h = self.x * z, self.y * z, self.w * z, self.h * z
            pR, pD = self.pR, self.pR * 2
            
            # cadre
            cadre = QtGui.QPainterPath()
            cadre.moveTo(-1, -1)
            cadre.lineTo(imW, -1)
            cadre.lineTo(imW, imH)
            cadre.lineTo(-1, imH)
            cadre.closeSubpath()
            cadre.moveTo(x, y)
            cadre.lineTo(x + w, y)
            cadre.lineTo(x + w, y + h)
            cadre.lineTo(x, y + h)
            cadre.closeSubpath()
            list.append(["cadre", cadre])
            
            # haut gauche
            poignee1 = QtGui.QPainterPath()
            poignee1.moveTo(x-pR, y-pR)
            poignee1.lineTo(x+pR, y-pR)
            poignee1.lineTo(x+pR, y+pR)
            poignee1.lineTo(x-pR, y+pR)
            poignee1.closeSubpath()
            list.append(["poignee", poignee1])
            # haut droit
            poignee2 = QtGui.QPainterPath()
            poignee2.moveTo(x+w-pR, y-pR)
            poignee2.lineTo(x+w+pR, y-pR)
            poignee2.lineTo(x+w+pR, y+pR)
            poignee2.lineTo(x+w-pR, y+pR)
            poignee2.closeSubpath()
            list.append(["poignee", poignee2])
            # bas gauche
            poignee3 = QtGui.QPainterPath()
            poignee3.moveTo(x-pR, y+h-pR)
            poignee3.lineTo(x+pR, y+h-pR)
            poignee3.lineTo(x+pR, y+h+pR)
            poignee3.lineTo(x-pR, y+h+pR)
            poignee3.closeSubpath()
            list.append(["poignee", poignee3])
            # bas droit
            poignee4 = QtGui.QPainterPath()
            poignee4.moveTo(x+w-pR, y+h-pR)
            poignee4.lineTo(x+w+pR, y+h-pR)
            poignee4.lineTo(x+w+pR, y+h+pR)
            poignee4.lineTo(x+w-pR, y+h+pR)
            poignee4.closeSubpath()
            list.append(["poignee", poignee4])
            
        return list
        
        
########################################################################
class CropDialog(QtGui.QDialog):
    def __init__(self, images, args=None, code="", parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.codeBefore = code
        
        #  zoom  | effacer| couleur
        #  action| action | h | editH | w | editW | editer
        #  image
        #                                   ok    | annuler
        
        ### widget #####################################################
        ### image ###
        self.imW = QtGui.QComboBox(self)
        self.images = []
        for i, v in enumerate(images):
            f = os.path.split(v)[1]
            self.imW.addItem(f)
            self.images.append(v)

        ### effacer ###
        self.eraseW = QtGui.QToolButton(self)
        self.eraseW.setAutoRaise(True)
        self.eraseW.setIcon(QtGui.QIcon(QtGui.QPixmap('icons/black_eraser.svg')))
        ### couleur ###
        self.color = QtGui.QColor(0, 0, 0)
        self.colorIcon = QtGui.QPixmap(22, 22)
        self.colorIcon.fill(self.color)
        
        self.colorW = QtGui.QToolButton(self)
        self.colorW.setAutoRaise(True)
        self.colorW.setIcon(QtGui.QIcon(self.colorIcon))
        
        ### zoom buttons ###
        self.zoomInW = QtGui.QToolButton()
        self.zoomInW.setAutoRaise(True)
        self.zoomInW.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/black_zoom_in.svg")))
        self.zoomOutW = QtGui.QToolButton()
        self.zoomOutW.setAutoRaise(True)
        self.zoomOutW.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/black_zoom_out.svg")))
        self.zoomOneW = QtGui.QToolButton()
        self.zoomOneW.setAutoRaise(True)
        self.zoomOneW.setIcon(QtGui.QIcon(QtGui.QPixmap("icons/black_zoom_one.svg")))
        
        ### labels info ###
        self.oriL = QtGui.QLabel("original size")
        self.oriWL = QtGui.QLabel("")
        self.oriHL = QtGui.QLabel("")
        self.newL = QtGui.QLabel("new size")
        self.newWL = QtGui.QLabel("")
        self.newHL = QtGui.QLabel("")
        
        ### viewer ###
        self.painting = Painting(self, args)
        self.painting.fig = Fig(self, args)
        self.viewer = Viewer(self)
        self.viewer.setWidget(self.painting)
        
        ### action ###
        self.actionL = QtGui.QLabel("action")
        self.actionW = QtGui.QComboBox(self)
        self.actionW.addItem("ignore aspect ratio")
        self.actionW.addItem("keep aspect ratio")
        self.actionW.addItem("keep aspect ratio and resize")
        self.actionW.addItem("recadre au pixel pres")      
        
        ### w ###
        self.wL = QtGui.QLabel("largeur : ")
        self.wW = QtGui.QLineEdit("0")
        self.wW.setValidator(QtGui.QIntValidator(self.wW))
        
        ### h ###
        self.hL = QtGui.QLabel("hauteur : ")
        self.hW = QtGui.QLineEdit("0")
        self.hW.setValidator(QtGui.QIntValidator(self.hW))
        
        ### edit ###
        self.editW = QtGui.QPushButton('editer', self)
        
        ### apply, undo ###
        self.okW = QtGui.QPushButton('appliquer', self)
        self.undoW = QtGui.QPushButton('annuler', self)
        
        ### function ###################################################
        self.imChanged(self.images[0])
        self.rectChanged()
        
        ### connexion ##################################################
        self.imW.activated[str].connect(self.imChanged)
        self.eraseW.clicked.connect(self.eraseClicked)
        self.colorW.clicked.connect(self.colorClicked)
        
        self.actionW.activated[str].connect(self.actionChanged) 
        self.wW.textChanged.connect(self.actionChanged)
        self.hW.textChanged.connect(self.actionChanged)
        self.editW.clicked.connect(self.editClicked)
        self.painting.fig.rectChanged.connect(self.rectChanged)
        
        self.okW.clicked.connect(self.okClicked)
        self.undoW.clicked.connect(self.undoClicked)
        
        self.zoomInW.clicked.connect(self.zoomIn)
        self.viewer.zoomIn.connect(self.zoomIn)
        self.zoomOutW.clicked.connect(self.zoomOut)
        self.viewer.zoomOut.connect(self.zoomOut)
        self.zoomOneW.clicked.connect(self.zoomOne)
        
        ### layout #####################################################
        
        toolBox = QtGui.QHBoxLayout()
        toolBox.addWidget(self.zoomInW)
        toolBox.addWidget(self.zoomOutW)
        toolBox.addWidget(self.zoomOneW)
        toolBox.addWidget(self.eraseW)
        toolBox.addWidget(self.colorW)
        toolBox.addStretch(0)
        
        grid = QtGui.QGridLayout()
        
        grid.addWidget(self.imW, 0, 1, 1, 2)
        grid.addWidget(self.editW, 1, 1, 1, 2)
        grid.addLayout(toolBox, 2, 1, 1, 2)
        
        grid.addWidget(self.actionW, 0, 3, 1, 2)
        grid.addWidget(self.wL, 1, 3)
        grid.addWidget(self.hL, 2, 3)
        grid.addWidget(self.wW, 1, 4)
        grid.addWidget(self.hW, 2, 4)
        
        grid.addWidget(self.oriL, 0, 5)
        grid.addWidget(self.oriWL, 1, 5)
        grid.addWidget(self.oriHL, 2, 5)
        
        grid.addWidget(self.newL, 0, 6)
        grid.addWidget(self.newWL, 1, 6)
        grid.addWidget(self.newHL, 2, 6)
        
        ### ok, undo ###
        okBox = QtGui.QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.okW)
        okBox.addWidget(self.undoW)
        
        ### layout ###
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(2)
        layout.addLayout(grid)
        layout.addWidget(self.viewer)
        layout.addLayout(okBox)
        
        self.setLayout(layout)
        self.exec_()
        
    def zoomIn(self):
        self.painting.zoom(2.0)
        self.viewer.zoom(2.0)
        
    def zoomOut(self):
        self.painting.zoom(0.5)
        self.viewer.zoom(0.5)
        
    def zoomOne(self):
        self.painting.zoom(0)
        
    def imChanged(self, text):
        im = self.images[self.imW.currentIndex()]
        self.painting.changeImage(im, self.codeBefore)
                    
    def colorClicked(self):
        self.color = QtGui.QColorDialog.getColor(self.color)
        if self.color.isValid():
            self.colorIcon.fill(self.color)
            self.colorW.setIcon(QtGui.QIcon(self.colorIcon))
            self.painting.color = self.color
        self.painting.draw()
            
    def eraseClicked(self):
        self.painting.erase()
        
    def actionChanged(self, text):
        action = self.actionW.currentText()
        w = self.wW.text().toInt()[0]
        h = self.hW.text().toInt()[0]
        
        if w > 0 and h > 0:
            if action == "ignore aspect ratio":
                self.painting.fig.keepRatio = False
                self.painting.fig.scale = True
                self.painting.fig.outW = False
                self.painting.fig.outH = False
            elif action == "keep aspect ratio":
                self.painting.fig.keepRatio = True
                self.painting.fig.scale = True
                self.painting.fig.outW = False
                self.painting.fig.outH = False
                self.painting.fig.ratio = (w, h)
                
                self.painting.fig.KeepRatio()
                self.painting.draw()
                
            elif action == "keep aspect ratio and resize":
                self.painting.fig.scale = False ## TODO
                self.painting.fig.keepRatio = False
                self.painting.fig.w = w
                self.painting.fig.h = h
            elif action == "recadre au pixel pres":
                self.painting.fig.keepRatio = True
                self.painting.fig.scale = True
                self.painting.fig.ratio = (w, h)
                self.painting.fig.outW = w ## TODO
                self.painting.fig.outH = h ## TODO
        else:
            self.actionW.setCurrentIndex(0)
        
    def editClicked(self):
        
        ok, x, y, w, h =  EditDialog(self, self.painting.fig.x, 
                                           self.painting.fig.y, 
                                           self.painting.fig.w, 
                                           self.painting.fig.h).getReturn()
        if ok:
            self.painting.fig.x = x
            self.painting.fig.y = y
            self.painting.fig.w = w
            self.painting.fig.h = h
            self.painting.fig.KeepRatio()
            self.painting.fig.exist = True
            self.painting.draw()
            
    def rectChanged(self, info=None):
        if info:
            text = "taille de l'image: %s px / %s px      nouvelle taille: %s px / %s px" %(self.painting.imW, self.painting.imH, info["w"], info["h"])
        else:
            text = "taille de l'image: %s px / %s px      nouvelle taille: %s px / %s px          " %(self.painting.imW, self.painting.imH, self.painting.imW, self.painting.imH)

        
    def okClicked(self):
        self.accept()
    def undoClicked(self):
        self.reject()
    def get_return(self):
        if self.result():
            x = int(self.painting.fig.x)
            y = int(self.painting.fig.y)
            w = int(self.painting.fig.w)
            h = int(self.painting.fig.h)
            code = "$i = $i.copy(%s, %s, %s, %s)" %(x, y, w, h)
            desc = """x = %s y = %s 
w = %s h = %s""" %(x, y, w, h)
            args = (x, y, w, h)
            return True , code, desc, args
        else:
            return False, None, None, None
            
            
class EditDialog(QtGui.QDialog):
    def __init__(self, parent=None, x=0, y=0, w=1, h=1):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        
        self.xL = QtGui.QLabel("x")
        self.xW = QtGui.QLineEdit(self)
        self.xW.setValidator(QtGui.QIntValidator(self.xW))
        self.xW.setText(str(x))
        self.yL = QtGui.QLabel("y")
        self.yW = QtGui.QLineEdit(self)
        self.yW.setValidator(QtGui.QIntValidator(self.yW))
        self.yW.setText(str(y))
        self.wL = QtGui.QLabel("w")
        self.wW = QtGui.QLineEdit(self)
        self.wW.setValidator(QtGui.QIntValidator(self.wW))
        self.wW.setText(str(w))
        self.hL = QtGui.QLabel("h")
        self.hW = QtGui.QLineEdit(self)
        self.hW.setValidator(QtGui.QIntValidator(self.hW))
        self.hW.setText(str(h))
        
        ### appliquer ###
        self.okW = QtGui.QPushButton('appliquer', self)
        self.okW.clicked.connect(self.okClicked)
        ### annuler ###
        self.undoW = QtGui.QPushButton('annuler', self)
        self.undoW.clicked.connect(self.undoClicked)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(2)
        grid.addWidget(self.xL, 0, 0)
        grid.addWidget(self.xW, 0, 1)
        grid.addWidget(self.yL, 1, 0)
        grid.addWidget(self.yW, 1, 1)
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
        
    def getReturn(self):
        if self.result():
            x = self.xW.text().toInt()[0]
            y = self.yW.text().toInt()[0]
            w = self.wW.text().toInt()[0]
            h = self.hW.text().toInt()[0]
            return True, x, y, w, h
        else:
            return False, None, None, None, None
            
    def okClicked(self):
        self.accept()
    def undoClicked(self):
        self.reject()
        

if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    win = CropDialog([image])
    app.exec_()
