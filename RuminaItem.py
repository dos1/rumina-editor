from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from RuminaGraphicsObject import RuminaGraphicsObject

class RuminaItem(RuminaGraphicsObject):
    
    image = None
    source = None
    plane = None
    planes = None
    z = 0
    zOffset = 0
    highlighted = False
    hidden = None
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
    spritesheetPos = None
    sourcePos = None
    itemRemoved = pyqtSignal(RuminaGraphicsObject)
    zChanged = pyqtSignal(float)
    padding = 10
    name = None
    
    def __init__(self, pixmap, parent=None):
        super(RuminaItem, self).__init__(QGraphicsPixmapItem(pixmap), parent=parent)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.image = pixmap.toImage()
        
    def __repr__(self):
        return "<RuminaItem '%s' @ plane %d, pos %dx%d, size %dx%d, spritesheet pos %dx%d>" % (self.name, self.plane, self.pos().x(), self.pos().y(), self.image.width(), self.image.height(), self.spritesheetPos.x() if self.spritesheetPos else -1, self.spritesheetPos.y() if self.spritesheetPos else -1)
        
    def setPlane(self, plane):
        if self.plane is not None:
            offset = plane * 2400 - self.plane * 2400
            self.setX(self.x() - offset)
        self.plane = plane
        if self.planes:
            self.setParentItem(self.planes[plane])
        
    def setZ(self, z):
        self.z = z
        self.zChanged.emit(z)
        
    def setZOffset(self, zOffset):
        self.zOffset = zOffset

    def setSource(self, source):
        self.source = source.filename
        
    def remove(self):
        self.scene().removeItem(self)
        self.itemRemoved.emit(self)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remove()
        if event.key() == Qt.Key_W:
            self.setY(self.y() - 1)
        if event.key() == Qt.Key_A:
            self.setX(self.x() - 1)
        if event.key() == Qt.Key_S:
            self.setY(self.y() + 1)
        if event.key() == Qt.Key_D:
            self.setX(self.x() + 1)
        if event.key() == Qt.Key_Q:
            self.setZ(self.z - 10)
        if event.key() == Qt.Key_E:
            self.setZ(self.z + 10)
        if event.key() == Qt.Key_Z:
            newPlane = self.plane - 1
            if newPlane == -1:
                newPlane = 3
            self.setPlane(newPlane)
        if event.key() == Qt.Key_X:
            newPlane = self.plane + 1
            if newPlane == 4:
                newPlane = 0
            self.setPlane(newPlane)
        return super(RuminaItem, self).keyPressEvent(event)
    
    def setSpritesheetPos(self, pos):
        self.spritesheetPos = pos
        
    def setSourcePos(self, pos):
        self.sourcePos = pos
        
    def paint(self, painter, option, widget):
        if self.blending == 1:
            painter.setCompositionMode(QPainter.CompositionMode_Multiply)
        super(RuminaItem, self).paint(painter, option, widget)

    # pypacker's interface
    def get_size(self):
        return (self.image.width() + 2 * self.padding, self.image.height() + 2 * self.padding)
