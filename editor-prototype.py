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
from pypacker import pack_images, sort_images_by_size

app = QApplication(sys.argv)

signal.signal(signal.SIGINT, signal.SIG_DFL)

lastPlane = -1

results = []

class RuminaSpriteSheet:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.pixmap = QPixmap(QSize(w,h))
        self.pixmap.fill(QColor('transparent'))
        self.canvas = QPainter(self.pixmap)

    def paste(self, image, pos):
        global lastPlane
        #print(image.sprite, pos)
        #if lastPlane != image.sprite.plane:
        #  print('SwitchPlane(l, cam, %d);' % image.sprite.plane)
        #  lastPlane = image.sprite.plane
          
        #print('DrawScenePart(game, data->sceneBitmap, %d, %d, %d, %d, l, cam, %d, %d); // %s' % (pos[0], pos[1], image.width(), image.height(), image.sprite.x, image.sprite.y, image.sprite.sprite_name))
        results.append((pos[0], pos[1], image.width(), image.height(), image.sprite.x - (2400 * image.sprite.plane), image.sprite.y, image.sprite.plane, image.sprite.index, image.sprite.sprite_name))
        self.canvas.drawImage(pos[0], pos[1], image)

class RuminaSprite:
    def __init__(self, name, element, x, y, plane, file_index):
        self.sprite_name = name
        self.index = file_index
        self.image = element.getImage()
        self.element = element
        self.image.sprite = self
        self.padding = 10
        self.x = x
        self.y = y
        self.plane = plane

    def __repr__(self):
        return '<RuminaSprite %s at %d,%d; %dx%d +%d on plane %d>' % (self.sprite_name, self.x, self.y, self.image.width(), self.image.height(), self.padding, self.plane)

    def get_size(self):
        (w,h) = self.image.width(), self.image.height();
        return (self.image.width() + 2*self.padding, self.image.height() + 2*self.padding)


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
          print("done pass1", x1,y1,x2-x1+1,y2-y1+1)
          while hasSomePixel(image, x1, y2 + 1, x2, y2 + 1):
            allClear = False
            y2 = y2 + 1
          print("done pass2", x1,y1,x2-x1+1,y2-y1+1)
          while hasSomePixel(image, x1 - 1, y1, x1 - 1, y2):
            allClear = False
            x1 = x1 - 1
          print("done pass3", x1,y1,x2-x1+1,y2-y1+1)
          while hasSomePixel(image, x1, y1 - 1, x2, y1 - 1):
            allClear = False
            y1 = y1 - 1
          print("done pass4", x1,y1,x2-x1+1,y2-y1+1)
        
        print(x1,y1,x2-x1+1,y2-y1+1)
        #print(lastFileSelection.rect().x(), lastFileSelection.rect().y())
        if lastFileSelection.rect().x() == x1 and lastFileSelection.rect().y() == y1:
          return super(SourceItem, self).mousePressEvent(event)
        
        lastFileSelection.setRect(QRectF(x1, y1, x2 - x1 + 1, y2 - y1 + 1))

        plane = activePlane
        if plane == None:
          plane = x1 // 2400
          #setActivePlane(plane)
        SceneElement(self.pixmap().copy(x1, y1, x2 - x1 + 1, y2 - y1 + 1), x1, y1, planes[plane], currentFile)
        
        
        #print(self.pixmap().toImage().pixelColor(event.pos().x(), event.pos().y()))
        return super(SourceItem, self).mousePressEvent(event)

class RuminaGraphicsView(QGraphicsView):
  def  __init__(self, parent=None):
    super(QGraphicsView, self).__init__(parent=parent)

  def wheelEvent(self, event):
    """
    Zoom in or out of the view.
    """
    if not (event.modifiers() & Qt.ControlModifier):
      return super(QGraphicsView, self).wheelEvent(event)
    zoomInFactor = 1.0 + 0.001 * event.angleDelta().y()
    zoomOutFactor = 1 / zoomInFactor

    # Save the scene pos
    oldPos = self.mapToScene(event.pos())

    # Zoom
    #if event.angleDelta().y() > 0:
    zoomFactor = zoomInFactor
    #else:
    #    zoomFactor = zoomOutFactor
    self.scale(zoomFactor, zoomFactor)

    # Get the new position
    newPos = self.mapToScene(event.pos())

    # Move scene to old position
    delta = newPos - oldPos
    self.translate(delta.x(), delta.y())

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
      planes[i].setBrush(QBrush(QColor(255, 255, 255, 32 if activePlane == i else 0)))

def selectionChanged():
  items = scene.selectedItems()
  if len(items):
    setActivePlane(items[0].plane)
  else:
    setActivePlane(None)

def renderFile(name):
  global lastFileSelection, currentFile
  fileScene.clear()
  currentFile = name
  #fileScene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("lightgrey")))
  checkerboard = fileScene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("grey"), Qt.Dense3Pattern))
  checkerboard.setFlags(QGraphicsItem.ItemIgnoresTransformations)

  f = QPixmap.fromImage(QImage("frozen/" + name))
  fileScene.addItem(SourceItem(f))
  fileScene.setSceneRect(QRectF(f.rect()))
  
  lastFileSelection = fileScene.addRect(QRectF(0, 0, 0, 0), QPen(QColor("red")), QBrush(QColor(0,0,255, 64)))

  fileView.setScene(fileScene)
  fileView.fitInView(fileScene.sceneRect(), Qt.KeepAspectRatio)

def fileChanged(index):
  global currentFileIndex
  currentFileIndex = index
  renderFile(files[index])
  
def doStuff():
  global lastPlane, results
  lastPlane = -1
  items = [ x.getSprite() for x in scene.items() if isinstance(x, SceneElement) ]
  sorted_items = sort_images_by_size(items)
  image_packing = pack_images(sorted_items, True, () )
  print('Packed into size', image_packing.rect.wd, image_packing.rect.hgt)
  results = []
  ss = RuminaSpriteSheet(image_packing.rect.wd, image_packing.rect.hgt)
  image_packing.render(ss)
  ss.canvas.end()
  ss.pixmap.save("output.png")
  #print(results)
  results_sorted = sorted(results, key = lambda x: x[8])
  #results_sorted.reverse()
  #          results.append((pos[0], pos[1], image.width(), image.height(), image.sprite.x, image.sprite.y, image.sprite.sprite_name, image.sprite.plane, image.sprite.index))

  for res in results_sorted:
    #if lastPlane != res[7]:
    #  print('SwitchPlane(l, cam, %d);' % res[7])
    #  lastPlane = res[7]
          
    #print(res)
    print('DrawScenePart(game, data->sceneBitmap, %d, %d, %d, %d, l, cam, %d, %d, %d, %d); // %s' % res)

  print('done')

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

view = RuminaGraphicsView()
bg = QPixmap.fromImage(QImage("bg.webp"))
scene = QGraphicsScene()


#scene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("lightgrey")))
checkerboard = scene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("grey"), Qt.Dense3Pattern))
checkerboard.setFlags(QGraphicsItem.ItemIgnoresTransformations)

scene.addPixmap(bg)
scene.setSceneRect(QRectF(bg.rect()))

scene.selectionChanged.connect(selectionChanged)

activePlane = None
currentFile = None
currentFileIndex = None
planes = []


planes = [scene.addRect(QRectF(240+2400*i, 135, 1920, 1080), QPen(QColor("white"), 20)) for i in range(4)];

for i in range(4):
  #planes[i].setFlags(QGraphicsItem.ItemIsSelectable)
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

fileView = RuminaGraphicsView()

fileScene = QGraphicsScene()
lastFileSelection = None
renderFile(files[0])
currentFileIndex = 0

vbox.addWidget(fileView)

widget = QWidget()
widget.setLayout(vbox)
w.setCentralWidget(widget)

w.resized.connect(onResize)


button = QPushButton("do stuff")
#button.setLabel("do stuff")
button.clicked.connect(doStuff)
vbox.addWidget(button)
#loadFrameData()
#advanceFrame()
#QTimer.singleShot(0, advanceFrame)

w.show()

sys.exit(app.exec_())
