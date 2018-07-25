from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RuminaItem import RuminaItem
from RuminaPlane import RuminaPlane
from RuminaGraphicsObject import RuminaGraphicsObject
from RuminaSpritesheet import RuminaSpritesheet
from os import listdir
from os.path import isfile, join
import struct
from pypacker import pack_images, sort_images_by_size

class RuminaScene(QObject):
    
    bg = None
    planes = None
    scene = None
    items = None
    selectionChanged = pyqtSignal(RuminaGraphicsObject)
    
    class Deserializer(object):
        f = None
        
        class InvalidSceneException(Exception):
            pass
        
        class MalformedStringException(Exception):
            pass
        
        version = None
        
        def __init__(self, f):
            self.f = f
            rumina = self.f.read(6)
            if rumina != b'RUMINA':
                raise RuminaScene.Deserializer.InvalidSceneException(rumina)
            self.version = self.readUInt32()
            
        def readString(self):
            length = self.readUInt8()
            val = self.read(length).decode('utf-8')
            zero = self.read(1)
            if zero != b'\0':
                raise RuminaScene.Deserializer.MalformedStringException(length, val, zero)
            return val
            
        def readUInt8(self):
            (val,) = self.unpack('<B')
            return val

        def readUInt32(self):
            (val,) = self.unpack('<I')
            return val

        def readBool(self):
            (val,) = self.unpack('<?')
            return val

        def readDouble(self):
            (val,) = self.unpack('<d')
            return val
        
        def setSpritesheet(self, filename):
            self.spritesheet = QPixmap(filename)
        
        def readItem(self):
            name = self.readString()
            source_filename = self.readString()
            plane = self.readUInt8()
            curved = self.readBool()
            hidden = self.readBool()
            x = self.readDouble()
            y = self.readDouble()
            z = self.readDouble()
            zOffset = self.readDouble()
            scale = self.readDouble()
            spritesheetX = self.readUInt32()
            spritesheetY = self.readUInt32()
            width = self.readUInt32()
            height = self.readUInt32()
            sourceX = self.readUInt32()
            sourceY = self.readUInt32()
            px = self.readDouble()
            py = self.readDouble()
            rx = self.readDouble()
            ry = self.readDouble()
            rz = self.readDouble()
            ox = self.readDouble()
            oy = self.readDouble()
            intensity = self.readDouble()
            speed = self.readDouble()
            blending = self.readUInt8()
            opacity = self.readDouble()
            
            item = RuminaItem(self.spritesheet.copy(spritesheetX, spritesheetY, width, height))
            item.name = name
            item.source = source_filename
            item.setPlane(plane)
            item.curved = curved
            item.hidden = hidden
            item.setPos(QPointF(x, y))
            item.setZ(z)
            item.setZOffset(zOffset)
            item.setSpritesheetPos(QPointF(spritesheetX, spritesheetY))
            item.setSourcePos(QPoint(sourceX, sourceY))
            item.setScale(scale)
            item.setPivot(px, py)
            item.setRotation(rx, ry, rz)
            item.ox = ox
            item.oy = oy
            item.intensity = intensity
            item.speed = speed
            item.blending = blending
            item.setOpacity(opacity)
            
            return item
        
        def read(self, count):
            return self.f.read(count)
        
        def unpack(self, fmt):
            return struct.unpack(fmt, self.f.read(struct.calcsize(fmt)))
    
    class Serializer(object):
        
        f = None
        def __init__(self, f):
            self.f = f
        
        def writeString(self, string):
            if not string:
                string = ''
            utf = string.encode('utf-8')
            self.writeUInt8(len(utf))
            self.write(utf)
            self.write(bytes([0]))
            
        def writeUInt32(self, val):
            self.write(struct.pack('<I', val))
            
        def writeUInt8(self, val):
            self.write(struct.pack('<B', val))
            
        def writeBool(self, val):
            self.write(struct.pack('<?', val))
            
        def writeDouble(self, val):
            self.write(struct.pack('<d', val))
            
        def writeItem(self, item):
            self.writeString(item.name)
            self.writeString(item.source)
            self.writeUInt8(item.plane)
            self.writeBool(item.curved)
            self.writeBool(item.hidden)
            self.writeDouble(item.pos().x())
            self.writeDouble(item.pos().y())
            self.writeDouble(item.z)
            self.writeDouble(item.zOffset)
            self.writeDouble(item.scale())
            self.writeUInt32(int(item.spritesheetPos.x()))
            self.writeUInt32(int(item.spritesheetPos.y()))
            self.writeUInt32(item.image.width())
            self.writeUInt32(item.image.height())
            self.writeUInt32(item.sourcePos.x())
            self.writeUInt32(item.sourcePos.y())
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
            self.writeDouble(item.opacity())
            
        def write(self, val):
            self.f.write(val)
        
    def __init__(self, filename=None):
        super(RuminaScene, self).__init__()
        self.bg = QPixmap.fromImage(QImage("bg.webp"))
        self.planes = [RuminaPlane(i) for i in range(4)]
        self.items = []
        if filename:
            self.deserialize(filename)
        
    def getSources(self):
        files = [f for f in listdir("frozen") if isfile(join("frozen", f))]
        files.sort()
        return files
    
    def serialize(self, filename, quickSave=False):
        ss_filename = filename+'.webp'

        if not quickSave:
            sorted_items = sort_images_by_size(self.items)
            image_packing = pack_images(sorted_items, True, () )
            ss = RuminaSpritesheet(image_packing.rect.wd, image_packing.rect.hgt)
            image_packing.render(ss)
            ss.save(ss_filename, quality=100)

        with open(filename, 'wb') as f:
            serializer = RuminaScene.Serializer(f)
            serializer.write(b'RUMINA')
            version = 1
            serializer.writeUInt32(version) # version
            serializer.writeString(ss_filename) # filename
            serializer.writeString('bg.webp') # background
            serializer.writeDouble(0) # bg_distance
            serializer.writeUInt32(len(self.items)) # number_of_items
            for item in self.items: #TODO: sort by ZValue/drawing order
                serializer.writeItem(item)
        
    def deserialize(self, filename):
        with open(filename, 'rb') as f:
            deserializer = RuminaScene.Deserializer(f)
            filename = deserializer.readString()
            background = deserializer.readString()
            bg_distance = deserializer.readDouble()
            deserializer.setSpritesheet(filename)
            
            items = deserializer.readUInt32()
            for i in range(items):
                item = deserializer.readItem()
                item.setZValue(i)
                self.items.append(item)
            
            #print(filename, background, bg_distance)

    def getNextItem(self, item):
        idx = self.items.index(item)
        idx = idx + 1
        if idx == len(self.items):
            idx = 0
        return self.items[idx]
    
    def getPrevItem(self, item):
        idx = self.items.index(item)
        idx = idx - 1
        if idx == -1:
            idx = len(self.items) - 1
        return self.items[idx]
    
    def render(self, scene):
        self.scene = scene
        scene.clear()
        scene.addPixmap(self.bg)
        scene.setSceneRect(QRectF(self.bg.rect()))
        for plane in self.planes:
            scene.addItem(plane)

        for item in self.items:
            self._renderItem(item)
            
        scene.selectionChanged.connect(self._updateProperties)
            
            
    def highlightPlane(self, nr):
        for plane in self.planes:
            plane.setActive(False)
        if nr is not None:
            self.planes[nr].setActive(True)
        
    def _updateProperties(self):
        sel = self.scene.selectedItems()
        if len(sel) == 1:
            self.selectionChanged.emit(sel[0])
            self.highlightPlane(sel[0].plane)
        else:
            self.selectionChanged.emit(None)
            self.highlightPlane(None)
            
    def _renderItem(self, item):
        if not self.scene:
            return
        #print(item)
        plane = self.planes[item.plane]
        item.setParentItem(plane)
        item.planes = self.planes
        item.xChanged.connect(self._updateProperties)
        item.yChanged.connect(self._updateProperties)
        item.zChanged.connect(self._updateProperties)
        item.rotationChanged.connect(self._updateProperties)
        item.parentChanged.connect(self._updateProperties)
        
    def _removeItem(self, item):
        self.items.remove(item)
            
    def addItem(self, source, rect):
        plane = rect.x() // 2400
        item = RuminaItem(source.pixmap.copy(rect))
        item.setPos(QPointF(rect.x() - plane*2400, rect.y()))
        item.setSourcePos(rect.topLeft())
        item.setZValue(len(self.items)) # Qt
        item.setZ(0)
        item.setZOffset(0)
        item.setPlane(plane)
        item.setSource(source)
        item.itemRemoved.connect(self._removeItem)
        self.items.append(item)
        self._renderItem(item)
