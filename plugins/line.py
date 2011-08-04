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


class Line(QtCore.QObject):
    """ classe représentant une ligne
        args = (x1, y1, x2, y2)
    """
    figChanged = QtCore.pyqtSignal()
    def __init__ (self, parent=None, args=None):
        QtCore.QObject.__init__(self, parent)
        self.parent = parent
        
        # coordonnées du rectangle
        # si le rectangle existe
        if args:
            self.x1 = args[0]
            self.y1 = args[1]
            self.x2 = args[2]
            self.y2 = args[3]
            self.visible = True
        else:
            self.x1, self.y1 = 0, 0
            self.x2, self.y2 = 0, 0
            self.visible = False
        self.selP = None
        
        # rayon des poignées de la figure
        self.pR = 5
        
        # connection
        self.parent.clicSignal.connect(self.clic)
        self.parent.moveSignal.connect(self.move)
        
    def hide(self):
        self.visible = False
            
    def clic(self, mouseX, mouseY, zoom):
        """ fonction apelé au clic sur l'image
            recoit la position de la souris et le zoom
            clic: cree poignees ou selectionne la poignee à déplacer
            move: deplace poignee selectionnée
        """
        mouseX = int(mouseX / zoom)
        mouseY = int(mouseY / zoom)
        self.visible = True
        #self.alendroit()
        x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
        pR = int(self.pR / zoom)
        
        # verifie la poignée 1
        if x1-pR <= mouseX <= x1+pR and y1-pR <= mouseY <= y1+pR:
            self.selP = 1
        # verifie la poignée 2
        elif x2-pR <= mouseX <= x2+pR and y2-pR <= mouseY <= y2+pR:
            self.selP = 2
        # sinon enregistre la position de la souris
        else:
            self.selP = 2
            self.x1, self.y1 = mouseX, mouseY
            self.x2, self.y2 = mouseX, mouseY
            
        self.figChanged.emit()
            
    def move(self, mouseX, mouseY, zoom):
        """ fonction apelée par un clic mouvement sur l'image
            enregistre la position et taille du rectangle
            ou son déplacement
        """
        mouseX = int(mouseX / zoom)
        mouseY = int(mouseY / zoom)
        if self.selP == 1:
            self.x1 = mouseX
            self.y1 = mouseY
        elif self.selP == 2:
            self.x2 = mouseX
            self.y2 = mouseY
            
        self.figChanged.emit()

    def to_draw(self, z, imW, imH):
        """ renvoi la liste des éléments à dessiner sur l'image
        """
        list = []
        if self.visible:
            x1, y1 = int(self.x1 * z), int(self.y1 * z)
            x2, y2 = int(self.x2 * z), int(self.y2 * z)
            pR, pD = self. pR, self.pR * 2
            
            # ligne
            line = QtGui.QPainterPath()
            line.moveTo(x1, y1)
            line.lineTo(x2, y2)
            line.closeSubpath()
            list.append(["ligne", line])
            
            # poignee 1
            poignee1 = QtGui.QPainterPath()
            poignee1.moveTo(x1-pR, y1-pR)
            poignee1.lineTo(x1+pR, y1-pR)
            poignee1.lineTo(x1+pR, y1+pR)
            poignee1.lineTo(x1-pR, y1+pR)
            poignee1.closeSubpath()
            list.append(["poignee", poignee1])
            # poignee2
            poignee2 = QtGui.QPainterPath()
            poignee2.moveTo(x2-pR, y2-pR)
            poignee2.lineTo(x2+pR, y2-pR)
            poignee2.lineTo(x2+pR, y2+pR)
            poignee2.lineTo(x2-pR, y2+pR)
            poignee2.closeSubpath()
            list.append(["poignee", poignee2])
            
        return list
