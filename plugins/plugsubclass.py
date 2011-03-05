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


class Viewer(QtGui.QScrollArea):
    """ Class doc """
    
    def __init__ (self, parent=None):
        QtGui.QScrollArea.__init__(self, parent)
        self.parent = parent
        self.setAlignment(QtCore.Qt.AlignCenter)
        
    def event(self, event):
        # clic millieu: on memorise l'endroit pour le drag
        if (event.type()==QtCore.QEvent.MouseButtonPress) and (event.button()==QtCore.Qt.MidButton):
            self.mouseX = event.x()
            self.mouseY = event.y()
            return True
            
        # drag millieu: on se deplace dans l'image
        elif (event.type()==QtCore.QEvent.MouseMove) and (event.buttons()==QtCore.Qt.MidButton):
            diffX = event.x() - self.mouseX
            self.mouseX = event.x()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diffX)
            diffY = event.y() - self.mouseY
            self.mouseY = event.y()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diffY)
            return True
        return QtGui.QScrollArea.event(self, event)  
