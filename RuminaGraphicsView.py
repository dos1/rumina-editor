#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class RuminaGraphicsView(QGraphicsView):
    
    scene = None
    selection = None
    
    def  __init__(self, parent=None):
        self.scene = QGraphicsScene()
        super(QGraphicsView, self).__init__(parent=parent)
        self.setScene(self.scene)
        self.clear()
        self.resize()
        
    def clear(self):
        self.scene.clear()
        checkerboard = self.scene.addRect(QRectF(-20000, -20000, 40000, 40000), QPen(QColor("transparent")), QBrush(QColor("grey"), Qt.Dense3Pattern))
        checkerboard.setFlags(QGraphicsItem.ItemIgnoresTransformations)
        self.selection = self.scene.addRect(QRectF(-20000, -20000, 0, 0), QPen(QColor("red")), QBrush(QColor(0,0,255, 64)))
        self.selection.setZValue(99999)

    def setSelection(self, x, y, w, h):
        self.selection.setRect(QRectF(x, y, w, h))

    def resize(self):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        """
        Zoom in or out of the view.
        """
        if not (event.modifiers() & Qt.ControlModifier):
            return super(QGraphicsView, self).wheelEvent(event)
        
        zoomFactor = 1.0 + 0.001 * event.angleDelta().y()

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
