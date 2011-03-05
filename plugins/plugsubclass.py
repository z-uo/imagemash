#!/usr/bin/env python
#-*- coding: utf-8 -*-
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
