#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import sys
import signal
from os import listdir
from os.path import isfile, join
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *

app = QApplication(sys.argv)

signal.signal(signal.SIGINT, signal.SIG_DFL)

#imagecache = {}

#frameNr = 0


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

def renderFile(name):
  fileScene.clear()
  fileScene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("lightgrey")))
  checkerboard = fileScene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("grey"), Qt.Dense3Pattern))
  checkerboard.setFlags(QGraphicsItem.ItemIgnoresTransformations)

  f = QPixmap.fromImage(QImage("frozen/" + name))
  fileScene.addPixmap(f)
  fileScene.setSceneRect(QRectF(f.rect()))

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
setActivePlane(0)

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
