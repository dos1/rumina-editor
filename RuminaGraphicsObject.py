from PyQt5.QtWidgets import *

class RuminaGraphicsObject(QGraphicsObject):
    
    item = None
    
    def __init__(self, item, parent=None):
        super(RuminaGraphicsObject, self).__init__(parent=parent)
        item.setVisible(False)
        item.setParentItem(self)
        self.item = item
        
    def boundingRect(self):
        return self.item.boundingRect()
    
    def paint(self, painter, option, widget):
        return self.item.paint(painter, option, widget)

