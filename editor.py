#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import signal
from PyQt5.QtWidgets import *
from RuminaEditor import RuminaEditor
from RuminaScene import RuminaScene

app = QApplication(sys.argv)
        
signal.signal(signal.SIGINT, signal.SIG_DFL)

window = RuminaEditor()
window.loadScene(RuminaScene("scene.ruminascene"))
window.showMaximized()
sys.exit(app.exec())
