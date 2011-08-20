#!/usr/bin/env python3
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
from PyQt4 import QtGui
from PyQt4 import QtCore


class Rect(QtCore.QObject):
    """ classe représentant le rectangle défini pour recadrer l'image
        args = (x, y, w, h)
    """
    figChanged = QtCore.pyqtSignal()
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
        
        # hauteur et largeur de l'image en sortie
        # permet de redimmentionner en meme temp l'image
        self.outW = False
        self.outH = False
        
        # rayon des poignées de la figure
        self.pR = 5
        # si on peut ou pas scaler le rectangle
        self.scale = True
        
        # voir clic
        self.action = "scale"
        self.diffX, self.diffY = 0, 0
        self.oppositeX, self.oppositeY = 0, 0
        
        # connection
        self.parent.clicSignal.connect(self.clic)
        self.parent.moveSignal.connect(self.move)
        
    def erase(self):
        self.exist = False
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.figChanged.emit()
        
    def action_changed(self, index, w, h):
        if index == 0: #ignore aspect ratio
            self.keepRatio = False
            self.scale = True
            self.ratio = (w, h)
            self.outW = False
            self.outH = False
        elif index == 1 and w > 0 and h > 0: #keep aspect ratio
            self.keepRatio = True
            self.scale = True
            self.ratio = (w, h)
            self.outW = False
            self.outH = False
            self.keep_ratio()
        elif index == 2 and w > 0 and h > 0:#keep aspect ratio and resize
            self.keepRatio = True
            self.scale = True
            self.ratio = (w, h)
            self.outW = w ## TODO
            self.outH = h ## TODO
            self.keep_ratio()
        elif index == 3 and w > 0 and h > 0:#set width and height
            self.keepRatio = True
            self.scale = False
            self.ratio = (w, h)
            self.outW = False
            self.outH = False
            self.w = w
            self.h = h
        else:
            return False
        self.figChanged.emit()
        return True
        
    def set_xywh(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.keep_ratio()
        self.exist = True
        self.figChanged.emit()
        
    def alendroit(self):
        """ remet le rectangle à l'endroit si besoin
        """
        if self.w < 0:
            self.x = self.x + self.w
            self.w = -self.w
        if self.h < 0:
            self.y = self.y + self.h
            self.h = -self.h
            
    def clic(self, mouseX, mouseY, zoom):
        """ fonction apelé au clic sur l'image
            recoit la position de la souris et le zoom
            defini l'action a effectuer et enregistre des variables temporaires
            scale: enregistre le coté opposé                      > oppositeX
            move: enregistre la différence x,y rect / x,y souris  > diffX
        """
        mouseX = int(mouseX / zoom)
        mouseY = int(mouseY / zoom)
        if self.exist:
            #self.alendroit()
            x, y, w, h = self.x, self.y, self.w, self.h
            pR = int(self.pR / zoom)
            if self.scale:
                # verifie la poignée haut gauche
                if x-pR <= mouseX <= x+pR and y-pR <= mouseY <= y+pR:
                    self.action = "scale"
                    self.oppositeX = x + w
                    self.oppositeY = y + h
                # verifie la poignée haut droit
                elif x+w-pR <= mouseX <= x+w+pR and y-pR <= mouseY <= y+pR:
                    self.action = "scale"
                    self.oppositeX = x
                    self.oppositeY = y + h
                # verifie la poignée bas gauche
                elif x-pR <= mouseX <= x+pR and y+h-pR <= mouseY <= y+h+pR:
                    self.action = "scale"
                    self.oppositeX = x + w
                    self.oppositeY = y
                # verifie la poignée bas droit
                elif x+w-pR <= mouseX <= x+w+pR and y+h-pR <= mouseY <= y+h+pR:
                    self.action = "scale"
                    self.oppositeX = x
                    self.oppositeY = y
                # verifie le rectangle
                elif x <= mouseX <= x+w and y <= mouseY <= y+h:
                    self.action = "move"
                    self.diffX = mouseX - x
                    self.diffY = mouseY - y
                # verifie le rectangle
                elif x <= mouseX <= x+w and y <= mouseY <= y+h:
                    self.action = "move"
                    self.diffX = mouseX - x
                    self.diffY = mouseY - y
                # sinon enregistre la position de la souris
                # pour créer un nouveau rectangle au premier mouvement
                else:
                    self.action = "scale"
                    self.oppositeX = mouseX
                    self.oppositeY = mouseY
            else: #self.scale == False
                # verifie le rectangle
                if x <= mouseX <= x+w and y <= mouseY <= y+h:
                    self.action = "move"
                    self.diffX = mouseX - x
                    self.diffY = mouseY - y
                else:
                    self.exist = True
                    self.action = "move"
                    self.x = mouseX
                    self.y = mouseY
                    self.w = int(self.parent.parent.wW.text())
                    self.h = int(self.parent.parent.hW.text())
                    self.diffX = 0
                    self.diffY = 0
        elif not self.scale:
            self.exist = True
            self.action = "move"
            self.x = mouseX
            self.y = mouseY
            self.w = int(self.parent.parent.wW.text())
            self.h = int(self.parent.parent.hW.text())
            self.diffX = 0
            self.diffY = 0
        # sinon enregistre la position de la souris 
        # pour créer un nouveau rectangle au premier mouvement
        else:
            self.action = "scale"
            self.oppositeX = mouseX
            self.oppositeY = mouseY
        self.figChanged.emit()
            
    def move(self, mouseX, mouseY, zoom):
        """ fonction apelée par un clic mouvement sur l'image
            enregistre la position et taille du rectangle
            ou son déplacement
        """
        mouseX = int(mouseX / zoom)
        mouseY = int(mouseY / zoom)
        self.exist = True
        if self.action == "scale":
            self.x = self.oppositeX
            self.y = self.oppositeY
            self.w = mouseX - self.oppositeX
            self.h = mouseY - self.oppositeY
            self.keep_ratio()
            self.alendroit()
            self.figChanged.emit()
            
        elif self.action == "move":
            self.x = mouseX - self.diffX
            self.y = mouseY - self.diffY
            self.figChanged.emit()

    def keep_ratio(self, side="w"):
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
                            
    def to_draw(self, z, imW, imH):
        """ renvoi la liste des éléments à dessiner sur l'image
        """
        list = []
        if self.exist:
            x, y = int(self.x * z), int(self.y * z)
            w, h = int(self.w * z), int(self.h * z)
            pR, pD = self. pR, self.pR * 2
            
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
            
            if self.scale:
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
