from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RuminaPlane(QGraphicsItem):
        
    active = False
    
    nr = None
        
    def __init__(self, nr, parent=None):
        super(RuminaPlane, self).__init__(parent=parent)
        self.nr = nr
        self.setX(nr * 2400)
        self.setZValue(0)

    def boundingRect(self):
        return QRectF(0, 0, 2400, 1350)
    
    def setActive(self, active):
        self.active = active
        self.update()
    
    def paint(self, painter, option, widget):
        painter.setPen(QPen(QColor("white"), 20))
        if self.active:
            painter.setBrush(QBrush(QColor(255, 255, 255, 64)))
        painter.drawRect(QRectF((2400-1920)/2, (1350-1080)/2, 1920, 1080))

