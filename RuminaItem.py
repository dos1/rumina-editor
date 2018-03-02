from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from RuminaGraphicsObject import RuminaGraphicsObject

class RuminaItem(RuminaGraphicsObject):
    
    image = None
    source = None
    plane = None
    z = 0
    zOffset = 0
    highlighted = False
    hidden = None
    scale = 1
    px = 0.5
    py = 0.5
    rx = 0
    ry = 0
    rz = 0
    ox = 0.5
    oy = 0.5
    intensity = 0
    speed = 0
    blending = 0
    opacity = 1
    spritesheetPos = None
    sourcePos = None
    itemRemoved = pyqtSignal(RuminaGraphicsObject)
    padding = 10
    name = None
    
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
