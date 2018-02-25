#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import sys
import signal
import math
from os import listdir
from os.path import isfile, join
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RuminaSourceFile import RuminaSourceFile
from EditorUI import Ui_MainWindow
from pypacker import pack_images, sort_images_by_size

app = QApplication(sys.argv)

class SceneElement(QGraphicsPixmapItem):
    plane = None
    
    def  __init__(self, pixmap, x, y, plane, name):
        super(QGraphicsPixmapItem, self).__init__(pixmap, parent=plane)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.plane = plane.plane
        self.setPos(x, y)
        self.name = name
        self.index = currentFileIndex
                
    def getSprite(self):
        return RuminaSprite(self.name, self, self.pos().x(), self.pos().y(), self.plane, self.index)
    
    def getImage(self):
        return self.pixmap().toImage()

class Scene(object):
    
    bg = None
    
    def __init__(self, filename):
        self.bg = QPixmap.fromImage(QImage("bg.webp"))
        
    def getSources(self):
        files = [f for f in listdir("frozen") if isfile(join("frozen", f))]
        files.sort()
        return files


class Window(QMainWindow):
    
    resized = pyqtSignal()
    
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabs.fileChanged.connect(self.fileChanged)
        self.ui.tabWidget.currentChanged.connect(lambda x: self.ui.fileView.resize())
        self.ui.fileView.rubberBandChanged.connect(self.ui.fileView.setSelectionFromRubberBand)
        self.ui.spriteView.setDragMode(QGraphicsView.NoDrag)
                
    def loadScene(self, scene):
        self.scene = scene
        self.ui.sceneGraphicsView.scene.addPixmap(self.scene.bg)
        self.ui.sceneGraphicsView.scene.setSceneRect(QRectF(self.scene.bg.rect()))
        self.ui.tabs.setTabs(self.scene.getSources())
        
    def resizeEvent(self, event):
        self.resized.emit()
        self.ui.sceneGraphicsView.resize()
        self.ui.fileView.resize()
        return super(Window, self).resizeEvent(event)
    
    def fileChanged(self, filename):
        pixmap = QPixmap.fromImage(QImage("frozen/"+filename))
        self.ui.fileView.clear()
        source = RuminaSourceFile(pixmap)
        self.ui.fileView.scene.addItem(source)
        source.selectionChanged.connect(self.ui.fileView.setSelection)
        source.selectionCleared.connect(self.ui.fileView.clearSelection)
        self.ui.fileView.scene.setSceneRect(QRectF(pixmap.rect()))
        self.ui.fileView.resize()
    
    def show(self):
        super(Window, self).show()
        self.ui.sceneGraphicsView.resize()
        self.ui.fileView.resize()
        
signal.signal(signal.SIGINT, signal.SIG_DFL)

window = Window()
window.loadScene(Scene("scene.ruminascene"))
window.showMaximized()
sys.exit(app.exec())
