#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class RuminaGraphicsView(QGraphicsView):
    
    scene = None
    selection = None
    _scale = 1
    _lastRb = None
    keyPressed = pyqtSignal(QKeyEvent)
    
    def  __init__(self, parent=None, scene=None):
        super(QGraphicsView, self).__init__(parent=parent)
        self.scene = scene if scene else QGraphicsScene(parent=self)
        self.setRenderHints(QPainter.SmoothPixmapTransform);
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor("grey"), Qt.Dense3Pattern))
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.clear()
        self.resize()
        
    def drawBackground(self, painter, rect):
        painter.setWorldMatrixEnabled(False)
        painter.fillRect(self.mapFromScene(rect).boundingRect(), self.backgroundBrush())
        painter.setWorldMatrixEnabled(True)
        painter.fillRect(self.scene.sceneRect(), QBrush(QColor(255, 255, 255, 64)))
        
    def drawForeground(self, painter, rect):
        if self.selection:
            painter.fillRect(self.selection, QBrush(QColor(0, 0, 255, 64)))
        
    def clear(self):
        self.scene.clear()
        self.clearSelection()

    def setSelection(self, x, y, w, h):
        selections = []
        if self.selection:
            selections.append(self.selection)
        self.selection = QRectF(x, y, w, h)
        selections.append(self.selection)
        self.updateScene(selections)
            
    def setSelectionFromRubberBand(self, rect, pointFrom, pointTo):
        if rect:
            self._lastRb = QRectF(pointFrom, pointTo).normalized().intersected(self.scene.sceneRect())
        else:
            self.setSelection(self._lastRb.x(), self._lastRb.y(), self._lastRb.width(), self._lastRb.height())
        
    def clearSelection(self):
        selection = self.selection
        self.selection = None
        if selection:
            self.updateScene([selection])

    def resize(self):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def keyPressEvent(self, event):
        self.keyPressed.emit(event)
        return super(RuminaGraphicsView, self).keyPressEvent(event)

    def wheelEvent(self, event):
        # Zoom in or out of the view.
        
        if not (event.modifiers() & Qt.ControlModifier):
            return super(QGraphicsView, self).wheelEvent(event)
        
        zoomFactor = 1.0 + 0.001 * event.angleDelta().y()

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        self.scale(zoomFactor, zoomFactor)
        self._scale = zoomFactor

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
