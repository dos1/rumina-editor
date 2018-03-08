#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class RuminaMapView(QGraphicsView):
        
    def  __init__(self, parent=None, scene=None):
        super(QGraphicsView, self).__init__(parent=parent)
        #self.setOptimizationFlags(QGraphicsView.OptimizationFlags(0x8)) # IndirectPainting
        self.setScene(scene)
        self.resize()
                        
    #def drawItems(self, painter, numItems, items, options):
    #    print("yay")
    
    def resize(self):
        if self.scene():
            self.fitInView(QRectF(-3394.11, -3394.11, 3394.11 * 2, 3394.11 * 2), Qt.KeepAspectRatio)
