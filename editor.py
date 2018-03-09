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
    currentItem = None
    preview = None
    
    def __init__(self, parent=None):
        super(RuminaEditor, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabs.fileChanged.connect(self.fileChanged)
        self.ui.tabWidget.currentChanged.connect(lambda x: self.ui.fileView.resize())
        self.ui.fileView.rubberBandChanged.connect(self.ui.fileView.setSelectionFromRubberBand)
        self.ui.spriteView.setDragMode(QGraphicsView.NoDrag)
        self.preview = QGraphicsPixmapItem(QPixmap(1,1))
        self.ui.spriteView.scene.addItem(self.preview)
        self.ui.mapView.setScene(self.ui.sceneGraphicsView.scene)
        self.ui.mapView.setInteractive(False)
        
        self.ui.sceneGraphicsView.keyPressed.connect(self.keyPressed)
        
        self.ui.pushButton.clicked.connect(lambda: self.scene.serialize('scene.ruminascene'))
        
        controls = [self.ui.name, self.ui.plane, self.ui.highlighted, self.ui.hidden, self.ui.x, self.ui.y, self.ui.z, self.ui.scaleVal,
                    self.ui.sx, self.ui.sy, self.ui.sw, self.ui.sh, self.ui.px, self.ui.py, self.ui.rx, self.ui.ry, self.ui.rz, self.ui.ox, self.ui.oy,
                    self.ui.intensityVal, self.ui.blendmode, self.ui.opacityVal]
        for control in controls:
            if hasattr(control, 'stateChanged'):
                control.stateChanged.connect(self.applyProperties)
            elif hasattr(control, 'textChanged'):
                control.textChanged.connect(self.applyProperties)
            elif hasattr(control, 'valueChanged'):
                control.valueChanged.connect(self.applyProperties)
            elif hasattr(control, 'currentIndexChanged'):
                control.currentIndexChanged.connect(self.applyProperties)
                
        sliders = [ self.ui.scale, self.ui.opacity, self.ui.intensity ]
        for slider in sliders:
            slider.valueChanged.connect(self.applySliders)
                
    def updateProperties(self, item):
        self.currentItem = None
        if not item:
            self.ui.tabWidgetPage1.setEnabled(False)
            self.ui.sceneGraphicsView.clearSelection()
            self.preview.setVisible(False)
            self.ui.spriteView.scene.setSceneRect(QRectF(0, 0, 0, 0))
            return
        self.ui.tabWidgetPage1.setEnabled(True)
        self.ui.name.setText(item.name)
        self.ui.plane.setValue(item.plane)
        self.ui.highlighted.setChecked(item.highlighted)
        self.ui.hidden.setChecked(item.hidden)
        self.ui.x.setValue(item.x())
        self.ui.y.setValue(item.y())
        self.ui.z.setValue(item.z)
        self.ui.scale.setValue(item.scale()*100)
        self.ui.scaleVal.setValue(item.scale())
        self.ui.sx.setValue(item.sourcePos.x())
        self.ui.sy.setValue(item.sourcePos.y())
        self.ui.sw.setValue(item.image.width())
        self.ui.sh.setValue(item.image.height())
        self.ui.px.setValue(item.px)
        self.ui.py.setValue(item.py)
        self.ui.rx.setValue(item.rx)
        self.ui.ry.setValue(item.ry)
        self.ui.rz.setValue(item.rz)
        self.ui.ox.setValue(item.ox)
        self.ui.oy.setValue(item.oy)
        self.ui.intensity.setValue(item.intensity*100)
        self.ui.intensityVal.setValue(item.intensity)
        self.ui.blendmode.setCurrentIndex(item.blending)
        self.ui.opacity.setValue(item.opacity()*100)
        self.ui.opacityVal.setValue(item.opacity())
        self.ui.filename.setText(item.source)
        self.preview.setPixmap(item.item.pixmap())
        self.preview.setVisible(True)
        self.ui.spriteView.scene.setSceneRect(QRectF(QPointF(0,0), QSizeF(item.item.pixmap().size())))
        self.ui.spriteView.fitInView(self.ui.spriteView.scene.sceneRect(), Qt.KeepAspectRatio)
        rect = item.mapToScene(item.boundingRect()).boundingRect()
        self.ui.sceneGraphicsView.setSelection(rect.x(), rect.y(), rect.width(), rect.height())
        self.currentItem = item

    
    def applyProperties(self):
        item = self.currentItem
        if not item:
            return
        item.name = self.ui.name.text()
        item.highlighted = self.ui.highlighted.isChecked()
        item.hidden = self.ui.hidden.isChecked()
        item.setX(self.ui.x.value())
        item.setY(self.ui.y.value())
        item.setZ(self.ui.z.value())
        item.setPlane(self.ui.plane.value())
        self.scene.highlightPlane(item.plane)
        item.setScale(self.ui.scaleVal.value())
        # TODO: sourcepos, width, height
        item.px = self.ui.px.value()
        item.py = self.ui.py.value()
        item.rx = self.ui.rx.value()
        item.ry = self.ui.ry.value()
        item.rz = self.ui.rz.value()
        item.ox = self.ui.ox.value()
        item.oy = self.ui.oy.value()
        item.intensity = self.ui.intensityVal.value()
        item.blending = self.ui.blendmode.currentIndex()
        item.setOpacity(self.ui.opacityVal.value())
        
        self.updateProperties(self.currentItem)
        
    def applySliders(self):
        item = self.currentItem
        if not item:
            return
        item.intensity = self.ui.intensity.value() / 100
        item.setOpacity(self.ui.opacity.value() / 100)
        item.setScale(self.ui.scale.value() / 100)
        self.updateProperties(self.currentItem)
    
    def keyPressed(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.currentItem:
                nextItem = self.scene.getNextItem(self.currentItem)
                self.currentItem.setSelected(False)
                nextItem.setSelected(True)
                nextItem.setFocus()
        if event.key() == Qt.Key_PageDown:
            if self.currentItem:
                prevItem = self.scene.getPrevItem(self.currentItem)
                self.currentItem.setSelected(False)
                prevItem.setSelected(True)
                prevItem.setFocus()
                
    def loadScene(self, scene):
        self.scene = scene
        scene.selectionChanged.connect(self.updateProperties)
        self.updateProperties(None)
        scene.render(self.ui.sceneGraphicsView.scene)
        self.ui.tabs.setTabs(self.scene.getSources())
        
    def resizeEvent(self, event):
        self.resized.emit()
        self.ui.sceneGraphicsView.resize()
        self.ui.fileView.resize()
        self.ui.mapView.resize()
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
        self.ui.mapView.resize()
        
signal.signal(signal.SIGINT, signal.SIG_DFL)

window = RuminaEditor()
window.loadScene(RuminaScene("scene.ruminascene"))
window.showMaximized()
sys.exit(app.exec())
