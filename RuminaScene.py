from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RuminaItem import RuminaItem
from RuminaPlane import RuminaPlane
from os import listdir
from os.path import isfile, join
import struct

class RuminaScene(object):
    
    bg = None
    planes = None
    scene = None
    items = None
    
    class Serializer(object):
        
        f = None
        def __init__(self, f):
            self.f = f
        
        def writeString(self, string):
            if not string:
                string = ''
            utf = string.encode('utf-8')
            self.writeUInt32(len(utf))
            self.f.write(utf)
            
        def writeUInt32(self, val):
            self.f.write(struct.pack('I', val))
            
        def writeUInt8(self, val):
            self.f.write(struct.pack('B', val))
            
        def writeBool(self, val):
            self.f.write(struct.pack('?', val))
            
        def writeDouble(self, val):
            self.f.write(struct.pack('d', val))
            
        def writeItem(self, item):
            self.writeString(item.name)
            self.writeString(item.source.filename)
            self.writeUInt8(item.plane)
            self.writeBool(item.highlighted)
            self.writeBool(item.hidden)
            self.writeDouble(item.pos().x())
            self.writeDouble(item.pos().y())
            self.writeDouble(item.z)
            self.writeDouble(item.zOffset)
            self.writeDouble(item.scale)
            self.writeUInt32(item.sourcePos.x())
            self.writeUInt32(item.sourcePos.y())
            self.writeUInt32(item.image.width())
            self.writeUInt32(item.image.height())
            self.writeDouble(item.px)
            self.writeDouble(item.py)
            self.writeDouble(item.rx)
            self.writeDouble(item.ry)
            self.writeDouble(item.rz)
            self.writeDouble(item.ox)
            self.writeDouble(item.oy)
            self.writeDouble(item.intensity)
            self.writeDouble(item.speed)
            self.writeUInt8(item.blending)
            self.writeDouble(item.opacity)
            self.writeUInt32(item.spritesheetPos.width())
            self.writeUInt32(item.spritesheetPos.height())
        
    def __init__(self, filename=None):
        self.bg = QPixmap.fromImage(QImage("bg.webp"))
        self.planes = [RuminaPlane(i) for i in range(4)]
        self.items = []
        if filename:
            self.deserialize(filename)
        
    def getSources(self):
        files = [f for f in listdir("frozen") if isfile(join("frozen", f))]
        files.sort()
        return files
    
    def serialize(self, filename):
        with open(filename, 'wb') as f:
            serializer = self.Serializer(f)
            serializer.writeString('bg.webp')
            version = 0
            serializer.writeUInt32(version)
            serializer.writeUInt32(len(self.items))
            for item in self.items:
                serializer.writeItem(item)
        
    def deserialize(self, filename):
        with open(filename, 'rb') as f:
            pass
    
    def render(self, scene):
        self.scene = scene
        scene.clear()
        scene.addPixmap(self.bg)
        scene.setSceneRect(QRectF(self.bg.rect()))
        for plane in self.planes:
            scene.addItem(plane)

        for item in self.items:
            self._renderItem(self.items)
            
    def _renderItem(self, item):
        if not self.scene:
            return
        plane = self.planes[item.plane]
        item.setParentItem(plane)
        
    def _removeItem(self, item):
        self.items.remove(item)
            
    def addItem(self, source, rect):
        plane = rect.x() // 2400
        item = RuminaItem(source.pixmap.copy(rect))
        item.setPos(QPointF(rect.x() - plane*2400, rect.y()))
        item.setSourcePos(rect.topLeft())
        item.setZValue(0) # Qt
        item.setZ(0)
        item.setZOffset(0)
        item.setPlane(plane)
        item.setSource(source)
        item.itemRemoved.connect(self._removeItem)
        self.items.append(item)
        self._renderItem(item)
