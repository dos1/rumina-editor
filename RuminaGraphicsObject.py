from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class RuminaGraphicsObject(QGraphicsObject):
    
    item = None
    
    def __init__(self, item, parent=None):
        super(RuminaGraphicsObject, self).__init__(parent=parent)
        item.setVisible(False)
        item.setParentItem(self)
        item.setBoundingRegionGranularity(1)
        self.item = item
        
    def boundingRect(self):
        return self.item.boundingRect()
        
    def shape(self):
        return self.item.shape()
    
    def paint(self, painter, option, widget):
        return self.item.paint(painter, option, widget)

