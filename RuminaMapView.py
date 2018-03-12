#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RuminaItem import RuminaItem
import random

class RuminaMapView(QGraphicsView):
    
    dataScene = None
    matrix = None
    size = 1024
        
    # TODO: change to item-per-item representation, so they can be mouse-selectable
    # TODO: item order is WRONG!!!
        
    def  __init__(self, parent=None, scene=None):
        super(QGraphicsView, self).__init__(parent=parent)
        self.setScene(QGraphicsScene())
        self.image = self.scene().addPixmap(QPixmap(self.size, self.size))
        self.image.setPos(QPointF(-self.size/2, -self.size/2))
        
        self.matrix = QMatrix4x4()
        self.matrix.viewport(0, 0, self.size, self.size)
        self.matrix.ortho(-3395/2, 3395/2, -3395/2, 3395/2, 1, 3395*2)
        self.matrix.lookAt(QVector3D(2400/2, -2400, 2400/2), QVector3D(2400/2, 0, 2400/2), QVector3D(0, 0, 1))
        
        self.resize()
        
    def drawScene(self):
        pixmap = self.image.pixmap()
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor("gray"), 5))
        painter.drawArc(QRect(0, 0, self.size, self.size), 0, 5760);

        currentItem = None
        for item in self.dataScene.items():
            if item.isSelected():
                currentItem = item
                break

        painter.setPen(QPen(QColor("transparent")))
        for plane in range(4):
            planeMatrix = QMatrix4x4()
            if plane == 1:
                planeMatrix.translate(2400, 0, 0)
                planeMatrix.rotate(-90, QVector3D(0, 1, 0))
            elif plane == 2:
                planeMatrix.translate(2400, 0, 2400)
                planeMatrix.rotate(-180, QVector3D(0, 1, 0))
            elif plane == 3:
                planeMatrix.translate(0, 0, 2400)
                planeMatrix.rotate(90, QVector3D(0, 1, 0))
                
            vertices = []
            vertices.append(QVector3D(2400/2, 0, 900))
            vertices.append(QVector3D(2400/2 - 2*1920/2, 0, -900))
            vertices.append(QVector3D(2400/2 + 2*1920/2, 0, -900))
            mapped = [ self.matrix.map(planeMatrix.map(vertex)) for vertex in vertices ]
            flattened = [ QPointF(vec[0], vec[1]) for vec in mapped ]
            if currentItem and plane == currentItem.plane:
                painter.setBrush(QBrush(QColor(0, 0, 255, 32)))
            else:
                painter.setBrush(QBrush(QColor(0, 0, 255, 16)))
            painter.drawPolygon(QPolygonF(flattened))
        
        beforeCurrent = True
        for item in self.dataScene.items():
            if not isinstance(item, RuminaItem):
                continue
            color = "black"
            if beforeCurrent:
                color = "gray"
            if item.isSelected():
                beforeCurrent = False
            painter.setPen(QPen(QColor("red" if item.isSelected() else color), 10))
            painter.setBrush(QBrush(QColor(255 if item.isSelected() else 0, 0, 0, 32)))
            polygon = item.mapToScene(item.boundingRect())
            #polygon = QPolygonF(QRectF(2400 * item.plane, 0, 1920*1.25, 1080*1.25))
            #print("polygon", item)
            planeMatrix = QMatrix4x4()
            
            if item.plane == 1:
                planeMatrix.translate(2400, 0, 0)
                planeMatrix.rotate(-90, QVector3D(0, 1, 0))
            elif item.plane == 2:
                planeMatrix.translate(2400, 0, 2400)
                planeMatrix.rotate(-180, QVector3D(0, 1, 0))
            elif item.plane == 3:
                planeMatrix.translate(0, 0, 2400)
                planeMatrix.rotate(90, QVector3D(0, 1, 0))
                
            # z-scale adjustment
            factor = 1.0 - (item.z / (2400 / 2.0 - 2400 / 8.0 - 0.01))
            planeMatrix.translate(2400 / 2, 1350 / 2, 0)
            planeMatrix.scale(factor, factor, 1)
            planeMatrix.translate(-2400 / 2, 1350 / 2, 0)                
                
            planeMatrix.translate((item.x() + item.image.width() * item.px), (item.y() + item.image.height() * item.py), item.z) 
            planeMatrix.rotate(item.ry, QVector3D(0, 1, 0))
            planeMatrix.rotate(item.rx, QVector3D(1, 0, 0))
            #planeMatrix.rotate(item.rz, QVector3D(0, 0, 1)) # already taken care by QGraphicsView
            planeMatrix.translate(-(item.x() + item.image.width() * item.px), -(item.y() + item.image.height() * item.py), -item.z) 
                        
            planeMatrix.translate(-2400*item.plane, 0, 0)
                
            for i in range(polygon.size()):
                point = polygon[i]
                vec1 = planeMatrix.map(QVector3D(point.x(), point.y(), item.z))
                vec = self.matrix.map(vec1)
                polygon[i] = QPointF(vec[0], vec[1])
                #print(polygon[i])
            painter.drawPolygon(polygon)
        painter.end()
        self.image.setPixmap(pixmap)
        
    def setDataScene(self, scene):
        self.dataScene = scene
        scene.changed.connect(self.drawScene)
        self.update()
    
    def resize(self):
        if self.scene():
            self.fitInView(QRectF(-self.size/2, -self.size/2, self.size, self.size), Qt.KeepAspectRatio)
