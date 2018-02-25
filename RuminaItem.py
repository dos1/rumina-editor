from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from RuminaGraphicsObject import RuminaGraphicsObject

class RuminaItem(RuminaGraphicsObject):
    
    image = None
    source = None
    plane = None
    z = None
    zOffset = None
    spritesheetPos = None
    sourcePos = None
    itemRemoved = pyqtSignal(RuminaGraphicsObject)
    padding = 10
    
    def __init__(self, pixmap, parent=None):
        super(RuminaItem, self).__init__(QGraphicsPixmapItem(pixmap), parent=parent)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.image = pixmap.toImage()
        
    def setPlane(self, plane):
        self.plane = plane
        
    def setZ(self, z):
        self.z = z
        
    def setZOffset(self, zOffset):
        self.zOffset = zOffset

    def setSource(self, source):
        self.source = source
        
    def remove(self):
        self.scene().removeItem(self)
        self.itemRemoved.emit(self)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remove()
        return super(RuminaItem, self).keyPressEvent(event)
    
    def setSpritesheetPos(self, pos):
        self.spritesheetPos = pos
        
    def setSourcePos(self, pos):
        self.sourcePos = pos

    # pypacker's interface
    def get_size(self):
        return (self.image.width() + 2 * self.padding, self.image.height() + 2 * self.padding)
