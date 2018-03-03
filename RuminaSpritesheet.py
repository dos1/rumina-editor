from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RuminaSpritesheet(QPixmap):
    def __init__(self, w, h):
        super(RuminaSpritesheet, self).__init__(QSize(w, h))
        self.fill(QColor('transparent'))
        self.canvas = QPainter(self)

    def paste(self, item, pos):
        item.setSpritesheetPos(QPoint(pos[0], pos[1]))
        self.canvas.drawImage(pos[0], pos[1], item.image)
        
    def save(self, url):
        self.canvas.end()
        super(RuminaSpritesheet, self).save(url)
