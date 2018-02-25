#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from RuminaGraphicsObject import RuminaGraphicsObject

class RuminaSourceFile(RuminaGraphicsObject):
                        
    selectionChanged = pyqtSignal(int, int, int, int)
    selectionCleared = pyqtSignal()
    itemAdded = pyqtSignal(RuminaGraphicsObject, QRect)
    image = None
    pixmap = None
    filename = None
    
    def __init__(self, filename, parent=None):
        self.filename = filename
        self.image = QImage(self.filename)
        self.pixmap = QPixmap.fromImage(self.image)
        super(RuminaSourceFile, self).__init__(QGraphicsPixmapItem(self.pixmap), parent=parent)
        self.setFlags(QGraphicsItem.ItemIsFocusable)
                
    def _hasSomePixel(self, x1, y1, x2, y2):
        if x1 < 0 or x2 < 0 or y1 < 0 or y2 < 0:
            return False
        w, h = self.image.width(), self.image.height()
        if x1 >= w or x2 >= w or y2 >= h or y1 >= h:
            return False

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                if self.image.pixelColor(x, y).alpha() > 0:
                    return True
        return False
    
    def rect(self):
        return self.pixmap.rect()
        
    def mousePressEvent(self, event):
        x = math.floor(event.pos().x())
        y = math.floor(event.pos().y())
        
        x1 = x
        y1 = y
        x2 = x
        y2 = y
        
        allClear = False

        while not allClear:
          allClear = True
          while self._hasSomePixel(x2 + 1, y1, x2 + 1, y2):
            allClear = False
            x2 = x2 + 1
          #print("done pass1", x1,y1,x2-x1+1,y2-y1+1)
          while self._hasSomePixel(x1, y2 + 1, x2, y2 + 1):
            allClear = False
            y2 = y2 + 1
          #print("done pass2", x1,y1,x2-x1+1,y2-y1+1)
          while self._hasSomePixel(x1 - 1, y1, x1 - 1, y2):
            allClear = False
            x1 = x1 - 1
          #print("done pass3", x1,y1,x2-x1+1,y2-y1+1)
          while self._hasSomePixel(x1, y1 - 1, x2, y1 - 1):
            allClear = False
            y1 = y1 - 1
          #print("done pass4", x1,y1,x2-x1+1,y2-y1+1)
        
        
        if (x1 != x2) or (y1 != y2):
            self.selectionChanged.emit(x1, y1, x2 - x1 + 1, y2 - y1 + 1)
        else:
            self.selectionCleared.emit()
        
        return super(RuminaSourceFile, self).mousePressEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            selection = self.scene().views()[0].selection
            if selection:
                self.itemAdded.emit(self, selection.toRect())
                self.selectionCleared.emit()
        return super(RuminaSourceFile, self).keyPressEvent(event)

