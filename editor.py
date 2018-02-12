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
from PyQt5.QtMultimedia import *

app = QApplication(sys.argv)

signal.signal(signal.SIGINT, signal.SIG_DFL)

def hasSomePixel(image, x1, y1, x2, y2):
  if x1 < 0 or x2 < 0 or y1 < 0 or y2 < 0:
    return False
  w, h = image.width(), image.height()
  if x1 >= w or x2 >= w or y2 >= h or y1 >= h:
    return False

  for x in range(x1, x2 + 1):
    for y in range(y1, y2 + 1):
      #print(x, y, image.pixelColor(x, y).alpha())
      if image.pixelColor(x, y).alpha() > 0:
        return True
  return False  

class SceneElement(QGraphicsPixmapItem):
    plane = None
    
    def  __init__(self, pixmap, x, y, plane):
        super(QGraphicsPixmapItem, self).__init__(pixmap, parent=plane)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.plane = plane.plane
        self.setPos(x, y)

class SourceItem(QGraphicsPixmapItem):
        
    def mousePressEvent(self, event):
        x = math.floor(event.pos().x())
        y = math.floor(event.pos().y())
        image = self.pixmap().toImage()
        
        
        x1 = x
        y1 = y
        x2 = x
        y2 = y
        
        allClear = False

        while not allClear:
          allClear = True
          while hasSomePixel(image, x2 + 1, y1, x2 + 1, y2):
            allClear = False
            x2 = x2 + 1
          while hasSomePixel(image, x1, y2 + 1, x2, y2 + 1):
            allClear = False
            y2 = y2 + 1
          while hasSomePixel(image, x1 - 1, y1, x1 - 1, y2):
            allClear = False
            x1 = x1 - 1
          while hasSomePixel(image, x1, y1 - 1, x2, y1 - 1):
            allClear = False
            y1 = y1 - 1
          #print("done pass", x1,y1,x2-x1+1,y2-y1+1)
        
        print(x1,y1,x2-x1+1,y2-y1+1)
        
        lastFileSelection.setRect(QRectF(x1, y1, x2 - x1 + 1, y2 - y1 + 1))
        plane = activePlane
        if plane == None:
          plane = x1 // 2400
          #setActivePlane(plane)
        scene.addItem(SceneElement(self.pixmap().copy(x1, y1, x2 - x1 + 1, y2 - y1 + 1), x1, y1, planes[plane]))
        
        
        #print(self.pixmap().toImage().pixelColor(event.pos().x(), event.pos().y()))
        return super(SourceItem, self).mousePressEvent(event)

class Window(QMainWindow):
    resized = pyqtSignal()
    def  __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)

    def resizeEvent(self, event):
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

def onResize():
  view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
  fileView.fitInView(fileScene.sceneRect(), Qt.KeepAspectRatio)

def setActivePlane(plane):
  global activePlane
  activePlane = plane
  for i in range(4):
      planes[i].setBrush(QBrush(QColor(255, 255, 255, 64 if activePlane == i else 0)))

def selectionChanged():
  items = scene.selectedItems()
  if len(items):
    setActivePlane(items[0].plane)
  else:
    setActivePlane(None)

def renderFile(name):
  global lastFileSelection
  fileScene.clear()
  fileScene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("lightgrey")))
  checkerboard = fileScene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("grey"), Qt.Dense3Pattern))
  checkerboard.setFlags(QGraphicsItem.ItemIgnoresTransformations)

  f = QPixmap.fromImage(QImage("frozen/" + name))
  fileScene.addItem(SourceItem(f))
  fileScene.setSceneRect(QRectF(f.rect()))
  
  lastFileSelection = fileScene.addRect(QRectF(0, 0, 0, 0), QPen(QColor("red")), QBrush(QColor(0,0,255, 64)))

  fileView.setScene(fileScene)
  fileView.fitInView(fileScene.sceneRect(), Qt.KeepAspectRatio)

def fileChanged(index):
  renderFile(files[index])

#def fileChanged(name):
#  print("Detected changed file", name)
#  if name in imagecache:
#    del imagecache[name]
#  else:
#    print(name, "was not loaded!")

#watcher = QFileSystemWatcher()
#watcher.fileChanged.connect(fileChanged)

#seqends = None
#frames = None

w = Window()
w.setWindowTitle('Rumina Editor')

view = QGraphicsView()
bg = QPixmap.fromImage(QImage("bg.webp"))
scene = QGraphicsScene()


scene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("lightgrey")))
checkerboard = scene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("grey"), Qt.Dense3Pattern))
checkerboard.setFlags(QGraphicsItem.ItemIgnoresTransformations)

scene.addPixmap(bg)
scene.setSceneRect(QRectF(bg.rect()))

scene.selectionChanged.connect(selectionChanged)

activePlane = None
planes = []


planes = [scene.addRect(QRectF(240+2400*i, 135, 1920, 1080), QPen(QColor("white"), 20)) for i in range(4)];

for i in range(4):
  planes[i].setFlags(QGraphicsItem.ItemIsSelectable)
  planes[i].plane = i

view.setScene(scene)
view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)

vbox = QVBoxLayout()

vbox.addWidget(view)



tabs = QTabBar()
#tabs.addTab("podglad_calej_sceny03.png")
files = [f for f in listdir("frozen") if isfile(join("frozen", f))]
files.sort()
for f in files:
  tabs.addTab(f)
tabs.setDocumentMode(True)
tabs.setDrawBase(False)
tabs.currentChanged.connect(fileChanged)
vbox.addWidget(tabs)

fileView = QGraphicsView()

fileScene = QGraphicsScene()
lastFileSelection = None
renderFile(files[0])

vbox.addWidget(fileView)

widget = QWidget()
widget.setLayout(vbox)
w.setCentralWidget(widget)

w.resized.connect(onResize)
#loadFrameData()
#advanceFrame()
#QTimer.singleShot(0, advanceFrame)

w.show()

sys.exit(app.exec_())
