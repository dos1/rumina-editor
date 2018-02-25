from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RuminaItem import RuminaItem
from RuminaPlane import RuminaPlane
from os import listdir
from os.path import isfile, join

class RuminaScene(object):
    
    bg = None
    planes = None
    scene = None
    items = None
    
    def __init__(self, filename):
        self.bg = QPixmap.fromImage(QImage("bg.webp"))
        self.planes = [RuminaPlane(i) for i in range(4)]
        self.items = []
        
    def getSources(self):
        files = [f for f in listdir("frozen") if isfile(join("frozen", f))]
        files.sort()
        return files
    
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
        item.setZValue(0)
        item.setZ(0)
        item.setZOffset(0)
        item.setPlane(plane)
        item.setSource(source)
        item.itemRemoved.connect(self._removeItem)
        self.items.append(item)
        self._renderItem(item)
