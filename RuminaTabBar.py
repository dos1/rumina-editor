#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QTabBar

class RuminaTabBar(QTabBar):
    
    files = []
    fileChanged = pyqtSignal(str)
    
    def __init__(self, parent):
        super(RuminaTabBar, self).__init__(parent)
        self.setDocumentMode(True)
        self.setDrawBase(False)
        self.setShape(QTabBar.RoundedSouth)
        self.currentChanged.connect(self._currentChanged)

    def setTabs(self, tabs):
        self.clear()
        self.files = tabs
        for f in self.files:
            self.addTab(f)
            
    def _currentChanged(self, index):
        self.fileChanged.emit(self.files[index])

    def clear(self):
        count = self.count()
        for i in range(count):
            self.removeTab(0)
