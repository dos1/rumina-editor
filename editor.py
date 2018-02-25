#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml
import sys
import signal
import math
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RuminaSourceFile import RuminaSourceFile
from RuminaScene import RuminaScene
from EditorUI import Ui_MainWindow
from pypacker import pack_images, sort_images_by_size

app = QApplication(sys.argv)

class RuminaEditor(QMainWindow):
    
    resized = pyqtSignal()
    
    def __init__(self, parent=None):
        super(RuminaEditor, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabs.fileChanged.connect(self.fileChanged)
        self.ui.tabWidget.currentChanged.connect(lambda x: self.ui.fileView.resize())
        self.ui.fileView.rubberBandChanged.connect(self.ui.fileView.setSelectionFromRubberBand)
        self.ui.spriteView.setDragMode(QGraphicsView.NoDrag)
        self.ui.mapView.setScene(self.ui.sceneGraphicsView.scene)
        self.ui.mapView.setInteractive(False)
                
    def loadScene(self, scene):
        self.scene = scene
        scene.render(self.ui.sceneGraphicsView.scene)
        self.ui.tabs.setTabs(self.scene.getSources())
        
    def resizeEvent(self, event):
        self.resized.emit()
        self.ui.sceneGraphicsView.resize()
        self.ui.fileView.resize()
        return super(RuminaEditor, self).resizeEvent(event)
    
    def fileChanged(self, filename):
        source = RuminaSourceFile("frozen/"+filename)
        self.ui.fileView.clear()
        self.ui.fileView.scene.addItem(source)
        source.selectionChanged.connect(self.ui.fileView.setSelection)
        source.selectionCleared.connect(self.ui.fileView.clearSelection)
        source.itemAdded.connect(self.scene.addItem)
        self.ui.fileView.scene.setSceneRect(QRectF(source.rect()))
        self.ui.fileView.resize()
    
    def show(self):
        super(RuminaEditor, self).show()
        self.ui.sceneGraphicsView.resize()
        self.ui.fileView.resize()
        
signal.signal(signal.SIGINT, signal.SIG_DFL)

window = RuminaEditor()
window.loadScene(RuminaScene("scene.ruminascene"))
window.showMaximized()
sys.exit(app.exec())
