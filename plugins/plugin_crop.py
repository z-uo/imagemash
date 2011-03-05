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

### plugin infos #######################################################
NAME = "recadrage"
MOD_NAME = "plugin_crop"
DESCRIPTION = "recadre les images"
AUTHOR = "pops"
VERSION = 0.1
EXEC_CLASS = "CropDialog"#(images, args)

### plugin prefs #######################################################
FIG_COLOR = "#000000"
FIG_POIGNEES = True
IMAGE = "img/1.jpg"
OUT = True
KEEP_RATIO = False
RATIO = (0, 0)
ZOOM_DIC = { "10%" : 0.1,
             "25%" : 0.25,
             "50%" : 0.5,
             "75%" : 0.75,
             "100%" : 1,
             "200%" : 2,
             "400%" : 4,
             "800%" : 8,
             "1600%" : 16
           }

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
        self.keepRatio = KEEP_RATIO
        self.ratio = RATIO
        
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
class Painting(QtGui.QWidget):
    """ prévisualisation de l'image et interaction avec la souris
    """
    def __init__(self, parent=None, args=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        
        self.fig = Fig(self, args)
        self.color = QtGui.QColor()
        self.color.setNamedColor(FIG_COLOR)
        
        self.zoomN = 1
        #image originale pre zoom
        self.imOri = QtGui.QImage()
        
    def clic(self, event):
        self.fig.clic(event.x(), event.y(), self.zoomN)

    def move(self, event):
        self.fig.move(event.x(), event.y(), self.zoomN)
        self.draw()
        
    def paintEvent(self, ev):
        p = QtGui.QPainter()
        p.begin(self)
        p.drawImage(QtCore.QPoint(0, 0), self.imQPainter)
        p.end()
            
    def draw(self):
        p = QtGui.QPainter()
        p.begin(self.imQPainter)
        p.drawImage(QtCore.QPoint(0, 0), self.imOriZoomed)
        for i in self.fig.toDraw(self.zoomN, self.zImW, self.zImH):
            if i[0] == "cadre":
                p.setPen(QtGui.QPen(self.color, 1, QtCore.Qt.SolidLine))
                alpha = self.color
                alpha.setAlpha(100)
                p.setBrush(alpha)
                p.drawPath(i[1])
            if i[0] == "ligne":
                p.drawPath(i[1])
            if i[0] == "poignee":
                p.setPen(QtGui.QPen(self.color, 1, QtCore.Qt.SolidLine))
                p.setBrush(QtGui.QColor(255, 255, 255, 255))
                p.drawPath(i[1])
        p.end()
        self.update()
                
    def zoom(self, n):
        self.zoomN = n
        self.zImH = self.imH * self.zoomN
        self.zImW = self.imW * self.zoomN
        self.imOriZoomed = self.imOri.scaled(self.zImW, self.zImH)
        self.imQPainter = self.imOri.scaled(self.zImW, self.zImH)
        self.setFixedSize(self.zImW, self.zImH)
        self.draw()
        
    def erase(self):
        self.fig.exist = False
        self.draw()
                
    def event(self, event):
        if (event.type()==QtCore.QEvent.MouseButtonPress) and (event.button()==QtCore.Qt.LeftButton):
            self.clic(event)
            return True
        elif (event.type()==QtCore.QEvent.MouseMove) and (event.buttons()==QtCore.Qt.LeftButton):
            self.move(event)
            return True
        return QtGui.QWidget.event(self, event)
        
    def changeImage(self, image, code=""):
        self.imOri.load(image)
        code = code.replace("$i", "self.imOri")
        exec code
        ###pil code
        #~ if code:
            #~ im = Image.open(image)
            #~ exec code
            #~ self.imOri = ImageQt.ImageQt(im)
        #~ else:
            #~ self.imOri.load(image)
        self.imH = self.imOri.height()
        self.imW = self.imOri.width()
        self.zoom(self.zoomN)
        
class ViewerDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        #  zoom  | effacer| couleur
        #  action| action | h | editH | w | editW | editer
        #  image
        #                                   ok    | annuler
        
        ### zoom ###
        self.zoom = 1    
        self.zoomW = QtGui.QComboBox(self)
        self.zoomW.addItem("10%")
        self.zoomW.addItem("25%")
        self.zoomW.addItem("50%")
        self.zoomW.addItem("75%")
        self.zoomW.addItem("100%")
        self.zoomW.addItem("200%")
        self.zoomW.addItem("400%")
        self.zoomW.addItem("800%")
        self.zoomW.addItem("1600%")
        self.zoomW.setCurrentIndex(4)
        self.zoomW.activated[str].connect(self.zoomChanged)
        
        ### image ###
        self.imW = QtGui.QComboBox(self)
        self.imW.setCurrentIndex(0)
        self.imW.activated[str].connect(self.imChanged)
        
        ### effacer ###
        self.eraseW = QtGui.QPushButton(self)
        self.eraseW.setIcon(QtGui.QIcon(QtGui.QPixmap('img/eraser.png')))
        self.eraseW.clicked.connect(self.eraseClicked)
        
        ### couleur ###
        self.color = QtGui.QColor(0, 0, 0) 
        self.colorIcon = QtGui.QPixmap(22, 22)
        self.colorIcon.fill(self.color)
        
        self.colorW = QtGui.QPushButton(self)
        self.colorW.setIcon(QtGui.QIcon(self.colorIcon))
        self.colorW.clicked.connect(self.colorClicked)
        
        ### cadre ###
        self.infoL = QtGui.QLabel(" ")
        
        ### appliquer ###
        self.okW = QtGui.QPushButton('appliquer', self)
        self.okW.clicked.connect(self.okClicked)

        ### annuler ###
        self.undoW = QtGui.QPushButton('annuler', self)
        self.undoW.clicked.connect(self.undoClicked)
        
        # zoom / effacer / couleur
        self.toolBox = QtGui.QHBoxLayout()
        self.toolBox.setSpacing(2)
        self.toolBox.addWidget(self.zoomW)
        self.toolBox.addWidget(self.imW)
        self.toolBox.addWidget(self.eraseW)
        self.toolBox.addWidget(self.colorW)
        self.toolBox.insertSpacing(4, 6)
        self.toolBox.addWidget(self.infoL)
        self.toolBox.addStretch(0)
        
        # ok annuler
        self.okBox = QtGui.QHBoxLayout()
        self.okBox.setSpacing(2)
        self.okBox.addStretch(0)
        self.okBox.addWidget(self.okW)
        self.okBox.addWidget(self.undoW)
        
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(2)
        self.grid.addLayout(self.toolBox, 0, 0)
        self.grid.addLayout(self.okBox, 3, 0)
        
        self.setLayout(self.grid)
       
    def zoomChanged(self, text):
        print "zoomChanged"
        print text
    def imChanged(self, text):
        print "imChanged"
        print text
    def colorClicked(self):
        print "colorClicked"
    def eraseClicked(self):
        print "eraseClicked"
    def okClicked(self):
        print "okClicked"
    def undoClicked(self):
        print "undoClicked"
        
        
class CropDialog(ViewerDialog):
    def __init__(self, images, args=None, code="", parent=None):
        ViewerDialog.__init__(self, parent)
        
        ### liste des images ###
        self.images = []
        for i, v in enumerate(images):
            f = os.path.split(v)[1]
            self.imW.addItem(f)
            self.images.append(v)
            
        ### code a apliquer a une image a l'ouverture ###
        self.codeBefore = code
            
        ### viewer ###
        self.painting = Painting(self, args)
        self.viewer = Viewer(self)
        self.viewer.setWidget(self.painting)
        self.imChanged(self.images[0])
        
        ### action ###
        self.actionL = QtGui.QLabel("action")
        self.actionW = QtGui.QComboBox(self)
        self.actionW.addItem("none")
        self.actionW.addItem("ratio")
        self.actionW.addItem("pixel")
        self.actionW.addItem("redim")
        self.actionW.activated[str].connect(self.actionChanged)       
        
        ### w ###
        self.wL = QtGui.QLabel("largeur : ")
        self.wW = QtGui.QLineEdit(self)
        self.wW.setValidator(QtGui.QIntValidator(self.wW))
        self.wW.setText("0")
        self.wW.textChanged.connect(self.actionChanged)
        
        ### h ###
        self.hL = QtGui.QLabel("hauteur : ")
        self.hW = QtGui.QLineEdit(self)
        self.hW.setValidator(QtGui.QIntValidator(self.hW))
        self.hW.setText("0")
        self.hW.textChanged.connect(self.actionChanged)
        
        ### editer ###
        self.editW = QtGui.QPushButton('editer', self)
        self.editW.clicked.connect(self.editClicked)
        
        ### label infoL ###
        self.painting.fig.rectChanged.connect(self.rectChanged)
        self.rectChanged()
        
        self.cropBox = QtGui.QHBoxLayout()
        self.cropBox.setSpacing(2)
        self.cropBox.addWidget(self.actionL)
        self.cropBox.addWidget(self.actionW)
        self.cropBox.insertSpacing(2, 6)
        self.cropBox.addWidget(self.wL)
        self.cropBox.addWidget(self.wW)
        self.cropBox.addWidget(self.hL)
        self.cropBox.addWidget(self.hW)
        self.cropBox.insertSpacing(7, 6)
        self.cropBox.addWidget(self.editW)
        
        self.grid.addLayout(self.cropBox, 1, 0)
        self.grid.addWidget(self.viewer, 2, 0)
        self.exec_()
       
    def zoomChanged(self, text):
        z = ZOOM_DIC[str(text)]
        self.painting.zoom(z)
        
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
            if action == "none":
                self.painting.fig.keepRatio = False
                self.painting.fig.scale = True
                self.painting.fig.outW = False
                self.painting.fig.outH = False
            elif action == "ratio":
                self.painting.fig.keepRatio = True
                self.painting.fig.scale = True
                self.painting.fig.outW = False
                self.painting.fig.outH = False
                self.painting.fig.ratio = (w, h)
                
                self.painting.fig.KeepRatio()
                self.painting.draw()
                
            elif action == "pixel":
                self.painting.fig.scale = False ## TODO
                self.painting.fig.keepRatio = False
                self.painting.fig.w = w
                self.painting.fig.h = h
            elif action == "redim":
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
        self.infoL.setText(text)
        
    def okClicked(self):
        self.accept()
    def undoClicked(self):
        self.reject()
    def getReturn(self):
        if self.result():
            x = int(self.painting.fig.x)
            y = int(self.painting.fig.y)
            w = int(self.painting.fig.w)
            h = int(self.painting.fig.h)
            
            #~ code = "im = im.crop((%s, %s, %s, %s))" %(x, y, x+w, y+h)
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
    app=QtGui.QApplication(sys.argv)
    win=CropDialog([IMAGE])
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
                app, QtCore.SLOT("quit()"))
    app.exec_()
